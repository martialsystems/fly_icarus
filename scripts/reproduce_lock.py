#!/usr/bin/env python3
# Copyright (c) 2026 Martial Systems LLC
"""Hash-check or rebuild locked fly_icarus logs. Never overwrite the lock files."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOGS = ROOT / "logs"

EXPECTED_SHA256 = {
    "p1_contact_s1.json": "117febfb78085c857f17c9bcc206113689c9a4c4b6dd5f081aa8befedfd897f4",
    "p1_da1_dose_s1.json": "f0fabf87378319bedb5b66c434bb901f167867524b379067713a4603c3d1de57",
}

LOCKED = ("p1_contact_s1.json", "p1_da1_dose_s1.json")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_hashes() -> int:
    failed = 0
    for name, expected in EXPECTED_SHA256.items():
        path = LOGS / name
        if not path.is_file():
            print(f"MISSING {name}", file=sys.stderr)
            failed += 1
            continue
        got = sha256_file(path)
        if got != expected:
            print(f"HASH {name} {got} != {expected}", file=sys.stderr)
            failed += 1
        else:
            print(f"ok {name}")
    return 1 if failed else 0


def contact_snapshot(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = {str(r["condition"]): r for r in data["conditions"]}
    return {
        "3c": float(rows["3c"]["p1_mean"]),
        "3d": float(rows["3d"]["p1_mean"]),
        "copresent": float(rows["copresent"]["p1_mean"]),
        "driver": data["control_3d"]["driver"],
    }


def dose_snapshot(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        "w_crit": float(data["critical_weight"]["w_p1_da1"]),
        "p1_at_default": float(data["p1_at_default"]),
        "crossed": bool(data["critical_weight"]["crossed"]),
    }


def rerun() -> int:
    sys.path.insert(0, str(ROOT / "src"))
    sys.path.insert(0, str(ROOT))
    from fly_icarus.assay import AssayConfig, run_assay, write_run
    from fly_icarus.dose import run_da1_dose

    locked_c = contact_snapshot(LOGS / "p1_contact_s1.json")
    locked_d = dose_snapshot(LOGS / "p1_da1_dose_s1.json")
    errs: list[str] = []
    with tempfile.TemporaryDirectory(prefix="fly_icarus_repro_") as tmp:
        tmp_path = Path(tmp)
        contact_out = tmp_path / "contact.json"
        dose_out = tmp_path / "dose.json"
        cfg = AssayConfig(seed=1, steps=2000)
        write_run(run_assay(cfg), contact_out)
        write_run(run_da1_dose(cfg), dose_out)
        if contact_out.resolve() == (LOGS / "p1_contact_s1.json").resolve():
            raise SystemExit("refuse: rerun would touch the lock")
        got_c = contact_snapshot(contact_out)
        got_d = dose_snapshot(dose_out)
        for key in ("3c", "3d", "copresent"):
            if abs(got_c[key] - locked_c[key]) > 1e-9:
                errs.append(f"contact {key} {got_c[key]} != {locked_c[key]}")
        if got_c["driver"] != locked_c["driver"]:
            errs.append(f"driver {got_c['driver']} != {locked_c['driver']}")
        if abs(got_d["w_crit"] - locked_d["w_crit"]) > 1e-9:
            errs.append(f"W_crit {got_d['w_crit']} != {locked_d['w_crit']}")
        if abs(got_d["p1_at_default"] - locked_d["p1_at_default"]) > 1e-9:
            errs.append(f"p1_at_default {got_d['p1_at_default']} != {locked_d['p1_at_default']}")
        print(f"wrote temp {contact_out} {dose_out}")
    if errs:
        print("\n".join(errs), file=sys.stderr)
        return 1
    print("rerun matches seed-1 contact P1 means and W_crit=-1.5262")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Hash-check or rebuild locked fly_icarus logs")
    p.add_argument("--rerun", action="store_true", help="rebuild seed-1 2000-step assay and dose in temp")
    args = p.parse_args(argv)
    rc = check_hashes()
    if args.rerun:
        rc = rc or rerun()
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
