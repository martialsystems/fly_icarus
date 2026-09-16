# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

import pytest

from icarusforge.gate import (
    FLYWIRE_N,
    MALECNS_N,
    LawBlockedError,
    require_assay_order,
    require_claims,
    require_engine,
    require_templates,
    require_wiring,
    scan_text_flags,
)
from icarusforge.product_laws import laws


def test_laws_catalog_has_five() -> None:
    ids = [row["id"] for row in laws()]
    assert ids == [
        "icarus.claim_bans",
        "icarus.wiring_frozen",
        "icarus.engine_shared",
        "icarus.template_identity",
        "icarus.assay_order",
    ]


def test_claims_refuse() -> None:
    require_claims()
    with pytest.raises(LawBlockedError):
        require_claims(unique_brains=True)
    with pytest.raises(LawBlockedError):
        require_claims(population_answers_circuit=True)


def test_engine_and_templates() -> None:
    require_engine(n_live_w=1)
    with pytest.raises(LawBlockedError):
        require_engine(n_live_w=3)
    require_templates(female_n=FLYWIRE_N, male_n=MALECNS_N, slice_n=11)
    with pytest.raises(LawBlockedError):
        require_templates(female_n=FLYWIRE_N, male_n=MALECNS_N, slice_n=11, hop_count_extract=True)


def test_assay_order() -> None:
    require_assay_order(n=2, exp1_passed=False)
    with pytest.raises(LawBlockedError):
        require_assay_order(n=1000, exp1_passed=False)
    with pytest.raises(LawBlockedError):
        require_assay_order(n=2, unfreeze=True, exp1_passed=False)
    require_assay_order(n=2, unfreeze=True, exp1_passed=True)
    require_wiring(wiring_changed=False)


def test_scan_readme_current_is_clean() -> None:
    from pathlib import Path

    text = Path(__file__).resolve().parents[1].joinpath("README.md").read_text(encoding="utf-8")
    flags = scan_text_flags(text)
    assert not any(flags.values()), flags
