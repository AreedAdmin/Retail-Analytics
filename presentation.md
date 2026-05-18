# AI‑Augmented Retail Analytics Dashboard — Technical Presentation

> Source-of-truth narrative for building `presentation.html`. Each `## Slide`
> is one slide; **Speaker notes** are the talk track; code/▮ blocks are
> on-slide visuals. All numbers are taken from the shipped model outputs.

---

## ⚑ BUILD DIRECTIVE — How `presentation.html` Must Look

**This deck is VISUAL, not wordy.** The text in this `.md` is the *script the
presenter speaks* — it must NOT be dumped onto slides. Each slide is **one
strong visual + ≤6 words of label**, and the presenter explains it aloud
using the Speaker notes.

**Hard rules for the HTML build:**
- **One hero visual per slide.** Diagram, chart, metric counter, animated
  flow, or icon system — never a paragraph. Max ~25 words of on-slide text;
  bullets become **labelled visual nodes**, not sentences.
- **Show, don't tell.** Architecture → animated layered diagram with flowing
  connectors. Metrics → big animated number counters + sparklines/gauges.
  Services → pipeline diagrams. AI layer → request‑flow animation
  (prompt → context → model → guardrail → answer).
- **Speaker notes** go in a hidden presenter pane (e.g. reveal.js notes /
  `aside class="notes"`), never on the slide face.
- **Modern Palantir aesthetic — match the live product exactly:**
  - Canvas `#0a0d13`, panels `#11151d`, hairline borders `#1d2430`
  - Text `#d7dde6`, muted `#79838f`, single accent `#4d9bff`
    (+ soft glow `rgba(77,155,255,.12)`)
  - Fonts: **Space Grotesk** (headlines), **Inter** (labels),
    **IBM Plex Mono** (numbers, micro‑labels, captions)
  - Sharp 4px radius, thin 1px lines, generous negative space, subtle grid /
    scanline texture, restrained motion (fade/slide ≤300ms, count‑up,
    connector draw‑on). Dark‑first. Feels like an internal intelligence tool.
- **Self‑contained `presentation.html`** (inline CSS/JS or CDN reveal.js),
  16:9, keyboard‑navigable, presenter notes view, works offline.
- Diagrams: inline **SVG** (crisp, themeable) — not screenshots. Charts:
  lightweight (Chart.js/ECharts CDN or hand‑built SVG) styled to the palette.

**Per‑slide hero visual (what to render instead of text):**

| Slide | Hero visual |
|---|---|
| 1 Title | Full‑bleed dark hero, geometric logo mark, animated accent underline |
| 2 Problem | Left "1 CSV" tile → 4 question chips, arrow to "decisions" |
| 2b Manager Qs | 4 assignment questions → module numbers (rubric map) |
| 3 Product | 11‑tile module grid, icons, accent active state |
| 3b Analytics | 3-column: Promo · Elasticity · Scenario (methods + modules) |
| Rubric | 5-row criterion → what we delivered (20/30/20/10/20) |
| 4 Stack | Layered chip stack (UI→Data→ML→GenAI→Deploy), logos/icons |
| 5 Architecture | **Animated layered SVG**, connectors draw left→right |
| 6 Contracts | Contract "schema card" ↔ loader ↔ module link diagram |
| 7 Forecast | Mini actual‑vs‑predicted line + CI band + 3 metric counters |
| 7b Forecast deep | Feature pipeline → HistGBR → intervals (method diagram) |
| 8 Promo Lift | Horizontal lift bar chart (top SKUs) + R²/MAE gauges |
| 8b Promo method | SCAN*PRO brief vs XGBoost counterfactual (lift formula) |
| 9 Elasticity | Demand curve + elasticity histogram split at β=−1 |
| 9b AI eval | Benefit ↔ limitation ledger + 5-tile "how we close every gap" row |
| 10 LLM client | Backend fallback ladder, animated "resolve" path |
| 11 Grounding | Prompt → CONTEXT JSON → answer flow, "[Data‑grounded]" stamp |
| 12 Guardrails | 3‑step pipeline icons (check → label → log), red‑flag node |
| 13 GenAI feats | 3 device‑style cards (chat / summarise / multi) |
| 13b AI summary | Chart click → context JSON → narrative flow (8b/8c) |
| 14 AI Analytics | TTFT/TPS gauges + category donut, live‑log ticker |
| 15 UI/UX | Side‑by‑side dark/light product mock, palette swatches |
| 16 Deploy | HF Space ⇄ Ollama Cloud topology, "free" badge |
| 17 Scale | Stateless app vs elastic LLM diagram, degradation ladder |
| 18 Quality | Repo tree + PR/CI flow ribbon |
| 19 Limitations | Honest "trade‑off" matrix, muted tone, caution accents |
| 20 Roadmap | Timeline arrow + one‑line closing statement |
| Appendices | Compact reference tables (only place dense text is allowed) |

