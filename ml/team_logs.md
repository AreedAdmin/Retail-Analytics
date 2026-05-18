# Team Logs

## Forecasting (Module 6) — 2026-05-18

Decisions:
- **Problem framing:** global model over all SKUs (one model, SKU character
  via engineered + one-hot features; raw `sku` not a feature). Target =
  `log1p(weekly_sales)`; metrics back-transformed to real units.
- **Split:** chronological panel split, 13-week validation, 13-week test
  (`panel_data_split`). No random split (would leak future).
- **Leakage controls:** dropped current-week `weekly_revenue` and
  sales/revenue %-change; `price_vs_sku_mean` and one-hot encoder fit on
  train only; val/test features carry prior history then sliced back.
- **Feature engineering:** lags, price %-change, promotion, calendar,
  trailing rolling stats, price-shape, trend, log target, `is_promo`. All
  trailing windows past-only. First `max_lag` warm-up rows dropped.
- **Models compared (validation MAE, real units):** HistGBR 37.0 (best),
  HistGBR_tuned 37.3, Naive 47.9, ARIMA 48.7, Ridge 48.7.
- **Selected:** HistGBR, refit on train+val for delivery. Test MAE ≈ 58.8
  vs Naive ≈ 90.9 (≈35% lift).
- **Tuning:** week-based expanding-window CV (panel-safe). Tuned ≈ default
  (model not tuning-sensitive here).
- **Intervals:** residual-based, log space, from train-only validation
  residuals. Test coverage: 95% band ≈94% (well-calibrated, shipped in
  contract); 80% band ≈72% (slightly narrow, later-period drift).
- **Output:** backtest only (val+test, `y_true` filled) — no true-future
  periods (no future price/promo available).

Open / future: true-future forecasts (needs future-exogenous assumptions);
one-hot `sku` ablation; MAPE-blowup investigation on worst SKUs.

Deliverables: `ml/ml_forecasting/outputs/{forecast.csv,
per_sku_metrics.csv, test_summary.csv}`; regen steps in
`ml/ml_forecasting/README.md`.
