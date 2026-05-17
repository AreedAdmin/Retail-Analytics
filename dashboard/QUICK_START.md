# Dashboard Analytics Team - Quick Start Guide

## 📋 Setup (First Time Only)

### 1. Clone & Branch
```bash
# Already done in your workspace:
# git clone https://github.com/AreedAdmin/Retail-Analytics
# git checkout -b salomee
```

### 2. Install Dependencies
```bash
# From project root
pip install -r requirements.txt
```

### 3. Verify Data
```bash
# Check raw data exists
python -c "from analytics.common.data_loader import get_data_loader; loader = get_data_loader(); print(loader.get_normalized_data())"
```

---

## 🚀 Development Workflow

### Day-to-Day Commands

```bash
# Switch to project directory
cd c:\Users\salom\Downloads\Retail

# Pull latest from main branch
git checkout main
git pull origin main

# Switch to your working branch
git checkout analytics  # or your team's branch

# Create a feature branch for your work (recommended)
git checkout -b feature/module-1-overview

# Do your work...
# (edit files, test, etc.)

# Stage changes
git add dashboard/

# Commit with clear message
git commit -m "feat(dashboard): implement Module 1 overview with KPI cards"

# Push to remote
git push origin feature/module-1-overview

# Create Pull Request on GitHub (when ready for review)
```

### Running the Dashboard
```bash
# Run the Gradio app
python -m dashboard.app.main

# Navigate to http://localhost:7860 in your browser
```

### Running Tests
```bash
# All tests
pytest

# Specific module
pytest dashboard/analytics/common/test_data_loader.py

# With verbose output
pytest -v
```

### Code Quality
```bash
# Check linting
ruff check .

# Format code
black .

# Both together
ruff check . && black .
```

---

## 📁 Your Files This Week

As part of the **Dashboard Analytics team**, focus on these:

### ✅ Already Created
- `dashboard/analytics/common/schemas.py` — Integration contracts
- `dashboard/analytics/common/kpi_definitions.py` — KPI registry
- `dashboard/analytics/common/data_loader.py` — Load & normalize CSV
- `dashboard/app/main.py` — Gradio entry point (skeleton)
- `dashboard/README.md` — Full architecture guide

### ⬜ You Need to Build

**Priority 1: Data Foundation**
- `dashboard/analytics/common/kpi_calculator.py` — Compute KPI values (total revenue, avg price, etc.)
  - Used by Module 1 (Overview)

**Priority 2: Module 1 (Overview)**
- `dashboard/modules/overview.py` — High-level KPI cards
  - Display summary metrics
  - Link to other modules

**Priority 3: Module 2 (Data Explorer)**
- `dashboard/modules/data_explorer.py` — Raw data inspection
  - Paginated table
  - Column descriptions
  - Basic statistics

**Priority 4: Reusable Components**
- `dashboard/components/kpi_cards.py` — KPI card component
- `dashboard/components/plotly_charts.py` — Chart wrapper
- `dashboard/components/data_tables.py` — Table component

---

## 🔗 Key Classes to Use

### Loading Data
```python
from dashboard.analytics.common.data_loader import get_data_loader

loader = get_data_loader()
df = loader.get_normalized_data()  # All data, normalized columns
stats = loader.get_summary_stats()  # For Module 1 KPIs
sku_list = loader.get_sku_list()    # All SKUs
```

### Using Schemas
```python
from dashboard.analytics.common.schemas import (
    ForecastOutput,
    PromotionOutput,
    ElasticityOutput,
    ScenarioOutput,
    AIContextPayload,
)

# When ML team provides outputs, wrap them:
forecast = ForecastOutput(
    sku_id="SKU-1",
    period="2024-W01",
    y_true=100.0,
    y_pred=105.2,
    y_lower=95.0,
    y_upper=115.0,
    model_name="gradient_boosting",
)

# Serialize to dict
data = forecast.to_dict()
```

### Using KPIs
```python
from analytics.common.kpi_definitions import KPIRegistry, KPIThresholds

# Get KPI display name
name = KPIRegistry.get_display_name(KPIRegistry.TOTAL_REVENUE)
# Output: "Total Revenue"

# Check thresholds
if lift > KPIThresholds.HIGH_PROMOTION_RESPONSE_THRESHOLD:
    status = "High responder"
```

### Creating AI Context
```python
from dashboard.analytics.common.schemas import AIContextPayload

context = AIContextPayload(
    module_name="promotion_effectiveness",
    chart_id="promo_chart_1",
    metrics={
        "avg_lift": 8.5,
        "num_skus_with_promotion": 5,
        "best_sku": "SKU-3",
    },
    key_findings=[
        "SKU-3 shows strongest response (15% lift)",
        "SKU-1 shows minimal response (2% lift)",
    ],
)

# Send to LLM later
json_string = context.to_json_string()
```