---

## Slide 1 — Title

**AI‑Augmented Retail Analytics Dashboard**
A grounded GenAI decision console for retail pricing & promotions.

- 11 interactive views · 3 ML/analytics services · 1 provider‑agnostic AI layer
- Built on Gradio · deployed free on Hugging Face Spaces · Ollama Cloud LLM
- Group assignment — Imperial College, Retail & Marketing Analytics

**Speaker notes:** One sentence — *"We turned a raw weekly sales spreadsheet
into a deployed, AI‑assisted analytics product that a marketing manager can
actually ask questions to, with every answer grounded in our own models."*

---

## Slide 2 — The Problem & Scope

**Input:** one CSV — 44 SKUs × 100 weeks (4,400 rows) of weekly sales,
price, promotion flag, and product attributes.

**The question the business asks:**
- What drives demand? How sensitive is each SKU to price?
- Do promotions actually pay back, and for which SKUs?
- What happens to revenue if we change price?
- …and can a non‑technical manager just *ask* this in plain English?

**Scope delivered:** a full layered product — data → models → analytics →
dashboard → grounded GenAI → observability → deployment.

**Speaker notes:** Emphasise the gap we closed: raw data on one side, a
manager who needs decisions on the other. Everything between is what we built.

---

## Slide 2b — The Manager's Four Questions (Assignment Map)

**Each row = one grading question → where we answer it in the product:**

| Marketing manager asks… | Dashboard answer |
|-------------------------|------------------|
| *Expected demand next periods?* | **Module 6** — per-SKU forecast + 95% band + AI narrative |
| *Do promotions boost demand? For which SKUs?* | **Modules 3 & 7** — incremental sales, lift %, rankings |
| *Which SKUs are price-sensitive? What if ±10% price?* | **Modules 4 & 5** — elasticity β, scenarios, revenue waterfall, AI memo |
| *Can I ask in plain English?* | **Module 8** — grounded chat + chart summaries |

**Speaker notes:** This slide is for the marker — we did not build features in
isolation; every module maps to a question in the brief. Walk the four rows in
~30 seconds, then say the next slide shows the full product.

---

## Slide 3 — What We Delivered (the Product)

A single Gradio app, **11 tabs**, Palantir‑style command console:

| # | Module | What it does |
|---|--------|--------------|
| 1 | Overview | Headline KPIs, trends, promo score |
| 2 | Data Explorer | Filterable raw panel + per‑SKU stats |
| 3 | Promotion Effectiveness | Lift per SKU + AI summary |
| 4 | Price Elasticity | Own‑price elasticity, demand curves |
| 5 | Scenario Simulator | What‑if pricing, revenue waterfall |
| 6 | Demand Forecasting | Backtested forecast + intervals |
| 7 | Promotion Lift Model | Model diagnostics + AI narrative |
| 8 | AI Assistant | Grounded chat, click‑to‑summarise, multi‑select |
| — | **AI Analytics** | Prompt categorisation + AI perf (TTFT/TPS) |
| 9 | Critical Reflection | Guardrail failure log + limitations |
| 10 | Appendix & Export | Method notes + dataset downloads |

**Speaker notes:** Stress it's *one cohesive product*, not 11 scripts —
shared contracts, shared theme, shared AI layer.

---

## Slide 3b — Analytics Suite (Three Engines)

The dashboard analytics are **three distinct statistical engines**, not one
generic "ML block":

| Engine | Method | Question answered | Modules |
|--------|--------|-------------------|---------|
| **Promotion lift** | XGBoost counterfactual + matched control (SCAN*PRO‑style decomposition) | Incremental units & % lift per SKU | 3, 7 |
| **Price elasticity** | Log–log OLS per SKU (`log Q ~ log P + promo`) | Own‑price sensitivity β | 4 |
| **Scenario projection** | Constant‑elasticity what‑if (chains Module 4) | Revenue impact at ±5/10/20/30% | 5 |

Plus **demand forecasting** (HistGBR, separate ML track) in Module 6.

