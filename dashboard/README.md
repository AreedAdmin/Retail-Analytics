# Dashboard & Analytics Structure

## Quick Start

### Running the Dashboard
```bash
# Install dependencies
pip install -r requirements.txt

# Run the Gradio app
python -m dashboard.app.main

# Or use Gradio CLI
gradio dashboard/app/main.py
```

The app will be available at `http://localhost:7860` (or 7861+ if ports are in use)

### Status
- ✅ **Module 1 (Overview)**: COMPLETE - Professional dark BI dashboard with KPI cards, charts, tables, and collapsible sections (Project Description, Key Findings, Key Assumptions)
- ✅ **Data Integration**: Real data from `data/data_raw.csv` (44 SKUs, 104 weeks ~1.9 years) with automatic date-to-period conversion
- ✅ **Data Pipeline**: Period indexing fixed - dates converted to numeric week numbers (1-104) automatically on load
- ⏳ **Modules 2-10**: To be implemented (Data Explorer, Analytics, ML, AI, Export)
- ✨ **Features**: Responsive collapsible sections, professional dark theme, all KPIs calculated from real data

---

## Architecture Overview

### Module 1 - Overview (Implemented)

**KPI Cards:**
- Total SKUs: 44 unique products analyzed
- Data Periods: 104 weeks (1.9 years)
- Average Price: Calculated from all SKUs
- Promotions Run: Total promotion instances in dataset

**Visualizations:**
- Weekly Sales Trend: Line chart (Teal + Orange promoted sales)
- Top Performers: Ranked list with gold/silver/bronze badges
- Promo Score: Half-doughnut gauge (% promo instances per week)
- Sales by Functionality: Horizontal bar chart
- SKU Status Snapshot: Table with 8 SKUs (Online/Active/Low status)

**Documentation Sections (Collapsible):**
- 📋 Project Description & Navigation: Sidebar guide
- ⭐ Key Findings: Auto-populated from Module 3-7 outputs
- ✓ Key Assumptions: 6 documented assumptions (data, causality, stationarity, etc.)

