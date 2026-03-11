# KWSL Market Reports — Project Instructions

## What This Project Does
Generates monthly Phoenix real estate market reports for KW Sonoran Living.
One HTML file per month. Pushed to GitHub Pages.

## Scope
This project does ONE thing: produce and publish market report HTML files.
Do not take actions outside this scope without explicit instruction.

## Monthly Workflow
1. Read calculator JSON from /input/
2. Fetch Cromford research
3. Source article options — present to user, wait for selection
4. Generate narratives using /prompts/narrative-prompts.md
5. Assemble HTML from /templates/base-report.html
6. Push to GitHub Pages

## Output Naming Convention
phoenix-market-report-[month]-[year].html
Example: phoenix-market-report-march-2026.html

## Rules — Never Break These
- No em dashes in any generated copy
- No filler transitions ("In conclusion", "It's worth noting", etc.)
- No AI writing patterns
- Narrative prose only — no bullet points in report copy
- All directional claims must be verified against input data before writing
- Never predict rate direction — report current state only

## Error Log — Read Before Every Run
Any error encountered in a prior run is logged below with its fix.
Before generating anything, read this section and apply all listed fixes.

### Known Issues
*(none yet — errors will be logged here as they occur)*

## How To Log An Error
When something goes wrong or produces bad output:
1. Add an entry below under Known Issues
2. Format: `[DATE] — [what broke] — [what the fix