**Speaker notes:** Markers often conflate "analytics" — we separate *causal‑style
promo lift*, *descriptive elasticity*, and *forward scenario math*. Module 5
does not retrain; it projects from Module 4. Module 3 shows business rankings;
Module 7 shows model diagnostics (R², residuals, SHAP in notebook).

---

## Slide 3c — Grading Criteria → Our Evidence

| Criterion (pts) | How we demonstrate it |
|-----------------|-------------------------|
| **Clarity & Structure (20)** | 11-tab console, sidebar routing, consistent Palantir UI, this deck |
| **Content Insight (30)** | HistGBR forecast, promo lift per SKU, elasticity + 8 scenarios, exportable tables |
| **GenAI Integration (20)** | Context JSON, versioned prompts, labels, guardrails, 3 GenAI features |
| **Critical Reflection (10)** | Module 9, failure log, limitations stated in-product and here |
| **Use of Visuals (20)** | Plotly charts, CIs, heatmaps, waterfalls, drill-down SKU selectors |

**Speaker notes:** Optional slide — use if the audience includes the marker.
Otherwise fold into the close. Points to *evidence*, not claims.

---

## Slide 4 — Tech Stack

| Layer | Technology |
|-------|------------|
| UI / App | **Gradio 6.9**, custom Palantir CSS theme, Plotly |
| Data | pandas, numpy, pyarrow |
| ML / Stats | scikit‑learn (HistGBR), XGBoost, **statsmodels** (OLS) |
| GenAI | **Ollama Cloud** (`gpt-oss:120b-cloud`); pluggable Anthropic / OpenAI / local HF / offline |
| Config | python‑dotenv (`.env` → env), HF Space secrets |
| Deploy | **Hugging Face Spaces** (Gradio SDK, free CPU tier) |
| Quality | pytest, ruff, black; pinned `requirements.txt` |

Design rule: **the dashboard never trains a model.** Models are produced
offline in `ml/`; the app is a pure consumer of validated output files.

**Speaker notes:** The pin discipline matters — we caught and fixed
non‑existent version pins that would have broken the Space build.

---

## Slide 5 — Architecture (Layered)

```
        ┌─────────────────────────── data/data_raw.csv ───────────────────────────┐
        │                                                                          │
   ┌────▼─────┐   OFFLINE (ml/)                ┌────────────────────────────────┐  │
   │ Forecast │  HistGBR  → forecast.csv       │  Contracts (schemas.py)        │  │
   │ Promo    │  XGBoost  → promotion_output   │  ForecastOutput / Promotion    │  │
   │ Elastic. │  OLS      → elasticity_output  │  Elasticity / Scenario / AICtx │  │
   └────┬─────┘                                └────────────────────────────────┘  │
        │  CSV / JSON contracts                                                     │
   ┌────▼───────────────── dashboard/analytics/common/*_loader.py ───────────────┐ │
   │  contract‑validated, cached loaders (Forecast / Promotion / Elasticity / Data)│ │
   └────┬──────────────────────────────────────────────────────────────────────┘ │
        │                                                                          │
   ┌────▼──── dashboard/modules/*  (11 Gradio tabs) ──────────┐   ┌───────────────┐│
   │  charts + KPIs + tables   ── click‑to‑summarise / chat ──┼──▶│  AI LAYER     ││
   └──────────────────────────────────────────────────────────┘   │ ai/services/ ││
                                                                    │ context →   ││
                                                                    │ LLMClient → ││
                                                                    │ guardrail → ││
                                                                    │ telemetry   ││
                                                                    └──────┬──────┘│
                                                                           ▼       │
                                                            Ollama Cloud (stream)  │
```

**Speaker notes:** Walk left→right: data is fixed input; models run offline;
contracts decouple ML from UI; the AI layer is a sidecar every module can call.

---

## Slide 6 — Data Foundation & Contracts

- **`DataLoader`** normalises the raw CSV to a snake_case schema
  (`week→period`, `sku→sku_id`, `weekly_sales→demand_units`), cached singleton.
- **`schemas.py`** defines dataclass *contracts*: `ForecastOutput`,
  `PromotionOutput`, `ElasticityOutput`, `ScenarioOutput`, `AIContextPayload`.
- Every model writes a CSV/JSON that **matches a contract**; every loader
  **validates** required columns on load and fails loudly if a notebook
  wasn't run.

