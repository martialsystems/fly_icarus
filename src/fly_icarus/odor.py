# Copyright (c) 2026 Martial Systems LLC
"""Distance kernels for 7,11-HD, cVA / 7-T, contact CHC, and a size/shape visual token."""

from __future__ import annotations

import math

from fly_icarus.icarus import (
    ABDOMEN_FEMALE,
    ODOR_HD,
    ODOR_MALE,
    Body,
)

ODOR_LEN = 4.0
VIS_LEN = 8.0
TAP_RADIUS = 1.2
COP_RADIUS = 0.85
SONG_RADIUS = 3.5


def dist(a: Body, b: Body) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)


def bearing(subject: Body, obj: Body) -> float:
    return math.atan2(obj.y - subject.y, obj.x - subject.x)


def wrap_angle(a: float) -> float:
    while a > math.pi:
        a -= 2.0 * math.pi
    while a < -math.pi:
        a += 2.0 * math.pi
    return a


def heading_error(subject: Body, obj: Body) -> float:
    return wrap_angle(bearing(subject, obj) - subject.heading)


def plume(obj: Body, d: float) -> tuple[float, float]:
    """Return (hd, cva) at distance d from the object."""
    fall = math.exp(-d / ODOR_LEN)
    if obj.odor == ODOR_HD:
        return fall, 0.0
    if obj.odor == ODOR_MALE:
        return 0.0, fall
    return 0.0, 0.0


def visual_token(obj: Body, d: float) -> float:
    """LC10a here is a frozen size/shape proxy, not a T4/T5 motion extract."""
    prox = math.exp(-d / VIS_LEN)
    scale = 0.85 if obj.abdomen == ABDOMEN_FEMALE else 0.35
    return scale * prox


def contact_chc(obj: Body, d: float) -> tuple[float, float]:
    """ppk23 female-CHC vs male-CHC. HD odor includes the female CHC tag."""
    if d > TAP_RADIUS:
        return 0.0, 0.0
    if obj.odor == ODOR_HD:
        return 1.0, 0.0
    if obj.odor == ODOR_MALE:
        return 0.0, 1.0
    return 0.0, 0.0
