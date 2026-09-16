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
    odor: bool = True,
    female_body: bool = True,
) -> Body:
    """House rule. Wiring sex is copied, never rewritten."""
    wiring = int(body.wiring_sex)
    out = replace(
        body,
        icarus=True,
        wings=False,
        mass=ICARUS_MASS,
        abdomen=ABDOMEN_FEMALE if female_body else ABDOMEN_MALE,
        odor=ODOR_HD if odor else ODOR_NONE,
        frozen=True,
        wiring_sex=wiring,
    )
    require_wiring(wiring_changed=out.wiring_sex != wiring)
    return out


def icarus_from_male(*, odor: bool = True, female_body: bool = True) -> Body:
    return apply_icarus(intact_male(), odor=odor, female_body=female_body)


def icarus_from_female(*, odor: bool = True, female_body: bool = True) -> Body:
    return apply_icarus(intact_female(), odor=odor, female_body=female_body)
