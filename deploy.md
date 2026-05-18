# Deployment Plan (DRAFT — for review)

Status: proposal. Nothing here is built yet; this is the decision document for
how the three layers are hosted. Aligns with `docs/tech_stack.md` (Gradio,
Plotly, Ollama + API providers, CSV/parquet data, secrets via repo secrets,
pinned `requirements.txt`, `ml`/`ai`/`analytics` → PR to `main`).

## Scope: three deployable layers

| # | Layer | What it is | Nature |
|---|-------|------------|--------|
| 1 | **Application / client** | The Gradio dashboard (`dashboard/app/main.py`, modules, charts) | Stateless web app |
| 2 | **ML services** | Prediction *algorithms*: forecasting (`HistGBR` etc.) + promo-lift models. Tabular scikit-learn / statsmodels artifacts | CPU, sub-second, tiny artifacts |
| 3 | **AI services** | The chat/narrative **LLM** (Module 8 chat, click-to-summarise, reflections), grounded in ML outputs | LLM inference, network-bound |

These are **independent** concerns. The ML layer produces numbers; the AI
layer turns numbers into language. They must not be conflated (an LLM runtime
like Ollama cannot serve a scikit-learn model, and the sklearn model never
calls an LLM).

---

## Layer 1 — Application / client (Gradio dashboard)

**Decision: host the single Gradio app on a free Hugging Face Space (CPU).**

- One process: `python -m dashboard.app.main`. HF Spaces natively runs Gradio
  and auto-exposes API routes for each module function (free programmatic
  access — no separate API server needed).
- Free CPU Space (~2 vCPU / 16 GB) is ample; the app + ML models are light.
- Trade-offs: free Spaces **sleep after inactivity** (~30 s cold start on
  wake); fine for an assignment/demo. Alternative: run locally or on an
  institutional VM for live grading sessions.
- `requirements.txt` (repo root) must be **pinned** — see Environment parity.

**Open decision:** is the deliverable a public live URL (→ HF Space) or only
run locally during assessment (→ no hosting needed)? Recommend HF Space *plus*
a documented local run path.

---

## Layer 2 — ML services (prediction algorithms)

**Decision: run ML models in-process inside the dashboard app (co-located),
loading committed artifacts. No separate model server, no Ollama.**

Rationale: the forecasting artifact (`HistGBR` + `OneHotEncoder` + small
arrays via `joblib`) is a few MB, CPU-only, <1 s inference. A dedicated
microservice / GPU endpoint / Ollama is unnecessary and against the 8 GB,
simplicity, and reproducibility goals.

- **Artifact storage:** commit `ml/ml_forecasting/outputs/model_artifacts.joblib`
  to the repo (use Git LFS only if >~10 MB — expected not). Version-pinned
  with code; reproducible; no external account. (Alternative: HF Hub model
  repo via `hf_hub_download` — only worth it to swap models without an app
  redeploy; deferred.)
- **Serving path:** `ml/ml_forecasting/pipeline.py` (feature functions lifted
  from the notebook) + `train.py` (fits, dumps artifact) + `forecast_new()`
  (same pipeline → contract rows). Dashboard imports this `ml` API; **no model
  code under `dashboard/`** (preserves Layer 3–4 ownership).
- **Inference constraints (host-independent):** new-data inference needs
  ≥~13 prior weeks of history per SKU and that week's `price`/`feat_main_page`
  (known-in-advance exogenous). `forecast_new()` stitches uploads onto the
  historical tail.
- **Promo-lift model** (`ml/promotions/`) follows the same in-process,
  committed-artifact pattern.

**Expansion (not now, per tech_stack Layer 4):** split ML into a FastAPI
microservice + model registry + drift/retraining triggers if scale demands.

---

## Layer 3 — AI services (chat / narrative LLM)

**Decision: use Ollama Cloud for the AI narrative/chat layer, with an
OpenAI/Anthropic API fallback. The LLM is called over the network from the
app; it never runs the ML model.**

- **Primary:** Ollama Cloud (hosted LLM inference) for chat responses,
  click-to-summarise, and reflection narratives.
- **Fallback:** OpenAI/Anthropic API path (already anticipated in
  tech_stack) when Ollama Cloud is unavailable or rate-limited. Local Ollama
  remains an option for offline dev.
- **Free-tier caveat:** Ollama Cloud offers a free tier with usage limits and
  paid plans for higher throughput. **Exact current quotas must be verified on
  the official pricing page** (they change; not hard-coded here). Design for
  this: short timeouts, retry-then-fallback, and **cache narratives keyed by
  the AI context payload** so repeated views don't re-spend quota.