**Styling:**
- Professional dark theme (Navy #0d1b2a, Teal #00d4aa, Blue #3b82f6)
- All text in white (#ffffff)
- Interactive collapsible sections with blue text
- SKU 25 highlighted in green, SKU 42 in orange
- Smooth animations (0.25s cubic-bezier)

---

### Three Main Components

#### 1. **Dashboard** (`dashboard/`)
The user-facing Gradio application with persistent sidebar navigation.

```
dashboard/
├── app/main.py          # Gradio entry point - sidebar + module routing
├── modules/             # 10 module implementations
│   ├── overview.py              # Module 1: Overview
│   ├── data_explorer.py         # Module 2: Data Explorer
│   ├── promotion_effectiveness.py   # Module 3
│   ├── price_elasticity.py      # Module 4
│   ├── scenario_simulator.py    # Module 5
│   ├── demand_forecasting.py    # Module 6 (ML output)
│   ├── promotion_lift_model.py  # Module 7 (ML output)
│   ├── chat_interface.py        # Module 8 (AI output)
│   ├── critical_reflection.py   # Module 9
│   └── appendix_export.py       # Module 10
└── components/          # Reusable UI components
    ├── kpi_cards.py             # KPI metric cards
    ├── plotly_charts.py         # Plotly wrapper components
    ├── data_tables.py           # Paginated data tables
    └── ai_narratives.py         # AI summary pop-ups
└── analytics/           # Analytics layer (consolidated under dashboard)
    ├── common/              # Shared utilities
    │   ├── schemas.py           # Integration contracts (ForecastOutput, etc.)
    │   ├── kpi_definitions.py   # KPI registry and thresholds
    │   ├── data_loader.py       # Load & normalize raw CSV
    │   └── kpi_calculator.py    # Compute KPI values (TBD)
    ├── promotions/          # Promotion lift analysis
    ├── pricing/             # Price elasticity & scenarios
    └── scenarios/           # Scenario simulator
```

**Responsibilities:**
- User interface and routing
- Visualization layout
- Click-to-summarise event handlers
- Multi-select functionality
- State management

#### 2. **Analytics** (`dashboard/analytics/`)
Analytical calculations and statistical models (consolidated under dashboard team).

```
dashboard/analytics/
├── common/              # Shared utilities
│   ├── schemas.py           # Integration contracts (ForecastOutput, etc.)
│   ├── kpi_definitions.py   # KPI registry and thresholds
│   ├── data_loader.py       # Load & normalize raw CSV
│   └── kpi_calculator.py    # Compute KPI values (TBD)
├── promotions/          # Promotion lift analysis
│   └── __init__.py
├── pricing/             # Price elasticity & scenarios
│   └── __init__.py
└── scenarios/           # Scenario simulator
    └── __init__.py
```

**Responsibilities:**
- Load raw data from `data/data_raw.csv`
- Normalize column names to contracts
- Compute statistical metrics and KPIs
- Generate analysis outputs (promotion lift, elasticity, scenarios)
- Produce AIContextPayload for LLM integration

#### 3. **ML & AI** (other teams)
These teams produce outputs consumed by the dashboard.

- **ML Team** → produces ForecastOutput, PromotionOutput, ElasticityOutput
- **AI Team** → consumes AIContextPayload, produces LLM responses

---

## Data Flow

### 1️⃣ **Data Load**
```
data/data_raw.csv
    ↓ (DataLoader)
dashboard/analytics/common/data_loader.py
    ↓ (normalizes columns: sku→sku_id, week→period)
normalized DataFrame (ready for analytics)
```

### 2️⃣ **Analytics Processing**
```
normalized DataFrame
    ↓
dashboard/analytics/promotions/
dashboard/analytics/pricing/
dashboard/analytics/scenarios/
    ↓ (produces outputs matching schemas.py contracts)
PromotionOutput, ElasticityOutput, ScenarioOutput
```

### 3️⃣ **Dashboard Visualization**
```
PromotionOutput (from ML)
    ↓
dashboard/modules/promotion_effectiveness.py
    ↓ (renders Plotly chart)
Visual display in Module 3
    ↓
AIContextPayload (chart data extracted)
    ↓ (user clicks "Summarise this chart")
AI layer (responds with narrative)
```

### 4️⃣ **AI Integration**
```
AIContextPayload (from any dashboard module/chart)
    ↓
ai/services/llm_client.py (LLM API call)
    ↓
LLM response (with [Data-grounded] / [General inference] labels)
    ↓
dashboard/components/ai_narratives.py (render pop-up or block)
```

---

## Integration Contracts (DO NOT MODIFY WITHOUT COORDINATION)

All data passing between teams must conform to these schemas:

### From ML → Analytics/Dashboard

**ForecastOutput** (Layer 4: ML → Layer 2: Orchestration)
```python
sku_id: str
period: str  # week identifier
y_true: Optional[float]  # actual demand
y_pred: float  # forecast
y_lower: float  # 80% confidence bound
y_upper: float  # 95% confidence bound
model_name: str  # e.g., "gradient_boosting"
```

**PromotionOutput** (Layer 3: Analytics → Layer 2: Orchestration)
```python
sku_id: str
period: str
promotion_flag: bool
incremental_sales: float
lift_pct: float
```

**ElasticityOutput** (Layer 3: Analytics → Layer 2: Orchestration)
```python
sku_id: str
elasticity_value: float  # e.g., -1.2
confidence_low: float
confidence_high: float
model_type: str
```

### From Dashboard → AI

**AIContextPayload** (Layer 2: Orchestration → Layer 5: AI Intelligence)
```python
module_name: str  # e.g., "promotion_effectiveness"
chart_id: str  # unique chart identifier
metrics: Dict[str, Any]  # raw numbers from chart
key_findings: List[str]  # bullet points to narrate
```

See `analytics/common/schemas.py` for full definitions.

---

## KPI Registry

All dashboard KPIs are defined in `analytics/common/kpi_definitions.py`:

**Overview KPIs (Module 1)**
- Total Revenue
- Total Demand (Units)
- Number of SKUs
- Analysis Periods
- Average Price
- Promotions Run

**Module-Specific KPIs**
- Promotion Lift (total and average %)
- High-response SKUs
- Elasticity (average and distribution)
- Forecast Error (MAPE)
- Forecast Uncertainty

See `kpi_definitions.py` for thresholds used for color-coding and alerts.

---

## Module Dependencies

| Module | Depends On | Produces |
|--------|-----------|----------|
| 1 Overview | Data Loader, KPI Calc | KPI summary |
| 2 Data Explorer | Data Loader | Table view |
| 3 Promotion Effectiveness | PromotionOutput (ML) | Visuals → AIContextPayload |
| 4 Price Elasticity | ElasticityOutput (ML) | Visuals → AIContextPayload |
| 5 Scenario Simulator | ElasticityOutput + ForecastOutput | ScenarioOutput → AIContextPayload |
| 6 Demand Forecasting | ForecastOutput (ML) | Visuals → AIContextPayload |
| 7 Promotion Lift Model | PromotionOutput (ML) | Diagnostics → AIContextPayload |
| 8 Chat Interface | All modules via AIContextPayload | LLM responses |
| 9 Critical Reflection | All modules | Reflection summary |
| 10 Appendix & Export | All outputs | Downloadable tables/charts |

---

## Development Workflow

### 1. Load Data
```python
from dashboard.analytics.common.data_loader import get_data_loader

loader = get_data_loader()
df = loader.get_normalized_data()  # DataFrame with normalized columns
stats = loader.get_summary_stats()  # For Module 1 KPIs
```

### 2. Create Visualizations
```python
from dashboard.analytics.common.schemas import AIContextPayload
import plotly.graph_objects as go

# Build chart with Plotly
fig = go.Figure(...)

# Prepare context for LLM (click-to-summarise)
context = AIContextPayload(
    module_name="promotion_effectiveness",
    chart_id="promo_lift_chart_1",
    metrics={...},  # numbers from chart
    key_findings=["SKU-1 shows 15% lift", "SKU-5 shows 2% lift"]
)
```

### 3. Integrate with AI Layer
```python
from ai.services.context_builder import build_context_payload

# When user clicks "Summarise this chart"
ai_context = build_context_payload(chart_data)

# LLM responds with grounded narrative
response = llm_client.summarize_chart(ai_context)
```

---

## Testing

### Unit Tests
```bash
pytest analytics/common/test_schemas.py
pytest analytics/common/test_data_loader.py
pytest dashboard/components/test_kpi_cards.py
```

### Integration Tests
```bash
pytest analytics/test_integration.py  # Data contracts
pytest dashboard/test_modules.py      # Module rendering
```

### E2E Tests
```bash
pytest dashboard/test_e2e.py  # Full workflow
```

### Performance Profiling
```bash
# Ensure < 8 GB RAM usage
python -m memory_profiler dashboard/app/main.py
```

---

## Best Practices

### Column Naming
All columns must use snake_case. The DataLoader normalizes raw CSV:
- `sku` → `sku_id`
- `week` → `period`
- `weekly_sales` → `demand_units`

### Schema Compliance
Always use classes from `dashboard/analytics/common/schemas.py` when creating outputs:
```python
from dashboard.analytics.common.schemas import PromotionOutput

output = PromotionOutput(
    sku_id="SKU-1",
    period="2024-W01",
    promotion_flag=True,
    incremental_sales=150.5,
    lift_pct=12.3,
)

# Serialize to dict for JSON/API
data = output.to_dict()
```

### AI Context Packaging
Never pass raw data rows to the LLM. Always use AIContextPayload:
```python
context = AIContextPayload(
    module_name="promotion_effectiveness",
    chart_id="chart_1",
    metrics={"avg_lift": 8.5, "best_sku": "SKU-3"},
    key_findings=["Strong response from SKU-3", "Weak response from SKU-1"],
)

# Send only the structured context to LLM
response = llm.summarize(context.to_json_string())
```

### Caching & Performance
Use DataLoader singleton:
```python
from dashboard.analytics.common.data_loader import get_data_loader

loader = get_data_loader()  # Returns same instance
df = loader.get_normalized_data()  # Uses cache
```

---

## Troubleshooting

### Data not found
```
FileNotFoundError: Raw data file not found: .../data/data_raw.csv
```
→ Ensure `data/data_raw.csv` exists in project root

### Column not found
```
ValueError: Missing expected columns: {'demand_units'}
```
→ Check raw CSV has required columns: week, sku, weekly_sales, price, feat_main_page, color, vendor, functionality

### Import errors
```
ModuleNotFoundError: No module named 'analytics'
```
→ Ensure running from project root and `analytics/common/__init__.py` exists

---

## Next Steps

1. **Implement `kpi_calculator.py`** - Compute overview KPIs
2. **Build Module 1 (Overview)** - Display KPI cards
3. **Build Module 2 (Data Explorer)** - Paginated data table
4. **Coordinate with ML team** - Confirm output contracts
5. **Build analytics/* modules** - Promotion, pricing, scenarios
6. **Integrate AI layer** - Click-to-summarise handlers

See `DASHBOARD_ANALYTICS_PLAN.md` for detailed roadmap.
