# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

import json
from pathlib import Path

from fly_icarus.claims import scan_text

REPO = Path(__file__).resolve().parents[1]
LOCK = REPO / "logs" / "p1_frozen_s1.json"
TERMS = REPO / "logs" / "p1_terms_s1.json"
QUESTION = (
    "Does a live male P1 network (DA1 / ppk23 / motion still feeding it) "
    "treat a frozen grounded Icarus-from-male as a female?"
)
ALLOWED = (
    "In this 11-cell published-sign slice, rewriting odor to 7,11-HD with cVA off "
    "is necessary and sufficient for the 3≈1 gate. Icarus morphology, pinned "
    "contact, and feminized cuticle are not."
)


def test_readme_question_first() -> None:
    text = (REPO / "README.md").read_text(encoding="utf-8")
    assert text.startswith("# fly_icarus\n")
    body = text.split("\n", 1)[1].lstrip()
    assert body.startswith(QUESTION)
    rest = body[len(QUESTION) :].lstrip()
    assert rest.startswith(ALLOWED)
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
    assert "schema gate" in text.lower() or "@1244f09" in text
    assert "@1244f09" in text
    assert "odor_rewrite" in text
    assert "p1_terms_s1.json" in text
    assert "p1_contact_s1.json" in text
    assert "saturating" in text.lower()
    assert "necessary and sufficient" in text
    desc = (REPO / "description.txt").read_text(encoding="utf-8")
    assert "3≈1" in desc or "3≈1" in text
    assert "Unfreeze stubbed" in desc or "stay stubbed" in text
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
    assert TERMS.is_file(), "run p1_terms_s1 lock"
    terms = json.loads(TERMS.read_text(encoding="utf-8"))
    assert terms["schema"] == "fly_icarus.p1_frozen.v2"
    assert terms["control_3b"]["driver"] == "odor_rewrite"
    assert terms["tag_leak"]["matched"] is True
    trows = {str(r["condition"]): r for r in terms["conditions"]}
    assert str(trows["3b"]["p1_mean"]) in text
    assert str(trows["6"]["p1_mean"]) in text
    for name in ("ORN_HD", "DA1", "ppk23_f", "ppk23_m", "LC10a"):
        assert str(trows["3"]["p1_terms"][name]) in text
    assert "Do not overwrite" in text
    contact = REPO / "logs" / "p1_contact_s1.json"
    assert contact.is_file(), "run p1_contact_s1 lock"
    cdata = json.loads(contact.read_text(encoding="utf-8"))
    assert cdata["schema"] == "fly_icarus.p1_frozen.v3"
    assert cdata["control_3c"]["more_negative_than_3b"] is True
    assert cdata["control_3d"]["driver"] == "da1_wins_full_excitatory_bundle"
    assert cdata["copresent"]["both_ligands"] is True
    crows = {str(r["condition"]): r for r in cdata["conditions"]}
    assert str(crows["3c"]["p1_mean"]) in text
    assert str(crows["3d"]["p1_mean"]) in text
    assert str(crows["copresent"]["p1_mean"]) in text
    dose = REPO / "logs" / "p1_da1_dose_s1.json"
    assert dose.is_file(), "run p1_da1_dose_s1 lock"
    ddata = json.loads(dose.read_text(encoding="utf-8"))
    assert ddata["schema"] == "fly_icarus.p1_da1_dose.v1"
    assert ddata["critical_weight"]["crossed"] is True
    assert str(ddata["critical_weight"]["w_p1_da1"]) in text
    assert str(ddata["p1_at_default"]) in text
