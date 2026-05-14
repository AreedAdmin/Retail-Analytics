# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project context

This is an Imperial College group assignment to build an **AI-augmented retail marketing analytics dashboard** in Python. The project is graded against a 100-point rubric (see `docs/scope.md`) and the full module-level deliverable spec is in `docs/deliverable.md`. The mandatory team rules — branching, naming, dependency pinning, secrets — live in `docs/rules.md`.

**Before making any non-trivial change, read every `.md` file in `docs/`** to gather full context. The `docs/` folder is the canonical brief for this project — assignment scope, module spec, team rules, tech stack, and this `CLAUDE.md` itself all live there. New docs added to `docs/` should be treated as required reading too, so list the directory (`ls docs/`) and read whatever is present, not only the files named here.

The repo is currently a scaffold: top-level folders (`ai/`, `analytics/`, `dashboard/`, `ml/`, `data/`) and their subfolders exist as empty placeholders. `requirements.txt` is empty. The only real content right now is `data/data_raw.csv` and the docs.

## Dataset

`data/data_raw.csv` — weekly SKU-level sales data. Columns: `week`, `sku`, `weekly_sales`, `feat_main_page` (promotion flag, boolean), `color`, `price`, `vendor`, `functionality` (product category). This is the single source of truth for all modules; treat it as read-only. Processed outputs go into the owning team's folder.

## Architecture — module ownership and layering

The app is a single Gradio web app with a persistent sidebar that routes to 10 modules. Module owners and folder ownership are split across four teams, and this split is enforced:

| Team | Folder | Modules they own |
|---|---|---|
| Dashboard Lead | `dashboard/` | 1 Overview, 2 Data Explorer, 5 Scenario Simulator (shared), 10 Appendix/Export |
| ML Pod A | `ml/forecasting/`, `ml/ml_forecasting/` | 6 Demand Forecasting, 7 Promotion Lift (shared) |
| ML Pod B | `ml/promotions/`, `ml/pricing/`, `ml/ml_promotions_pricing/` | 3 Promotion Effectiveness, 4 Price Elasticity, 7 Promotion Lift (shared) |
| AI Pod | `ai/` (prompts, services, context_builders, guardrails, evaluations) | 8a/b/c Chat + Click-to-Summarise + Multi-select |
| Analytics (Dashboard) | `analytics/promotions/`, `analytics/pricing/`, `analytics/scenarios/`, `analytics/common/` | Statistical calculations consumed by Modules 3–5 |

`docs/tech_stack.md` describes the 7-layer architecture (Presentation → Orchestration → Analytics → ML → AI → Data Access → Infra). Each team works within their layer and folder; cross-team coupling happens **only** through the integration contracts below.

## Integration contracts (DO NOT change without coordinating)

These data shapes are how the dashboard, ML, analytics, and AI layers communicate. Changing a contract requires updating consumers in every other folder, so flag it explicitly before editing.

- **Forecast output:** `sku_id`, `period`, `y_true`, `y_pred`, `y_lower`, `y_upper`, `model_name`
- **Promotion output:** `sku_id`, `period`, `promotion_flag`, `incremental_sales`, `lift_pct`
- **Elasticity output:** `sku_id`, `elasticity_value`, `confidence_low`, `confidence_high`
- **Scenario output:** `sku_id`, `scenario_name`, `price_change_pct`, `demand_change_pct`, `revenue_change_pct`
- **AI context payload:** structured JSON with `module_name`, `chart_id`, `metrics`, `key_findings`

Note: the raw CSV uses `sku` (not `sku_id`) and `week` (not `period`). Loaders should normalise to the contract names at the data-access boundary, not deep inside model code.

## AI integration design — non-optional grading criteria

The AI layer is part of the grade, not a feature. When adding anything that calls an LLM:

1. **Context packaging** — the LLM never sees raw CSV rows. Build a structured `{module_name, chart_id, metrics, key_findings}` payload from model outputs and pass that.
2. **Prompt templates live in `ai/prompts/`** as files, not inline strings. If you're about to write a prompt as a Python f-string in a module, stop and put it in `ai/prompts/` instead.
3. **Response labelling** — every AI response must be tagged `[Data-grounded]` (traceable to a specific figure in the context) or `[General inference]` (reasoning beyond supplied data). This is enforced in the response post-processor, not left to the prompt.
4. **Hallucination guardrails** — the prompt must instruct the model to say "I don't have data on this" when context is insufficient; the guardrail layer (`ai/guardrails/`) then validates numbers in the response against the context payload.
5. **Failure logging** — bad AI outputs are captured for Module 9 (Critical Reflection). Don't silently fix prompts; log the failure case.

LLM provider is Claude (Anthropic) or OpenAI via API. Local LLMs via Ollama are allowed within the 8 GB RAM cap. **API keys are GitHub Repository Secrets only** — never commit a `.env`, and read via `os.environ[...]`.

## Hard rules — these are non-negotiable

From `docs/rules.md`:

- **snake_case everywhere** — files, variables, functions, columns. Not camelCase, not PascalCase. The raw CSV happens to use snake_case already; keep it that way through processing.
- **8 GB RAM cap** on every model. No model is allowed to break this — it must run on every team member's laptop. If you need XGBoost/LightGBM, fine. If you need a large neural net, quantise or drop it.
- **`requirements.txt` is pinned, root-level, single file.** All teams contribute. Pin exact versions (`pandas==2.2.2`, not `pandas`). Update it in the same commit that introduces the import.
- **Branching:** `ml`, `ai`, `analytics` branches → PR to `main`. Never push directly to `main`. The Dashboard/integration lead does the final merge.
- **AI-generated code must carry `# AI-assisted: reviewed by [name]`** and be reviewed by a human before commit.
- **Each team folder has a `team_logs.md`** (note: the existing files use the plural `team_logs.md`, not `team_log.md` as the rules doc says). Update it when meaningful work happens — date, author, work done, files changed, blockers.

## Common commands

The repo has no source files yet, so the conventional commands aren't wired up. Once code lands, expect:

- Install deps: `pip install -r requirements.txt`
- Run the app: `python -m dashboard.app` (or `gradio dashboard/app.py` — pick one and document it here when the entry point is created)
- Lint/format: `ruff check .` and `black .` (both listed in `docs/tech_stack.md` as tooling)
- Tests: `pytest` (per-module test runs: `pytest ml/forecasting/`)
- Memory check before merging a model: profile with `memory_profiler` to confirm < 8 GB

Update this section once the entry points actually exist.

## When working in this repo

- **Don't create files outside your team's folder** without coordinating — this is a strict rule from `docs/rules.md` to prevent merge conflicts across four teams.
- **Don't modify `data/data_raw.csv`.** Processed outputs go into the owning team's folder or an agreed `outputs/` subfolder.
- **Don't invent contracts.** If a module needs a new field, propose it as a contract change and update every consumer — don't quietly add a column to one team's output.
- The `team_logs.md` in `ai/`, `ml/`, `dashboard/` are currently empty placeholders — they exist so the directories show up on GitHub. Treat them as the team's living work log once real work starts.
