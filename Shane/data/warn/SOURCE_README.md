# US WARN Act Layoff Notices — normalized, daily-updated dataset

[![US WARN layoffs 2026](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2FAPVentureEngine%2Fwarn-act-notices%2Fmain%2Fdata%2Fbadge.json)](https://approjects-warn-act-notices.static.hf.space/yearly/index.html) [![data updated](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2FAPVentureEngine%2Fwarn-act-notices%2Fmain%2Fdata%2Fbadge-updated.json)](https://github.com/APVentureEngine/warn-act-notices/commits/main) — live, embeddable: [get these badges](API.md#live-badges)

**61,431 layoff notices since 1988 · 48 states · one clean schema · CSV + JSON · updated 2026-09-25**

**Browse it:** [live site, search + per-state pages](https://approjects-warn-act-notices.static.hf.space/index.html) · **Machine-readable:**
[`data/warn_notices.csv`](data/warn_notices.csv) · **Hugging Face:**
[APProjects/us-warn-act-layoffs-notices-daily](https://huggingface.co/datasets/APProjects/us-warn-act-layoffs-notices-daily)

Every US state publishes WARN Act layoff notices differently — different sites,
formats, column names, and date conventions. This repo normalizes them into one
deduplicated dataset, refreshed daily. We checked the official source behind all 48 states on 2026-09-18: **0 publish a feed you can subscribe to**, 3 post a spreadsheet, and the other 45 publish a web page, a pile of PDFs, a search form — or no WARN page at all ([the per-state census](https://approjects-warn-act-notices.static.hf.space/sources.html), re-run weekly). Background on the law itself: the
[Worker Adjustment and Retraining Notification Act of 1988](https://en.wikipedia.org/wiki/Worker_Adjustment_and_Retraining_Notification_Act_of_1988)
on Wikipedia.

**Using this dataset? Two free things that take five seconds.** They cost you
nothing and they are the only thing keeping this pipeline funded and findable:

- [**Star the repo**](https://github.com/APVentureEngine/warn-act-notices) — stars are how the next person who was about
  to write their own 48-state WARN scraper finds this instead of rebuilding it.
- [**Watch → Custom → Releases**](https://github.com/APVentureEngine/warn-act-notices/subscription) — GitHub then notifies
  you whenever the snapshot is republished (not every day; the `data/` folder, the site and the
  Hugging Face mirror refresh every day regardless). The release notes carry the row
  counts and the per-state freshness table, so a new state or a changed field
  reaches you on the day it lands. No signup here and no email address for us to
  hold — GitHub does the notifying. This, not the email list, is the route that
  tells you about a schema or coverage change; the list below only announces a
  new dataset or tier.

**Have a question, or need a state we do not cover?**
[Ask in Discussions](https://github.com/APVentureEngine/warn-act-notices/discussions) — no issue etiquette required, and the
answer stays public so the next person with your question finds it instead of
asking. Found a wrong value in a row, or a state source that moved?
[Open an issue](https://github.com/APVentureEngine/warn-act-notices/issues) — the last reader's README fix shipped the
same day.

**Need to be told when a name on your list files?** The files below are yours to
poll. WARN Watch does the polling: your employer terms and states are matched on
every daily refresh and hits are pushed to a private alert page, a calendar (.ics) and a private
RSS feed you point Slack / Discord / Teams at yourself — no login, no account here.
[Check your employers right now](https://approjects-warn-act-notices.static.hf.space/watch-now.html) (free, no signup — the last 180 days, matched in your browser) ·
[Start the free 30-day trial](https://approj.gumroad.com/l/warn-free-watch) (3 employers or 1 state, no card) ·
[WARN Watch — $49/year](https://approj.gumroad.com/l/warn-watch) ·
[the whole 1988+ archive, free](https://github.com/APVentureEngine/warn-act-notices/releases/latest) (61,431 rows)


<!--state-rates-readme--> 📊 **[US layoffs per capita by state — 48 states x 7 years](data/state_layoff_rates.csv)** — WARN notices and workers per 100k residents (Census denominator), coverage-gated; 2025: District of Columbia leads at 5.302 notices per 100k. [Card on Hugging Face](https://huggingface.co/datasets/APProjects/us-layoffs-per-capita-by-state-warn-act).
<!--largest-events-readme--> 🏭 **[The 1,000 largest US layoff events since 1988](LARGEST-LAYOFF-EVENTS.md)** — notices clustered per resolved employer (rolling programmes = one event); #1 United Airlines 2020, 45,455 workers over 26 notices. [Card on Hugging Face](https://huggingface.co/datasets/APProjects/us-largest-layoffs-events-warn-act).
<!--sectors-readme--> 🏥 **[US layoffs by industry sector](LAYOFFS-BY-INDUSTRY.md)** — 19 sectors assigned from each resolved employer name by an auditable rule table (52.5% of notices classified, the rest kept as unclassified); 2026 leader Logistics, transport & warehousing, 23,761 workers. [Card on Hugging Face](https://huggingface.co/datasets/APProjects/us-layoffs-by-industry-sector-warn-act). One-industry cuts, rebuilt daily: [tech](https://huggingface.co/datasets/APProjects/us-tech-company-layoffs-warn-act-notices-daily) · [hospitals](https://huggingface.co/datasets/APProjects/us-hospital-healthcare-layoffs-warn-act-notices-daily) · [retail](https://huggingface.co/datasets/APProjects/us-retail-store-closings-layoffs-warn-act-notices-daily) · [restaurants & hotels](https://huggingface.co/datasets/APProjects/us-restaurant-hotel-closings-layoffs-warn-act-notices-daily) · [factories](https://huggingface.co/datasets/APProjects/us-factory-plant-closings-manufacturing-layoffs-warn-act-notices-daily) · [banks & insurance](https://huggingface.co/datasets/APProjects/us-bank-insurance-finance-layoffs-warn-act-notices-daily) · [warehouses & trucking](https://huggingface.co/datasets/APProjects/us-warehouse-trucking-logistics-layoffs-warn-act-notices-daily) · [aerospace](https://huggingface.co/datasets/APProjects/us-airline-aerospace-defense-layoffs-warn-act-notices-daily) · [automotive](https://huggingface.co/datasets/APProjects/us-auto-plant-automotive-layoffs-warn-act-notices-daily) · [pharma](https://huggingface.co/datasets/APProjects/us-biotech-pharma-layoffs-warn-act-notices-daily) · [food](https://huggingface.co/datasets/APProjects/us-food-beverage-plant-meatpacking-agriculture-layoffs-warn-act-notices-daily) · [energy](https://huggingface.co/datasets/APProjects/us-oil-gas-energy-mining-utility-layoffs-warn-act-notices-daily) · [education](https://huggingface.co/datasets/APProjects/us-university-college-school-district-education-layoffs-warn-act-notices-daily) · [media](https://huggingface.co/datasets/APProjects/us-media-newspaper-publishing-telecom-layoffs-warn-act-notices-daily) · [government](https://huggingface.co/datasets/APProjects/us-government-nonprofit-public-sector-layoffs-warn-act-notices-daily).

- **[Use it in Google Sheets](GOOGLE-SHEETS.md)** — one `=IMPORTDATA(...)` formula, refreshes itself, per state or nationwide.

<!-- STATE_MD_INDEX:START -->
**Browse by state — readable right here on GitHub:** [all 48 states](https://github.com/APVentureEngine/warn-act-notices/blob/main/states/README.md) · [California](https://github.com/APVentureEngine/warn-act-notices/blob/main/states/california.md) · [Texas](https://github.com/APVentureEngine/warn-act-notices/blob/main/states/texas.md) · [New York](https://github.com/APVentureEngine/warn-act-notices/blob/main/states/new-york.md) · [Florida](https://github.com/APVentureEngine/warn-act-notices/blob/main/states/florida.md) · [Illinois](https://github.com/APVentureEngine/warn-act-notices/blob/main/states/illinois.md) · [Washington](https://github.com/APVentureEngine/warn-act-notices/blob/main/states/washington.md) · [Georgia](https://github.com/APVentureEngine/warn-act-notices/blob/main/states/georgia.md) · [North Carolina](https://github.com/APVentureEngine/warn-act-notices/blob/main/states/north-carolina.md)
<!-- STATE_MD_INDEX:END -->

<!-- EMPLOYER_MD_INDEX:START -->

### Browse by employer

[**29,971 per-employer pages**](employers/README.md) — every notice an employer has filed, which states, which years. Most notices on record: [Boeing](employers/b/boeing.md), [Aramark](employers/a/aramark.md), [Sodexo](employers/s/sodexo.md), [Stanadyne](employers/s/stanadyne.md), [Kmart](employers/k/kmart.md), [Kaiser Foundation Hospitals](employers/k/kaiser-foundation-hospitals.md), [Macy's](employers/m/macy-s.md), [Wells Fargo](employers/w/wells-fargo.md).

<!-- EMPLOYER_MD_INDEX:END -->

<!-- ALERT_MD_INDEX:START -->
**Want to be told when a company files? Alert options and real alert volume, per state:** [all 48 states](https://github.com/APVentureEngine/warn-act-notices/blob/main/layoff-alerts/README.md) · [California alerts](https://github.com/APVentureEngine/warn-act-notices/blob/main/layoff-alerts/california.md) · [Texas alerts](https://github.com/APVentureEngine/warn-act-notices/blob/main/layoff-alerts/texas.md) · [New York alerts](https://github.com/APVentureEngine/warn-act-notices/blob/main/layoff-alerts/new-york.md) · [Florida alerts](https://github.com/APVentureEngine/warn-act-notices/blob/main/layoff-alerts/florida.md) · [Illinois alerts](https://github.com/APVentureEngine/warn-act-notices/blob/main/layoff-alerts/illinois.md) · [Washington alerts](https://github.com/APVentureEngine/warn-act-notices/blob/main/layoff-alerts/washington.md)
<!-- ALERT_MD_INDEX:END -->

## Get the data

- CSV: [`data/warn_notices.csv`](data/warn_notices.csv)
- JSON: [`data/warn_notices.json`](data/warn_notices.json)
- Coverage/freshness metadata: [`data/coverage.json`](data/coverage.json)
- Per-state CSVs: [`data/by-state/`](data/by-state/) — see table below
- Monthly time series: [`data/monthly_series.csv`](data/monthly_series.csv) (one row per month, 1988 → today, zeros included, notice-date and effective-date bases, `states_reporting` column) and [`data/monthly_by_state.csv`](data/monthly_by_state.csv) (month × state) — also on [Hugging Face](https://huggingface.co/datasets/APProjects/us-layoffs-monthly-time-series-warn-act)
- Employer rollup: [`data/employer_history.csv`](data/employer_history.csv) (one row per canonical employer: notices, workers, states, first/latest filing) — also on [Hugging Face](https://huggingface.co/datasets/APProjects/us-warn-act-employer-layoff-history)
- **New filings, last 7 days:** [`data/latest.csv`](data/latest.csv) / [`data/latest.json`](data/latest.json) — stable raw URLs for "new WARN notices" alerting and dashboards. Rows a state backfilled from its own archive in that window are excluded (old `notice_date`, fresh `first_seen`), so this file stays usable as an alerting trigger; `latest.json` reports how many were dropped as `backfilled_excluded` (no delay)
- **GitHub Release** (versioned snapshot, republished on days the run has time left — `data/` and Hugging Face refresh every day; biggest notices of the fortnight in the notes): [releases](https://github.com/APVentureEngine/warn-act-notices/releases) · stable alias `https://github.com/APVentureEngine/warn-act-notices/releases/latest/download/warn_notices.csv`
- **Every year since 1988, charted** (notices, workers affected and states filing per year — every one of those years is in the free files): https://approjects-warn-act-notices.static.hf.space/history.html
- **How much notice workers actually got** — `notice_days` (layoff date − notice date) computed for every notice in the archive: **15,389 of 31,632** (49%) gave workers under 60 days, median 60 days. Free per-notice CSV from 1988, plus a whole-archive **state × year summary** ([`notice_period_by_state_year.csv`](https://approjects-warn-act-notices.static.hf.space/data/notice_period_by_state_year.csv)). No other free WARN dataset derives this: https://approjects-warn-act-notices.static.hf.space/notice-period.html (as of 2026-09-25)
<!-- notice-period-md --> 📏 **[Notice-period analysis (Markdown, rebuilt daily)](NOTICE-PERIOD.md)** — 15,389 of 31,632 notices gave under 60 days; by state, by year, state × year.
<!--mls-readme--> 📉 **[US Mass Layoff Statistics — monthly, rebuilt daily](MASS-LAYOFF-STATISTICS.md)** — 142 events / 22,737 workers in Jul 2026; the successor in purpose to the BLS MLS program (ended 2013).
<!--upcoming-link--> ⏳ **[Upcoming layoffs — separations dated in the next 90 days](UPCOMING-LAYOFFS.md)** — 21,525 workers across 266 notices separate within 30 days; the forward-looking view, rebuilt every morning.
<!--county-readme--> 🗺️ **[US layoffs by county — 1,837 counties, county FIPS on 90.8% of notices](LAYOFFS-BY-COUNTY.md)** — no state publishes a county code; this resolves the free-text site to the Census join key. Archive daily, county join weekly.
- [Coverage by state](https://approjects-warn-act-notices.static.hf.space/coverage.html) — which states publish a WARN list, which publish none, and how far back each archive goes. <!--coverage-readme-->
- [Layoffs by industry](https://approjects-warn-act-notices.static.hf.space/industries.html) — 15 industry pages (tech, healthcare, plant closings, logistics, retail…), each with its own employers, states and yearly series. <!--industry-readme-->
<!--api-readme--> 🔌 **[Free JSON/CSV API — no key, CORS open](API.md)** — every file above as an HTTP endpoint, with curl/python examples and the schema; [warn-layoff-alert-bot](https://github.com/APVentureEngine/warn-layoff-alert-bot) is a fork-and-run Slack/Discord alert built on it.
- **Employers laying off across state lines** — **2,759** employers filed WARN notices in 2+ states since 1988 (605 in 5 or more), 2,917,877 workers: https://approjects-warn-act-notices.static.hf.space/multi-state.html (as of 2026-09-25)
- **Rebuilt and committed every day** — **26 consecutive days** of data commits to this repo, 2026-08-30 through 2026-09-24, none missed. Counted from `git log -- data` on every build; the commit history is the proof.
- **This year against last, same months** — **2,367** WARN notices Jan-Jul 2026 vs **2,428** Jan-Jul 2025 (**-2.5%**), 211,464 workers this year vs 223,433. By notice date, counted from `data/warn_notices.csv` on every build; the two most recent months are left out because states post late.
- Stats page: https://approjects-warn-act-notices.static.hf.space/index.html
- RSS feed of newly-published notices: https://approjects-warn-act-notices.static.hf.space/feed.xml (no delay)
- Per-state RSS feeds (one state per feed — pipe a single state into Slack/Feedly/Zapier): OPML bundle https://approjects-warn-act-notices.static.hf.space/feeds/feeds.opml, or `feeds/<state>.xml`, e.g. https://approjects-warn-act-notices.static.hf.space/feeds/california.xml
- Weekly summaries (biggest layoffs, per-state totals, one page per week): https://approjects-warn-act-notices.static.hf.space/weekly/index.html
- Monthly summaries (current month updates daily): https://approjects-warn-act-notices.static.hf.space/monthly/index.html
- Yearly totals (current year is a running total, updated daily): https://approjects-warn-act-notices.static.hf.space/yearly/index.html
- Browse layoffs by employer: https://approjects-warn-act-notices.static.hf.space/employers/index.html
- Instant employer search (free tier): https://approjects-warn-act-notices.static.hf.space/search.html
- How this compares to WARNTracker, Intellizence, warn-scraper & state portals: https://approjects-warn-act-notices.static.hf.space/compare.html
- Use it as a free layoffs API (stable raw URLs, curl/pandas/Sheets examples): [API.md](API.md)
- Hugging Face mirror (same free tier, `load_dataset` / pandas ready, re-uploaded every refresh): [APProjects/us-warn-act-layoffs-notices-daily](https://huggingface.co/datasets/APProjects/us-warn-act-layoffs-notices-daily)
- This year only, with by-state, by-month and top-employer rollups already computed (c295): [APProjects/layoffs-2026-us-warn-act-notices-daily](https://huggingface.co/datasets/APProjects/layoffs-2026-us-warn-act-notices-daily)
- Live explorer on Hugging Face Spaces (search employers, newest notices, per-state freshness; reads this repo directly): [APProjects/us-layoff-notices-explorer](https://huggingface.co/spaces/APProjects/us-layoff-notices-explorer)
- Machine-readable schema: [`datapackage.json`](datapackage.json) · Cite this dataset: [`CITATION.cff`](CITATION.cff) · License: [CC BY 4.0](LICENSE)

No login, no API key. Scope of the free dataset, stated plainly: notices from
**1988-01-01** onward, **with no delay** (every notice is published on the refresh that first sees it). The full archive back to 1988
(61,431 notices) and per-customer WARN Watch alerts are the commercial products
that fund the pipeline.

## Schema

Why this repo exists in one paragraph: of the 48 state sources in this refresh, 47 arrive in **37 different column layouts** using **193 distinct column names**, and the employer's name alone is published under **8 different headings** — `Doing Business As Name` (IL) · `Name of Company` (MT) · `Organization Name` (DC). Every one is mapped to the 11 fields below on every refresh, dates parsed to ISO and employers resolved to a canonical name, so one company can be followed across state lines. Counted from the raw files on each build, never hand-written.

| Field | Meaning |
|---|---|
| `id` | stable dedupe hash of (state, company, effective_date, employees) |
| `state` | 2-letter postal code |
| `company` | employer name as published by the state |
| `company_canonical` | cleaned employer name: legal suffixes (Inc/LLC/Corp), store numbers and site tails stripped, casing fixed — groups the same employer across states and renotices |
| `company_dba` | trade name when the state published a "dba"/"aka" alias |
| `location` | city/county/address, best effort |
| `employees_affected` | integer count, empty if the state omitted it |
| `notice_date` | ISO date the notice was received/posted |
| `effective_date` | ISO date the layoff/closure takes effect |
| `notice_type` | layoff/closure label as published |
| `first_seen` | UTC timestamp our pipeline first saw this notice (for imported history — CT 2010–2025 from the agency's archived annual listings — set to the notice date) |

## Coverage

| State | Rows, full archive (1988→, all free) | Rows in free files (1988→, no delay) | CSV | Source last scraped | Newest notice on file | Source status |
|---|---:|---:|---|---|---|---|
| [Alaska](https://approjects-warn-act-notices.static.hf.space/states/alaska.html) (AK) | 66 | 66 | [ak.csv](data/by-state/ak.csv) | 2026-09-24 14:04 UTC | 2026-07-06 | quiet: agency portal checked by hand 2026-09-07, nothing newer published |
| [Alabama](https://approjects-warn-act-notices.static.hf.space/states/alabama.html) (AL) | 1,062 | 1,062 | [al.csv](data/by-state/al.csv) | 2026-09-24 14:05 UTC | 2026-09-21 | current |
| [Arizona](https://approjects-warn-act-notices.static.hf.space/states/arizona.html) (AZ) | 639 | 639 | [az.csv](data/by-state/az.csv) | 2026-09-24 14:04 UTC | 2026-09-15 | current |
| [California](https://approjects-warn-act-notices.static.hf.space/states/california.html) (CA) | 16,640 | 16,640 | [ca.csv](data/by-state/ca.csv) | 2026-09-24 14:06 UTC | 2026-09-18 | current |
| [Colorado](https://approjects-warn-act-notices.static.hf.space/states/colorado.html) (CO) | 841 | 841 | [co.csv](data/by-state/co.csv) | 2026-09-24 14:06 UTC | 2026-09-10 | current |
| [Connecticut](https://approjects-warn-act-notices.static.hf.space/states/connecticut.html) (CT) | 870 | 870 | [ct.csv](data/by-state/ct.csv) | 2026-09-24 14:04 UTC | 2026-09-09 | current |
| [District of Columbia](https://approjects-warn-act-notices.static.hf.space/states/district-of-columbia.html) (DC) | 143 | 143 | [dc.csv](data/by-state/dc.csv) | 2026-09-22 12:26 UTC | 2026-07-27 | current |
| [Delaware](https://approjects-warn-act-notices.static.hf.space/states/delaware.html) (DE) | 100 | 100 | [de.csv](data/by-state/de.csv) | 2026-09-24 14:04 UTC | 2026-08-10 | current |
| [Florida](https://approjects-warn-act-notices.static.hf.space/states/florida.html) (FL) | 3,116 | 3,116 | [fl.csv](data/by-state/fl.csv) | 2026-09-24 14:05 UTC | 2026-09-16 | current |
| [Georgia](https://approjects-warn-act-notices.static.hf.space/states/georgia.html) (GA) | 284 | 284 | [ga.csv](data/by-state/ga.csv) | 2026-09-24 14:03 UTC | 2026-09-14 | current |
| [Hawaii](https://approjects-warn-act-notices.static.hf.space/states/hawaii.html) (HI) | 460 | 460 | [hi.csv](data/by-state/hi.csv) | 2026-09-24 14:04 UTC | 2026-08-20 | current |
| [Iowa](https://approjects-warn-act-notices.static.hf.space/states/iowa.html) (IA) | 419 | 419 | [ia.csv](data/by-state/ia.csv) | 2026-09-24 14:04 UTC | 2026-09-22 | current |
| [Idaho](https://approjects-warn-act-notices.static.hf.space/states/idaho.html) (ID) | 200 | 200 | [id.csv](data/by-state/id.csv) | 2026-09-24 14:04 UTC | 2026-09-17 | current |
| [Illinois](https://approjects-warn-act-notices.static.hf.space/states/illinois.html) (IL) | 4,847 | 4,847 | [il.csv](data/by-state/il.csv) | 2026-09-24 14:06 UTC | 2026-09-16 | current |
| [Indiana](https://approjects-warn-act-notices.static.hf.space/states/indiana.html) (IN) | 1,182 | 1,182 | [in.csv](data/by-state/in.csv) | 2026-09-24 14:06 UTC | 2026-09-02 | current |
| [Kansas](https://approjects-warn-act-notices.static.hf.space/states/kansas.html) (KS) | 791 | 791 | [ks.csv](data/by-state/ks.csv) | 2026-09-24 14:04 UTC | 2026-05-01 | quiet: agency portal checked by hand 2026-09-07, nothing newer published |
| [Kentucky](https://approjects-warn-act-notices.static.hf.space/states/kentucky.html) (KY) | 807 | 807 | [ky.csv](data/by-state/ky.csv) | 2026-09-24 14:04 UTC | 2026-09-10 | current |
| [Louisiana](https://approjects-warn-act-notices.static.hf.space/states/louisiana.html) (LA) | 39 | 39 | [la.csv](data/by-state/la.csv) | 2026-09-24 14:03 UTC | 2026-09-15 | current |
| [Massachusetts](https://approjects-warn-act-notices.static.hf.space/states/massachusetts.html) (MA) | 294 | 294 | [ma.csv](data/by-state/ma.csv) | 2026-09-24 14:04 UTC | 2026-08-31 | current |
| [Maryland](https://approjects-warn-act-notices.static.hf.space/states/maryland.html) (MD) | 1,277 | 1,277 | [md.csv](data/by-state/md.csv) | 2026-09-22 12:28 UTC | 2026-09-14 | current |
| [Maine](https://approjects-warn-act-notices.static.hf.space/states/maine.html) (ME) | 86 | 86 | [me.csv](data/by-state/me.csv) | 2026-09-24 14:04 UTC | 2026-09-09 | current |
| [Michigan](https://approjects-warn-act-notices.static.hf.space/states/michigan.html) (MI) | 2,202 | 2,202 | [mi.csv](data/by-state/mi.csv) | 2026-09-24 14:04 UTC | 2026-09-25 | current |
| [Minnesota](https://approjects-warn-act-notices.static.hf.space/states/minnesota.html) (MN) | 457 | 457 | [mn.csv](data/by-state/mn.csv) | 2026-09-24 14:06 UTC | 2026-06-15 | quiet: agency posts in batches (see state page) |
| [Missouri](https://approjects-warn-act-notices.static.hf.space/states/missouri.html) (MO) | 375 | 375 | [mo.csv](data/by-state/mo.csv) | 2026-09-24 14:04 UTC | 2026-09-16 | current |
| [Mississippi](https://approjects-warn-act-notices.static.hf.space/states/mississippi.html) (MS) | 136 | 136 | [ms.csv](data/by-state/ms.csv) | 2026-09-24 14:06 UTC | 2026-05-11 | quiet: agency posts in batches (see state page) |
| [Montana](https://approjects-warn-act-notices.static.hf.space/states/montana.html) (MT) | 46 | 46 | [mt.csv](data/by-state/mt.csv) | 2026-09-24 14:04 UTC | 2026-07-21 | behind cadence — not yet investigated |
| [North Carolina](https://approjects-warn-act-notices.static.hf.space/states/north-carolina.html) (NC) | 1,086 | 1,086 | [nc.csv](data/by-state/nc.csv) | 2026-09-24 14:06 UTC | 2026-09-16 | current |
| [North Dakota](https://approjects-warn-act-notices.static.hf.space/states/north-dakota.html) (ND) | 54 | 54 | [nd.csv](data/by-state/nd.csv) | 2026-09-24 14:06 UTC | 2026-01-15 | quiet: agency posts in batches (see state page) |
| [Nebraska](https://approjects-warn-act-notices.static.hf.space/states/nebraska.html) (NE) | 845 | 845 | [ne.csv](data/by-state/ne.csv) | 2026-09-24 14:04 UTC | 2026-08-26 | current |
| [New Jersey](https://approjects-warn-act-notices.static.hf.space/states/new-jersey.html) (NJ) | 2,330 | 2,330 | [nj.csv](data/by-state/nj.csv) | 2026-09-24 14:04 UTC | 2026-09-01 | current |
| [New Mexico](https://approjects-warn-act-notices.static.hf.space/states/new-mexico.html) (NM) | 116 | 116 | [nm.csv](data/by-state/nm.csv) | 2026-09-24 14:03 UTC | 2026-06-29 | quiet: agency portal checked by hand 2026-09-07, nothing newer published |
| [Nevada](https://approjects-warn-act-notices.static.hf.space/states/nevada.html) (NV) | 613 | 613 | [nv.csv](data/by-state/nv.csv) | 2026-09-24 14:05 UTC | 2026-06-29 | quiet: agency posts in batches (see state page) |
| [New York](https://approjects-warn-act-notices.static.hf.space/states/new-york.html) (NY) | 6,515 | 6,515 | [ny.csv](data/by-state/ny.csv) | 2026-09-24 14:07 UTC | 2026-08-25 | current |
| [Ohio](https://approjects-warn-act-notices.static.hf.space/states/ohio.html) (OH) | 1,072 | 1,072 | [oh.csv](data/by-state/oh.csv) | 2026-09-24 14:06 UTC | 2026-09-21 | current |
| [Oklahoma](https://approjects-warn-act-notices.static.hf.space/states/oklahoma.html) (OK) | 220 | 220 | [ok.csv](data/by-state/ok.csv) | 2026-09-24 14:04 UTC | 2026-08-17 | current |
| [Oregon](https://approjects-warn-act-notices.static.hf.space/states/oregon.html) (OR) | 1,371 | 1,371 | [or.csv](data/by-state/or.csv) | 2026-09-24 14:04 UTC | 2026-09-23 | current |
| [Pennsylvania](https://approjects-warn-act-notices.static.hf.space/states/pennsylvania.html) (PA) | 1,896 | 1,896 | [pa.csv](data/by-state/pa.csv) | 2026-09-24 14:05 UTC | 2026-09-21 | current |
| [Rhode Island](https://approjects-warn-act-notices.static.hf.space/states/rhode-island.html) (RI) | 126 | 126 | [ri.csv](data/by-state/ri.csv) | 2026-09-24 14:06 UTC | 2026-06-29 | quiet: agency portal checked by hand 2026-09-07, nothing newer published |
| [South Carolina](https://approjects-warn-act-notices.static.hf.space/states/south-carolina.html) (SC) | 604 | 604 | [sc.csv](data/by-state/sc.csv) | 2026-09-24 14:04 UTC | 2026-08-28 | current |
| [South Dakota](https://approjects-warn-act-notices.static.hf.space/states/south-dakota.html) (SD) | 80 | 80 | [sd.csv](data/by-state/sd.csv) | 2026-09-24 14:04 UTC | 2026-08-10 | current |
| [Tennessee](https://approjects-warn-act-notices.static.hf.space/states/tennessee.html) (TN) | 1,061 | 1,061 | [tn.csv](data/by-state/tn.csv) | 2026-09-24 14:05 UTC | 2026-09-02 | current |
| [Texas](https://approjects-warn-act-notices.static.hf.space/states/texas.html) (TX) | 2,391 | 2,391 | [tx.csv](data/by-state/tx.csv) | 2026-09-24 14:05 UTC | 2026-09-15 | current; agency posts in batches (see state page) |
| [Utah](https://approjects-warn-act-notices.static.hf.space/states/utah.html) (UT) | 282 | 282 | [ut.csv](data/by-state/ut.csv) | 2026-09-24 14:04 UTC | 2026-08-13 | current |
| [Virginia](https://approjects-warn-act-notices.static.hf.space/states/virginia.html) (VA) | 1,126 | 1,126 | [va.csv](data/by-state/va.csv) | 2026-09-24 14:04 UTC | 2026-09-16 | current |
| [Vermont](https://approjects-warn-act-notices.static.hf.space/states/vermont.html) (VT) | 70 | 70 | [vt.csv](data/by-state/vt.csv) | 2026-09-24 14:04 UTC | 2026-06-17 | quiet: agency portal checked by hand 2026-09-07, nothing newer published |
| [Washington](https://approjects-warn-act-notices.static.hf.space/states/washington.html) (WA) | 1,519 | 1,519 | [wa.csv](data/by-state/wa.csv) | 2026-09-24 14:04 UTC | 2026-09-22 | current |
| [Wisconsin](https://approjects-warn-act-notices.static.hf.space/states/wisconsin.html) (WI) | 617 | 617 | [wi.csv](data/by-state/wi.csv) | 2026-09-24 14:04 UTC | 2026-08-24 | current |
| [West Virginia](https://approjects-warn-act-notices.static.hf.space/states/west-virginia.html) (WV) | 58 | 58 | [wv.csv](data/by-state/wv.csv) | 2026-09-24 14:05 UTC | 2026-08-19 | current |

**Not covered (3 states):** [Arkansas](https://dws.arkansas.gov/workforce-services/employers/dislocated-worker-services/) (the state does not publish company-level WARN notices at all (confidentiality, A.C.A. § 11-10-314)), [New Hampshire](https://www.nhes.nh.gov/employers/business-compliance) (agency web server refuses every request from our servers, including robots.txt (403)), Wyoming (WARN filings are non-public by state statute). We do not guess or
backfill these from third parties; if a state opens a public listing it is added.

## What normalization actually does

State portals spell the same employer many ways (store numbers, site tails,
suffixes, ALL CAPS). `company_canonical` collapses them so you can count and
watch an employer across states and years — the part no raw scraper output gives you:

- **Kmart** ← 131 raw spellings, e.g. `KMART`; `KMART #3035`; `KMART #3729`; `KMART #3999`
- **Burlington Coat Factory of Texas** ← 82 raw spellings, e.g. `Burlington Coat Factory of Texas Inc. dba Burlington # 285`; `Burlington Coat Factory of Texas Inc. dba Burlington #1007`; `Burlington Coat Factory of Texas Inc. dba Burlington #1022`; `Burlington Coat Factory of Texas Inc. dba Burlington #1029`
- **Cinemark** ← 72 raw spellings, e.g. `CineMark`; `Cinemark`; `Cinemark *`; `Cinemark USA Inc.`

**Archive sample (free):** the complete Oregon back-catalogue, 1988→present
(1,371 rows, same schema as the full free 1988+ archive):
[`data/samples/oregon-warn-notices-1988-present.csv`](data/samples/oregon-warn-notices-1988-present.csv).

Each state also ships as its own CSV in [`data/by-state/`](data/by-state/) —
e.g. California layoff notices: [`data/by-state/ca.csv`](data/by-state/ca.csv).

## Biggest layoff notices — last 30 days (2026-08-26 to 2026-09-25)

| Company | State | Location | Workers | Notice date (or layoff date where the state publishes none) |
|---|---|---|---:|---|
| Legendary Fruit | WA | Yakima, Wapato | 1,220 | 2026-09-10 |
| Conifer's Health Solutions | TX | Dallas, Dallas | 1,037 | 2026-09-08 |
| Blue Cascade Orchards | WA | Yakima, Okanogan, Franklin, Grant, Adams, Walla Walla, and Benton Counties | 792 | 2026-09-14 |
| 24Hr Homecare | CA | Los Angeles County | 738 | 2026-08-31 |
| Columbia Reach Chiawana Orchards | WA | Yakima, Kittitas, and Grant Counties | 570 | 2026-09-17 |
| Crothall Healthcare | VA | Richmond | 545 | 2026-08-28 |
| Wonder Group | NJ | Parsippany | 533 | 2026-09-01 |
| Pacific Ag Services | WA | Grant and Franklin Counties | 530 | 2026-09-16 |
| Gilbert Orchards | WA | Yakima, Franklin and Grant Counties | 518 | 2026-09-03 |
| Sagemoor Group Management Services | WA | Yakima, Franklin, and Adams Counties | 443 | 2026-09-17 |
| Owens & Minor (Avid Medical LLC) | VA | Toano | 419 | 2026-09-16 |
| Oracle America | CA | Santa Clara County, San Mateo County | 378 (2 phases) | 2026-09-15 |
| Loftus Administrative Services | WA | Yakima County | 376 | 2026-09-15 |
| Uber Technologies | IL | Chicago, 433 West Van Buren St. | 363 | 2026-09-02 |
| Oracle America | WA | Seattle | 359 | 2026-09-14 |

_Grouped per notice (phased notices count once, workers summed). 5 row(s) naming only a facility are omitted here, kept in the CSV._

## Monthly trend (last 12 months, this dataset)

| Month | Notices | Workers affected |
|---|---:|---:|
| 2025-09 | 310 | 33,850 |
| 2025-10 | 501 | 50,621 |
| 2025-11 | 325 | 27,283 |
| 2025-12 | 174 | 13,847 |
| 2026-01 | 377 | 35,748 |
| 2026-02 | 366 | 29,544 |
| 2026-03 | 340 | 24,463 |
| 2026-04 | 381 | 33,698 |
| 2026-05 | 294 | 45,939 |
| 2026-06 | 370 | 20,868 |
| 2026-07 | 239 | 21,204 |
| 2026-08 | 253 | 23,889 |
| 2026-09 _(month to date, 25 days)_ | 176 | 18,831 |

Machine-readable trends (per-state monthly notices + workers affected, last 24
months): [`data/trends.json`](data/trends.json) — stable raw URL for embedding
in dashboards/articles:
`https://raw.githubusercontent.com/APVentureEngine/warn-act-notices/main/data/trends.json`
(CC BY 4.0, credit "WARN Feed").

More states are added as their sources are verified. Some states publish
incomplete fields; we normalize what exists and never invent values. Precision
note: NJ publishes only the posting month, so NJ `notice_date` is month
precision (day pinned to 01, year inferred from the effective date); PA's
archived monthly listings (2011–2025) likewise carry the month received, day
pinned to 01. IL `notice_date` is the earliest notification on record; amended
IL notices carry the latest revised headcount. **Blank `notice_date` is not a
gap in our coverage:** South Carolina, Michigan and Pennsylvania's current
listing publish no notice date at all, and Minnesota and Indiana publish one for
only some rows — almost all of those rows carry the layoff date in
`effective_date` instead, and the per-state freshness in `coverage.json` is
measured on whichever of the two the agency publishes. Sorting or filtering on
`effective_date` rather than `notice_date` is what you want if you need every
dated row.

**The exception, stated plainly: 196 of 61,431 notices (0.3%) carry
no date in either column** — mostly IN 164, NJ 10, PA 6 — because the agency
published none. We do not invent one, so those rows are absent from every
monthly count, time series and chart on this site and in the data files;
a per-month sum will therefore fall short of the headline total by that many
rows. Filter on `notice_date == "" and effective_date == ""` to list them.
Where an agency lists several dates for one notice (phased layoffs, a
range), we carry the first date listed.

## WARN Watch — the only paid tier

The free files above are complete and carry no delay. What they cannot do is
watch YOUR list every morning. Commercial options:

- **[WARN Watch — $49/year, one payment](https://approjects-warn-act-notices.static.hf.space/watch.html)** — up to 500 employer
  terms plus whole-state watches across all 48 covered states, matched on
  every daily refresh for 365 days; hits land on a private alert page + calendar
  (.ics, 14-day reminders) + a private RSS feed for Slack (`/feed subscribe`), Teams
  (Workflows app → "Post to a channel when an RSS feed is published") or classic
  Outlook — no login, no email, and no credential of yours ever handed to us.
  Every alert carries that employer's whole filing record ("Boeing — 403rd WARN notice from this employer since 1998 · 13 states · 42,893 workers to date · last filed 2025-04-04") — history a keyword rule on an RSS feed cannot see.
  [See a real alert page](https://approjects-warn-act-notices.static.hf.space/watch-sample.html) · [what it checks and its limits](https://approjects-warn-act-notices.static.hf.space/watch.html) · [free 30-day trial](https://approj.gumroad.com/l/warn-free-watch) · [buy — $49/year](https://approj.gumroad.com/l/warn-watch).
That is the only thing we sell. The data is not: every notice we have back to
1988 (61,431 rows, all 48 states, CSV + JSON) is in the free files above,
with no paywalled years and no account.

Questions first? [Open an issue](https://github.com/APVentureEngine/warn-act-notices/issues) with the label `commercial`.

**Not deciding today?** [Join the update list →](https://approj.gumroad.com/subscribe) — one email when a
new dataset or tier is published here; nothing promotional, and nothing else (a
state added or a column renamed ships in the [`data/` folder and the GitHub release](https://github.com/APVentureEngine/warn-act-notices/releases)
instead, which needs no address). The list is
shared across APProjects datasets, holds an email address only, is run by
Gumroad, and any message unsubscribes you. Rather give no address at all?
[Watch the repo's releases](https://github.com/APVentureEngine/warn-act-notices/subscription) — GitHub notifies you on
every daily republish, and a new state or changed field is in those notes the
day it lands.

## Sources & attribution

Data originates from official state labor department WARN listings. Collection
uses the excellent Apache-2.0 [biglocalnews/warn-scraper](https://github.com/biglocalnews/warn-scraper)
(Stanford Big Local News) plus our own normalization, dedup, and freshness
layer. This project is not affiliated with Big Local News or any state agency.

## License & disclaimer

Dataset (this repo's `data/`): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) —
use it for anything, credit "WARN Feed (https://github.com/APVentureEngine/warn-act-notices)".

Best-effort normalization of public records. States amend and correct notices;
verify against the official state source before relying on any single row.