- **Grounding contract:** all LLM calls receive the `AIContextPayload`
  (`module_name, chart_id, metrics, key_findings`) from `schemas.py`. The AI
  must not fabricate figures and must label grounded vs inferred content
  (tech_stack non-functional constraint, `rules.md`).
- **Secrets:** Ollama Cloud / provider API keys are **HF Space secrets**
  (and/or GitHub repo secrets for CI) — never committed (`.env` local-only).
- **Network:** outbound HTTPS from the HF Space to Ollama Cloud — supported on
  Spaces.

---

## Target topology (Phase 1 — recommended)

```
            ┌────────────────────────── Hugging Face Space (free CPU) ──────────────────────────┐
  Browser ──┤  Gradio app (Layer 1)                                                             │
            │    ├── Module 6 Forecasting tab ── reads ml/.../outputs/forecast.csv (contract)   │
            │    ├── forecast_new()  ── in-process sklearn model (Layer 2, committed artifact)  │
            │    └── Chat / narrative  ── AIContextPayload ──▶ HTTPS ──▶ Ollama Cloud (Layer 3) │
            │                                                   └─ fallback ▶ OpenAI/Anthropic  │
            └───────────────────────────────────────────────────────────────────────────────────┘
   Secrets: Ollama/provider keys = Space secrets. Data: data_raw.csv + outputs/ shipped in repo.
```

- Layer 1 + Layer 2 are **co-located** in one Space (simple, free, fast).
- Layer 3 is **remote** (Ollama Cloud) — the only external inference, and only
  for language, not predictions.

## Phase 2 (expansion, optional / future)

Split Layer 2 into a standalone FastAPI ML service (own Space/container) +
model registry; introduce an AI gateway service with provider routing and a
response-quality scorer. Only if scale, multi-model, or retraining needs it.

---

## Cross-cutting

- **Environment parity (critical):** `joblib`/pickle is scikit-learn-version
  sensitive. Root `requirements.txt` must pin the **training versions**
  (`scikit-learn==1.6.1`, `statsmodels`, `pandas`, `numpy`, `gradio`,
  `plotly`). Mismatch is the #1 HF Spaces failure mode for sklearn artifacts.
- **Secrets:** no secrets committed; HF Space secrets + GitHub repo secrets;
  `python-dotenv` local dev only.
- **Data:** `data/data_raw.csv` and `ml/ml_forecasting/outputs/*` ship in the
  repo so the Space is self-contained.
- **CI / branches:** `ml`/`ai`/`analytics` → PR to `main`; lint/test before
  deploy; each team updates its `team_log.md`.
- **Cost:** Phase 1 is $0 (free HF Space + Ollama Cloud free tier). Paid only
  if LLM usage exceeds the free quota → then provider fallback or a paid tier.

## Open decisions for the team to confirm

1. Public HF Space URL vs local-only for assessment? (Rec: both.)
2. Confirm Ollama Cloud free-tier limits are sufficient for demo traffic;
   choose the fallback provider (OpenAI vs Anthropic).
3. Artifact in-repo vs HF Hub model repo (Rec: in-repo for now).
4. Single Space (Phase 1) vs split ML/AI services (Phase 2) — Rec: Phase 1.

## Risks

- Ollama Cloud free-tier throttling during a live demo → mitigated by
  caching + provider fallback.
- HF Space cold start (~30 s) on first hit after sleep → warm it before a
  demo.
- sklearn version drift breaking artifact load → pinned requirements + a
  smoke test in CI that loads the artifact.
  **Action item:** `requirements.txt` currently pins `scikit-learn==1.8.0`
  but the model was developed/validated on `1.6.1`. Before building the
  shipped artifact, align these (either retrain on 1.8.0 or pin 1.6.1) — a
  pickled sklearn model must load on the same major/minor.

---

## Appendix A — Get an Ollama Cloud API key

The AI narrative layer (Module 8 chat, summaries, reflections) uses
**Ollama Cloud** with model **`gpt-oss:120b-cloud`**. To obtain and wire a key:

