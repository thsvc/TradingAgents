import statistics as st

rows = []
with open("logs/wf/SUMMARY.tsv") as f:
    next(f)
    for line in f:
        w, pts, sh, mdd, log = line.rstrip().split("\t")
        rows.append((w, int(pts), float(sh), float(mdd), log))


def md_table(data):
    lines = ["| Window | Points | Sharpe | MDD | Log |", "|---|---:|---:|---:|---|"]
    for w, pts, sh, mdd, log in data:
        lines.append(f"| {w} | {pts} | {sh:.3f} | {mdd:.3f} | `{log}` |")
    return "\n".join(lines)


sharpes = [r[2] for r in rows if r[1] > 0]
mdds = [r[3] for r in rows if r[1] > 0]
verdict = "UNSTABLE"

if len(sharpes) >= 5:
    if sum(1 for s in sharpes if s > 0) >= len(sharpes) // 2 and st.median(mdds) <= 0.25:
        verdict = "STABLE-ish"

print("## Walk-forward Summary\n")
print(md_table(rows), "\n")
print("**Verdict (heuristic):**", verdict, "\n")
if sharpes:
    print(f"- Sharpe > 0 in {sum(1 for s in sharpes if s > 0)}/{len(sharpes)} windows")
    print(f"- Median Sharpe: {st.median(sharpes):.3f}")
if mdds:
    print(f"- Median MDD: {st.median(mdds):.3f}")
