# Recommended research design for AI DataLab

Prepared November 5, 2026. This is a research recommendation based on the current workspace, not a new model result. Existing datasets, pilots, and historical documents are unchanged.

## Recommendation

**Keep the original economic benchmarking and policy objective. Use companies within metros to measure the outcome and study differences among businesses. Account explicitly for the metro conditions those businesses share.**

The intended design is a company–metro presence model, connected to the existing metro economic variables and aggregated back into an Atlanta benchmark. Add a smaller study of verified openings, expansions, and relocations to investigate the mechanisms behind those patterns. This preserves the original approach much more closely than predicting a metro name from company revenue and industry.

Company records can add useful information about industry, size, company networks, and location patterns. Repeating a city's economic variables across office rows does not create additional independent cities or identify the effect of an incentive.

The practical constraint is outcome collection. The current office data cannot yet support an ordinary presence classifier or a general attraction/retention model. Start with the 50 already collected metros, a single consistently dated company footprint, and a limited feature set. Expand the company roster only after a timed validation wave establishes whether comparable location labels can be collected. Avoid committing immediately to 200 metros, 500 firms, or eleven years of office histories.

Suggested study statement:

> We will benchmark Atlanta's corporate presence and verified business location activity against comparable U.S. metros. We will analyze company characteristics together with regional workforce, cost, industry, and site conditions to identify robust associations and Atlanta-specific gaps. We will use those findings, verified company decisions, and program evidence to prioritize interventions within Invest Atlanta's practical authority and capacity.

Presence and recent attraction must be reported separately. If the final dataset supports only a current footprint, the main quantitative claim must concern that footprint. Relocation and expansion claims require dated events.

## 1. What the workspace currently supports

The review covered the research plans, catalogs, QA reports, model reports, and data layouts across the workspace; the shared metro tables and manifests; core archived office tables; relevant feature-building and model code; and the structure of the supplied local workbooks, spatial data, and notebook. It did not independently revalidate every underlying company source, rerun the models, or inspect confidential business-level revenue/employee values. Original office CSVs were read directly from their recoverable archives. Current Parquet schemas and views were checked through their catalogs, manifests, and construction code.

