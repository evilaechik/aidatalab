"""Build a public, reproducible employer-establishment entry model for peer metros.

This script uses Census Business Dynamics Statistics (BDS) metro data.  It
predicts next-year employer-establishment entries, not a constructed score and
not the arrival of identifiable large corporations.  All predictors are
lagged one year before the outcome.
"""

from __future__ import annotations

from pathlib import Path
import warnings

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Lasso, PoissonRegressor, Ridge
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore", category=UserWarning, module="xgboost")

try:
    from xgboost import XGBRegressor
except ImportError:  # pragma: no cover - explicit error is clearer than silent omission
    XGBRegressor = None

try:
    from catboost import CatBoostRegressor
except ImportError:  # pragma: no cover
    CatBoostRegressor = None


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "business_entry_models"
RAW_PATH = DATA_DIR / "raw_inputs" / "census_bds_2023_msa.csv"

# 2023 OMB metropolitan statistical area codes.  The research unit remains
# metro-wide; these results must not be interpreted as City of Atlanta results.
METROS = {
    12060: "Atlanta",
    12420: "Austin",
    16740: "Charlotte",
    19100: "Dallas",
    19740: "Denver",
    26420: "Houston",
    34980: "Nashville",
    39580: "Raleigh",
    33100: "Miami",
    12580: "Baltimore",
    14460: "Boston",
    16980: "Chicago",
    17140: "Cincinnati",
    18140: "Columbus OH",
    26900: "Indianapolis",
    28140: "Kansas City",
    31080: "Los Angeles",
    33460: "Minneapolis",
    35620: "New York",
    36740: "Orlando",
    37980: "Philadelphia",
    38060: "Phoenix",
    38300: "Pittsburgh",
    38900: "Portland OR",
    41620: "Salt Lake City",
    41700: "San Antonio",
    41740: "San Diego",
    41860: "San Francisco",
    42660: "Seattle",
    45300: "Tampa",
    47900: "Washington DC",
}

NUMERIC_COLUMNS = [
    "firms",
    "estabs",
    "emp",
    "estabs_entry",
    "estabs_entry_rate",
    "estabs_exit_rate",
    "job_creation_rate",
    "job_creation_rate_births",
    "job_destruction_rate",
    "net_job_creation_rate",
    "reallocation_rate",
]

LAGGED_FEATURES = [
    "lag_entry_rate",
    "lag_exit_rate",
    "lag_job_creation_rate",
    "lag_birth_job_creation_rate",
    "lag_job_destruction_rate",
    "lag_net_job_creation_rate",
    "lag_reallocation_rate",
    "log_lag_estabs",
    "log_lag_emp",
]

MODEL_ORDER = [
    "mean_rate_baseline",
    "lagged_entry_rate_baseline",
    "poisson_rate",
    "ridge_log_count",
    "lasso_log_count",
    "random_forest",
    "xgboost_rate",
    "catboost_rate",
]


def load_panel() -> pd.DataFrame:
    """Load selected metro rows and construct lagged, next-year-safe features."""
    if not RAW_PATH.exists():
        raise FileNotFoundError(
            f"Missing {RAW_PATH}. Download the public BDS metro file from "
            "https://www2.census.gov/programs-surveys/bds/tables/time-series/2023/bds2023_msa.csv"
        )

    usecols = ["year", "msa", *NUMERIC_COLUMNS]
    data = pd.read_csv(RAW_PATH, usecols=usecols, low_memory=False)
    data = data[data["msa"].isin(METROS)].copy()
    data["metro"] = data["msa"].map(METROS)
    for column in NUMERIC_COLUMNS:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    data = data.sort_values(["msa", "year"]).reset_index(drop=True)

    # t-1 inputs predict entry counts at t.  This guards against target leakage.
    lag_map = {
        "estabs_entry_rate": "lag_entry_rate",
        "estabs_exit_rate": "lag_exit_rate",
        "job_creation_rate": "lag_job_creation_rate",
        "job_creation_rate_births": "lag_birth_job_creation_rate",
        "job_destruction_rate": "lag_job_destruction_rate",
        "net_job_creation_rate": "lag_net_job_creation_rate",
        "reallocation_rate": "lag_reallocation_rate",
        "estabs": "lag_estabs",
        "emp": "lag_emp",
    }
    for source, destination in lag_map.items():
        data[destination] = data.groupby("msa", sort=False)[source].shift(1)

    data["log_lag_estabs"] = np.log1p(data["lag_estabs"])
    data["log_lag_emp"] = np.log1p(data["lag_emp"])
    data["entry_rate_from_count"] = 100 * data["estabs_entry"] / data["lag_estabs"]

    # A descriptive outcome index is exported for exploration only.  It is never
    # passed into a model or used as a target, avoiding circular pseudo-scoring.
    score_components = {
        "estabs_entry_rate": 0.50,
        "job_creation_rate_births": 0.25,
        "net_job_creation_rate": 0.25,
    }
    score = pd.Series(0.0, index=data.index)
    for column, weight in score_components.items():
        rank = data.groupby("year")[column].rank(pct=True, method="average")
        score = score + weight * rank * 100
    data["descriptive_business_dynamism_score"] = score

    # BDS is complete for the selected large metros, but retain only observations
    # with the exposure and count required for reliable rate evaluation.
    panel = data[(data["year"] >= 2011) & data["lag_estabs"].gt(0) & data["estabs_entry"].notna()].copy()
    panel = panel.replace([np.inf, -np.inf], np.nan)
    return panel


