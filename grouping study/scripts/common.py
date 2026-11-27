"""Shared, training-only transforms, soft kernels, and scoring."""
import hashlib
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import xlogy
from sklearn.compose import ColumnTransformer
from sklearn.exceptions import ConvergenceWarning
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
R1 = REPO / "study_1/feature_refinement"
ATL = "12060"
TARGET = "reported_hq_presence"
SEED = 20261125
BLOCKS = {
    "size": ["log_msa_private_employment"],
    "workforce": ["bachelors_plus_share_2024", "soc_business_financial_jobs_per_1000", "soc_computer_math_jobs_per_1000"],
    "industry": [f"cbp_{s}_share_2023" for s in ["manufacturing", "retail", "transport_warehousing", "information", "finance_insurance", "professional_technical", "health_social"]],
    "cost": ["log_median_gross_rent", "regional_price_parity_2024"],
    "dynamics": ["bds_establishment_entry_rate_2023", "bds_establishment_exit_rate_2023"],
}
COMPANY = ["log_company_revenue", "log_company_workforce", "company_broad_industry", "ownership_listing_type_2025"]
FAMILIES = ["EMP", "R1_GLOBAL", "FOCUS_GLOBAL", "GROUPED"]
GRID = [dict(C=c, alpha=0, k_m=0, k_c=0) for c in [.01, .1, 1.]] + [
    dict(C=c, alpha=a, k_m=m, k_c=k)
    for c in [.01, .1, 1.] for m in [5, 10, 20] for k in [25, 75, 150] for a in [.25, .5, .75]]


def read(path):
    return pd.read_csv(path, dtype={f: str for f in ["cbsa", "company_id", "donor_cbsa", "donor_company_id", "query_company_id"]}, float_precision="round_trip")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def save(name, rows, folder="reports"):
    frame = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    frame.to_csv(ROOT / folder / f"{name}.csv", index=False)
    return frame


def ordered(frame):
    return frame.sort_values(["cbsa", "company_id"]).reset_index(drop=True)


def unique_views(frame):
    metros = frame.drop_duplicates("cbsa").sort_values("cbsa").set_index("cbsa")
    companies = frame.drop_duplicates("company_id").sort_values("company_id").set_index("company_id")
    return metros, companies


def fit_global(train, spec, c):
    cats = spec["categorical_predictors"]
    nums = [x for x in spec["primary_predictors"] if x not in cats]
    prep = ColumnTransformer([
        ("numeric", make_pipeline(SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True), StandardScaler()), nums),
        ("category", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cats),
    ], sparse_threshold=0, verbose_feature_names_out=False)
    model = Pipeline([("preprocess", prep), ("model", LogisticRegression(
        C=c, solver="lbfgs", max_iter=1500, tol=1e-8, class_weight=None, random_state=SEED))])
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        model.fit(train[spec["primary_predictors"]], train[TARGET])
    return model


def predict_global(model, frame, spec):
    return model.predict_proba(frame[spec["primary_predictors"]])[:, 1].reshape(-1, 498)


def standardized(train, query, fields):
    """Fit one median/mean/population scale per unique donor entity."""
    x, q = train[fields].to_numpy(float), query[fields].to_numpy(float)
    if np.isnan(x).all(axis=0).any():
        raise ValueError("All-missing distance column")
    med = np.nanmedian(x, axis=0)
    x, q = np.where(np.isnan(x), med, x), np.where(np.isnan(q), med, q)
    mean, scale = x.mean(axis=0), x.std(axis=0)
    audit = [dict(field=f, median=float(med[i]), mean=float(mean[i]), scale=float(scale[i] or 1),
                  constant=bool(scale[i] == 0), missing_training=int(train[f].isna().sum()),
                  missing_query=int(query[f].isna().sum()), fitted_entities=len(train)) for i, f in enumerate(fields)]
    scale[scale == 0] = 1
    return (x-mean)/scale, (q-mean)/scale, audit


def distances(train, query, blocks=BLOCKS):
    tm, tc = unique_views(train)
    qm, qc = unique_views(query)
    contributions, audits = {}, []
    for name, fields in blocks.items():
        x, q, audit = standardized(tm, qm, fields)
        contributions[name] = ((q[:, None, :] - x[None, :, :]) ** 2).mean(axis=2)
        audits += [dict(entity="metro", block=name, **row) for row in audit]
    dm = np.mean(list(contributions.values()), axis=0)
    x, q, audit = standardized(tc, qc, COMPANY[:2])
    dc = .4 * ((q[:, None, :] - x[None, :, :]) ** 2).mean(axis=2)
    for f, weight in zip(COMPANY[2:], [.5, .1]):
        dc += weight * (qc[f].to_numpy()[:, None] != tc[f].to_numpy()[None, :])
    audits += [dict(entity="company", block="company", **row) for row in audit]
    y = train.pivot(index="cbsa", columns="company_id", values=TARGET).loc[tm.index, tc.index].to_numpy()
    assert y.shape == (len(tm), 498) and set(tm.index).isdisjoint(qm.index)
    return dict(dm=dm, dc=dc, blocks=contributions, audit=audits, tm=tm, tc=tc, qm=qm, qc=qc, y=y)


