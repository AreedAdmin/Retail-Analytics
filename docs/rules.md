# Project Rules & Standards

All team members must follow these rules regardless of whether work is done manually or AI-assisted. These are non-negotiable ground rules to prevent conflicts, bugs, and integration failures.

---

## 1. Syntax & Naming Conventions

- All variable names, function names, file names, and column names must use **snake_case**.
- No camelCase, PascalCase, or kebab-case anywhere in the codebase.
- Examples:
  - `demand_forecast.py` not `DemandForecast.py`
  - `price_elasticity` not `priceElasticity`
  - `sku_id` not `SKUId`

---

## 2. Environment Variables

- **All environment variables (API keys, secrets, config values) must be stored as GitHub Repository Secrets**, not in local `.env` files.
- Never commit secrets or API keys to any file in the repo.
- Access secrets in code via environment variables (e.g., `os.environ["OPENAI_API_KEY"]`).
- Do not rely on `.gitignore` to protect secrets — assume any local file can accidentally be committed.
- To add a secret: GitHub repo → Settings → Secrets and variables → Actions → New repository secret.

---

## 3. Folder Structure

Each team works exclusively within their own folder. Do not create files outside your designated folder unless coordinating with the integration lead.

```
Retail-Group-Assignment/
├── ml_forecasting/          # ML Pod A: Demand Forecasting
├── ml_promotions_pricing/   # ML Pod B: Promotion + Price Elasticity
├── ai/                      # AI Pod: Narratives + Query Interface
├── dashboard/               # Dashboard & Integration Lead
├── data/                    # Shared read-only raw and processed data (no edits without agreement)
├── requirements.txt         # Root-level dependency file (all teams contribute here)
├── rules.md
└── Scope.md
```

- Each team reads from `data/` but does not modify raw files.
- Processed outputs should be written to your own folder or a shared `outputs/` subfolder agreed with the integration lead.

---

## 4. Version Control (Dependencies)

- A single `requirements.txt` file lives in the **root directory**.
- When you add a new package, add it to `requirements.txt` with a pinned version:
  ```
  pandas==2.2.2
  scikit-learn==1.4.2
  ```
- Do not use unpinned versions (e.g., `pandas` with no version number).
- Before pushing, run `pip freeze | grep <your_package>` to confirm the exact version.
- If you install something locally, update `requirements.txt` in the same commit.

---

## 5. Team Logs

- Every team folder must contain a `team_log.md` file.
- This log must be updated **every time meaningful work is done** — treat it as a living record.
- When using AI to generate code, prompt it to update `team_log.md` as part of every session.
- Required log entry format:

  ```markdown
  ## YYYY-MM-DD
  **Author(s):** [names]
  **Work done:** [brief description]
  **Files changed:** [list of files]
  **Blockers / notes:** [anything relevant for integration]
  ```

---

## 6. Branching & Version Control Workflow

- Each team works on their own dedicated branch:
  - ML Forecasting: `ml`
  - ML Promotions + Pricing: `ml` (same branch, coordinate with the other ML pair)
  - AI Pod: `ai`
  - Dashboard Lead: `analytics`
- **Never push directly to `main`.**
- Workflow:
  1. Pull latest from your branch before starting work.
  2. Commit regularly with clear messages (e.g., `add elasticity model for SKU-level outputs`).
  3. When a feature is complete and tested, open a **Pull Request to `main`**.
  4. At least one other team member must review and approve the PR before it is merged.
  5. The integration lead performs the final merge into `main`.

---

## 7. Model Footprint & Hosting

- ML models are lightweight and **CPU-only** — the forecasting model is a
  few MB with sub-second inference. The app deploys on a **free Hugging Face
  Spaces CPU instance**; no GPU is used or required.
- Guidelines:
  - Prefer lightweight models: linear regression, gradient boosting
    (HistGBM/XGBoost/LightGBM), classical time series.
  - The LLM is **not** run in-process: the AI narrative layer calls
    **Ollama Cloud** (`gpt-oss:120b-cloud`) with OpenAI/Anthropic API
    fallback and an offline grounded extractor — so model size never
    constrains the dashboard.
  - Keep `requirements.txt` pinned to the validated environment so the
    Space build is reproducible.

---

## 8. General AI-Assisted Coding Rules

- AI-generated code must be reviewed, understood, and tested by a human before committing.
- Do not commit AI output blindly atleast understand what has been written at a high level so you know whats going on.
- Always prompt AI to follow these rules (snake_case, update team_log.md, pin dependencies).
- Document any AI-generated sections with a comment: `# AI-assisted: reviewed by [name]`.
