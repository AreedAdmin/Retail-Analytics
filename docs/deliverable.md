# Deliverable: AI-Augmented Retail Analytics Dashboard

## Overview

The final deliverable is a **multi-module, interactive web application** built in Python (Gradio) that serves as a fully integrated, AI-augmented analytics platform for a retail e-commerce marketing manager. It is not a static report — it is a living decision support tool that combines machine learning predictions, statistical analysis, interactive visualisations, and a generative AI layer into a single, navigable interface.

The application consumes data from the `data/` directory and presents all analytical outputs through a **persistent side navigation bar**, allowing users to move freely between modules without losing state.

---

## Application Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Side Navigation Bar (persistent across all modules)        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Overview                                                │
│  2. Data Explorer                                           │
│  ── Analytics ──────────────────────────────────────────   │
│  3.  └─ Promotion Effectiveness                             │
│  4.  └─ Price Elasticity                                    │
│  5.  └─ Scenario Simulator                                  │
│  ── ML ─────────────────────────────────────────────────   │
│  6.  └─ Demand Forecasting                                  │
│  7.  └─ Promotion Lift Model                                │
│  ── AI ─────────────────────────────────────────────────   │
│  8.  └─ Chat Interface                                      │
│  9. Critical Reflection                                     │
│  10. Appendix & Export                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Module Specifications

### Module 1 — Overview

**Owner:** Dashboard Lead  
**Purpose:** Entry point for any user opening the dashboard.

- High-level KPI summary cards: total SKUs, total demand periods, average price, number of promotions run.
- Short project description and instructions on how to navigate the dashboard.
- Summary of key findings from each analytical section (auto-populated from model outputs).
- Key assumptions made during the analysis clearly listed.

---

### Module 2 — Data Explorer

**Owner:** Dashboard Lead  
**Purpose:** Transparent data layer so any user can inspect the raw and processed inputs.

- Paginated preview of the raw dataset loaded from `data/`.
- Column-level descriptions and data types.
- Basic descriptive statistics per SKU (mean, std, min, max demand and price).
- Missing value and outlier summary.
- All preprocessing and cleaning steps documented inline.
- Filter controls: by SKU, date range, promotion flag.

---

### Module 3 — Analytics: Promotion Effectiveness

**Owner:** ML Pod B  
**Purpose:** Quantify how much feature promotions drive incremental sales per SKU.

- Use SCAN*PRO model or a statistically justified alternative.
- Visualisations:
  - Bar chart of incremental sales lift per SKU (with confidence intervals).
  - Heatmap of promotion response across SKUs and time periods.
  - Comparison of promoted vs. non-promoted demand distributions per SKU.
- Interactive SKU selector to drill into individual results.
- **Click-to-summarise:** clicking any chart triggers an AI pop-up that narrates the promotion result for that SKU — identifying whether the lift is significant and whether the promotion appears cost-effective.
- **Multi-select visualisation summary:** user can tick multiple charts and request a combined AI narrative across all selected SKUs.
- AI-generated commentary block at the bottom of the page interpreting the full set of results: strongest responders, negligible responders, strategic implications.

---

### Module 4 — Analytics: Price Elasticity

**Owner:** ML Pod B  
**Purpose:** Identify which SKUs are most and least price-sensitive.

- Estimate price elasticity of demand for each SKU using a log-log regression or equivalent model.
- Visualisations:
  - Elasticity coefficient bar chart ranked by sensitivity (most elastic to least).
  - Demand curve plots per SKU showing price vs. demand relationship.
  - Revenue impact chart: how total revenue changes as price shifts.
- Interactive SKU selector.
- **Click-to-summarise:** clicking any elasticity chart triggers an AI pop-up explaining what the elasticity value means in plain language for that SKU.
- **Multi-select summary:** user can select multiple SKU charts and ask for a combined AI interpretation.

---

### Module 5 — Analytics: Scenario Simulator

**Owner:** ML Pod B + Dashboard Lead  
**Purpose:** Enable what-if pricing decisions with projected demand and revenue outcomes.

- User selects a SKU (or all SKUs) and a price change scenario.
- Supported scenarios:
  - Price increases: +5%, +10%, +20%, +30%
  - Price decreases: −5%, −10%, −20%, −30%
- Visualisations:
  - Side-by-side demand and revenue bar charts: baseline vs. scenario.
  - Revenue waterfall chart showing impact of the selected change.
- For each scenario, an **AI-generated strategic recommendation memo** is produced, covering:
  - Projected demand and revenue implications.
  - Whether the price change is likely to be beneficial based on elasticity.
  - Caveats and limitations of the recommendation.
- Memo must clearly state when it is drawing from model outputs vs. making general inferences.
- User can export the memo as a text block for external use.

---

### Module 6 — ML: Demand Forecasting

**Owner:** ML Pod A  
**Purpose:** Predict future demand per SKU for the next N periods.

- Models implemented: regression baseline + at least one non-linear model (e.g., gradient boosted trees or a lightweight neural network ≤ 8 GB RAM).
- Per-SKU forecast display:
  - Time series chart of historical demand with forecast overlaid.
  - Confidence intervals (80% and 95%) where the model supports it.
  - Model performance metrics: MAE, RMSE, MAPE displayed clearly.
- SKU selector dropdown to navigate between individual forecasts.
- **AI-generated narrative below each forecast**, automatically interpreting:
  - Whether demand is trending up, down, or flat.
  - Whether uncertainty is unusually high.
  - Whether there are strong seasonal patterns.
  - Flags for SKUs at risk of demand decline.
