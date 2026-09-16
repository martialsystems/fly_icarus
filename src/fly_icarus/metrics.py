# Copyright (c) 2026 Martial Systems LLC
"""P1 rate, orientation time, song bouts, copulation attempts."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Acc:
    n: int = 0
    p1_sum: float = 0.0
    orient_ticks: int = 0
    song_ticks: int = 0
    song_bouts: int = 0
    attempts: int = 0
    _song_on: bool = False
    _try_on: bool = False
    p1_series: list[float] = field(default_factory=list)

    def tick(self, *, p1: float, aligned: bool, singing: bool, trying: bool) -> None:
        self.n += 1
        self.p1_sum += float(p1)
        if aligned:
            self.orient_ticks += 1
        if singing:
            self.song_ticks += 1
            if not self._song_on:
                self.song_bouts += 1
            self._song_on = True
        else:
            self._song_on = False
        if trying:
            if not self._try_on:
                self.attempts += 1
            self._try_on = True
        else:
            self._try_on = False
        if len(self.p1_series) < 400 or self.n % 5 == 0:
            self.p1_series.append(round(float(p1), 4))

    def summary(self) -> dict:
        n = max(self.n, 1)
        return {
            "steps": self.n,
            "p1_mean": round(self.p1_sum / n, 4),
            "orient_frac": round(self.orient_ticks / n, 4),
            "song_frac": round(self.song_ticks / n, 4),
            "song_bouts": int(self.song_bouts),
            "copulation_attempts": int(self.attempts),
        }


def gate_looks_like_female(rows: dict[int, dict]) -> dict:
    """Condition 3 with 1, not with 2, on song and orientation."""
    a = rows[1]
    b = rows[2]
    c = rows[3]
    d31 = abs(c["song_frac"] - a["song_frac"]) + abs(c["orient_frac"] - a["orient_frac"])
    d32 = abs(c["song_frac"] - b["song_frac"]) + abs(c["orient_frac"] - b["orient_frac"])
    p1_31 = abs(c["p1_mean"] - a["p1_mean"])
    p1_32 = abs(c["p1_mean"] - b["p1_mean"])
    passed = (
        d31 < d32
        and p1_31 < p1_32
        and c["song_frac"] > b["song_frac"]
        and a["song_frac"] > b["song_frac"]
        and c["p1_mean"] > b["p1_mean"]
        and a["p1_mean"] > 0.2
    )
    return {
        "passed": bool(passed),
        "d31": round(d31, 4),
        "d32": round(d32, 4),
        "p1_d31": round(p1_31, 4),
        "p1_d32": round(p1_32, 4),
        "rule": "condition 3 closer to 1 than to 2 on song, orient, and P1; 1 and 3 above 2 on song and P1",
    }
