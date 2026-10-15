# -*- coding: utf-8 -*-
"""
S40_registered_join_v1.py - joins the predictions registered for the three grid
families to UNIFIED_DATASET_v4.xlsx and scores them. Replaces the undocumented
join recorded in CLAUDE.md on 2026-08-21 (manuscript v6.4 sec. 3.1 CHECK).

Inputs (same folder as this script):
  registered_predictions_batchA.xlsx    gridS, gridL  (EA_J_pred, registered 2026-07-23)
  registered_predictions_batchB_T.xlsx  gridT         (EA_norm_pred, EA_J_pred_T, registered 2026-07-30)
  UNIFIED_DATASET_v4.xlsx               measured EA_J, EA_norm (= EA_J / (n_col x Hr))
Join key: registered `design` == dataset `run_id`.
Scores: Spearman rho (average ranks for ties, numpy only), standard MAPE
  = mean(|pred - meas| / meas), and MAPE relative to the prediction
  = mean(|pred - meas| / pred) for reference.
Output: S40_registered_join_v1.csv (one row per family x metric), printed table.
ASCII output only.
"""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
P = lambda f: os.path.join(HERE, f)


def ranks(x):
    x = np.asarray(x, float)
    order = np.argsort(x, kind="mergesort")
    r = np.empty(len(x))
    r[order] = np.arange(1, len(x) + 1)
    for v in np.unique(x):                      # average ranks for ties
        m = x == v
        r[m] = r[m].mean()
    return r


def spearman(a, b):
    return float(np.corrcoef(ranks(a), ranks(b))[0, 1])


def score(fam, metric, pred, meas):
    pred, meas = np.asarray(pred, float), np.asarray(meas, float)
    err = np.abs(pred - meas)
    return {"family": fam, "metric": metric, "n": len(pred),
            "rho": spearman(pred, meas),
            "MAPE_std_pct": 100 * float(np.mean(err / meas)),
            "MAPE_vs_pred_pct": 100 * float(np.mean(err / pred)),
            "mean_pred": float(pred.mean()), "mean_meas": float(meas.mean())}


def main():
    ds = pd.read_excel(P("UNIFIED_DATASET_v4.xlsx")).set_index("run_id")
    ra = pd.read_excel(P("registered_predictions_batchA.xlsx"))
    rt = pd.read_excel(P("registered_predictions_batchB_T.xlsx"))
    rows = []
    for grid, fam in (("gridS", "B_gridS"), ("gridL", "C_gridL")):
        r = ra[ra["grid"] == grid].set_index("design")
        j = r.join(ds[["family", "EA_J", "EA_norm"]], how="inner")
        assert len(j) == len(r) == 12 and (j["family"] == fam).all(), grid
        rows.append(score(grid, "EA_J", j["EA_J_pred"], j["EA_J"]))
    r = rt.set_index("design")
    j = r.join(ds[["family", "EA_J", "EA_norm", "n_col", "Hr", "H"]], how="inner")
    assert len(j) == len(r) == 12 and (j["family"] == "D_gridT").all(), "gridT"
    rows.append(score("gridT", "EA_norm", j["EA_norm_pred"], j["EA_norm"]))
    rows.append(score("gridT", "EA_J", j["EA_J_pred_T"], j["EA_J"]))
    out = pd.DataFrame(rows)
    out.to_csv(P("S40_registered_join_v1.csv"), index=False, float_format="%.4f")
    pd.set_option("display.width", 200)
    print(out.round(4).to_string(index=False))
    print("gridT dataset H = %.3f mm, n_col = %d, Hr = %.4f" % (j["H"].iloc[0], j["n_col"].iloc[0], j["Hr"].iloc[0]))


if __name__ == "__main__":
    main()
