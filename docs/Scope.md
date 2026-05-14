# PATH 2: Methodological path

## Topic: AI-Powered Marketing Analytics Dashboard
Background

This assignment gives you the opportunity to work hands-on with data visualization, analytics, and generative AI, building a practical tool that informs high-impact marketing decisions in an e-commerce setting.

As the marketing manager of an e-commerce platform, you are focused on using data-driven
insights to better forecast demand, evaluate promotions, and optimize pricing strategies for
your product line. You've reached out to your analytics team for an AI-powered dashboard
that goes beyond static charts — one that can explain its findings in plain language and
respond to questions, acting as an intelligent decision support tool for the next period's
planning.

## Objective
Using the provided dataset [https://demandprediction.github.io/dataset.html], your task is to
develop an interactive, AI-augmented marketing mix dashboard using R or Python that
answers the marketing manager's key questions. The dashboard should combine predictive
analytics with a generative AI layer that narrates insights and responds to natural language
queries, enabling faster, more accessible data-driven decision-making.

## Scope of Work to Achieve (from assignment instructions)

### Assessment Criteria (100 points)

| Criterion | Description | Points |
| --- | --- | --- |
| Clarity and Structure | Is the presentation well-organized, clear, and easy to follow? | 20 |
| Content Insight | Does the dashboard accurately forecast demand; provide meaningful promotion effectiveness analysis; enable intuitive price sensitivity exploration; and present findings in a usable format for decision-making? | 30 |
| GenAI Integration | Are the AI-generated narratives accurate and useful? Does the query interface return grounded, relevant responses? Has the team made deliberate design choices about what context to supply the LLM, and how to prevent hallucinated figures? | 20 |
| Critical Reflection | Has the group thoughtfully discussed the benefits, limitations, and risks of using AI-augmented dashboards for retail decision-making, including specific examples from their own tool? | 10 |
| Use of Visuals | Are visuals and data presented effectively to support insights? | 20 |

### Note on AI Use

The generative AI components of this assignment are part of the assessment itself. We are expected to design, evaluate, and critique them. Simply connecting an API and displaying its output uncritically will not score well on GenAI integration and critical reflection criteria. Strong submissions should show evidence of:

- prompt engineering
- output validation
- honest reflection on failure cases

### Required Work Packages

#### 1. Tool Selection and Setup

- Build the dashboard in Python (e.g., Streamlit, Dash, Plotly, Voila) or R (Shiny, Flexdashboard).
- Ensure interactive charts and user-friendly data output presentation.
- Integrate a generative AI API (Claude/Anthropic or equivalent such as OpenAI) in two ways:
	- AI Insight Narration: automatically generate plain-language summaries of each analytical section.
	- Natural Language Query Interface: allow users to ask questions and receive AI-generated responses grounded in dashboard outputs.

#### 2. Demand Forecasting

Question to address: What is the expected demand for each SKU in the next few periods?

- Implement suitable ML models (e.g., regression, neural network models) to predict demand for each SKU.
- Create a visual forecast display per SKU, including confidence intervals where possible.
- Under each forecast visual, include an AI-generated narrative interpreting trends (e.g., declining demand, high uncertainty, strong seasonality).

#### 3. Feature Promotion Effectiveness

Questions to address: Do feature promotions effectively boost demand, and for which SKUs? How much incremental sales are generated from feature promotions?

- Use the SCAN*PRO model or a justified alternative to assess promotion impact.
- Measure sales lift attributable to feature promotions, reported as incremental sales per SKU.
- Visualize which SKUs show significant demand increases due to promotions.
- Include an AI-generated commentary block interpreting lift results, identifying strongest and weakest responders, and suggesting strategic implications (e.g., continue or discontinue promotions).

#### 4. Price Elasticity and Scenario Testing

Questions to address: Which SKUs are most sensitive to price changes? How would a 10% price increase or decrease impact demand and revenue?

- Use a suitable model from the module to estimate price elasticity for each SKU.
- Visualize how price changes impact demand.
- Run what-if scenarios for demand changes under:
	- price increases: 5%, 10%, 20%, 30%
	- price decreases: 5%, 10%, 20%, 30%
- For each scenario, generate an AI-written strategic recommendation memo on revenue implications and pricing advice.
- Critically evaluate whether AI recommendations are consistent with underlying data.

#### 5. Natural Language Query Interface

- Embed a conversational query interface in the dashboard for plain-English questions.
- Connect it to Claude API (or equivalent) and provide relevant model outputs as context so responses are grounded in dashboard data, not general knowledge.
- A single-turn Q&A interface is sufficient (full conversational agent not required).
- Responses should clearly indicate when they draw from dashboard outputs versus general inference.
- Design the system to avoid fabricating figures not present in outputs.

Example queries to support:

- Which SKUs should I prioritise for promotion next quarter?
- What happens to total revenue if I reduce prices by 10% across all SKUs?
- Which products are most at risk of demand decline?
- Is the promotion for SKU 4 generating enough incremental sales to justify the discount?