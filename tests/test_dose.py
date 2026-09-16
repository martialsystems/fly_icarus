# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from fly_icarus.assay import AssayConfig
from fly_icarus.dose import (
    DEFAULT_W_P1_DA1,
    interpolate_zero_crossing,
    run_da1_dose,
)
from fly_icarus.subject import I_DA1, I_P1, SubjectNet, load_W

REPO = Path(__file__).resolve().parents[1]
CONTACT = REPO / "logs" / "p1_contact_s1.json"


def test_with_p1_da1_weight_does_not_mutate_template() -> None:
    w0 = float(load_W()[I_P1, I_DA1])
    net = SubjectNet.with_p1_da1_weight(0.0)
    assert net.W[I_P1, I_DA1] == 0.0
    assert float(load_W()[I_P1, I_DA1]) == w0
    assert w0 == DEFAULT_W_P1_DA1


def test_interpolate_zero_crossing() -> None:
    curve = [
        {"w_p1_da1": 0.0, "p1_mean": 0.4},
        {"w_p1_da1": -1.0, "p1_mean": 0.1},
        {"w_p1_da1": -1.2, "p1_mean": -0.1},
    ]
    hit = interpolate_zero_crossing(curve)
    assert hit["crossed"] is True
    assert hit["w_p1_da1"] == -1.1


def test_da1_dose_crosses_on_3d_pin() -> None:
    grid = np.array([0.0, -0.8, -1.2, -1.8, -2.4])
    result = run_da1_dose(AssayConfig(seed=1, steps=400), weights=grid)
    assert result["condition"] == "3d"
    assert result["critical_weight"]["crossed"] is True
    w_crit = float(result["critical_weight"]["w_p1_da1"])
    assert -1.8 < w_crit < 0.0
    by_w = {round(r["w_p1_da1"], 4): r["p1_mean"] for r in result["curve"]}
    assert by_w[0.0] > 0.0
    assert by_w[-1.8] < 0.0


def test_contact_museum_untouched() -> None:
    data = json.loads(CONTACT.read_text(encoding="utf-8"))
    assert data["schema"] == "fly_icarus.p1_frozen.v3"
    rows = {str(r["condition"]): r for r in data["conditions"]}
    assert rows["3d"]["p1_mean"] == -0.3324


def test_dose_lock_critical_weight() -> None:
    path = REPO / "logs" / "p1_da1_dose_s1.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["critical_weight"]["w_p1_da1"] == -1.5262
    assert data["p1_at_default"] == -0.3324
    assert data["default_w_p1_da1"] == -1.8
