# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from fly_icarus.claims import scan_text

REPO = Path(__file__).resolve().parents[1]
QUESTION = (
    "Does a live male P1 network (DA1 / ppk23 / motion still feeding it) "
    "treat a frozen grounded Icarus-from-male as a female?"
)


def test_methods_card() -> None:
    text = (REPO / "METHODS.yaml").read_text(encoding="utf-8")
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    assert text.startswith("question: " + QUESTION)
    assert "pre_specified: false" in text
    assert "science_lock: 2cf5fd6" in text
    assert "object: constrained toy dynamics" in text
    assert "named types only" in text
    assert "not LIF" in text
    assert "tanh" in text
    assert "What it is not" not in text
    assert "—" not in text
    assert scan_text(text) == []
    assert "METHODS.yaml" in readme
    assert "Prior constraints" in readme
    assert "assumed published sign" in readme
    cite = (REPO / "CITATION.cff").read_text(encoding="utf-8")
    assert "cff-version: 1.2.0" in cite
    assert "10.5281" not in cite
    third = (REPO / "THIRD_PARTY.md").read_text(encoding="utf-8")
    assert "10.1016/j.cell.2026.08.015" in third
    assert "166,691" in third
    assert "166,700" not in third
    assert scan_text(third) == []
    repro = (REPO / "REPRODUCE.md").read_text(encoding="utf-8")
    assert "117febfb78085c857f17c9bcc206113689c9a4c4b6dd5f081aa8befedfd897f4" in repro
    assert "—" not in repro


def test_reproduce_lock_hashes() -> None:
    python = REPO / ".venv" / "bin" / "python"
    exe = str(python) if python.is_file() else sys.executable
    proc = subprocess.run(
        [exe, str(REPO / "scripts" / "reproduce_lock.py")],
        cwd=REPO,
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout
    assert "ok p1_contact_s1.json" in proc.stdout
    assert "ok p1_da1_dose_s1.json" in proc.stdout