**Why it matters:** ML, analytics, UI and AI teams integrate through frozen
data contracts — no hidden coupling, parallel workstreams, safe refactors.

**Speaker notes:** This is the architectural backbone — call out that the
loaders raise a clear "run the notebook" error rather than silently breaking.

---

## Slide 6b — Architecture: The Layered Cake

*(Placed before the per-service deep-dives — the one-glance mental model.)*

```
 ╔══ DEPLOYED · HUGGING FACE SPACES (free CPU) ══════════╗  ╔═ DEPLOYED ═══╗
 ║ ┌────────────────────────────────────────────────────┐ ║  ║ OLLAMA CLOUD ║
 ║ │  CLIENT · Presentation                              │ ║  ╟──────────────╢
 ║ │  Gradio app · 11 tabs · charts · KPIs               │ ║  ║  AI LAYER    ║
 ║ ├────────────────────────────────────────────────────┤ ║  ║  (sidecar)   ║
 ║ │  SERVICES · ML & Analytics                          │◀───║ ai/services  ║
 ║ │  ┌────────────┐ ┌────────────┐ ┌─────────────────┐  │ ║  ║ context →    ║
 ║ │  │ Demand     │ │ Promotion  │ │ Price Elasticity │  │ ║  ║ LLMClient →  ║
 ║ │  │ Forecasting│ │ Lift       │ │ + Scenario       │  │ ║  ║ guardrail →  ║
 ║ │  │ HistGBR    │ │ XGBoost    │ │ OLS              │  │ ║  ║ telemetry →  ║
 ║ │  └────────────┘ └────────────┘ └─────────────────┘  │ ║  ║ gpt‑oss:120b ║
 ║ ├────────────────────────────────────────────────────┤ ║  ╚══════════════╝
 ║ │  DATA · Foundation                                  │ ║
 ║ │  data_raw.csv · schemas.py · cached loaders         │ ║
 ║ └────────────────────────────────────────────────────┘ ║
 ╚════════════════════════════════════════════════════════╝
        each layer ⇄ the one below via frozen contracts
```

**One hero visual:** a 3-tier cake — **Client** on top, **Services** in the
middle, **Data** at the base — each tier depending only on the tier below
through frozen contracts. The whole stack sits inside one **deployment box:
Hugging Face Spaces** (free CPU, models in-process). The **AI layer** is a
separate deployment box — a sidecar on **Ollama Cloud** — callable from
every tier.

**Speaker notes:** Orientation slide before the service deep-dives. Two
deployment boundaries are the headline: (1) Client/Services/Data ship
together on a free Hugging Face Space with the ML/analytics models running
in-process — no separate model server; (2) the AI layer is a remote sidecar
on Ollama Cloud (gpt-oss:120b), called by any layer. Inside the HF box,
top-down: client consumes, services are produced offline and integrate via
contracts, data is the fixed foundation. The next slides go one service deep.

---

## Slide 7 — Service 1: Demand Forecasting (ML)

**Goal:** weekly demand per SKU with uncertainty.

- Model: **HistGradientBoostingRegressor** on `log1p(weekly_sales)`.
- Features: lags, rolling mean/std, calendar/seasonality, promo, price —
  all *past‑only* (no leakage).
- Split: chronological panel — 13‑week validation, 13‑week test.
- 95% intervals from residual quantiles.

**Backtest (held‑out test, `test_summary.csv`):**
MAE **58.7** · RMSE 312.9 · MAPE 61.4% · 95%‑interval coverage **93.5%** · n=572

- Output → `ml/ml_forecasting/outputs/{forecast,per_sku_metrics,test_summary}.csv`
- Consumed by `ForecastLoader` → Module 6 (per‑SKU actual vs predicted + band).

**Speaker notes:** Honest framing — it beats the naive baseline materially
and the intervals are well‑calibrated; it is a *backtest*, not a live forecast.

---

## Slide 7b — Forecasting Methodology (In Depth)

**Problem:** predict weekly `demand_units` per SKU with uncertainty.

**Pipeline (all past‑only — no leakage):**
1. **Features:** lags 1–4w, rolling mean/std, promo history, calendar
   (week-of-year, quarter), price shape (log price, vs-SKU mean, discount flag).
2. **Candidates:** Naive, Ridge, **HistGradientBoostingRegressor** (+ CV‑tuned),
   per-SKU ARIMA — selected on validation MAE.
3. **Target:** `log1p(weekly_sales)` — stabilises variance across SKUs.
4. **Split:** chronological — 13‑week validation, 13‑week test (panel).
5. **Intervals:** residual quantiles in log space → 95% band in `forecast.csv`.

