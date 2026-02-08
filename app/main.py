import random
import time
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

from app.store import MetricsStore
from app.insight import generate_insights, compute_scores

app = FastAPI(title="AI Dev Productivity & Reliability Platform (Phase 1)")
store = MetricsStore(maxlen=8000)

BASE_DIR = Path(__file__).resolve().parent.parent

# Action profiles: (base_ms, jitter_ms, fail_rate)
ACTION_PROFILES = {
    "write_code": (120, 220, 0.03),
    "commit_code": (80, 140, 0.02),
    "fix_bug": (180, 320, 0.07),
    "miss_deadline": (250, 450, 0.15),
}

@app.get("/", response_class=HTMLResponse)
def home():
    return (BASE_DIR / "web" / "index.html").read_text(encoding="utf-8")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/action")
def do_action(action: str = "write_code"):
    if action not in ACTION_PROFILES:
        return JSONResponse(status_code=400, content={"ok": False, "error": "unknown_action"})

    base, jitter, fail_rate = ACTION_PROFILES[action]
    start = time.perf_counter()

    # Simulate work
    sleep_ms = base + random.randint(0, jitter)
    time.sleep(sleep_ms / 1000.0)

    ok = random.random() >= fail_rate
    duration_ms = (time.perf_counter() - start) * 1000.0

    store.add(action=action, ok=ok, duration_ms=duration_ms)

    return {"ok": ok, "action": action, "duration_ms": round(duration_ms, 2)}


@app.get("/api/dashboard")
def dashboard(window_sec: int = 300):
    summary = store.summary(window_sec=window_sec)
    scores = compute_scores(summary)
    insights = generate_insights(summary)

    return {
        "summary": summary,
        "scores": scores,
        "insights": insights,
    }
