# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

import json
from pathlib import Path

from fly_icarus.assay import AssayConfig, make_object, make_subject, run_assay, run_condition
from fly_icarus.physics import step_bodies
from fly_icarus.subject import P1_TERM_CELLS, SubjectNet
import numpy as np

REPO = Path(__file__).resolve().parents[1]
MUSEUM = REPO / "logs" / "p1_frozen_s1.json"


def test_frozen_object_does_not_move() -> None:
    rng = np.random.default_rng(0)
    cfg = AssayConfig(seed=0, steps=40)
    obj = make_object("3")
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
    female = run_condition("1", cfg, rng)
    rng = np.random.default_rng(1)
    male = run_condition("2", cfg, rng)
    assert female["p1_mean"] > male["p1_mean"]
    assert female["song_frac"] > male["song_frac"]
    assert female["orient_frac"] > male["orient_frac"]
    assert male["song_bouts"] == 0 or male["song_frac"] < 0.05


def test_default_conditions_include_3b_and_6() -> None:
    result = run_assay(AssayConfig(seed=1, steps=500))
    rows = {str(r["condition"]): r for r in result["conditions"]}
    assert set(rows) == {"1", "2", "3", "3b", "4", "5", "6"}
    assert result["n_agents"] == 2
    assert result["n_live_w"] == 1
    assert result["gate"]["passed"] is True
    assert rows["3"]["p1_mean"] > rows["2"]["p1_mean"]
    assert rows["3"]["object"]["wiring_sex"] == 1
    assert rows["3"]["object"]["frozen"] is True
    assert rows["3b"]["object"]["odor"] == "male"
    assert rows["3b"]["object"]["abdomen"] == "female"
    assert rows["3b"]["object"]["wings"] is False
    assert rows["6"]["object"]["wiring_sex"] == 0
    assert rows["6"]["object"]["odor"] == "hd"
    assert result["tag_leak"]["matched"] is True
    for name in P1_TERM_CELLS:
        assert name in rows["3"]["p1_terms"]
        assert name in result["p1_term_weights"]
    assert rows["1"]["p1_terms"]["ORN_HD"] > 0
    assert rows["2"]["p1_terms"]["DA1"] < 0


def test_ablations_and_3b() -> None:
    result = run_assay(AssayConfig(seed=1, steps=500))
    rows = {str(r["condition"]): r for r in result["conditions"]}
    assert rows["4"]["object"]["odor"] == "none"
    assert rows["5"]["object"]["abdomen"] == "male"
    assert rows["3"]["object"]["odor"] == "hd"
    assert rows["3"]["object"]["abdomen"] == "female"
    assert rows["3b"]["object"]["odor"] == "male"
    assert result["control_3b"]["present"] is True
    assert result["control_3b"]["driver"] in {
        "odor_rewrite",
        "shape_overrules_cva",
        "mixed",
    }


def test_terms_come_from_W() -> None:
    net = SubjectNet.fresh()
    w = net.p1_term_weights()
    assert w["ORN_HD"] == 1.2
    assert w["DA1"] == -1.8
    assert w["P1"] == 0.35
    net.r[:] = 0.0
    net.r[0] = 1.0
    terms = net.p1_terms()
    assert terms["ORN_HD"] == 1.2
    assert terms["DA1"] == 0.0


def test_museum_schema_gate_not_overwritten() -> None:
    data = json.loads(MUSEUM.read_text(encoding="utf-8"))
    assert data["schema"] == "fly_icarus.p1_frozen.v1"
    rows = {int(r["condition"]): r for r in data["conditions"]}
    assert set(rows) == {1, 2, 3, 4, 5}
    assert rows[3]["p1_mean"] == 0.9824
    assert rows[1]["p1_mean"] == 0.9824
    assert "3b" not in {str(r["condition"]) for r in data["conditions"]}