**Why HistGBR (not a neural net):** fits the **8 GB RAM** rule; strong on tabular
panel data; faster iteration than deep learning for 44 SKUs × 100 weeks.

**Speaker notes:** The assignment asks for regression *or* neural nets — we chose
HistGBR as the production model after benchmarking in the notebook. Be explicit:
delivered file is a **backtest** on held-out weeks; true forward forecast would
need assumed future price/promo paths (stated in Module 6 / README).

---

## Slide 8 — Service 2: Promotion Lift (ML)

**Goal:** incremental sales & % lift attributable to a promotion.

- Model: **XGBoost** (log1p target), counterfactual + matched‑control ensemble.
- Validation: 5‑fold **time‑series** CV.
- 43 SKUs with promotions · 1,502 promo SKU‑weeks · median lift **≈21%**.

**Out‑of‑sample:** MAE 65.3 · RMSE 227.5 · sMAPE 52.1% · R² 0.215

- Outputs → `promotion_output.csv`, `sku_lift_summary.csv`,
  `ai_context_module7.json` (pre‑built AI context).
- Consumed by `PromotionLoader` → Modules 3 & 7 (rankings, CIs, AI narrative).

**Speaker notes:** We *show* the modest R² in‑product and the AI is instructed
to state it — reliability is communicated, not hidden. Strong responders are
rank‑trustworthy even where absolute error is high.

---

## Slide 8b — Promotion Methodology: SCAN*PRO & Our Alternative

**Assignment asks for SCAN*PRO** — a marketing-mix model that decomposes sales into
base, trend, seasonality, and **promotion increment** per SKU.

**Our justified alternative (documented in notebook):**
```
incremental_sales = actual_sales − counterfactual_baseline
lift_pct          = incremental / counterfactual × 100
```

| Step | What we do |
|------|------------|
| 1 | **XGBoost** predicts demand with `feat_main_page` *excluded* → ML counterfactual (no-promo baseline) |
| 2 | **Matched control** — average sales in ±8 non-promo weeks around each promo week |
| 3 | **Ensemble** — 60% ML + 40% matched control when both exist |
| 4 | **Uncertainty** — 90% bootstrap CIs on SKU‑level lift summaries |
| 5 | **Validation** — 5‑fold TimeSeriesSplit (no future→past leakage) |

**Relation to SCAN*PRO:** same *intent* — isolate incremental demand from
promotion — but we use ML counterfactuals where SCAN*PRO uses multiplicative
decomposition. Trade-off: more flexible for sparse promos; weaker causal claim.

**Speaker notes:** This is the "Content Insight" depth slide for promotions.
Name SCAN*PRO, explain why XGBoost counterfactual is defensible (course allows
"alternative approach"), and show the lift formula on screen. Mention SHAP in
the notebook for feature attribution (price, lags, seasonality drive baseline).

---

## Slide 9 — Service 3: Price Elasticity + Scenario (Analytics)

**Price Elasticity (Module 4)** — `ml/pricing/price_elasticity_model.py`
- Per‑SKU **log–log OLS**: `log(demand) = α + β·log(price) + γ·promo`.
- β = own‑price elasticity; 95% CI from regression SEs.
- Result: **44/44 SKUs fitted**, median β **≈ −1.44**, 29 elastic /
  14 inelastic / 2 low‑evidence.

**Scenario Simulator (Module 5)** — no new model, pure projection:
```
demand%  ≈ β · price%
revenue% = (1+price%)·(1+demand%) − 1
```
- Combines elasticity + mean baseline → revenue **waterfall**
  (baseline → price effect → volume effect → projected) + AI memo.

**Speaker notes:** Module 5 is the payoff of Module 4 — chained services,
not a new model. Caveats (endogeneity, observational) stated in‑product.

---

## Slide 9b — AI Integration: Critical Evaluation

*(Placed deliberately **before** the AI‑layer deep‑dives — it states the
honest case for and against a GenAI layer, then the next three slides show
how each shortcoming is mitigated.)*

**Benefits — why we integrated GenAI:**
- **Plain‑English access** — a non‑technical manager queries the models
  directly instead of reading charts and tables.
- **Instant synthesis** — auto‑narratives across forecast, lift and
  elasticity in one memo.
- **Decision‑speed** — every chart explained on demand, in its own context.
- **One layer, many uses** — chat, click‑to‑summarise, executive briefing
  all share the same path.

