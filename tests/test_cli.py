# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

from fly_icarus.cli import main


def test_n_1000_refused_before_lock() -> None:
    assert main(["assay", "--n", "1000", "--steps", "10"]) == 2


def test_unfreeze_refused_before_lock() -> None:
    assert main(["assay", "--unfreeze", "--steps", "10"]) == 2


def test_female_brain_refused_before_lock() -> None:
    assert main(["assay", "--female-brain-icarus", "--steps", "10"]) == 2


def test_dose_unfreeze_stays_stubbed() -> None:
    assert main(["da1-dose", "--unfreeze", "--steps", "10"]) == 2
