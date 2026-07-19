import json
from pathlib import Path
from typing import Literal

ReviewStatus = Literal["pending", "confirmed_anomaly", "known_artifact"]

def load_review_state(path: Path) -> dict[str, dict]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}

def save_review_decision(path: Path, verse_ref: str, status: ReviewStatus, note: str = "") -> None:
    state = load_review_state(path)
    state[verse_ref] = {"status": status, "note": note}
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
