# Copyright (c) 2026 Martial Systems LLC
"""Five-condition two-agent frozen-object assay. Same subject, object flags change."""

from __future__ import annotations

import json
from dataclasses import dataclass

import numpy as np

from fly_icarus.icarus import Body, icarus_from_female, icarus_from_male, intact_female, intact_male
from fly_icarus.metrics import Acc, gate_looks_like_female
from fly_icarus.odor import contact_chc, dist, plume, visual_token
from fly_icarus.physics import DT, step_bodies
from fly_icarus.subject import (
    I_LC10,
    I_ORN_CVA,
    I_ORN_HD,
    I_PPK_F,
    I_PPK_M,
    CELLS,
    SubjectNet,
)
from icarusforge.gate import require_assay_order, require_engine

CONDITION_NAMES = {
    1: "flying_female",
    2: "flying_male",
    3: "icarus_from_male",
    4: "icarus_from_male_body_only",
    5: "icarus_from_male_odor_only",
    6: "icarus_from_female",
}

CONDITION_ROLES = {
    1: "positive control",
    2: "negative control",
    3: "the rule",
    4: "morphology without 7,11-HD",
    5: "7,11-HD without the fat wingless female shape",
    6: "same body+odor, female tag",
}


@dataclass
class AssayConfig:
    seed: int = 1
    steps: int = 2000
    conditions: tuple[int, ...] = (1, 2, 3, 4, 5)
    start_x: float = 6.0
    record_frames: bool = False
    frame_stride: int = 10


def make_object(condition: int) -> Body:
    if condition == 1:
        return intact_female(frozen=True)
    if condition == 2:
        return intact_male(frozen=True)
    if condition == 3:
        return icarus_from_male(odor=True, female_body=True)
    if condition == 4:
        return icarus_from_male(odor=False, female_body=True)
    if condition == 5:
        return icarus_from_male(odor=True, female_body=False)
    if condition == 6:
        return icarus_from_female(odor=True, female_body=True)
    raise ValueError(f"unknown condition {condition}")


def make_subject(cfg: AssayConfig, rng: np.random.Generator) -> Body:
    jitter = float(rng.normal(0.0, 0.15))
    heading = float(rng.uniform(-0.2, 0.2))
    return Body(
        x=cfg.start_x,
        y=jitter,
        heading=heading,
        wiring_sex=1,
        wings=True,
        mass=1.0,
        abdomen="male",
        odor="male",
        frozen=False,
        icarus=False,
    )


def sensory_current(subject: Body, obj: Body) -> np.ndarray:
    d = dist(subject, obj)
    hd, cva = plume(obj, d)
    vis = visual_token(obj, d)
    pk_f, pk_m = contact_chc(obj, d)
    i = np.zeros(len(CELLS), dtype=np.float64)
    i[I_ORN_HD] = hd
    i[I_ORN_CVA] = cva
    i[I_PPK_F] = pk_f
    i[I_PPK_M] = pk_m
    i[I_LC10] = vis
    return i


def run_condition(condition: int, cfg: AssayConfig, rng: np.random.Generator) -> dict:
    obj = make_object(condition)
    if obj.frozen is False:
        raise RuntimeError("object must be frozen in experiment 1")
    if condition in (3, 4, 5) and obj.wiring_sex != 1:
        raise RuntimeError("Icarus-from-male swapped wiring_sex")
    subject = make_subject(cfg, rng)
    net = SubjectNet.fresh()
    acc = Acc()
    frames: list[dict] = []
    for t in range(cfg.steps):
        d = dist(subject, obj)
        net.step(sensory_current(subject, obj))
        st = step_bodies(subject, obj, net, d)
        acc.tick(
            p1=float(st["p1"]),
            aligned=bool(st["aligned"]),
            singing=bool(st["singing"]),
            trying=bool(st["trying"]),
        )
        if cfg.record_frames and t % cfg.frame_stride == 0:
            frames.append(
                {
                    "t": round(t * DT, 3),
                    "sx": round(subject.x, 3),
                    "sy": round(subject.y, 3),
                    "sh": round(subject.heading, 3),
                    "p1": round(float(st["p1"]), 3),
                    "song": int(bool(st["singing"])),
                }
            )
    out = {
        "condition": condition,
        "name": CONDITION_NAMES[condition],
        "role": CONDITION_ROLES[condition],
        "object": {
            "wiring_sex": int(obj.wiring_sex),
            "wings": bool(obj.wings),
            "abdomen": obj.abdomen,
            "odor": obj.odor,
            "icarus": bool(obj.icarus),
            "frozen": bool(obj.frozen),
            "mass": obj.mass,
        },
        **acc.summary(),
    }
    if frames:
        out["frames"] = frames
    return out


def run_assay(cfg: AssayConfig) -> dict:
    require_assay_order(n=2, unfreeze=False, female_brain_icarus=False, exp1_passed=False)
    require_engine(n_live_w=1, unique_w_per_fly=False)
    rng = np.random.default_rng(cfg.seed)
    rows: dict[int, dict] = {}
    ordered = []
    for c in cfg.conditions:
        row = run_condition(c, cfg, rng)
        rows[c] = row
        ordered.append(row)
    gate = gate_looks_like_female(rows) if {1, 2, 3} <= set(rows) else {"passed": False, "rule": "missing 1-3"}
    return {
        "schema": "fly_icarus.p1_frozen.v1",
        "question": (
            "Does a live male P1 network (DA1 / ppk23 / motion still feeding it) "
            "treat a frozen grounded Icarus-from-male as a female?"
        ),
        "n_agents": 2,
        "n_live_w": 1,
        "seed": cfg.seed,
        "steps": cfg.steps,
        "dt": DT,
        "engine": "published_sign_schema",
        "parent_female_n": 139255,
        "parent_male_n": 166691,
        "slice_n": len(CELLS),
        "conditions": ordered,
        "gate": gate,
    }


def write_run(result: dict, path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