def kernel(d2, k):
    """All donors contribute; sorted IDs resolve equal-distance ranks."""
    assert k <= d2.shape[1]
    order = np.argsort(d2, axis=1, kind="stable")
    h2 = np.take_along_axis(d2, order[:, k-1:k], axis=1)[:, 0]
    fallback = h2 == 0
    positive = np.where(d2 > 0, d2, np.inf).min(axis=1)
    h2 = np.where(fallback, np.where(np.isfinite(positive), positive, 1), h2)
    logits = -d2 / (2*h2[:, None])
    logits -= logits.max(axis=1, keepdims=True)
    weights = np.exp(logits)
    underflow = (weights == 0).sum(axis=1)
    weights /= weights.sum(axis=1, keepdims=True)
    assert np.isfinite(weights).all() and (weights >= 0).all() and np.allclose(weights.sum(axis=1), 1)
    return dict(w=weights, neff=1/(weights**2).sum(axis=1), h=np.sqrt(h2),
                nearest=np.sqrt(d2.min(axis=1)), fallback=fallback, underflow=underflow, order=order)


def local(state, km, kc):
    b, a = kernel(state["dm"], km), kernel(state["dc"], kc)
    p = b["w"] @ state["y"] @ a["w"].T
    supported = (b["neff"][:, None] >= 10) & (a["neff"][None, :] >= 25)
    assert ((p >= 0) & (p <= 1)).all()
    return dict(p=p, b=b, a=a, supported=supported)


def blend(global_p, loc, alpha):
    effective = alpha * loc["supported"]
    return (1-effective)*global_p + effective*loc["p"], effective


def focus(train, query, atlanta):
    # Atlanta is only a covariate query, never a label donor.
    state = distances(train, pd.concat([query, atlanta], ignore_index=True))
    ai = list(state["qm"].index).index(ATL)
    h = kernel(state["dm"][ai:ai+1], 10)["h"][0]
    distances_to_atlanta = np.zeros(len(state["qm"]))
    tm, _ = unique_views(train)
    qm = state["qm"]
    for fields in BLOCKS.values():
        _, z, _ = standardized(tm, qm, fields)
        distances_to_atlanta += ((z-z[ai])**2).mean(axis=1)/5
    ids = sorted(query.cbsa.unique())
    return pd.Series(np.exp(-distances_to_atlanta/(2*h*h)), index=qm.index).loc[ids].to_numpy()


def losses(y, p):
    clipped = np.clip(p, 1e-12, 1-1e-12)
    return dict(mae=np.abs(y.sum(axis=1)-p.sum(axis=1)),
                rmse=(y.sum(axis=1)-p.sum(axis=1))**2,
                poisson_deviance=2*(xlogy(y.sum(axis=1), y.sum(axis=1)/np.maximum(p.sum(axis=1), 1e-12))-y.sum(axis=1)+p.sum(axis=1)),
                log_loss=(-y*np.log(clipped)-(1-y)*np.log1p(-clipped)).mean(axis=1),
                brier=((y-p)**2).mean(axis=1))


def metrics(y, p, w):
    result = {k: float(np.average(v, weights=w)) for k, v in losses(y, p).items()}
    result["rmse"] **= .5
    return result


def best(rows):
    """Compare full-precision scores with the protocol's absolute tie tolerance."""
    def tie(row):
        return (row.get("alpha", 0), -row.get("k_m", 0), -row.get("k_c", 0), row.get("C", 0))
    candidates = list(rows)
    for key in ["mae", "log_loss"]:
        minimum = min(r[key] for r in candidates)
        candidates = [r for r in candidates if r[key]-minimum < 1e-10]
    return min(candidates, key=tie)


def employment(train, query):
    tm, _ = unique_views(train)
    qm, _ = unique_views(query)
    rate = train[TARGET].sum()/np.exp(tm.log_msa_private_employment).sum()
    return np.repeat((rate*np.exp(qm.log_msa_private_employment).to_numpy()/498)[:, None], 498, axis=1)


def weighted_quantile(values, weights, q=.9):
    order = np.argsort(values, kind="stable")
    return float(np.asarray(values)[order][np.searchsorted(np.cumsum(np.asarray(weights)[order])/np.sum(weights), q)])
