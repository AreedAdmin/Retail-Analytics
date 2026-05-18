# AI-Augmented Retail Analytics Dashboard

Imperial College Retail & Marketing Analytics group project — an interactive Python (Gradio) dashboard combining ML outputs, statistical analytics, and a grounded GenAI layer.

## Quick start

```bash
pip install -r requirements.txt
python -m dashboard.app.main
```

Open the URL printed in the terminal (default `http://127.0.0.1:7860`).

### LLM provider (optional)

Set environment variables for live AI (otherwise echo/offline fallback):

```bash
# Ollama (local)
set LLM_PROVIDER=ollama

# AWS Bedrock
set LLM_PROVIDER=bedrock
```

See `ai/CLOUD_SETUP.md` for full configuration.

## Modules

| # | Module | Status |
|---|--------|--------|
| 1 | Overview | Implemented |
| 2 | Data Explorer | Implemented |
| 3 | Promotion Effectiveness | Implemented (ML outputs) |
| 4 | Price Elasticity | Implemented (log-log regression) |
| 5 | Scenario Simulator | Implemented |
| 6 | Demand Forecasting | Baseline linear forecast |
| 7 | Promotion Lift Model | Implemented (ML notebook outputs) |
| 8 | AI Chat | Implemented |
| 9 | Critical Reflection | Implemented |
| 10 | Appendix & Export | Implemented |

## Project structure

```
data/                 # Raw CSV (read-only)
dashboard/            # Gradio app + analytics layer
ml/                   # Notebooks and model outputs
ai/                   # Prompts, guardrails, LLM services
docs/                 # Assignment spec and team rules
```

## Generate ML outputs

Promotion lift (Modules 3 & 7):

```bash
# Run notebook: ml/ml_promotions_pricing/promotion_lift_model.ipynb
```

Forecasting (Module 6) auto-generates a baseline on first load; replace with `ml/ml_forecasting/forecasting.ipynb` outputs when ready.

## Documentation

- Full deliverable spec: `docs/deliverable.md`
- Team rules: `docs/rules.md`
- Dashboard plan: `dashboard/PLAN.md`
