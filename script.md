# Presentation Script & Speaker Allocation

Talk-track for the 26-slide deck (`presentation.html`), mapped to the grading
rubric so every point we make is "earning a mark". ~10 min presentation +
~5 min live demo.

> Source of the rubric: `docs/deliverable.md` → *Acceptance Criteria* and
> `docs/scope.md`. Module ownership: `docs/CLAUDE.md`.

---

## Project Overview — the elevator pitch (S1 delivers, ~45s)

> Read this once at the start so the whole room has the mental model before
> any detail. Memorise the bold lines.

**The objective in one sentence:**
> **"We took one raw weekly-sales spreadsheet and turned it into a deployed,
> AI-assisted decision tool a non-technical marketing manager can use to make
> pricing and promotion decisions — with every AI answer grounded in our own
> models, not made up."**

**The problem:** a marketing manager has one CSV — 44 SKUs × 100 weeks of
sales, price, and promotion flags — and four real questions they can't answer
from raw rows:
1. How much will each product sell next? → **Demand Forecasting**
2. Do promotions actually generate extra sales, and for which SKUs? → **Promotion Lift**
3. Which products are price-sensitive, and what happens to revenue if I change price? → **Price Elasticity + Scenario**
4. Can I just *ask* this in plain English? → **the grounded AI layer**

**What we built — the progression to anchor every section on:**
> **"Raw data → three models that each answer one manager question → a
> dashboard that shows them → an AI layer that explains them in plain English
> → deployed live."**

**The three ML/analytics services (each = one independent engine, trained
offline, the dashboard only displays the results):**

| Service | Goal (manager question) | Method | Headline result | Honest caveat |
|---|---|---|---|---|
| **Demand Forecasting** | How much will each SKU sell? | HistGBR on log1p sales, past-only features; benchmarked vs Naive/Ridge/ARIMA | Test MAE **58.7**, 95% interval coverage **93.5%** (≈ target — band is trustworthy) | a *backtest*, not a live forward forecast |
| **Promotion Lift** | Do promos pay off, for which SKUs? | XGBoost counterfactual (`lift = actual − counterfactual`) + matched control, bootstrap CIs | median lift ≈ **21%** across 43 SKUs; top SKU ≈ **92%** | modest R² (**0.215**) — shown in-product; *rankings* still reliable |
| **Price Elasticity + Scenario** | Which SKUs are price-sensitive? What if price ±10%? | Per-SKU log–log OLS (β = elasticity); Scenario *projects* from β (no new model) | **44/44** fitted, median β ≈ **−1.44**, 29 elastic; e.g. +10% price on SKU 1 → demand −12.9%, revenue 533→510 | descriptive not causal (price endogeneity); constant-elasticity assumption |

**The differentiator — say this, it earns the Insight + Reflection marks:**
> **"Our models don't just predict — they're built to be honest. Every one
> ships its own uncertainty and limitations, and the AI layer is forced to
> repeat those caveats rather than gloss over them. Where the data is genuinely
> noisy we surface it instead of hiding it, and the rankings and decisions are
> still actionable."**

**If asked "what was the single main objective?":**
> **"To bridge the gap between a raw sales file and a manager's decision —
> using ML to answer the demand, promotion and pricing questions, and a
> grounded GenAI layer so a non-technical user can safely interrogate those
> answers."**

---

## The grading rubric (100 pts) — what each slide must feed

| Criterion | Pts | Where we earn it in the deck |
|---|---|---|
| **Clarity & Structure** | 20 | Slides 1–7, 25 (problem → product → architecture → guided tour) |
| **Content Insight** | 30 | Slides 8–14 (forecasting, promo lift, elasticity, scenario + results) |
| **GenAI Integration** | 20 | Slides 15, 17–21 (features, client, grounding, guardrails, observability) |
| **Critical Reflection** | 10 | Slides 16, 19, 24, 26 (honest eval, limitations, in-product disclosure) |
| **Use of Visuals** | 20 | Slides 9–14, 21, 25 (charts, CI bands, waterfall, live screenshots) |

