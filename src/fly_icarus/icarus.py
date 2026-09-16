# Copyright (c) 2026 Martial Systems LLC
"""Icarus is a morphology and odor flag. It does not swap wiring_sex."""

from __future__ import annotations

from dataclasses import dataclass, replace

from icarusforge.gate import require_wiring

FEMALE = 0
MALE = 1

ODOR_NONE = "none"
ODOR_HD = "hd"
ODOR_MALE = "male"

ABDOMEN_MALE = "male"
ABDOMEN_FEMALE = "female"

MALE_MASS = 1.0
FEMALE_MASS = 1.35
ICARUS_MASS = 1.8


@dataclass
class Body:
    x: float
    y: float
    heading: float
    wiring_sex: int
    wings: bool
    mass: float
    abdomen: str
    odor: str
    frozen: bool
    icarus: bool


def intact_female(*, x: float = 0.0, y: float = 0.0, frozen: bool = True) -> Body:
    return Body(
        x=x,
        y=y,
        heading=0.0,
        wiring_sex=FEMALE,
        wings=True,
        mass=FEMALE_MASS,
        abdomen=ABDOMEN_FEMALE,
        odor=ODOR_HD,
        frozen=frozen,
        icarus=False,
    )


def intact_male(*, x: float = 0.0, y: float = 0.0, frozen: bool = True) -> Body:
    return Body(
        x=x,
        y=y,
        heading=0.0,
        wiring_sex=MALE,
        wings=True,
        mass=MALE_MASS,
        abdomen=ABDOMEN_MALE,
        odor=ODOR_MALE,
        frozen=frozen,
        icarus=False,
    )


def apply_icarus(
    body: Body,
    *,
    odor: str = ODOR_HD,
    female_body: bool = True,
) -> Body:
    """House rule. Wiring sex is copied, never rewritten.

    odor is a source tag: hd, male (cVA / 7-T), or none. The default Icarus
    rewrite writes HD. Condition 3b keeps male odor on a fat wingless body.
    """
    if odor not in (ODOR_HD, ODOR_MALE, ODOR_NONE):
        raise ValueError(f"unknown odor {odor!r}")
    wiring = int(body.wiring_sex)
    out = replace(
        body,
        icarus=True,
        wings=False,
        mass=ICARUS_MASS,
        abdomen=ABDOMEN_FEMALE if female_body else ABDOMEN_MALE,
        odor=odor,
        frozen=True,
        wiring_sex=wiring,
    )
    require_wiring(wiring_changed=out.wiring_sex != wiring)
    return out


def icarus_from_male(*, odor: str = ODOR_HD, female_body: bool = True) -> Body:
    return apply_icarus(intact_male(), odor=odor, female_body=female_body)


def icarus_from_female(*, odor: str = ODOR_HD, female_body: bool = True) -> Body:
    return apply_icarus(intact_female(), odor=odor, female_body=female_body)
