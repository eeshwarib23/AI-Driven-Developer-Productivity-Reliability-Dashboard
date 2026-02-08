from collections import deque
from dataclasses import dataclass
from time import time
from typing import Deque, Dict, List


@dataclass
class ActionEvent:
    ts: float
    action: str
    ok: bool
    duration_ms: float


class MetricsStore:
    """
    In-memory event store for last N actions.
    """
    def __init__(self, maxlen: int = 5000):
        self.events: Deque[ActionEvent] = deque(maxlen=maxlen)

    def add(self, action: str, ok: bool, duration_ms: float) -> None:
        self.events.append(ActionEvent(ts=time(), action=action, ok=ok, duration_ms=duration_ms))

    def recent(self, window_sec: int) -> List[ActionEvent]:
        now = time()
        return [e for e in self.events if now - e.ts <= window_sec]

    def summary(self, window_sec: int = 300) -> Dict:
        if window_sec <= 0:
            window_sec = 1

        recent = self.recent(window_sec)
        total = len(recent)
        failures = sum(1 for e in recent if not e.ok)
        avg_ms = (sum(e.duration_ms for e in recent) / total) if total else 0.0

        durations = sorted(e.duration_ms for e in recent)
        p95 = durations[int(0.95 * (total - 1))] if total else 0.0

        # Action counts
        by_action: Dict[str, int] = {}
        for e in recent:
            by_action[e.action] = by_action.get(e.action, 0) + 1

        error_rate = (failures / total) if total else 0.0
        throughput_rpm = (total / window_sec) * 60.0 if window_sec else 0.0

        return {
            "window_sec": window_sec,
            "actions": total,
            "failures": failures,
            "error_rate": error_rate,
            "avg_duration_ms": avg_ms,
            "p95_duration_ms": p95,
            "throughput_rpm": throughput_rpm,
            "by_action": by_action,
        }