**Rule for every speaker:** say the ONE bold sentence per slide, then 1–2
supporting points, then move on. Do not read the slide. The slide is the
visual; you are the narration.

---

## Speaker allocation (5 speakers — rename to real names)

| Speaker | Role / team (per CLAUDE.md) | Slides | ~Time |
|---|---|---|---|
| **S1 — Intro & Architecture** | Dashboard / Integration Lead | 1–7 | ~2:15 |
| **S2 — Forecasting (ML Pod A)** | ML Pod A | 8–10 | ~1:15 |
| **S3 — Promo & Pricing (ML Pod B / Analytics)** | ML Pod B + Analytics | 11–14 | ~1:45 |
| **S4 — AI Layer (AI Pod)** | AI Pod | 15–21 | ~3:00 |
| **S5 — Deploy, Reflection & Demo** | Dashboard Lead / All | 22–26 + drives demo | ~1:45 + 5:00 |

> If 4 speakers: merge S2 into S1 (slides 1–10). If 3: S4 also takes 22–26.

---

## Slide-by-slide script

### S1 — Intro & Architecture (Clarity & Structure, 20 pts)

**Slide 1 — Title**
- **"We turned one raw weekly-sales spreadsheet into a deployed, AI-assisted decision tool a marketing manager can actually ask questions to."**
- 11 views · 3 ML/analytics services · 1 AI layer · live on Hugging Face.
- *Criteria: Clarity (sets the frame).* ~10s.

**Slide 2 — The Problem & Scope**
- **"One CSV on one side, a manager who needs decisions on the other — everything between is what we built."**
- 44 SKUs × 100 weeks; four business questions (demand, promo payback, price change, plain-English ask).
- *Criteria: Clarity + Content framing.* ~25s.

**Slide 3 — The Manager's Four Questions (Assignment Map)**
- **"Every grading question maps to a specific module — we built to the brief, not in isolation."**
- Walk the 4 rows fast: forecast→M6, promo→M3/7, elasticity/scenario→M4/5, chat→M8.
- *Criteria: Clarity & Structure (explicit rubric alignment — say this out loud).* ~25s.

**Slide 4 — What We Delivered (the Product)**
- **"One cohesive product — 11 tabs, shared contracts, shared theme, shared AI layer — not 11 scripts."**
- *Criteria: Clarity & Structure.* ~15s.

**Slide 5 — Grading Criteria → Our Evidence**
- **"Here is the rubric, and here is exactly where each criterion is evidenced."** Name the 20/30/20/10/20 split.
- This is the slide that tells the marker we read the rubric. Do not skip.
- *Criteria: Clarity & Structure (meta — directly addresses grading).* ~20s.

**Slide 6 — Architecture: The Layered Cake**
- **"The simple mental model: Client on top, Services in the middle, Data at the base — each tier talks only to the one below through frozen contracts."** AI is a remote sidecar on Ollama Cloud.
- *Criteria: Clarity & Structure.* ~20s.

**Slide 7 — Architecture (detailed)**
- **"Same model, zoomed in: data is fixed input, models run offline, contracts decouple ML from UI, the AI layer is callable from every module."**
- *Criteria: Clarity & Structure.* ~20s.

---

### S2 — Forecasting / ML Pod A (Content Insight 30 + Use of Visuals 20)

**Slide 8 — Analytics Suite (Three Engines)**
- **"Three distinct statistical engines, not one generic ML block: promo lift (XGBoost), elasticity (OLS), scenario (projection) — plus forecasting on a separate ML track."**
- *Criteria: Content Insight (shows methodological breadth).* ~25s.

**Slide 9 — Demand Forecasting (HistGBR + methodology strip)**
- **"HistGradientBoostingRegressor on log1p sales, all past-only features — Test MAE 58.7, 95% interval coverage 93.5%."**
- Bottom strip = method: benchmarked Naive/Ridge/HistGBR/ARIMA, selected HistGBR; fits the 8 GB RAM rule, no neural net needed, no leakage. It is a backtest, not a live forecast.
- *Criteria: Content Insight + Use of Visuals (actual-vs-forecast + CI band).* ~30s.