**Limitations — what LLM integration gets wrong:**
- **Hallucination** — fabricated figures and unsupported claims.
- **No ground truth** — the base model does not know our dataset.
- **Off‑purpose / jailbreak** — prompt‑override; the assistant used for
  anything but its job.
- **Cost & throughput** — API bills; a request queue under concurrent demand.

**How we close every gap (the next slides):**
1. **RAG architecture** — grounds every answer in our own model outputs and
   gives the LLM relevant context to pull from → fewer hallucinations.
2. **System prompts** — enforced discipline (cite only context, declare
   uncertainty) → fewer hallucinations.
3. **Guardrails** — secure: no prompt‑override, usable *only* for its
   purpose, not as a free general‑purpose LLM.
4. **Open‑source LLM** (`gpt-oss:120b` via Ollama Cloud) — no expensive
   end‑of‑month bill, no cashflow stress, no extra cost for this intelligence.
5. **Fast TTFT (~1.7 s) · ~215 TPS** — snappy responses so concurrent users
   are not stuck in a request queue.

**Speaker notes:** The framing slide that wins credibility — we *name* the
risks of bolting an LLM onto an analytics product before we show the
architecture. Benefits are real: natural‑language access turns our models
into something a manager can actually use. But LLMs hallucinate, don't know
our data, can be pushed off‑purpose or jailbroken, and carry cost/throughput
risk. The bottom row is the promise: we did *not* just add a chatbot — every
gap is deliberately closed. Cautionary example for the guardrail point: the
Chipotle customer‑service bot that users jailbroke into writing a
reverse‑linked‑list — an assistant with no guardrail becomes a free
general‑purpose LLM running on the company's bill and brand. Make it explicit:
*"watch how each of these five mitigations closes a specific risk"* — this
sets up the LLM‑client, grounding and guardrail slides as answers, not
features.

---

## Slide 10 — The AI Layer: Provider‑Agnostic Client

`ai/services/llm_client.py` — one client, runtime‑resolved backend:

```
LLM_BACKEND=auto →
  1. OLLAMA_API_KEY  → Ollama Cloud  (primary, free, gpt-oss:120b-cloud)
  2. ANTHROPIC_API_KEY → Claude
  3. OPENAI_API_KEY   → OpenAI
  4. transformers     → local open model (CPU / ZeroGPU)
  5. else             → offline grounded extractor (stub)
```

- `.env` auto‑loaded (dotenv) before resolution; Space secrets override.
- `generate()` never raises — failures **degrade down the chain** to the
  offline stub, which echoes only supplied numbers (cannot hallucinate).
- Ollama call is **streamed** so we can measure latency precisely.

**Speaker notes:** This is the scalability/portability story — same code runs
free in a Space or fast on a paid key, with a guaranteed safe fallback.

---

## Slide 11 — The AI Layer: Grounding & System Prompt

Every answer is built from an **`AIContextPayload`** (`context_builder.py`):
a compact JSON snapshot of *explicit numbers* from the model outputs
(overview KPIs, promo lift, forecast accuracy, elasticity).

System prompt (`ai/prompts/chat_system.txt`) enforces:
- Cite **only** figures present in the CONTEXT block.
- Say *"I don't have data on this"* when context is insufficient.
- End every reply with `[Data-grounded]` or `[General inference]`.

Prompts are **files**, never inline — versioned & auditable
(`chat_system`, `click_to_summarise`, `multi_select_summary`,
`module7_lift_narrative`).

**Speaker notes:** Grounding is the anti‑hallucination strategy #1 — the model
is given the numbers and told to use nothing else.

---

## Slide 12 — The AI Layer: Guardrails

`ai/services/guardrail.py` — post‑processes **every** response:

1. **Numeric grounding check** — each number in the reply is matched
   (with rounding tolerance) against the context; unmatched → flagged.
2. **Label enforcement** — `[Data-grounded]` / `[General inference]` is
   *derived from the check*, not trusted from the model.
3. **Failure logging** — flagged outputs appended to `failure_log.jsonl`,
   surfaced live in Module 9 (Critical Reflection).

**Speaker notes:** Defence in depth — grounding *prevents*, guardrail
*verifies and labels*, Module 9 *evidences* it for the marker.

---

## Slide 13 — The AI Layer: 3 GenAI Features

Module 8 — all grounded, all guardrailed:

