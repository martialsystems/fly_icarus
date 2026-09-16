# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

import json
from pathlib import Path

from fly_icarus.claims import scan_text

REPO = Path(__file__).resolve().parents[1]
LOCK = REPO / "logs" / "p1_frozen_s1.json"
QUESTION = (
    "Does a live male P1 network (DA1 / ppk23 / motion still feeding it) "
    "treat a frozen grounded Icarus-from-male as a female?"
)


def test_readme_question_first() -> None:
    text = (REPO / "README.md").read_text(encoding="utf-8")
    assert text.startswith("# fly_icarus\n")
    body = text.split("\n", 1)[1].lstrip()
    assert body.startswith(QUESTION)
    assert "139,255" in text
    assert "166,691" in text
    assert "What it is not" not in text
    assert "—" not in text
    assert scan_text(text) == []
    assert ".venv/bin/python -m pytest" in text
    assert "icarusforge/" in text
    assert "AGENTS.md" in text
    assert "https://gist.github.com/martialsystems/12835f747d6360781f3cc7f91f243178" in text
    assert "published-sign" in text.lower() or "published sign" in text.lower()
    assert "1,000-fly box would be a physics toy" in text or "physics toy" in text
    desc = (REPO / "description.txt").read_text(encoding="utf-8")
    assert "Icarus-from-male" in desc
    assert "—" not in desc
    assert scan_text(desc) == []


def test_lock_numbers_in_readme() -> None:
    assert LOCK.is_file(), "run seed-1 lock before claim-done"
    data = json.loads(LOCK.read_text(encoding="utf-8"))
    text = (REPO / "README.md").read_text(encoding="utf-8")
    assert data["question"] == QUESTION
    assert data["gate"]["passed"] is True
    assert data["n_agents"] == 2
    assert data["parent_female_n"] == 139255
    assert data["parent_male_n"] == 166691
    rows = {int(r["condition"]): r for r in data["conditions"]}
    for c in (1, 2, 3, 4, 5):
        p1 = str(rows[c]["p1_mean"])
        assert p1 in text, f"missing P1 {p1} for condition {c}"
    assert "LOCK" not in text
    assert "d31 = 0.0" in text
    assert str(data["gate"]["d32"]) in text
