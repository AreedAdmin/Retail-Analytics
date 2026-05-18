# Dashboard Analytics Team - Implementation Plan

## Team Ownership & Responsibilities

### Modules Owned
1. **Module 1: Overview** - Entry point, KPI summary cards
2. **Module 2: Data Explorer** - Raw data inspection, preprocessing documentation
3. **Module 5: Scenario Simulator** - What-if pricing analysis (shared with ML)
4. **Module 10: Appendix & Export** - Methods, metrics, downloadable outputs

### Analytics Subteams
- **`dashboard/analytics/common/`** - Shared schemas, KPI definitions, data access utilities
- **`dashboard/analytics/promotions/`** - Promotion effectiveness visualizations & calculations
- **`dashboard/analytics/pricing/`** - Price elasticity visualizations & scenario engine
- **`dashboard/analytics/scenarios/`** - What-if analysis outputs & AI memo generation

---

## Data Contracts (Integration Points)

All outputs must conform to contracts in `dashboard/analytics/common/schemas.py`:

### From ML Team → Dashboard
- **ForecastOutput** (Module 6 & 5): `sku_id, period, y_true, y_pred, y_lower, y_upper, model_name`
- **PromotionOutput** (Module 3 & 7): `sku_id, period, promotion_flag, incremental_sales, lift_pct`
- **ElasticityOutput** (Module 4 & 5): `sku_id, elasticity_value, confidence_low, confidence_high`

### From Analytics → Dashboard Visualization
- All above contracts feed into Plotly visualizations in dashboard modules
- Module 5 (Scenario Simulator) extends ElasticityOutput with **ScenarioOutput**: `sku_id, scenario_name, price_change_pct, demand_change_pct, revenue_change_pct`

### From Dashboard → AI Layer
- **AIContextPayload** (Module 8 chat, click-to-summarise): `module_name, chart_id, metrics, key_findings`
- Every chart has a hidden context payload ready for LLM summarization

---

## Project Structure

```
dashboard/
  app/
    main.py                 # Gradio app shell with sidebar navigation
    __init__.py
  modules/
    overview.py             # Module 1 (TBD)
    data_explorer.py        # Module 2 (TBD)
    scenario_simulator.py   # Module 5 (TBD)
    appendix_export.py      # Module 10 (TBD)
    __init__.py
  components/
    kpi_cards.py            # Reusable KPI card component (TBD)
    plotly_charts.py        # Plotly wrapper components (TBD)
    data_tables.py          # Paginated, filterable tables (TBD)
    ai_narratives.py        # AI summary blocks (TBD)
    __init__.py
  analytics/
    common/
      schemas.py              # Data contracts (ForecastOutput, etc.)
      kpi_definitions.py      # KPI registry and thresholds
      data_loader.py          # Load raw CSV, normalize to contracts (TBD)
      __init__.py
    promotions/
      __init__.py             # Promotion analysis placeholders
    pricing/
      __init__.py             # Elasticity & scenario placeholders
    scenarios/
      __init__.py             # Scenario simulator placeholders
    team_logs.md              # Analytics team work log
```

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1)
- ✅ Create folder structure & schemas
- ⬜ Implement data loader (`dashboard/analytics/common/data_loader.py`)
  - Load `data/data_raw.csv`
  - Normalize columns to contract names
  - Cache processed data
- ⬜ Implement KPI calculations (`dashboard/analytics/common/kpi_calculator.py`)
  - Total revenue, demand, avg price, etc.
  - Used by Module 1 (Overview)

### Phase 2: Core Modules (Week 2-3)
- ⬜ **Module 1: Overview**
  - Display KPI cards
  - Summary of key findings from other modules
  - Key assumptions
- ⬜ **Module 2: Data Explorer**
  - Paginated raw data table
  - Column descriptions & statistics
  - Filters (SKU, date range, promotion flag)
- ⬜ **Module 10: Appendix & Export**
  - Method notes per module
  - Data dictionary
  - Download buttons (CSV, PNG charts)