def train_and_predict(
    model_name: str,
    train: pd.DataFrame,
    test: pd.DataFrame,
    seed: int = 42,
) -> np.ndarray:
    """Fit one pre-specified model on a temporal training fold and predict counts."""
    exposure_train = train["lag_estabs"].to_numpy()
    exposure_test = test["lag_estabs"].to_numpy()

    if model_name == "mean_rate_baseline":
        weighted_rate = train["estabs_entry"].sum() / train["lag_estabs"].sum()
        return np.full(len(test), weighted_rate) * exposure_test
    if model_name == "lagged_entry_rate_baseline":
        return (test["lag_entry_rate"].to_numpy() / 100) * exposure_test

    imputer = SimpleImputer(strategy="median")
    x_train = imputer.fit_transform(train[LAGGED_FEATURES])
    x_test = imputer.transform(test[LAGGED_FEATURES])
    y_count = train["estabs_entry"].to_numpy()
    y_rate = y_count / exposure_train

    if model_name == "poisson_rate":
        scaler = StandardScaler()
        x_train_scaled = scaler.fit_transform(x_train)
        x_test_scaled = scaler.transform(x_test)
        model = PoissonRegressor(alpha=0.10, max_iter=2_000)
        model.fit(x_train_scaled, y_rate, sample_weight=exposure_train)
        return model.predict(x_test_scaled) * exposure_test

    if model_name in {"ridge_log_count", "lasso_log_count"}:
        scaler = StandardScaler()
        x_train = scaler.fit_transform(x_train)
        x_test = scaler.transform(x_test)
        model = Ridge(alpha=10.0) if model_name == "ridge_log_count" else Lasso(alpha=0.05, max_iter=20_000)
        model.fit(x_train, np.log(y_rate))
        return np.exp(model.predict(x_test)) * exposure_test

    if model_name == "random_forest":
        model = RandomForestRegressor(
            n_estimators=400,
            min_samples_leaf=5,
            max_features=0.8,
            random_state=seed,
            n_jobs=1,
        )
        model.fit(x_train, y_rate)
        return model.predict(x_test) * exposure_test

    if model_name == "xgboost_rate":
        if XGBRegressor is None:
            raise ImportError("xgboost is not installed")
        model = XGBRegressor(
            objective="reg:squarederror",
            n_estimators=250,
            max_depth=3,
            learning_rate=0.04,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_lambda=10.0,
            random_state=seed,
            n_jobs=1,
        )
        model.fit(x_train, y_rate)
        return model.predict(x_test) * exposure_test

    if model_name == "catboost_rate":
        if CatBoostRegressor is None:
            raise ImportError("catboost is not installed")
        model = CatBoostRegressor(
            loss_function="RMSE",
            iterations=250,
            depth=4,
            learning_rate=0.04,
            l2_leaf_reg=8.0,
            random_seed=seed,
            thread_count=1,
            verbose=False,
            allow_writing_files=False,
        )
        model.fit(x_train, y_rate)
        return model.predict(x_test) * exposure_test

    raise ValueError(f"Unknown model: {model_name}")