| Component | Finding | Recommended use |
| --- | --- | --- |
| [Overall research context](research_context.md) and [Shane's progress](Shane/Research_progress.md) | The goal is coherent. Shane's October 21 note describes nine metros; the later shared collection contains 50. The data are separately dated source extracts, not one harmonized historical panel. | Retain the benchmark → explanation → feasible intervention sequence. Use the later inventory for collection status. |
| [Shared data](data/README.md) and [dataset context](data/datasets_context.md) | All 50 folders contain the nine required data files. A fresh check of all 450 files found no discrepancies in manifest row counts, byte sizes, or SHA-256 hashes. Each dataset filename has one consistent column schema across metros. | Reuse as economic context and descriptive business-dynamics evidence. File consistency does not establish historical or geographic comparability. |
| Artem employment-growth and BDS models | These measure regional employment growth or employer-establishment entry. Several complex models add little to persistence baselines, and employment-model results depend heavily on the history window. | Preserve as broad economic context and useful validation code. Their targets do not become corporate relocation or expansion outcomes when joined to office rows. |
| [Artem's Fortune/Data Axle audit](Artem/FORTUNE100_NATIONAL_COVERAGE_AUDIT.md) and [decision log](Artem/INVEST_ATLANTA_RESEARCH_DISCOVERIES.md) | Earlier national office-count experiments were retired after incomplete geography, company coverage, and identity matching were discovered. | Reuse source and geography infrastructure. Exclude archived candidate-count findings and feature ranks from substantive recommendations. |
| [Fortune 500 review queue](Artem/data/big_business_presence/README.md) | The CSV contains 100,000 company–metro rows, but 99,993 are unreviewed and only seven are verified qualifying presences. All 200 metro score statuses are non-publishable. | Treat as collection infrastructure. It provides almost no completed national outcome sample yet. |
| [Pilot A](office_approach/pilot_a/reports/collection_qa.md) | Fifty firms, 550 scheduled annual slots, 480 provisionally eligible slots, and 14 supported physical relocations. Many relocations remain within the same metro. Its current model uses 362 rows from 45 companies. | Useful historical executive-address acquisition prototype. Validate operating function, eligibility, and geography before expanding. Repeated HQ observations mostly measure location persistence. |
| [Pilot B](office_approach/pilot_b/reports/collection_qa.md) | Twenty-five firms × ten metros gives 250 search cells. There are 29 verified-presence cells, 81 bounded no-qualifying-found cells, and 140 unresolved cells. Sixty-three qualifying geocoded offices occur in those 29 cells. Two engineering firms contribute 52 of the 63 offices. | Useful office/evidence schema and a warning about collection bias. The other 221 cells are not validated absence labels. |
| Pilot B event ledger | Twenty-six supported distinct projects from 13 firms mix announcements, leases, renovations, pauses, and delivered actions. The public tracker elsewhere also contains selected cases. | Build a deduplicated case study and event inventory. Do not add the trackers together without checking overlaps, or call all projects realized entries. |
| Local license/project workbooks and parcel data | These supply Atlanta-only industry, site, and historical project context. The project workbook schema contains funding, investment, jobs, industry, address, and date fields. License data are a snapshot, not a verified opening/closure panel. | Use for local implementation and program investigation under the applicable access rules. They do not supply comparable outcomes for other metros or an untreated policy comparison group. |
| Public LODES, boundaries, and transit files | Existing public-source infrastructure can support City-versus-suburb and workforce-access work. Some QCEW downloads cover only ten core Atlanta counties. | Reuse for a focused local study. Ten core counties must not be relabeled the full 29-county Atlanta MSA. |
| Geospatial export and demo notebook | Includes a food-access layer and a demonstration of spatial joins/buffers. The demo hardcodes EPSG:3857 for distance buffers and references a city boundary file not supplied beside it. | Treat as a demonstration rather than a production office-analysis pipeline. Validate geometry, use a suitable local distance CRS, and select matching boundary vintages. |

Important qualifications to carry forward:

- Shared QCEW files have industry detail in 2023–2024 and exactly one all-industry/all-ownership row per metro in 2025. County aggregation can recover additional industry information where published and unsuppressed; the existing metro file cannot. BLS confirms the change to MSA totals-only publication beginning in second quarter 2025. [BLS QCEW overview](https://www.bls.gov/cew/overview.htm).
- Economic Census receipts are from 2022; shared CBP and BDS are from 2023; Fortune rosters are the 2025 edition; shared tax files are a 2026 snapshot. These are not interchangeable dates.
- The 435 shared Fortune roster rows include 403 with unknown current-metro verification. These are publisher/regional headquarters observations, not a national census of all Fortune offices. Sacramento and Salt Lake City's empty publisher rosters do not imply no corporate offices.
- Boundary changes affect Cleveland, Connecticut, New Orleans, and other comparisons. Hartford/Bridgeport lack collected 2023 GDP on the new planning-region geography. Preserve geographic vintage and suppression information.
- CBP employment/establishment projections overlap, as do Economic Census detail/summary and GDP county/metro rows. Their row counts cannot be added as independent data points.
- Some older summaries are superseded. For example, the early Atlanta HQ screen has 14 metro companies; the later shared 2025 roster has 15. The early county-regression builder does not check QCEW disclosure flags when making sector shares. Revalidate those outputs before use.
- Artem's external-factor model panel already provides 581 observations across 97 metros, but its feature years are 2017–2022 and target years 2018–2023. This is useful historical infrastructure, not current economic conditions for the 2026 office inventory.

## 2. Does using companies actually provide more data?

**Yes, when company observations contain information that an aggregate metro total loses. Flattening the same aggregate information into more rows provides no such gain.**

Suppose every company–Atlanta row receives the same metro employment, wage, tax, and housing values. Those variables still have only one Atlanta value at that date. A hundred offices do not provide a hundred independent observations of Atlanta's tax environment.

There is an exact version of this point. If every company in metro `m` has the same predicted presence probability `p_m`, then the ordinary independent Bernoulli likelihood is:

`L_m ∝ p_m^(number present) × (1 − p_m)^(number absent)`.

The counts present and absent contain all the information needed for that likelihood. Expanding them into company rows gives the same coefficient estimates as the corresponding grouped binomial fit. This equivalence assumes that simple likelihood; it does not justify treating firms as independent in the actual study.

Company data become valuable when they distinguish, for example:

- technology firms' response to relevant technical talent from financial firms' response to finance talent;
- firms with national office networks from firms with one regional footprint;
- company size, age, industry, and prior local presence;
- actual openings from incumbents, and expansions from moves within a metro;
- City locations from suburban sites with different access and building conditions.

This allows a question such as: **“Is Atlanta's technology-office footprint lower than expected for this company population, given its economic conditions?”** That is more informative than one total per city, and more defensible than treating every office as an independent city observation.

Uncertainty must reflect repeated companies and shared metro conditions. State tax has an even coarser source of variation: several metros share the same state policy. Clustered-data methods address this dependence; ordinary row-level standard errors can substantially overstate precision. [Cameron and Miller, A Practitioner's Guide to Cluster-Robust Inference](https://cameron.econ.ucdavis.edu/research/Cameron_Miller_JHR_2015_February.pdf).

## 3. Choose the row and outcome before choosing the algorithm

| Research question | Row used for estimation | Outcome | What must be observed |
| --- | --- | --- | --- |
| Where do defined companies currently have qualifying offices? | Company × metro × snapshot date | At least one qualifying office: 1/0/unknown | Consistent company roster, site/function rules, and comparable presence/absence ascertainment |
| Where does a specific new office or relocation go? | Decision × candidate metro | Chosen alternative: 1/0 | A dated decision and a defensible set of available destinations with their conditions |
| Does an existing local employer expand? | Baseline company–metro × period | Verified expansion, or local jobs/space change | An observed starting presence, follow-up coverage, and comparable expansion definitions |
| Does an existing site or company leave? | Baseline site/company–metro × period at risk | Verified exit/contraction | Baseline cohort, follow-up, censoring, and separate merger/reorganization handling |
| Where are reported public-company executive offices? | Company × candidate metro at one as-of date | Reported executive-office location | A consistently defined designated address; distributed/co-HQ arrangements handled explicitly |

For the requested company-cluster approach, **company × metro** is the best primary grain. Keep each physical office in a linked site table, then derive presence at the company–metro level. Ten offices belonging to one engineering company should count as one company presence in the primary outcome. Office counts can remain a separate outcome.

Do not repeat a metro Fortune count, GDP, or composite performance score as the dependent variable on every office row. This duplicates the outcome and overweights cities with more collected offices. Company-wide revenue can adjust company size; it is not local office revenue or local economic output.

Use three evidence states throughout collection:

1. Supported qualifying presence.
2. Audited non-presence under a defined source scope that can actually support that conclusion.
3. Unresolved coverage.

A bounded web search with no result belongs in the coverage ledger. It becomes a model zero only if the study's ascertainment standard is satisfied. A company directory that does not enumerate all relevant functions cannot establish their absence. Current Pilot B has no such validated zero-label population.

## 4. Recommended models

### A. Primary model once current footprint labels are adequate

Start with a small regularized logistic model. Include selected company attributes, metro conditions, and a few predeclared company–metro interactions. Compare it with a hierarchical logistic model if the sample supports estimating company and metro variation.

An illustrative hierarchical specification is:

`logit P(presence_i,m,t = 1) = α + βX_m,t + γZ_i,t + θH_i,m,t + u_i + v_m + τ_t`.

Here `X` contains metro conditions, `Z` company characteristics, and `H` matching variables such as industry × relevant occupation supply. `u_i` represents repeated-company differences, `v_m` residual metro differences, and `τ_t` period conditions when repeated snapshots exist. Companies operating in multiple metros create crossed company/metro structure, rather than simple offices nested in one city.

This is an associational model. Random metro effects do not remove the possibility that unmeasured metro characteristics correlate with observed features. A single cross-section cannot separately estimate unrestricted metro fixed intercepts and coefficients on metro-constant variables. With a genuine historical panel, distinguish within-metro changes from between-metro differences and consider correlated-effects specifications.

If footprint data are still limited, the regularized baseline is preferable to a complicated hierarchical model with poorly estimated variance components. Report both metro-level and company-level performance and use dependence-aware uncertainty. Adding random effects is not a substitute for reliable labels.

### B. Direct location activity when enough dated decisions exist

Use an alternative-specific conditional logit as the first destination model. Each decision has one row for every available candidate metro, and the features describe **each candidate**, rather than only the destination actually chosen. This is a standard discrete-choice structure. [Train, Discrete Choice Methods with Simulation, Chapter 2](https://eml.berkeley.edu/books/choice2nd/Ch02_p9-33.pdf), [statsmodels ConditionalLogit documentation](https://www.statsmodels.org/stable/generated/statsmodels.discrete.conditional_models.ConditionalLogit.html).

For a given project, compare Atlanta's labor, site, cost, and industry conditions with the alternatives' conditions at the relevant date. Define candidate eligibility before inspecting results. Do not assert that every company considered all 50 metros. A fixed broad candidate set is a modeling assumption and needs narrower-set sensitivity checks. Restricting to decisions inside the roster estimates destination choice conditional on that restriction; address destinations outside it explicitly when they matter.

Company attributes that do not vary across a decision's alternatives cancel out as standalone terms in a conditional logit. Use their interactions with alternative attributes where theoretically relevant. Repeated decisions by the same parent still require dependence-aware evaluation.

Unchosen alternatives are valid choice labels under this design; they are not claims that the firm has no existing office there. Fifty choices expanded to 2,500 candidate rows remain fifty observed decisions. A destination model conditional on an opening does not predict whether the company opens anywhere at all. That requires a separate observed opportunity/risk population.

Do not fit this as the headline attraction model to the current 14 supported HQ relocations or 26 heterogeneous projects. First distinguish intermetro moves, intrametro changes, expansions, plans, and completed activity; resolve overlap and dates. There is no universal event count that guarantees adequacy. Use concentration, validation stability, and a design-specific simulation to judge the eventual specification.

### C. Other methods and their roles

| Method | Role in this project |
| --- | --- |
| Regularized logistic regression | First presence baseline, with transparent limited interactions and calibrated probabilities |
| Hierarchical logistic regression | Partial pooling and crossed company/metro structure when data support it; requires explicit assumptions |
| Conditional logit | First model for actual destination choices, or a clearly labeled current HQ-distribution benchmark |
| Grouped binomial model | Direct aggregate benchmark for distinct-company presences out of a known common roster, when its assumptions fit |
| Poisson / negative binomial | Models for verified event or office counts. Specify exposure from the research question; population is not automatically the correct offset. Overdispersion alone is not a reason to invent a zero-inflation process. |
| Discrete-time exit/expansion model | Later, after a baseline cohort and consistent follow-up exist |
| XGBoost or CatBoost | One optional nonlinear challenger, evaluated on the same meaningful holdouts and outcome |
| Optuna | Optional parameter-search software. It is not a model and does not repair outcomes, dependence, or identification. |

A small fixed parameter grid is sufficient for the first comparison. Retain a more complex method only if it produces a useful, stable improvement over a strong simple baseline. Choose based on held-out probability calibration and metro benchmark accuracy, as well as interpretability and collection limits.

## 5. What the existing model results imply

[Pilot A's results](office_approach/pilot_a/analysis/RESULTS.md) show company-held-out log loss of 3.179 for XGBoost versus 3.160 for the prior baseline. Its familiar-firm temporal benchmark achieves 97.1% accuracy simply by retaining the last known location. Among 308 consecutive matched pairs, only two change reported metro. The broader reviewed-event ledger and these annual matched pairs are different views; the two counts should not be conflated. More annual unchanged addresses will not by themselves create many attraction events.

[Pilot B's results](office_approach/pilot_b/analysis/RESULTS.md) show apparently better documentation prediction, but held-out XGBoost SHAP depends entirely on revenue missingness. Two private engineering firms supply 18 documented-positive cells. In the public-firm sensitivity, XGBoost log loss is 0.208 versus the prior's 0.198. The apparent advantage disappears. These models diagnose the collection process, rather than establish economic location drivers.

The existing split, training-only preprocessing, and provenance work are useful. However, company-held-out evaluation alone does not test new-city transfer: the same city conditions can remain in training. Existing company-cluster intervals also do not capture all uncertainty from shared metros or label collection.

## 6. Reuse a small, meaningful economic feature set

Start with approximately six to ten concepts, chosen before fitting. This is a complexity limit for the first specification, not a claim that ten predictors are statistically supported by every possible sample.

| Concept | Preferred measurement | Existing starting point / next work |
| --- | --- | --- |
| Market scale and demand | Log employment or another justified scale measure | Shared QCEW and Artem builders; avoid putting several nearly identical scale measures into a small model |
| Relevant workforce | Occupation employment/concentration, occupation-specific wages | Add OEWS for selected office functions; broad average wage mixes pay and industry composition |
| Industry compatibility | Prior industry concentration matched to company industry | Reuse suppression-aware QCEW builders and harmonize NAICS |
| Company scale and footprint | Dated company size, industry, and prior national/local presence | Pilot company/evidence tables; company-wide revenue remains a size adjustment |
| Office/site cost and readiness | Comparable rents, suitable space blocks, delivery/readiness | Consistent reports for a limited peer group; residential permits are not office inventory |
| Housing/recruitment conditions | Rent burden or cost relative to relevant wages | ACS/HUD where comparable; FHFA growth and BEA price parity answer different questions |
| Access | Relevant worker/site access or a carefully defined metro proxy | Existing LODES/GTFS and boundaries support local work; transit commute share measures use, not service supply alone |
| Policy setting | Dated program availability/eligibility or state tax context | Shared 2026 tax is current context only; historical features need historical policy data |

An industry × occupation interaction is particularly useful: it turns a generic city feature into a measure of company–city compatibility. Preselect only a few such interactions. Do not search all industry/feature combinations and present the largest observed ones as established discoveries.

Not every existing exclusion rule should become permanent. Lagged industry-establishment density can be a legitimate cluster predictor. The problematic cases are contemporaneous totals that contain the target firms, direct copies of the target, or future outcomes. Use dated or leave-target-out measures where possible and state their descriptive role. A blanket statement that every CBP establishment variable is necessarily leakage is too broad.

For actual decisions, predictors must describe conditions before the decision. Preserve observation periods and publication dates. A retrospective study may use later-released estimates of earlier conditions if clearly labeled; it cannot call those estimates information available to a real-time forecaster. Current office presence can reflect decisions made decades ago, so lagging current conditions by one year does not establish that they caused that footprint.

## 7. Return company results to the original Atlanta comparison

Keep the metro benchmark as the main communication product:

1. **Observed footprint:** distinct sampled companies with qualifying presence, divided by the appropriate common eligible roster. Show unresolved coverage alongside it. Partial confirmed counts are lower bounds, not comparable final market shares.
2. **Industry/function breakdown:** show where Atlanta's composition differs, with uncertainty and sample sizes.
3. **Expected footprint:** sum predicted probabilities over the same company population for each metro. Standardize company composition rather than comparing cities with different observed company samples.
4. **Atlanta gap:** compare observed and expected presence using an Atlanta-held-out structural prediction. Do not estimate an Atlanta intercept from its own labels and call the resulting fit an independent benchmark. Carry prediction and coverage uncertainty into the comparison.
5. **City capture:** within adequately observed Metro Atlanta locations, show City versus suburb separately. Existing 3-inside/7-outside qualifying-site counts describe a small, incomplete subset; they are not the City's complete capture rate.

An unexplained gap is a reason to investigate industry history, source omissions, sites, and business constraints. It is not an estimate of offices that an incentive would create. Match weighting to the estimand: equal-company, equal-metro, office-weighted, and employment-weighted analyses answer different questions. Weighting alone does not account for clustering.

## 8. Validation and reporting

- Keep every company's history together for new-company evaluation, using the cross-pilot identity key. Fifteen companies overlap between the pilots.
- Separately hold out whole metros for geographic transfer. Integrate or omit the held-out metro's unobserved random effect rather than learning it from test labels.
- Use later-year holdouts when genuine history exists. Annual snapshots from the same unchanged site are correlated. A single snapshot cannot validate future attraction.
- Keep all alternatives of a decision in the same fold. Fit imputation, scaling, encoding, and tuning inside training folds.
- For broader claims, consider a joint new-company/new-metro test when sample size allows. Separate transfer tests should not be described as that joint test.
- Compare log loss, Brier score/calibration, and aggregate metro errors for presence. For destination choices, report decision-level log loss and top-k accuracy. Accuracy alone can reward predicting the majority outcome.
- Evaluate the economic layer against a company/industry baseline and, where appropriate, training-only metro popularity or persistence. Ask whether economic variables add useful information beyond those baselines.
- Use uncertainty procedures appropriate to repeated parent companies and shared metro/state conditions. A crossed-effects model, suitable multiway methods, or a justified resampling design may be appropriate. Do not apply a row bootstrap or assume one group split solves every dependence problem. With few cities, emphasize sensitivity and avoid precise-looking significance claims.
- Resample/refit when estimating model-development uncertainty. Intervals from saved held-out predictions alone condition on the fitted models and omit label errors.
- Report source coverage, firm/sector concentration, exclusions, and plausible alternative classifications. Complete-case analysis can remain biased when missingness depends on company or city type. Reweighting observed firms does not automatically fix that problem.
- Predeclare the main target, small feature set, evaluation splits, and model comparison. Keep an untouched final assessment if enough data remain. Repeatedly selecting the best specification on the same folds can overstate performance.

Grouped evaluation is supported in standard tooling; choosing the group requires matching the research question. [scikit-learn cross-validation documentation](https://scikit-learn.org/stable/modules/cross_validation.html).

## 9. A feasible collection and execution sequence

### Step 1: Freeze the minimum study specification

Use the collected 50 metros as the initial broad frame. Choose policy peers separately using baseline size, industry, and business conditions, before looking for metros that make Atlanta appear weak. Keep the original eight peer candidates as a sensitivity group rather than assuming they are all equivalent competitors.

Choose one primary footprint definition and date. For a 2026 snapshot, align economic context to consistently available measured years and label the dates. For a historical snapshot, collect historical location evidence. Decide whether the population is fixed Fortune firms or a broader size/industry-defined company sample. Fortune status can remain a descriptive flag. Results from a public-company or Fortune sample generalize to that population, not all Atlanta businesses.

### Step 2: Conduct a small additional, timed validation wave

Use roughly 10–15 additional firms, selected using the proposed industry/size rules rather than directory convenience. Apply a national directory/filing workflow and map the resulting locations to the 50 metros, rather than starting with thousands of separate searches. Audit whether those sources cover all eligible office functions before deriving zeros. Preserve unsupported companies and cities in the coverage report.

Measure actual analyst review time, geocoding/function disagreements, unresolved cells, office concentration by parent, and the yield of usable historical events. Have another researcher review positives, proposed negatives, and ambiguous cases. The existing pilots have no independently measured human-review error rate or complete analyst-time measurement.

The decision at the end is substantive: can the chosen population support comparable labels across the geography? A high overall completion percentage can still hide a missing industry or region. If unresolved-label sensitivity can reverse the Atlanta comparison, do not promote that comparison to a headline result.

### Step 3: Expand only the supported outcome

If validated footprint ascertainment works, a planning target of 100–200 firms across 50 metros yields 5,000–10,000 coverage cells. These are workload counts, not independent sample-size guarantees. Completing all-negative verification may dominate effort. Do not extrapolate current office density or search speed into a fully costed schedule.

If office ascertainment fails, use a consistently defined **reported executive-office geography benchmark** as the cheaper broad comparison. One designated location per eligible firm reduces the need to establish every firm's absence in every city. Handle co-HQ, distributed firms, and locations outside the roster explicitly. Use one well-validated snapshot first; eleven annual observations of an unchanged address add little to the cross-sectional macro comparison. Keep its title and conclusions about reported executive geography, rather than office attraction.

In that fallback, retain a smaller office/event study across approximately 8–12 policy peers for industry function, City capture, and practical recommendations. It is more useful to deliver a validated broad HQ benchmark plus a focused office study than to fit a national office model to unknowns.

### Step 4: Produce benchmarks before fitting complex models

Deliver the coverage matrix, company/industry composition, descriptive metro comparisons, City/suburb distinctions, and a small economic-variable scorecard. Resolve obvious source and geography artifacts before ranking drivers.

### Step 5: Fit one main specification and one challenger

Use the model appropriate to the supported outcome. Evaluate whether the economic variables improve the baseline and whether the Atlanta conclusions survive coverage, firm, peer, and feature sensitivities. If improvement is weak, report that result and retain the descriptive benchmark; it is still useful research.

### Step 6: Link a small number of gaps to program investigation

Select two or three robust industry/office-function gaps, then examine dated company decisions, employer constraints, suitable local sites, and comparable interventions. Keep a deduplicated event ledger with announcement, decision, and operation dates and delivery status. Announcements cannot be silently summed as delivered jobs.

Expansion and retention modeling should wait for a baseline cohort and consistent follow-up. Closures are often less publicized than openings, and delisting or acquisition does not establish physical office departure. A selected announcement sample can support case comparison without estimating population win rates.

## 10. Translate the research into feasible incentives

Keep statistical evidence and implementation feasibility as separate inputs. A high SHAP rank has neither the direction nor the causal effect needed to set incentive spending. A strong metro tax association also does not imply Invest Atlanta can change state corporate tax.

For each recommendation, record:

| Field | Required evidence |
| --- | --- |
| Defined gap | Industry/function, City or metro geography, affected company population, uncertainty |
| Mechanism | A documented constraint connecting the proposed action to that gap |
| Action and owner | What Invest Atlanta, City departments, state agencies, or partners would actually do |
| Comparable program | Eligibility, funding, delivery, job/wage requirements, accountability, and available evaluations |
| Feasibility | Authority, eligible location/firm, resources, delivery capacity, and timeline |
| Expected value | Credible additional activity, local access/job quality, costs, and potential displacement |
| Evaluation | Baseline, comparison strategy where possible, delivered outcomes, and follow-up dates |

Use authority and eligibility as mandatory gates. Then score budget practicality, administrative capacity, implementation time, and measurability with a written rubric, such as 0 = unsupported, 1 = material constraints, 2 = feasible with documented resources. A 0–100 rescaling of their average is an optional transparent feasibility score. The policy team should agree criteria and weights before ranking proposals and test how the ranking changes. Show evidence quality and expected benefit separately rather than multiplying feasibility by normalized model importance. Do not let unknown feasibility inputs quietly become favorable scores.

Illustrative mappings, conditional on findings:

- A relevant occupation shortage could motivate employer/college training coordination, with placement and retention outcomes.
- A shortage of suitable City office space could motivate building-readiness, leasehold, or redevelopment support tied to real site constraints and delivered occupancy.
- Poor access between target residents and jobs could motivate a focused site/access partnership after labor-shed analysis.
- A cost disadvantage controlled at state level could motivate a partner discussion rather than a claimed City policy lever.

Invest Atlanta already lists business assistance including workforce services and site-selection support, and its Economic Opportunity Fund is structured project by project. Those are starting points for a program inventory, not evidence that a particular project is eligible or that funding is available. Verify current terms for each proposed action. [Invest Atlanta business assistance](https://www.investatlanta.com/businesses/medium-large-businesses/business-assistance), [bonds, loans, grants, and incentives](https://www.investatlanta.com/businesses/medium-large-businesses/bonds-loans-grants-incentives).

Estimating incentive effectiveness requires a separate credible comparison, such as an eligibility threshold, rollout, or carefully justified comparison group. Existing award/project records alone select recipients and do not supply the counterfactual. Distinguish additional jobs from jobs promised, and project employment from wider economic effects. The incentive-evaluation literature supports treating those as separate empirical questions. [Slattery and Zidar, Evaluating State and Local Business Incentives](https://www.nber.org/papers/w26603).

## 11. Immediate deliverables and completion standard

The next work should produce:

1. A frozen study specification: population, geography, date, office/HQ function, outcome, label rules, peers, estimand, and validation design.
2. A timed independent validation report from the additional collection wave, including proposed-negative audits and unresolved coverage.
3. A company–metro outcome view linked to the existing company, site, event, factor, and evidence tables. Reuse the architecture in [the office data layout](office_approach/DATA_LAYOUT.md); retain immutable raw evidence.
4. A dated economic feature dictionary and compact metro feature table, with geography/suppression rules and predeclared interactions.
5. A descriptive Atlanta benchmark and one appropriately validated primary model, with a simple baseline and optional challenger.
6. Two or three source-supported intervention proposals with separate feasibility and evidence assessments and measurable pilot outcomes.

Successful research here means a defensible Atlanta comparison and a practical, testable intervention shortlist. It can succeed with a simple model, a narrower office sample, and a candid finding that current data do not isolate incentive effects.
