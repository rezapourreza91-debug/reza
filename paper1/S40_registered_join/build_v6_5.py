# -*- coding: utf-8 -*-
"""build_v6_5.py - manuscript v6.5 (2026-10-15) from v6.4 (v6.4 untouched).
Removes the last CHECK of sec. 3.1: the five registered-prediction values (rho 0.984 /
0.888 / 0.998, gridT standard MAPE 39.8 % / 47.7 %) are reproduced by the committed
script S40_registered_join_v1.py.  Run from H:\\claude:  python3 _handoff/V6_5/build_v6_5.py .
"""
import re, sys, os
root = sys.argv[1] if len(sys.argv) > 1 else "."
src = os.path.join(root, "manuscript/draft/MANUSCRIPT_PAPER1_v6_4_2026-10-15.md")
dst = os.path.join(root, "manuscript/draft/MANUSCRIPT_PAPER1_v6_5_2026-10-15.md")
t = open(src, encoding="utf-8").read()

old_v = "Version v6.4, 2026-10-15 (as v6.3, plus"
assert t.count(old_v) == 1
t = t.replace(old_v, "Version v6.5, 2026-10-15 (as v6.4, with the registered-prediction values of §3.1 "
              "reproduced by the committed script `S40_registered_join_v1.py` and their CHECK removed; "
              "v6.4 is v6.3 plus")

pat = re.compile(r"\[CHECK: these five values come from joining the\s+registered predictions to "
                 r"`UNIFIED_DATASET_v4\.xlsx`, recorded in `CLAUDE\.md`\s+on 2026-08-21; no committed "
                 r"script performs the join\.\]")
assert len(pat.findall(t)) == 1
t = pat.sub("The five values are\n  computed by `S40_registered_join_v1.py`, which joins the registered predictions\n"
            "  to `UNIFIED_DATASET_v4.xlsx` by design name.", t)
assert "[CHECK" not in t.replace("`[CHECK: …]`", "")
open(dst, "w", encoding="utf-8").write(t)
print("written", dst)