- **Click-to-summarise** and **multi-select summary** supported.

---

### Module 7 — ML: Promotion Lift Model

**Owner:** ML Pod A + ML Pod B  
**Purpose:** Present the ML modelling behind promotional lift, separate from the analytics visualisation layer.

- Model architecture description and justification.
- Feature importance chart: which variables most influence promotion-driven demand.
- Residual plots and model diagnostics.
- Out-of-sample performance metrics.
- Exportable model output table (incremental sales per SKU per promotion period).
- AI narrative summarising model reliability and any notable failure patterns.

---

### Module 8 — AI: Chat Interface

**Owner:** AI Pod  
**Purpose:** Allow marketing managers to ask plain-English questions grounded in the dashboard's actual outputs.

#### 8a. Persistent Chat Panel

- Single-turn Q&A interface (not a full conversational agent).
- Input: free-text question from the user.
- The system packages relevant model outputs and statistics as structured context before calling the LLM API.
- Response: LLM-generated answer clearly labelled as:
  - `[Data-grounded]` — drawn directly from model outputs in the dashboard.
  - `[General inference]` — reasoning not directly traceable to a specific figure.
- System-level guardrails prevent fabrication of figures not present in the context package.
- Example queries the interface must handle:
  - "Which SKUs should I prioritise for promotion next quarter?"
  - "What happens to total revenue if I reduce prices by 10% across all SKUs?"
  - "Which products are most at risk of demand decline?"
  - "Is the promotion for SKU 4 generating enough incremental sales to justify the discount?"

#### 8b. Click-to-Summarise (Chart AI Pop-Up)

- Every chart across all modules has a clickable **"Summarise this chart"** action.
- On click, the chart's underlying data is packaged into context and sent to the LLM.
- A pop-up modal displays the AI-generated plain-language interpretation.
- Response is grounded in the specific data points of that chart only.

#### 8c. Multi-Select Visualisation Summary

- User can select multiple charts (across a module or across modules) using checkboxes.
- A **"Summarise selected"** button sends the combined context of all selected charts to the LLM.
- The AI response synthesises insights across all selected visualisations into a coherent narrative.
- This feature supports cross-module synthesis (e.g., forecasting + elasticity + promotion together).

---

### Module 9 — Critical Reflection

**Owner:** All teams contribute; Dashboard Lead compiles.  
**Purpose:** Demonstrate the team's critical evaluation of the AI components — required for the GenAI Integration and Critical Reflection grading criteria.

- Documented prompt engineering decisions: what context was supplied to the LLM and why.
- Output validation methodology: how AI responses were checked against actual data.
- Specific failure case log: real examples from the dashboard where AI produced poor, wrong, or hallucinated outputs, and what was done to address them.
- Discussion of benefits, limitations, and risks of AI-augmented dashboards for retail decision-making.
- Honest assessment of where AI added value vs. where it was unreliable in this specific tool.

---

### Module 10 — Appendix & Export

**Owner:** Dashboard Lead  
**Purpose:** Reproducibility, transparency, and export capabilities.

- Full method notes per analytical section.
- Model specifications: algorithms, hyperparameters, training/test splits.
- Data dictionary.
- Downloadable tables: forecast outputs, elasticity coefficients, lift estimates, scenario results.
- Downloadable charts as PNG/SVG.
- Link to GitHub repo and `requirements.txt`.

---

## Cross-Cutting Technical Requirements

| Requirement | Detail |
| --- | --- |
| Language | Python |
| Framework | Gradio |
| Naming | snake_case throughout — all files, variables, functions, columns |
| Dependencies | Pinned in root `requirements.txt` |
| Secrets | All API keys stored as GitHub Repository Secrets, never in files |
| Model memory | All models must run within 8 GB RAM |
| LLM API | Claude (Anthropic) or OpenAI — API calls only, no local LLMs |
| Branching | `ml`, `ai`, `analytics` branches; PRs to `main` only |
| Data source | `data/` directory (read-only; no raw file modification) |
| AI code | All AI-assisted code reviewed and commented `# AI-assisted: reviewed by [name]` |

---

## AI Integration Design Principles

The following must be deliberately implemented and demonstrable for the GenAI grading criteria:

1. **Context packaging** — before every LLM call, structured model outputs (not raw data) are assembled as context. The LLM never sees the raw dataset directly.
2. **Hallucination prevention** — the prompt instructs the LLM to only reference figures present in the supplied context, and to explicitly say "I don't have data on this" when the context is insufficient.
3. **Response labelling** — every AI response indicates whether it is `[Data-grounded]` or `[General inference]`.
4. **Prompt templates** — all prompts are version-controlled in the `ai/` folder as reusable templates, not hardcoded inline.
5. **Failure documentation** — the team actively logs cases where AI outputs were inaccurate, and these appear in Module 9.

---

## Acceptance Criteria (mapped to grading rubric)

| Criterion | Points | How it is met in this deliverable |
| --- | --- | --- |
| Clarity and Structure | 20 | Multi-module sidebar app, consistent layout, clear navigation, Overview module |
| Content Insight | 30 | Modules 3–7 covering forecasting, promotion effectiveness, price elasticity, scenario testing |
| GenAI Integration | 20 | Modules 8a/b/c, context packaging, guardrails, prompt templates, response labelling |
| Critical Reflection | 10 | Module 9 with failure cases, validation methodology, honest assessment |
| Use of Visuals | 20 | Interactive Plotly charts, confidence intervals, heatmaps, waterfall charts, drilldowns |
| **Total** | **100** | |
