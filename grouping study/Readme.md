# Atlanta company–metro grouping study

Protocol version 1.0 · November 25, 2026 · **Documentation only; not implemented or trained.**

This study asks whether comparisons with similar company–metro observations improve an Atlanta-focused benchmark of reported Fortune 500 headquarters. It retains individual company outcomes and company characteristics, rather than reducing the analysis to metro totals before fitting.

The intended output is an Atlanta assessment. Other metros are comparison and validation material; national rankings and uniformly good predictions everywhere are not objectives. Nevertheless, Atlanta's one observed count cannot establish predictive accuracy, so comparable held-out metros supply validation evidence.

## Read in this order

1. [background.md](background.md): conversation rationale, existing findings, and methodological context.
2. [STUDY_DESIGN.md](STUDY_DESIGN.md): question, operational defaults, similarity dimensions, and precise grouping method.
3. [DATA_CONTRACT.md](DATA_CONTRACT.md): authoritative inputs, outcomes, keys, coverage, and prohibited fields.
4. [TRAINING_HANDOFF.md](TRAINING_HANDOFF.md): models, candidate grid, nested evaluation, execution sequence, and future artifacts.
5. [VALIDATION.md](VALIDATION.md): acceptance checks, Atlanta-focused metrics, support diagnostics, and uncertainty.
6. [REPORTING_AND_INTERPRETATION.md](REPORTING_AND_INTERPRETATION.md): required Atlanta outputs, sensitivities, and claim limits.
7. [SOURCES.md](SOURCES.md): local evidence and external primary references.

These files are the standalone handoff. Another agent should not need the preceding chat to understand the intended study. Version 1.0 numerical choices operationalize the discussion; they are proposed protocol defaults, not previously tested findings or thresholds established by the literature. Freeze them in a machine-readable execution contract before fitting. If an implementation requires a substantive departure, record the departure and its reason before inspecting its validation results.

## Scope

- Start with Study 1's frozen 2025 reported-HQ target: 498 eligible firms, 50 metros, Atlanta CBSA `12060` reserved, and 49 development metros.
- Build overlapping neighborhoods using company characteristics and metro conditions. These are economic comparisons, not new geographic boundaries or randomly assigned clusters.
- Use soft weights and a blend with a global company model to limit the instability of small local samples.
- Compare against employment and the existing R1 company logistic benchmark. An additional Atlanta-focused global logistic control separates the effect of localized tuning from the effect of grouping.
- Aggregate company probabilities only after prediction; preserve all company outputs.
- Ordinary-office modeling is a future gated extension. Current office observations are positives and unknowns, not a valid supervised presence/absence dataset.
- Incentive feasibility is a separate decision layer. It is not a training weight in this experiment.

## Folder structure

Only the eight Markdown files listed above exist as deliverables of this preparation. No scripts, copied tables, fitted models, new configurations, or generated reports are created now.

An implementing agent may later create the following structure inside this folder:

```text
grouping study/
  Readme.md
  background.md
  STUDY_DESIGN.md
  DATA_CONTRACT.md
  TRAINING_HANDOFF.md
  VALIDATION.md
  REPORTING_AND_INTERPRETATION.md
  SOURCES.md
  config/       # future frozen contracts, feature lists, and input hashes
  scripts/      # future preparation, training, and verification entry points
  tables/       # future derived comparison and assessment tables
  models/       # future final fitted pipelines and neighbor state
  reports/      # future validation, tuning, support, and Atlanta results
```

Repository root: `/Users/shanelarkin/Downloads/aidatalab`. Quote shell paths containing `grouping study`. References to `study_1/` or `artem/` in these documents are repository-relative unless stated otherwise.

## Preservation and completion

Treat all existing Study 1 and Artem data, code, models, and reports as read-only references. Put future grouping artifacts here. Do not run inherited training entry points merely to inspect their outputs: they can overwrite earlier runs. Do not use the retired 98-firm entry point.

The documentation package is ready for implementation, not evidence that the grouping approach works. Execution is complete only after verified data contracts, leakage-safe predictions, support and uncertainty checks, frozen selection, final Atlanta assessment, and an honest result report—including a negative or inconclusive result if appropriate.
