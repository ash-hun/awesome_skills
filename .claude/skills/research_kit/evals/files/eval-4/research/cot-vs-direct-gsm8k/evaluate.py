"""evaluation.md 의 집계를 다시 계산한다. runs/ 를 읽기만 한다."""
import json, re, statistics as st, sys
from pathlib import Path

PAT = re.compile(r"####\s*(-?[\d,]+(?:\.\d+)?)")
root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent
acc = {}
for run in sorted((root / "experiments/exp1-cot-vs-direct/runs").iterdir()):
    cond = run.name.split("-")[0]
    rows = [json.loads(l) for l in (run / "metrics.jsonl").open(encoding="utf-8")]
    correct = sum(1 for r in rows if r["prediction"] is not None and r["prediction"].replace(",", "") == str(r["gold"]))
    acc.setdefault(cond, []).append(correct / len(rows) * 100)
for c, v in acc.items():
    print(f"{c}: {st.mean(v):.1f} ± {st.stdev(v):.1f} (seeds {[round(x,1) for x in v]})")
print(f"prop - base = {st.mean(acc['prop']) - st.mean(acc['base']):+.1f}%p")