### Phase 3: Analytics Integration (Week 3-4)
- ⬜ Build **dashboard/analytics/promotions/** visualizations
  - Bar chart: incremental sales per SKU
  - Heatmap: promotion response over time
  - Click-to-summarise handlers (calls AI layer)
  - Multi-select summary support
- ⬜ Build **dashboard/analytics/pricing/** visualizations
  - Elasticity coefficient bar chart
  - Demand curves per SKU
  - Click-to-summarise, multi-select
- ⬜ Implement **Module 5: Scenario Simulator**
  - User input: SKU, price change %
  - Side-by-side demand/revenue charts
  - AI-generated memo with strategic recommendation
  - Export memo as text

### Phase 4: AI Integration (Week 4-5)
- ⬜ Implement click-to-summarise across all charts
  - Extract chart data → AIContextPayload
  - Send to AI layer
  - Render pop-up with AI summary
- ⬜ Implement multi-select visualization summary
  - User selects multiple charts via checkboxes
  - Combined AIContextPayload
  - AI synthesizes findings
- ⬜ Module 8 Chat Interface integration
  - Query input → AI layer
  - Context from all modules
  - Response with `[Data-grounded]` / `[General inference]` labels

### Phase 5: Polish & Testing (Week 5-6)
- ⬜ Refine UI/UX
- ⬜ Performance check (responsive on free HF Spaces CPU)
- ⬜ Module 9: Critical Reflection compilation

---

## Key Dependencies

| Module | Depends On | Provides To |
|--------|-----------|------------|
| **Module 1 (Overview)** | KPI calculations | — |
| **Module 2 (Data Explorer)** | Raw CSV data | — |
| **Module 3 (Promotion Effectiveness)** | PromotionOutput (ML) | Dashboard visuals → AI |
| **Module 4 (Price Elasticity)** | ElasticityOutput (ML) | Dashboard visuals → AI |
| **Module 5 (Scenario Simulator)** | ElasticityOutput + ForecastOutput | ScenarioOutput → Module 8 (Chat) |
| **Module 6 (Demand Forecasting)** | ForecastOutput (ML) | Dashboard visuals → AI |
| **Module 8 (Chat Interface)** | AIContextPayload (all modules) | LLM responses |
| **Module 10 (Appendix)** | All module outputs | Downloadable tables/charts |

---

## Testing Strategy

### Unit Tests
- `dashboard/analytics/common/` schemas and KPI calculations
- Component rendering (KPI cards, charts)

### Integration Tests
- Data loader: CSV → normalized schema
- Contract compliance: ML outputs match ForecastOutput, etc.
- AI payload generation: charts → AIContextPayload

### E2E Tests
- Full dashboard workflow: load data → visualize → click-to-summarise → AI response
- Multi-select scenario: select 3 charts → combined AI narrative

### Performance Tests
- Responsive on free HF Spaces CPU (cold start + interaction latency)
- Load time: data loading, chart rendering

---

## Communication Checklist

**Before merging to main:**
- ✅ Update `dashboard/analytics/team_logs.md` with work done
- ✅ Verify all data contracts match `dashboard/analytics/common/schemas.py`
- ✅ All code follows snake_case naming (see `docs/rules.md`)
- ✅ Pinned versions added to `requirements.txt`
- ✅ AI-assisted code marked with `# AI-assisted: reviewed by [name]`
- ✅ Pass linting: `ruff check .`, `black .`

---

## Next Steps (Immediate Actions)

1. **Load the raw data** → implement `dashboard/analytics/common/data_loader.py`
2. **Calculate baseline KPIs** → implement `dashboard/analytics/common/kpi_calculator.py`
3. **Sketch Module 1 (Overview)** → KPI card layout in Gradio
4. **Coordinate with ML team** → confirm output contracts for ForecastOutput, PromotionOutput, etc.
5. **Coordinate with AI team** → finalize AIContextPayload format for click-to-summarise

---

## Notes

- All work happens on the `analytics` branch (per `docs/rules.md`)
- Push regularly with clear commit messages
- Open a PR to `main` when a module is feature-complete and tested
- The Dashboard Lead reviews and merges PRs after team approval