- **8a Chat** — persistent Q&A; scope selector limits grounding to one
  module or "all"; prompt auto‑categorised.
- **8b Click‑to‑summarise** — one‑click narrative on Promotion, Elasticity,
  Forecasting, Scenario charts (`summarise_scope` / `summarise_payload`).
- **8c Multi‑select briefing** — combine modules into one executive memo.

`narrative_service.py` is the single orchestrator: prompt → context →
LLMClient → guardrail → telemetry.

**Speaker notes:** One code path powers chat, summaries and the Module‑7
narrative — consistency and one place to harden.

---

## Slide 13b — AI Chart Summary Feature (8b & 8c)

**8b — Click-to-summarise (per chart):**
```
User clicks "Summarise" on a chart
  → chart metrics packaged as AIContextPayload (numbers only)
  → click_to_summarise.txt prompt
  → LLMClient → guardrail (numeric check + label)
  → ≤120-word narrative beside the chart
```

**8c — Multi-select briefing:**
```
User ticks modules (Forecast + Promo + Elasticity…)
  → combined CONTEXT JSON from all selected scopes
  → multi_select_summary.txt
  → one executive memo synthesising cross-module insights
```

**Grounding rule:** the LLM never receives raw CSV rows — only pre-computed
metrics from `ml/*/outputs/` and analytics loaders.

**Where it appears:** Promotion, Elasticity, Forecasting, Scenario, Module 7
(every chart with a summarise button shares `narrative_service.summarise_payload`).

**Speaker notes:** This is the feature the brief calls "AI Insight Narration."
Contrast with Module 8a chat (free-form Q&A). Emphasise we built *two* narration
modes — surgical (one chart) and strategic (multi-module). Both use the same
guardrail path as chat.

---

## Slide 14 — AI Observability (AI Analytics module)

`ai/services/telemetry.py` + the **AI Analytics** tab:

- **Prompt categorisation** — deterministic intent buckets (Pricing &
  Elasticity, Scenario, Promotion, Forecasting, Model Reliability,
  Overview, Other).
- **Performance metrics** — measured by *streaming* the Ollama response:
  - **TTFT** ≈ 1.5–2 s (time to first token)
  - **TPS** ≈ 215 tokens/sec
  - end‑to‑end latency, token counts, success rate, backend.
- Every AI call logs one JSONL event → live dashboards by
  category / backend / source.

**Speaker notes:** We instrument our own AI like a production system —
this is the "how it scales / how we'd operate it" slide.

---

## Slide 15 — UI / UX

- **Palantir‑style** dark‑first theme: near‑black canvas, single steel‑blue
  accent, mono microtype, sharp 4px radius.
- **CSS token system** + light/dark toggle (persisted in `localStorage`);
  a *Gradio‑variable bridge* remaps Gradio's internal theme vars so all
  chrome stays readable.
- **Sidebar = real router**: JS maps each rail item to its tab; native tab
  bar hidden once wired; active state synced both ways.
- Reusable theme‑aware components (`components/ui.py`): KPI cards, panels,
  transparent Plotly layouts.

**Speaker notes:** Looks like an internal data product, not a class demo —
and the theming is systematic, not hardcoded.

---

## Slide 16 — Deployment

- **Entry point:** root `app.py` exposes module‑level `demo` for HF Spaces
  (Gradio SDK runs `app.py`); also runs locally `python -m dashboard.app.main`.
- **Hugging Face Spaces, free CPU tier** — no GPU, no usage caps.
- **LLM = Ollama Cloud** (`gpt-oss:120b-cloud`): heavy model, **zero local
  compute**, key set as a **Space secret** (`OLLAMA_API_KEY`).
- Secrets never committed (`.gitignore`: `.env`, runtime logs);
  `.env.example` documents required keys; `deploy.md` is the runbook.

**Speaker notes:** The deployment choice is deliberate — offload the 120B
model to Ollama Cloud so a free CPU Space stays light and reliable.

---

## Slide 17 — How It Scales & Stays Reliable

**App tier (Hugging Face Spaces — free CPU):**
- Stateless Gradio UI — reads CSV/JSON only; **no training at request time**
- Cold start: load 4,400 rows + ~3 MB of model outputs → seconds, not minutes
- Horizontal scale: duplicate Spaces instances behind a link (no session state)

**Model tier (offline `ml/` notebooks):**
- Retrain locally or in CI when data refreshes; ship new `outputs/` files
- 44 SKUs today → design supports hundreds via same contract (one row per SKU-week)

