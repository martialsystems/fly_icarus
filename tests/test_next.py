# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

from pathlib import Path

from fly_icarus.claims import scan_text
from fly_icarus.cli import main

REPO = Path(__file__).resolve().parents[1]
QUESTION = (
    "Do MaleCNS-derived signed weights onto P1/pC1 still make HD-on / cVA-off "
    "necessary and sufficient for the 3≈1 gate?"
)
CLOSED = (
    "Does a live male P1 network (DA1 / ppk23 / motion still feeding it) "
    "treat a frozen grounded Icarus-from-male as a female?"
)
CONTACT = REPO / "logs" / "p1_contact_s1.json"


def test_next_lock_file() -> None:
    text = (REPO / "NEXT_SENTENCE.md").read_text(encoding="utf-8")
    assert text.startswith("# Next sentence\n")
    body = text.split("\n", 1)[1].lstrip()
    assert body.startswith(QUESTION)
    assert "1, 2, 3, 3b, 3c, 3d, copresent" in text
    assert "New W" in text
    assert "Do not reopen `logs/p1_contact_s1.json`" in text
    assert "Unfreeze stays a later question" in text
    assert "2cf5fd6" in text
    assert "-1.5262" in text
    assert "stay stubbed" in text
    assert "Do not run this battery on this tree" in text
    assert "What it is not" not in text
    assert "—" not in text
    assert scan_text(text) == []
    assert CLOSED not in text


def test_next_md_does_not_reopen_contact() -> None:
    text = (REPO / "NEXT.md").read_text(encoding="utf-8")
    body = text.split("\n", 1)[1].lstrip()
    assert body.startswith(QUESTION)
    assert "Do not restamp `p1_contact_s1.json`" in text
    assert "2cf5fd6" in text
    assert CONTACT.is_file()


def test_closed_tree_stubs_unflipped() -> None:
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    body = readme.split("\n", 1)[1].lstrip()
    assert body.startswith(CLOSED)
    desc = (REPO / "description.txt").read_text(encoding="utf-8")
    assert "Unfreeze stubbed" in desc
    assert "W_crit=-1.5262" in desc or "W_crit = -1.5262" in desc
    assert main(["assay", "--n", "1000", "--steps", "10"]) == 2
    assert main(["assay", "--unfreeze", "--steps", "10"]) == 2
    assert main(["assay", "--female-brain-icarus", "--steps", "10"]) == 2
    assert main(["da1-dose", "--unfreeze", "--steps", "10"]) == 2
