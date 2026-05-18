# Tech Stack

## Purpose

This document defines the technical stack for the AI-augmented retail analytics dashboard and provides a layered architecture so the system can be expanded without major refactoring.

## Core Platform

- Language: Python 3.11+
- App Framework: Gradio
- Visualization: Plotly
- LLM Runtime: Ollama Cloud (`gpt-oss:120b-cloud`) primary, OpenAI/Anthropic API fallback, offline grounded extractor if none configured
- Data Source: CSV/parquet files from `data/`
- Version Management: `requirements.txt` in repository root (pinned to the validated environment)
- Hosting: Hugging Face Spaces (free CPU) — Gradio app + in-process ML models; see `deploy.md`
- Secrets Management: GitHub Repository / Hugging Face Space secrets (no local secret files committed)

## Baseline Python Packages

Use pinned versions in `requirements.txt` once agreed by the team.

### Application and UI

- gradio
- plotly
- pydantic
- python-dotenv (local development only, never commit secrets)

### Data Processing

- pandas
- numpy
- pyarrow
- scipy

### Machine Learning and Forecasting

- scikit-learn
- statsmodels
- xgboost (optional)

### Evaluation and Explainability

- scikit-learn metrics (built-in)
- shap (optional)

### LLM and AI Integration

- ollama
- openai and/or anthropic
- tiktoken (optional token estimation)

### Quality and Tooling

- pytest
- ruff
- black
- mypy (optional, if strict typing is adopted)

## Application Layers

The stack is organized by layers. Each layer has a clear responsibility and can be extended by adding new services/components without breaking existing modules.

### Layer 1: Presentation Layer

Purpose: User-facing interface and interaction flow.

Current components:

- Gradio app shell
- Route/module navigation (tabs or sidebar-like navigation pattern)
- Interactive charts and controls
- Modal/pop-up summaries from selected visualizations

Expansion options:

- Theming system
- Role-specific views (manager vs analyst)
- Multi-page state persistence

### Layer 2: Orchestration Layer

Purpose: Coordinates user actions with analytics, ML, and AI services.

Current components:

- Module controllers (analytics, ml, chat)
- Request routing for chart click events and multi-select summary requests
- Input validation and payload shaping

Expansion options:

- Event bus for cross-module actions
- Workflow engine for scheduled analytics runs

### Layer 3: Analytics Layer

Purpose: Business analytics and statistical calculations.

Current components:

- Promotion effectiveness calculations
- Price elasticity calculations
- Scenario testing engine

Expansion options:

- Basket analysis
- Customer segmentation
- Campaign attribution models

### Layer 4: ML Layer

Purpose: Model training, inference, and evaluation outputs.

Current components:

- Demand forecasting models per SKU
- Promotion lift model outputs
- Prediction intervals and model metrics

Expansion options:

- Model registry
- Auto model selection
- Drift detection and retraining triggers

### Layer 5: AI Intelligence Layer

Purpose: LLM-powered narration and Q&A grounded in model outputs.

Current components:

- Prompt templates
- Context packaging from dashboard outputs
- Local LLM inference via Ollama (primary local path)
- API fallback path via OpenAI/Anthropic when needed
- Single-turn Q&A responses
- Visualization summary generation (single-chart and multi-chart)

Expansion options:

- Prompt versioning store
- Guardrail policy engine
- Model routing policy (auto-select local vs API model per task)
- Response quality scorer

### Layer 6: Data Access Layer

Purpose: Controlled access to raw and processed datasets.

Current components:

- Data loaders from `data/`
- Shared schemas for module inputs/outputs
- Caching for repeated reads

Expansion options:

- Data contracts with schema validation
- Feature store abstraction
- Database backend swap (Postgres, DuckDB, BigQuery)

### Layer 7: Infrastructure and DevOps Layer

Purpose: Environment consistency, CI checks, and deployment standards.

Current components:

- Root `requirements.txt`
- Branch strategy (`ml`, `ai`, `analytics` -> PR to `main`)
- Lint/test pipeline

Expansion options:

- CI/CD workflows
- Containerization with Docker
- Staging deployment before release

## Team-to-Layer Mapping

- ML team: Layers 3 and 4
- AI team: Layer 5
- Dashboard analytics team: Layers 1 and 2
- Shared ownership: Layers 6 and 7

## Recommended Project Structure for Layered Growth

```text
Retail-Group-Assignment/
  ai/
    prompts/
    services/
  ml/
    forecasting/
    promotions/
    evaluation/
  dashboard/
    app/
    modules/
    components/
  analytics/
    pricing/
    promotions/
    scenarios/
  data/
  docs/
    Scope.md
    rules.md
    deliverable.md
    tech_stack.md
  requirements.txt
```

## Integration Contracts (Must Stay Stable)

To keep modules independent and scalable, preserve these contracts:

- Forecast output contract: `sku_id`, `period`, `y_true`, `y_pred`, `y_lower`, `y_upper`, `model_name`
- Promotion output contract: `sku_id`, `period`, `promotion_flag`, `incremental_sales`, `lift_pct`
- Elasticity output contract: `sku_id`, `elasticity_value`, `confidence_low`, `confidence_high`
- Scenario output contract: `sku_id`, `scenario_name`, `price_change_pct`, `demand_change_pct`, `revenue_change_pct`
- AI context contract: structured JSON with `module_name`, `chart_id`, `metrics`, `key_findings`

## Non-Functional Constraints

- All code follows snake_case naming.
- Models are lightweight and CPU-only (the forecasting model is a few MB,
  sub-second inference) — the app runs on a free Hugging Face Spaces CPU
  instance; no GPU is required.
- AI responses must avoid fabricated figures and label grounded vs inferred content.
- Every team updates `team_log.md` in their folder as work progresses.

## Next Update Trigger

Update this file when any of the following changes:

- Framework changes (UI, ML, or LLM provider)
- Ollama model choice or local runtime configuration changes
- New application layer is introduced
- Data contracts are modified
- New shared package is added to `requirements.txt`
