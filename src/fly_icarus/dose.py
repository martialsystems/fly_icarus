# Copyright (c) 2026 Martial Systems LLC
"""DA1 dose-response on the 3d pin. Sweep W[P1, DA1] until P1 mean crosses zero."""

from __future__ import annotations

import numpy as np

from fly_icarus.assay import AssayConfig, run_condition, write_run
from fly_icarus.physics import DT
from fly_icarus.subject import I_DA1, load_W
from icarusforge.gate import require_assay_order, require_engine

DEFAULT_W_P1_DA1 = -1.8


def da1_weight_grid() -> np.ndarray:
    """0.0 to -2.4 inclusive, 0.05 steps, default weight on the grid."""
    g = np.round(np.arange(0.0, -2.4001, -0.05), 4)
    if not np.any(np.isclose(g, DEFAULT_W_P1_DA1)):
        g = np.sort(np.concatenate([g, np.array([DEFAULT_W_P1_DA1])]))[::-1]
    return g


def interpolate_zero_crossing(curve: list[dict]) -> dict:
    """curve ordered from W=0 toward more negative. Crossing: p1 >= 0 then p1 < 0."""
    for a, b in zip(curve, curve[1:]):
        p_hi = float(a["p1_mean"])
        p_lo = float(b["p1_mean"])
        w_hi = float(a["w_p1_da1"])
        w_lo = float(b["w_p1_da1"])
        if p_hi >= 0.0 and p_lo < 0.0:
            if p_hi == p_lo:
                w = w_hi
            else:
                t = p_hi / (p_hi - p_lo)
                w = w_hi + t * (w_lo - w_hi)
            return {
                "crossed": True,
                "w_p1_da1": round(float(w), 4),
                "bracket_w": [w_hi, w_lo],
                "bracket_p1": [p_hi, p_lo],
            }
    return {
        "crossed": False,
        "w_p1_da1": None,
        "bracket_w": None,
        "bracket_p1": None,
    }


def run_da1_dose(cfg: AssayConfig, weights: np.ndarray | None = None) -> dict:
    require_assay_order(n=2, unfreeze=False, female_brain_icarus=False, exp1_passed=False)
    require_engine(n_live_w=1, unique_w_per_fly=False)
    w0 = float(load_W()[6, I_DA1])
    if abs(w0 - DEFAULT_W_P1_DA1) > 1e-9:
        raise RuntimeError(f"template W[P1,DA1] drifted: {w0}")
    grid = da1_weight_grid() if weights is None else np.asarray(weights, dtype=np.float64)
    curve: list[dict] = []
    for w in grid:
        rng = np.random.default_rng(cfg.seed)
        row = run_condition("3d", cfg, rng, da1_weight=float(w))
        terms = row.get("p1_terms") or {}
        curve.append(
            {
                "w_p1_da1": float(w),
                "p1_mean": row["p1_mean"],
                "song_frac": row["song_frac"],
                "DA1_term": terms.get("DA1"),
                "ppk23_f": terms.get("ppk23_f"),
                "LC10a": terms.get("LC10a"),
                "P1_latch": terms.get("P1"),
            }
        )
    crossing = interpolate_zero_crossing(curve)
    at_default = next((r for r in curve if abs(r["w_p1_da1"] - DEFAULT_W_P1_DA1) < 1e-9), None)
    return {
        "schema": "fly_icarus.p1_da1_dose.v1",
        "condition": "3d",
        "pin": True,
        "question": "On the 3d pin, at what W[P1, DA1] does mean P1 cross zero?",
        "honesty": (
            "Published-sign schema. Critical weight is a property of these "
            "weights on the 3d pin, not a MaleCNS hop-count."
        ),
        "n_agents": 2,
        "seed": cfg.seed,
        "steps": cfg.steps,
        "dt": DT,
        "default_w_p1_da1": DEFAULT_W_P1_DA1,
        "p1_at_default": None if at_default is None else at_default["p1_mean"],
        "critical_weight": crossing,
        "curve": curve,
    }
