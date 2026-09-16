# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

from fly_icarus.assay import make_object
from fly_icarus.icarus import (
    ABDOMEN_FEMALE,
    ABDOMEN_MALE,
    FEMALE,
    MALE,
    ODOR_HD,
    ODOR_MALE,
    ODOR_NONE,
    apply_icarus,
    intact_female,
    intact_male,
)
from icarusforge.gate import LawBlockedError, require_wiring
import pytest


def test_icarus_from_male_keeps_wiring() -> None:
    src = intact_male()
    out = apply_icarus(src, odor=True, female_body=True)
    assert src.wiring_sex == MALE
    assert out.wiring_sex == MALE
    assert out.wings is False
    assert out.abdomen == ABDOMEN_FEMALE
    assert out.odor == ODOR_HD
    assert out.icarus is True
    assert out.frozen is True
    assert out.mass > src.mass


def test_icarus_from_female_keeps_wiring() -> None:
    src = intact_female()
    out = apply_icarus(src, odor=True, female_body=True)
    assert out.wiring_sex == FEMALE
    assert out.wings is False
    assert out.odor == ODOR_HD


def test_body_only_and_odor_only() -> None:
    body = apply_icarus(intact_male(), odor=False, female_body=True)
    assert body.odor == ODOR_NONE
    assert body.abdomen == ABDOMEN_FEMALE
    odor = apply_icarus(intact_male(), odor=True, female_body=False)
    assert odor.odor == ODOR_HD
    assert odor.abdomen == ABDOMEN_MALE
    assert odor.wings is False


def test_require_wiring_blocks_swap() -> None:
    require_wiring(wiring_changed=False)
    with pytest.raises(LawBlockedError):
        require_wiring(wiring_changed=True)


def test_condition_objects() -> None:
    f = make_object(1)
    m = make_object(2)
    i = make_object(3)
    assert f.wiring_sex == FEMALE and f.odor == ODOR_HD and f.wings
    assert m.wiring_sex == MALE and m.odor == ODOR_MALE and m.wings
    assert i.wiring_sex == MALE and i.odor == ODOR_HD and not i.wings
    assert i.frozen and m.frozen and f.frozen