def evaluate_models(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Use rolling future-year holdouts: 2018 through 2023."""
    prediction_rows: list[pd.DataFrame] = []
    test_years = range(2018, 2024)
    available_models = [name for name in MODEL_ORDER if not ((name == "xgboost_rate" and XGBRegressor is None) or (name == "catboost_rate" and CatBoostRegressor is None))]

    for test_year in test_years:
        train = panel[panel["year"] < test_year].copy()
        test = panel[panel["year"] == test_year].copy()
        for model_name in available_models:
            predicted = np.clip(train_and_predict(model_name, train, test, seed=test_year), 0, None)
            result = test[["year", "msa", "metro", "estabs_entry", "lag_estabs", "entry_rate_from_count"]].copy()
            result["model"] = model_name
            result["predicted_entries"] = predicted
            result["predicted_entry_rate"] = 100 * predicted / result["lag_estabs"]
            result["absolute_error_entries"] = abs(result["predicted_entries"] - result["estabs_entry"])
            result["absolute_error_rate_pp"] = abs(result["predicted_entry_rate"] - result["entry_rate_from_count"])
            prediction_rows.append(result)

    predictions = pd.concat(prediction_rows, ignore_index=True)
    summary = (
        predictions.groupby("model", as_index=False)
        .agg(
            observations=("metro", "size"),
            entry_rate_mae_pp=("absolute_error_rate_pp", "mean"),
            entry_rate_rmse_pp=("absolute_error_rate_pp", lambda x: float(np.sqrt(np.mean(np.square(x))))),
            entry_count_mae=("absolute_error_entries", "mean"),
        )
        .sort_values("entry_rate_mae_pp")
        .reset_index(drop=True)
    )
    summary["primary_metric"] = "Lower is better: mean absolute error in next-year entry rate, percentage points"
    return predictions, summary


def permutation_importance_for_best_tree(panel: pd.DataFrame, summary: pd.DataFrame) -> pd.DataFrame:
    """Estimate held-out permutation importance for the better tree contender.

    Importance is predictive association only.  Each test-year fold is shuffled
    separately, so it cannot support causal claims about incentives or policy.
    """
    tree_models = {"random_forest", "xgboost_rate", "catboost_rate"}
    contenders = summary[summary["model"].isin(tree_models)]
    if contenders.empty:
        return pd.DataFrame(columns=["model", "feature", "mae_increase_pp", "folds", "interpretation"])
    model_name = contenders.iloc[0]["model"]
    rows: list[dict[str, object]] = []
    for test_year in range(2018, 2024):
        train = panel[panel["year"] < test_year].copy()
        test = panel[panel["year"] == test_year].copy()
        base = train_and_predict(model_name, train, test, seed=test_year)
        base_mae = np.mean(abs(100 * base / test["lag_estabs"].to_numpy() - test["entry_rate_from_count"].to_numpy()))
        for feature_index, feature in enumerate(LAGGED_FEATURES):
            shuffled = test.copy()
            shuffled[feature] = np.random.default_rng(test_year * 100 + feature_index).permutation(shuffled[feature].to_numpy())
            altered = train_and_predict(model_name, train, shuffled, seed=test_year)
            altered_mae = np.mean(abs(100 * altered / shuffled["lag_estabs"].to_numpy() - shuffled["entry_rate_from_count"].to_numpy()))
            rows.append({"model": model_name, "feature": feature, "test_year": test_year, "mae_increase_pp": altered_mae - base_mae})
    detail = pd.DataFrame(rows)
    output = (
        detail.groupby(["model", "feature"], as_index=False)
        .agg(mae_increase_pp=("mae_increase_pp", "mean"), folds=("test_year", "nunique"))
        .sort_values("mae_increase_pp", ascending=False)
    )
    output["interpretation"] = "Larger positive values indicate a stronger predictive association; not a causal effect."
    return output


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    panel = load_panel()
    panel_columns = [
        "year", "msa", "metro", "firms", "estabs", "emp", "estabs_entry",
        "estabs_entry_rate", "entry_rate_from_count", "estabs_exit_rate",
        "job_creation_rate", "job_creation_rate_births", "job_destruction_rate",
        "net_job_creation_rate", "reallocation_rate", "lag_estabs", "lag_emp",
        *LAGGED_FEATURES, "descriptive_business_dynamism_score",
    ]
    panel[panel_columns].to_csv(DATA_DIR / "bds_31_metro_entry_panel.csv", index=False)
    panel[["year", "msa", "metro", "estabs_entry_rate", "job_creation_rate_births", "net_job_creation_rate", "descriptive_business_dynamism_score"]].to_csv(
        DATA_DIR / "descriptive_business_dynamism_score.csv", index=False
    )

    predictions, summary = evaluate_models(panel)
    predictions.to_csv(DATA_DIR / "held_out_entry_predictions.csv", index=False)
    summary.to_csv(DATA_DIR / "entry_model_comparison.csv", index=False)
    importance = permutation_importance_for_best_tree(panel, summary)
    importance.to_csv(DATA_DIR / "tree_model_permutation_importance.csv", index=False)

    winner = summary.iloc[0]
    print(f"Panel: {len(panel):,} metro-years across {panel['metro'].nunique()} metros")
    print(f"Best held-out entry-rate model: {winner['model']} ({winner['entry_rate_mae_pp']:.3f} percentage-point MAE)")
    print(f"Outputs written to {DATA_DIR}")


if __name__ == "__main__":
    main()