1. Create / sign in to an Ollama account at <https://ollama.com>.
2. Open **Settings → Keys** (<https://ollama.com/settings/keys>) and
   **Create API key**. Copy it once (it is shown only at creation).
3. Confirm the cloud model is available to your account:
   `ollama run gpt-oss:120b-cloud` locally, or check the model list at
   <https://ollama.com>. (Cloud models have the `-cloud` suffix and run on
   Ollama's servers, not your machine.)
4. Review the current **free-tier limits** on the Ollama pricing page before a
   live demo — quotas/rate limits change and are not hard-coded here. If the
   free tier is too tight, either upgrade the Ollama plan or rely on the
   built-in fallback (set `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`).
5. Provide the key to the app via environment variables (never commit it):

   | Variable | Required | Default | Purpose |
   |---|---|---|---|
   | `OLLAMA_API_KEY` | yes | — | Ollama Cloud bearer token |
   | `OLLAMA_MODEL` | no | `gpt-oss:120b-cloud` | cloud model id |
   | `OLLAMA_HOST` | no | `https://ollama.com` | API host |
   | `OLLAMA_TIMEOUT` | no | `60` | per-request seconds |

   > **`OLLAMA_HOST` gotcha:** use `https://ollama.com` (no `/api` suffix).
   > The Ollama docs quote the base URL as `https://ollama.com/api`, but the
   > Python client appends `/api/...` itself — setting `.../api` here yields
   > `.../api/api/chat` (404). For local Ollama use `http://localhost:11434`.
   > Cloud models require `OLLAMA_API_KEY`; local does not.

   - **Local dev:** put them in a local `.env` (git-ignored;
     `python-dotenv` loads it). Never commit `.env`.
   - **HF Space:** add them under **Settings → Variables and secrets** as
     **Secrets** (see Appendix B).

When `OLLAMA_API_KEY` is set, `ai/services/llm_client.py` auto-selects the
`ollama` backend (primary). On any failure it degrades to a configured API
provider, then to the offline grounded extractor — the dashboard never
crashes and never fabricates figures.

---

## Appendix B — Deploy the app + ML models to Hugging Face Spaces

Phase-1 target: one **Gradio Space** running the dashboard with the ML models
loaded in-process. ~10–15 min, free.

### B.1 Prepare the repo
1. Ensure `requirements.txt` is pinned and consistent (see the sklearn
   action item above). Add `ollama` if not already present (it is).
2. Generate the ML artifacts: run `ml/ml_forecasting/forecasting.ipynb`
   top-to-bottom so `ml/ml_forecasting/outputs/{forecast.csv,
   per_sku_metrics.csv,test_summary.csv}` exist (and, once Part B lands,
   `model_artifacts.joblib`). These ship in the repo so the Space is
   self-contained.
3. Add a Space entrypoint at the repo root — Spaces runs `app.py` by default:

   ```python
   # app.py  (repo root)
   from dashboard.app.main import build_app

   demo = build_app()

   if __name__ == "__main__":
       demo.launch()
   ```
   (Gradio Spaces call `demo.launch()` automatically; keeping `__main__`
   lets it also run locally.)

### B.2 Create the Space
1. <https://huggingface.co/new-space> → **SDK: Gradio**, **Hardware: CPU
   basic (free)**, visibility public or private.
2. Push the repo to the Space remote (Spaces are git repos):

   ```bash
   git remote add space https://huggingface.co/spaces/<user>/<space-name>
   git push space main          # or your deploy branch -> main
   ```
   (Files >10 MB need Git LFS; the joblib artifact is expected <10 MB —
   verify after `train.py` and `git lfs track '*.joblib'` if needed.)

### B.3 Configure secrets (Space → Settings → Variables and secrets)
- `OLLAMA_API_KEY` = your Ollama Cloud key  (**Secret**)
- optional `OLLAMA_MODEL`, `OLLAMA_HOST`, `OLLAMA_TIMEOUT`  (Variables)
- optional fallback: `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`  (**Secret**)
- to force the LLM backend explicitly: `LLM_BACKEND=ollama`
- to skip heavy local-model deps on the free CPU Space, keep an API/cloud
  backend configured so `llm_client` never needs `transformers`/`torch`.

### B.4 Verify
- The Space builds, installs `requirements.txt`, and starts the Gradio app.
- Open it: Overview + **Demand Forecasting** tabs render
  (`forecast_loader` reads the committed `outputs/forecast.csv`).
- Trigger an AI summary/chat → UI footer should read
  `Ollama Cloud (gpt-oss:120b-cloud)`. If it instead shows the offline
  extractor, the key/secret is missing or the model id is wrong.
- Note free-Space **cold start (~30 s)** after inactivity — warm it before a
  demo.

### ML models on HF — clarification
The ML prediction models are **not** deployed as a separate HF endpoint. They
load in-process inside the same Space from the committed artifact (Layer 2 is
co-located with Layer 1 in Phase 1). HF **Inference Endpoints** (paid, GPU,
transformer-oriented) are *not* used and not appropriate for a few-MB sklearn
model. The only remote AI call is the Ollama Cloud LLM (Layer 3).
