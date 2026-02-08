from typing import Dict, List


def generate_insights(summary: Dict) -> List[str]:
    """
    Rule-based "AI-style" insights (Phase 1).
    Later you can replace this with a real LLM or ML model.
    """
    insights: List[str] = []

    actions = summary.get("actions", 0)
    err = float(summary.get("error_rate", 0.0))
    avg = float(summary.get("avg_duration_ms", 0.0))
    p95 = float(summary.get("p95_duration_ms", 0.0))
    by_action = summary.get("by_action", {}) or {}

    write = int(by_action.get("write_code", 0))
    commit = int(by_action.get("commit_code", 0))
    bugfix = int(by_action.get("fix_bug", 0))
    deadline = int(by_action.get("miss_deadline", 0))

    if actions == 0:
        return ["Click an action to generate activity and insights."]

    # Reliability insights
    if err >= 0.10:
        insights.append("High failure rate detected. Try smaller changes and more frequent testing.")
    elif err >= 0.05:
        insights.append("Moderate failure rate. Consider adding checkpoints (tests/lint) before committing.")
    else:
        insights.append("Reliability looks stable. Keep changes incremental to maintain quality.")

    # Performance / latency insights
    if p95 >= 600:
        insights.append("P95 duration is high. Break tasks into smaller steps to reduce long-tail delays.")
    elif avg >= 300:
        insights.append("Average task time is trending high. Try timeboxing and smaller deliverables.")

    # Process insights
    if write > 0 and commit == 0:
        insights.append("You’re writing code but not committing. Try committing small increments for better traceability.")
    if bugfix > commit and bugfix >= 3:
        insights.append("Many bug-fixes compared to commits. Consider adding tests to catch regressions earlier.")
    if deadline >= 1:
        insights.append("Deadline misses observed. Reduce scope per iteration or plan buffers for unknowns.")

    # Balance insight
    if commit >= 5 and bugfix == 0 and err < 0.03:
        insights.append("Healthy pace with low failures. Good balance of speed and stability.")

    return insights


def compute_scores(summary: Dict) -> Dict:
    """
    Simple scoring model (0–100). Transparent + explainable for Phase 1.
    """
    actions = int(summary.get("actions", 0))
    err = float(summary.get("error_rate", 0.0))
    avg = float(summary.get("avg_duration_ms", 0.0))
    p95 = float(summary.get("p95_duration_ms", 0.0))
    by_action = summary.get("by_action", {}) or {}

    commit = int(by_action.get("commit_code", 0))
    deadline = int(by_action.get("miss_deadline", 0))
    bugfix = int(by_action.get("fix_bug", 0))

    # Productivity: more actions + commits help; very slow tasks hurt
    prod = 50.0
    prod += min(actions, 60) * 0.6          # up to +36
    prod += min(commit, 20) * 1.0           # up to +20
    prod -= min(avg, 800) / 20.0            # up to -40
    prod -= deadline * 8.0                  # penalty
    prod = max(0.0, min(100.0, prod))

    # Reliability: low error rate helps; deadline misses + too many bugfixes hurt; high p95 hurts
    rel = 80.0
    rel -= err * 200.0                      # err 0.10 => -20
    rel -= min(p95, 1200) / 60.0            # up to -20
    rel -= deadline * 10.0
    rel -= min(bugfix, 20) * 1.0
    rel = max(0.0, min(100.0, rel))

    return {
        "productivity_score": round(prod, 1),
        "reliability_score": round(rel, 1),
    }
