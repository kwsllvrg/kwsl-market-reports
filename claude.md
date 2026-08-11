# KWSL Market Reports — Project Instructions

## What This Repo Is
The **publish + archive** home for KW Sonoran Living's monthly Greater Phoenix
market report. GitHub Pages serves it at **https://stats.mykwsl.com/** (custom
domain via `CNAME`; also answers at `kwsllvrg.github.io/kwsl-market-reports`).

This repo does NOT build the report. The report is **built in a separate dir**,
`/home/aafdev/cromford_workflow/`, and the finished HTML is copied here to go
live. Keep changes scoped to publishing, the Vault, and the design template.

## Where The Build Happens (not here)
`/home/aafdev/cromford_workflow/` — reads the month's ARMLS calculator JSON +
Cromford notes + article file, injects data, writes narratives, and produces:
- `output/report-<Month>-2026.html` (agent edition, 16 pages)
- `output/report-<Month>-2026-consumer.html` (consumer edition, 14 pages)

Build scripts there: `build_<month>.py` (numeric/structural injector, copy last
month's), `build_consumer.py` (derives the consumer edition). See that dir's
memory/notes for the per-page data map and known stale-value traps.

## Output Naming — REQUIRED
GitHub Pages URLs are **case-sensitive**, so everything here is **lowercase**.
Each month publishes FOUR files (two editions, each in two names):

| File in repo root | Purpose | Public URL |
|---|---|---|
| `report-<month>-2026.html` | agent, canonical | `/report-<month>-2026.html` |
| `report-<month>-2026-consumer.html` | consumer, canonical | `/report-<month>-2026-consumer.html` |
| `<mon>2026.html` | agent, short copy | `/​<mon>2026` (extensionless) |
| `<mon>2026con.html` | consumer, short copy | `/​<mon>2026con` |

- `<mon>` = 3-letter lowercase month (`aug`, `sep`, …).
- The short-name files are plain COPIES of the canonical files, added so the
  shareable link is short (replaces the old manual GoDaddy short-URL step).
  Pages serves them extensionless: **`stats.mykwsl.com/aug2026`**.
- **Keep BOTH names.** `build_archive.py` and the Vault key on the canonical
  `report-*` names — never rename those, only add the short copies.

## Monthly Publish Flow (run after the report is built + verified in cromford_workflow)
1. Copy both editions from `cromford_workflow/output/` into this repo root,
   renaming to **lowercase**:
   - `report-<Month>-2026.html` → `report-<month>-2026.html`
   - `report-<Month>-2026-consumer.html` → `report-<month>-2026-consumer.html`
2. Make the short-name copies: `cp report-<month>-2026.html <mon>2026.html` and
   `cp report-<month>-2026-consumer.html <mon>2026con.html`.
3. `python3 build_archive.py` — regenerates the Vault `index.html` (auto-picks up
   the new month from its `report-<month>-2026.html`).
4. `git add` the 4 report files + `index.html`, commit (with the standard
   Co-Authored-By trailer), `git push origin main`. If push is rejected:
   `git pull --rebase origin main` then push. (`origin` carries a working PAT.)
5. Verify: `curl -I` HTTP **200** on the short link (`/<mon>2026`) and the
   canonical (`/report-<month>-2026.html`). Pages rebuilds in ~1–3 min.

## Key Files In This Repo
- `index.html` — the **Market Update Vault** landing page (auto-generated; do not
  hand-edit). Grid of month cards newest-first, live cover previews, click-through
  modal. Also lists 7 legacy Heyzine editions (Aug 2025–Feb 2026).
- `build_archive.py` — the Vault generator. Scans `report-<month>-<year>.html`
  (excludes `-consumer`), sorts newest-first, writes `index.html`. Cover-preview
  crop differs by design era: new iron-ore design (**July 2026+ = 162px** nav),
  older serif (**through June 2026 = 257px**) — constants `NEW_DESIGN_FROM=(2026,7)`,
  `PV_SCALE=0.402`. Legacy Heyzine cards are a hardcoded `LEGACY` list.
- `preview-full-report.html` — the current design/UX template (iron-ore redesign).
- `tools/cromford-calculator_8.html` — the ARMLS data calculator.
- `CNAME` → `stats.mykwsl.com`.
- `report-*.html` / `<mon>2026*.html` — every published month.

## Copy Rules — Never Break These (report content)
- No em dashes anywhere in copy.
- No filler transitions ("In conclusion", "It's worth noting", etc.) or AI
  writing patterns.
- Narrative prose only — no bullet points in report copy.
- "Scripts" is not KW usage — say conversations or dialogues.
- All directional claims verified against the source JSON/Cromford notes before
  writing. Never predict rate direction — report current state only.
- Seller-concession % is a separate Alex-supplied figure, not the listing
  success rate; label month-to-date figures as such (e.g. "through Aug 10").

## Error Log — Read Before Every Publish
- **2026-07**: capital-`July` output filename shipped; Pages URLs are
  case-sensitive → always rename to lowercase on copy. Fixed in the flow above.
- **2026-08**: the old version of this file described a stale build workflow
  (`phoenix-market-report-[month]` naming, `/input/`, in-repo build). Rewritten
  to match the real pipeline: report is built in `cromford_workflow`, this repo
  publishes + archives. Naming is `report-<month>-2026.html` + short copies.

## How To Log An Error
When something breaks or produces bad output: add a dated entry under
**Error Log** — `YYYY-MM — what broke — the fix` — before the next run.