**LLM tier (Ollama Cloud / API):**
- Heavy model **offloaded** — app sends compact JSON context (~2–8 KB), not the dataset
- Concurrent users → cloud provider queues; app degrades to offline stub if down
- Swap `LLM_BACKEND` / API key without redeploying analytics

**Degradation ladder:** Ollama → Claude → OpenAI → local HF → **offline extractor**
( echoes only supplied numbers — cannot invent figures )

**Speaker notes:** Answer "what happens with more SKUs / more users?" in three
sentences: app stays cheap (precomputed files), ML retrains offline, LLM scales
externally. The bottleneck is never the Gradio layer.

---

## Slide 18 — Engineering Quality & Reproducibility

- Repo layout mirrors the architecture: `ml/`, `dashboard/analytics`,
  `dashboard/modules`, `ai/services`, `ai/prompts`, `docs/`.
- Pinned, **install‑verified** `requirements.txt` (fixed phantom versions).
- Every output regenerates from `ml/` notebooks/scripts.
- Reviewed via PRs (feature branch → PR), team logs, `deploy.md` runbook.

**Speaker notes:** Mention the bug discipline — we found and fixed the
double‑tab crash, the dark‑mode contrast, the dotenv/empty‑LLM issues.

---

## Slide 19 — Limitations & Critical Reflection

- Forecast & lift models: backtests on observational data — moderate lift R²
  (0.215); elasticity is descriptive, not causal (price endogeneity).
- Numeric guardrail catches fabricated *figures*, not flawed *reasoning*.
- Free open LLM < frontier APIs; offline stub is safe but extractive.
- Modules 4/5 use mean‑baseline projection (constant‑elasticity assumption).

All surfaced *in‑product* (Module 9) — limitations are disclosed, not hidden.

**Speaker notes:** This slide wins marks — we critique our own system and
the product itself tells the user where to be cautious.

---

## Slide 20 — What We Would Do Next

| Priority | Initiative | Why |
|----------|------------|-----|
| 1 | **True forward forecast** | Assume future price/promo paths; extend `forecast.csv` beyond backtest |
| 2 | **Full SCAN*PRO implementation** | Compare decomposition vs counterfactual; report side-by-side in Module 7 |
| 3 | **Causal inference** | DiD / IV for price and promo — move from descriptive to causal claims |
| 4 | **RAG over interaction log** | Learn from Module 9 failure cases to tighten prompts automatically |
| 5 | **Load testing** | Quantify concurrent-user behaviour on Ollama Cloud vs paid API |

**Closing line:** *We delivered a deployed, grounded, observable AI analytics
product — from one CSV to a manager‑ready decision console that answers every
question in the brief.*

**Speaker notes:** "What's next" shows intellectual honesty — we know the edges.
End with the four manager questions answered, GenAI critiqued, and a live demo link.

---

## Appendix A — Key File Map

| Concern | Path |
|---|---|
| App entry / theme / nav | `app.py`, `dashboard/app/main.py` |
| Contracts | `dashboard/analytics/common/schemas.py` |
| Loaders | `dashboard/analytics/common/{data,forecast,promotion,elasticity}_loader.py` |
| ML — forecast | `ml/ml_forecasting/forecasting.ipynb` → `outputs/` |
| ML — promo lift | `ml/promotions/promotion_lift_model.ipynb` |
| Analytics — elasticity | `ml/pricing/price_elasticity_model.py` |
| AI client / orchestrator | `ai/services/llm_client.py`, `narrative_service.py` |
| AI grounding / safety | `ai/services/context_builder.py`, `guardrail.py` |
| AI observability | `ai/services/telemetry.py`, `dashboard/modules/ai_analytics.py` |
| Prompts | `ai/prompts/*.txt` |
| Deploy | `app.py`, `deploy.md`, `.env.example` |

## Appendix B — Headline Metrics

| Service | Metric |
|---|---|
| Demand Forecasting | Test MAE 58.7 · MAPE 61.4% · 95% coverage 93.5% |
| Promotion Lift | OOS MAE 65.3 · R² 0.215 · median lift ≈21% (43 SKUs) |
| Price Elasticity | 44/44 fitted · median β ≈ −1.44 · 29 elastic |
| AI (Ollama Cloud) | TTFT ≈ 1.5–2 s · ≈215 TPS · grounded + labelled |
| Footprint | 44 SKUs × 100 wks · 11 views · free CPU Space |
