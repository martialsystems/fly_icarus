# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

import io
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from fly_icarus import BANNER
from fly_icarus.claims import ClaimBanError, require_clean, scan_text
from fly_icarus.cli import main

REPO = Path(__file__).resolve().parents[1]


def test_banner_is_clean() -> None:
    assert scan_text(BANNER) == []
    require_clean(BANNER, source="banner")


def test_public_copy_is_clean() -> None:
    for name in ("README.md", "AGENTS.md", "description.txt", "THIRD_PARTY.md", "viewer/index.html"):
        require_clean((REPO / name).read_text(encoding="utf-8"), source=name)
    buf = io.StringIO()
    with redirect_stdout(buf):
        with pytest.raises(SystemExit):
            main(["--help"])
    require_clean(buf.getvalue(), source="cli-help")


def test_banned_tokens_fail() -> None:
    with pytest.raises(ClaimBanError):
        require_clean("unique reconstructed brains in this vial", source="x")
    with pytest.raises(ClaimBanError):
        require_clean("the animation is the science result", source="x")
    with pytest.raises(ClaimBanError):
        require_clean("em dash here — no", source="x")
    with pytest.raises(ClaimBanError):
        require_clean("IBD F = 0.524 vs random", source="x")
    with pytest.raises(ClaimBanError):
        require_clean("MaleCNS P1 would court a fallen male", source="x")
    with pytest.raises(ClaimBanError):
        require_clean("males court fallen males", source="x")
    with pytest.raises(ClaimBanError):
        require_clean("shape overrules identity", source="x")
    with pytest.raises(ClaimBanError):
        require_clean("unfreeze is licensed", source="x")
