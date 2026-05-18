# Forecasting (Module 6)

Weekly per-SKU sales forecasting. Global model over all SKUs, log target,
chronological train/val/test split (13-week val, 13-week test).

## Regenerate

```bash
# from repo root, with the project env (numpy, pandas, scikit-learn,
# statsmodels) available
jupyter nbconvert --to notebook --execute --inplace \
  ml/ml_forecasting/forecasting.ipynb
```

Or open `ml/ml_forecasting/forecasting.ipynb` and run all cells top to bottom.
It reads `../../data/data_raw.csv` and is deterministic (seed 42).

## Outputs (`ml/ml_forecasting/outputs/`)

| File | Contents |
|---|---|
| `forecast.csv` | Forecast contract: `sku_id, period, y_true, y_pred, y_lower, y_upper, model_name`. Backtest (val + test weeks), `y_true` filled. `y_lower/y_upper` = 95% interval. |
| `per_sku_metrics.csv` | Per-SKU MAE/RMSE/MAPE on the test split (for the AI Pod narratives). |
| `test_summary.csv` | One-row overall test MAE/RMSE/MAPE + 80%/95% interval coverage. |

## Method

- **Features:** per-SKU lags (sales/revenue/price 1–4w), price %-change,
  promotion features (lagged promo, weeks-since-promo, promo count,
  promo×price), calendar (week-of-year cyclic, month, quarter, is-Q4),
  trailing rolling sales mean/std, price-shape (log price, vs-SKU-mean,
  discount flag), short-vs-long trend. All trailing windows are past-only.
- **Leakage controls:** current-week revenue and sales/revenue %-change
  dropped; `price_vs_sku_mean` and the one-hot encoder are fit on train only;
  val/test features carry prior history then are sliced back.
- **Models:** Naive (last week), Ridge, HistGradientBoostingRegressor (+
  time-series-CV tuned variant), per-SKU ARIMA. Selected on validation MAE.
- **Selected model** is refit on train+val for the delivered forecast;
  intervals are residual-based (log space) from the train-only validation
  residuals, 95% band shipped in the contract.

## Notes / limitations

- Backtest only — no true-future periods (would need assumed future
  price/promo, which are not in `data_raw.csv`).
- 95% interval coverage is well-calibrated on test; the 80% band runs a little
  narrow due to the later test period's distribution shift.
- Raw `sku` is not a model feature (SKU character carried by engineered
  features + one-hot vendor/color/functionality); one-hot `sku` is an easy
  future ablation.
