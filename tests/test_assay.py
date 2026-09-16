# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

from fly_icarus.assay import AssayConfig, make_object, make_subject, run_assay, run_condition
from fly_icarus.physics import step_bodies
from fly_icarus.subject import SubjectNet
import numpy as np


def test_frozen_object_does_not_move() -> None:
    rng = np.random.default_rng(0)
    cfg = AssayConfig(seed=0, steps=40)
    obj = make_object(3)
    x0, y0 = obj.x, obj.y
    subject = make_subject(cfg, rng)
    net = SubjectNet.fresh()
    for _ in range(40):
        d = ((subject.x - obj.x) ** 2 + (subject.y - obj.y) ** 2) ** 0.5
        net.step(np.zeros(11))
        step_bodies(subject, obj, net, d)
    assert obj.x == x0 and obj.y == y0


def test_female_lights_p1_male_does_not() -> None:
    rng = np.random.default_rng(1)
    cfg = AssayConfig(seed=1, steps=400)
    female = run_condition(1, cfg, rng)
    rng = np.random.default_rng(1)
    male = run_condition(2, cfg, rng)
    assert female["p1_mean"] > male["p1_mean"]
    assert female["song_frac"] > male["song_frac"]
    assert female["orient_frac"] > male["orient_frac"]
    assert male["song_bouts"] == 0 or male["song_frac"] < 0.05


def test_five_conditions_gate() -> None:
    result = run_assay(AssayConfig(seed=1, steps=500))
    rows = {int(r["condition"]): r for r in result["conditions"]}
    assert set(rows) == {1, 2, 3, 4, 5}
    assert result["n_agents"] == 2
    assert result["n_live_w"] == 1
    assert result["gate"]["passed"] is True
    assert rows[3]["p1_mean"] > rows[2]["p1_mean"]
    assert rows[1]["copulation_attempts"] >= 0
    assert rows[3]["object"]["wiring_sex"] == 1
    assert rows[3]["object"]["frozen"] is True


def test_ablations_are_not_the_full_rule() -> None:
    result = run_assay(AssayConfig(seed=1, steps=500))
    rows = {int(r["condition"]): r for r in result["conditions"]}
    assert rows[4]["object"]["odor"] == "none"
    assert rows[5]["object"]["abdomen"] == "male"
    assert rows[3]["object"]["odor"] == "hd"
    assert rows[3]["object"]["abdomen"] == "female"
