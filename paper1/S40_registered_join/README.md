# S40: join of the registered grid-family predictions

`S40_registered_join_v1.py` joins the predictions registered for gridS and gridL
(`registered_predictions_batchA.xlsx`, 2026-07-23) and gridT
(`registered_predictions_batchB_T.xlsx`, 2026-07-30) to `UNIFIED_DATASET_v4.xlsx`
by design name and scores them. The input workbooks live in `H:\claude` and are
not copied here; put the script next to them to run it.

Result (`S40_registered_join_v1.csv`), as quoted in manuscript v6.5 §3.1:

| family | metric | Spearman ρ | standard MAPE |
|---|---|---|---|
| gridS | EA_J | 0.984 | (not quoted) |
| gridL | EA_J | 0.888 | (not quoted) |
| gridT | EA_norm | 0.998 | 39.8 % |
| gridT | EA_J | 0.998 | 47.7 % |

Run on 2026-10-15 in the cloud and on Ali's PC; both gave the same output.
`build_v6_5.py` writes manuscript v6.5 from v6.4 and removes the last CHECK.