**Slide 10 — Forecast Results (held-out test)**
- **"Coverage 93.5% ≈ the 95% target is the headline — the intervals are calibrated."**
- Be honest: SKU 30's 688% MAPE is a near-zero-baseline artefact, disclosed in Module 9.
- *Criteria: Content Insight + Use of Visuals + a Critical-Reflection touch.* ~20s.

---

### S3 — Promo & Pricing / ML Pod B + Analytics (Content Insight 30 + Visuals 20)

**Slide 11 — Promotion Lift (XGBoost)**
- **"Incremental sales via an XGBoost counterfactual + matched-control ensemble; median lift ≈21% across 43 SKUs."**
- We SHOW the modest R² (0.215) in-product and the AI is instructed to state it — reliability communicated, not hidden. Strong responders are rank-trustworthy.
- *Criteria: Content Insight + Use of Visuals (lift bar chart).* ~30s.

**Slide 12 — SCAN*PRO Intent, XGBoost Counterfactual**
- **"The brief asks for SCAN*PRO; the course allows a justified alternative — ours: incremental = actual − counterfactual, with bootstrap CIs."**
- More flexible for sparse promos; weaker causal claim — stated in Module 9. SHAP in the notebook for attribution.
- *Criteria: Content Insight (method justification — explicitly name SCAN*PRO).* ~25s.

**Slide 13 — Price Elasticity + Scenario**
- **"Per-SKU log–log OLS, promo-controlled — 44/44 fitted, median β ≈ −1.44, 29 elastic SKUs."**
- Scenario Simulator does not retrain — it projects from β: `demand% ≈ β·price%`, into a revenue waterfall.
- *Criteria: Content Insight + Use of Visuals (demand curve + scenario).* ~25s.

**Slide 14 — Promo + Pricing Results**
- **"This is exactly what the brief asks: +10% price on SKU 1 cuts demand 12.9% and weekly revenue 533→510."**
- Frame weak R² (<0.05 on 2 SKUs) as transparency, not failure — flagged in-product.
- *Criteria: Content Insight + Use of Visuals + Critical Reflection.* ~30s.

---

### S4 — AI Layer / AI Pod (GenAI Integration 20 + Critical Reflection 10)

**Slide 15 — Three Grounded GenAI Features**
- **"Module 8 delivers the brief's three required GenAI features: 8a chat, 8b click-to-summarise, 8c multi-select briefing — through one orchestrator."**
- *Criteria: GenAI Integration (maps directly to deliverable 8a/b/c).* ~25s.

**Slide 16 — AI Integration: Critical Evaluation**
- **"We did not just bolt on a chatbot — here are the real risks of LLMs in a dashboard, and the five things we did to close each one."**
- Benefits (plain-English access, synthesis) vs limitations (hallucination, no ground truth, jailbreak, cost/throughput). The Chipotle bot jailbroken into writing a reverse-linked-list = a guardrail-less assistant becomes a free general-purpose LLM on the company's bill.
- *Criteria: Critical Reflection (this is THE reflection slide) + GenAI Integration.* ~35s.

**Slide 17 — One Client, Any Backend**
- **"Provider-agnostic client: Ollama Cloud → Anthropic → OpenAI → local → offline stub; `generate()` never raises."**
- Open-source LLM = zero marginal cost + data sovereignty retained. Stub echoes only supplied numbers → cannot hallucinate.
- *Criteria: GenAI Integration (robustness).* ~25s.