---

## 📊 Example: Building Module 1 (Overview)

```python
# dashboard/modules/overview.py
import gradio as gr
from dashboard.analytics.common.data_loader import get_data_loader
from dashboard.analytics.common.kpi_definitions import KPIRegistry

def build_overview_module():
    """Module 1: Overview - KPI summary."""
    loader = get_data_loader()
    stats = loader.get_summary_stats()
    
    with gr.Group():
        gr.Markdown("## Overview - Key Metrics")
        
        # KPI Cards Row 1
        with gr.Row():
            with gr.Column():
                gr.Number(
                    value=stats['total_revenue'],
                    label="Total Revenue ($)",
                    interactive=False,
                )
            with gr.Column():
                gr.Number(
                    value=stats['total_demand_units'],
                    label="Total Demand (Units)",
                    interactive=False,
                )
            with gr.Column():
                gr.Number(
                    value=stats['num_skus'],
                    label="Number of SKUs",
                    interactive=False,
                )
        
        # KPI Cards Row 2
        with gr.Row():
            with gr.Column():
                gr.Number(
                    value=stats['avg_price'],
                    label="Average Price ($)",
                    interactive=False,
                )
            with gr.Column():
                gr.Number(
                    value=stats['num_promotions'],
                    label="Promotions Run",
                    interactive=False,
                )
        
        # Summary findings
        gr.Markdown("### Key Findings")
        gr.Markdown("""
        - **Revenue**: Strong performance driven by high-volume SKUs
        - **Promotions**: XXX promotion events analyzed
        - **Price Range**: $XX - $XXX (avg: $XXX)
        - **Next Steps**: See detailed modules for promotion effectiveness, elasticity, forecasts
        """)

if __name__ == "__main__":
    with gr.Blocks() as demo:
        build_overview_module()
    demo.launch()
```

---

## 📞 Communication Checklist

Before pushing code to your branch:

- ✅ Update `dashboard/analytics/team_logs.md` with your work
- ✅ All code uses **snake_case** (file names, variables, functions)
- ✅ All imports from `dashboard.analytics.common.schemas` (don't invent contracts)
- ✅ No hardcoded file paths (use DataLoader)
- ✅ Run `ruff check . && black .`
- ✅ Run `pytest` to check tests pass
- ✅ `requirements.txt` updated if you added packages

---

## 🤝 Coordination Points

### With ML Team
- **Confirm output contracts** — Do their ForecastOutput, PromotionOutput match `schemas.py`?
- **Get sample data** — Request dummy outputs for testing your modules before real data arrives

### With AI Team
- **AIContextPayload format** — Is your payload structure clear for LLM context?
- **Click-to-summarise** — How does the LLM service receive and process your context?

### With Dashboard Lead (Integration)
- **Module dependencies** — Confirm Modules 1, 2, 5, 10 roadmap
- **Cross-team data flow** — PR review before merge to main

---

## 🐛 Troubleshooting

### Import Error: `ModuleNotFoundError: No module named 'analytics'`
→ Run from project root: `cd c:\Users\salom\Downloads\Retail`

### Data Not Found: `FileNotFoundError: Raw data file not found`
→ Verify `data/data_raw.csv` exists in project root

### Gradio Won't Start
→ Check port 7860 is not in use: `lsof -i :7860` (Linux/Mac) or find process on Windows

### Merge Conflicts
→ Pull latest from main, rebase your branch, resolve conflicts, test, then push again

---

## 📖 Additional Resources

- **Full Architecture:** `dashboard/README.md`
- **Detailed Roadmap:** `DASHBOARD_ANALYTICS_PLAN.md`
- **Project Rules:** `docs/rules.md`
- **Tech Stack:** `docs/tech_stack.md`
- **Deliverable Spec:** `docs/deliverable.md`
- **Integration Contracts:** `dashboard/analytics/common/schemas.py`

---

## Next Steps (Right Now)

1. **Read `dashboard/README.md`** — Understand full architecture
2. **Read `DASHBOARD_ANALYTICS_PLAN.md`** — See detailed roadmap
3. **Load data** — Test `dashboard/analytics/common/data_loader.py` works
4. **Start Module 1** — Build KPI cards for overview
5. **Commit regularly** — Add work to `dashboard/analytics/team_logs.md`
6. **Coordinate with teams** — Confirm data contracts

---

Good luck! 🚀 Let me know if you have questions.
