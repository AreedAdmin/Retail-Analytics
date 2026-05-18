---
title: AI-Augmented Retail Analytics Dashboard
emoji: 📊
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 6.9.0
app_file: app.py
python_version: "3.10"
pinned: false
---

# AI-Augmented Retail Analytics Dashboard

Gradio dashboard over weekly retail data: KPIs, demand forecasting, promotion
lift, and an LLM narrative/chat layer grounded in model outputs.

- **App entrypoint:** `app.py` (HF Spaces) / `python -m dashboard.app.main`
- **ML models:** load in-process from `ml/ml_forecasting/outputs/`
  (forecasting) — see `ml/ml_forecasting/README.md` to regenerate.
- **AI layer:** Ollama Cloud (`gpt-oss:120b-cloud`) with API/offline
  fallback — see `deploy.md`.

## Configuration (environment variables / Space secrets)

| Variable | Required | Purpose |
|---|---|---|
| `OLLAMA_API_KEY` | for AI narrative | Ollama Cloud bearer token |
| `OLLAMA_MODEL` | no | default `gpt-oss:120b-cloud` |
| `OLLAMA_HOST` | no | default `https://ollama.com` (no `/api` suffix) |
| `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` | optional | LLM fallback |

Without any key the dashboard still runs (offline grounded extractor). See
`deploy.md` Appendix A/B for getting the key and deploying.