**Slide 18 — Grounded in Our Own Numbers (Anti-Hallucination #1)**
- **"RAG-style grounding: the LLM never sees raw CSV — only a CONTEXT JSON of explicit figures from model outputs; prompts are versioned files, not inline."**
- Every reply ends `[Data-grounded]` or `[General inference]`.
- *Criteria: GenAI Integration (context packaging — a named grading principle).* ~25s.

**Slide 19 — Every Answer Is Verified (Anti-Hallucination #2)**
- **"Guardrail post-processes every response: numeric check → label enforced (not trusted from model) → failures logged to Module 9."**
- Defence in depth: grounding prevents, guardrail verifies, Module 9 evidences.
- *Criteria: GenAI Integration + Critical Reflection (failure logging).* ~25s.

**Slide 20 — We Instrument Our Own AI (Observability)**
- **"Production-grade telemetry: TTFT ≈1.7s, ≈215 TPS, 100% non-fallback, every call categorised — measured by streaming."**
- *Criteria: GenAI Integration (operational maturity).* ~20s.

**Slide 21 — Click-to-Summarise & Multi-Briefing**
- **"The brief's 'AI insight narration' — surgical per-chart (8b) and strategic cross-module (8c); same guardrail path, LLM never sees raw CSV."**
- *Criteria: GenAI Integration + Use of Visuals (the output mock).* ~25s.

---

### S5 — Deploy, Reflection & Close (Critical Reflection 10 + Clarity)

**Slide 22 — Deployment**
- **"Deliberate split: free CPU Hugging Face Space for the app, the heavy 120B model offloaded to Ollama Cloud — secrets never committed."**
- *Criteria: Clarity / engineering credibility.* ~20s.

**Slide 23 — Scale & Reliability**
- **"Three tiers scale independently: stateless app, offline-retrained models, cloud LLM with an offline stub that never hard-fails."**
- *Criteria: Critical Reflection (operational honesty).* ~20s.

**Slide 24 — Honest About the Edges (Critical Reflection)**
- **"We critique our own system: backtests not causal, elasticity has price endogeneity, guardrail catches fake figures not flawed reasoning, free LLM < frontier — all surfaced in-product in Module 9."**
- *Criteria: Critical Reflection (the 10-pt criterion — land this clearly).* ~25s.

**Slide 25 — Dashboard Walkthrough (bridge to demo)**
- **"30-second visual grounding before the live demo — note the consistent layout: KPIs top, chart middle, AI action right, on every module."**
- *Criteria: Use of Visuals + Clarity. Hands off to the live demo.* ~20s.

**Slide 26 — Roadmap & Close**
- **"We answered all four manager questions, critiqued GenAI honestly, and shipped a live, grounded, deployed product."** Give the HF Space URL if hosted, then invite questions.
- *Criteria: Critical Reflection (roadmap) + closes the loop.* ~15s.

---

## Demo (~5 min) — driven by S5 (or the Dashboard Lead)

| Step | Show | Criterion reinforced |
|---|---|---|
| 1 | **Analytics & findings** — open Module 6 (forecast + CI band), Module 4 (elasticity ranking), Module 5 (run a +10% price scenario → revenue waterfall) | Content Insight, Use of Visuals |
| 2 | **AI summary per page** — click "Summarise this chart" on the forecast and on an elasticity chart; point at the `[Data-grounded]` label | GenAI Integration |
| 3 | **AI chat module** — ask "Which SKUs should I prioritise for promotion next quarter?" then a question with no data ("what's the weather effect?") to show the guardrail saying *no data* | GenAI Integration, Critical Reflection |
| 4 | (If time) Module 9 — show a real logged failure case | Critical Reflection |

**Demo rule:** narrate what criterion each click demonstrates — the marker
should never have to guess.

---

## Criteria coverage check (sanity)

- **Clarity & Structure (20):** Slides 1–7, 25 ✔ + the explicit rubric slide 5.
- **Content Insight (30):** Slides 8–14 cover all of forecasting, promo
  effectiveness, elasticity, scenario ✔.
- **GenAI Integration (20):** Slides 15, 17–21 cover features, context
  packaging, guardrails, labelling, observability ✔ (matches the 5 named
  principles in `docs/deliverable.md`).
- **Critical Reflection (10):** Slides 16, 19, 24, 26 + Module 9 in demo ✔.
- **Use of Visuals (20):** Slides 9–14, 21, 25 — live charts, CI bands,
  waterfall, screenshots ✔.

No criterion is unaddressed. The two weakest-covered are **Critical
Reflection** (only 10 pts but make slide 24 + the demo Module-9 moment
count) and **Use of Visuals** (lean on the live demo, not just slide charts).
