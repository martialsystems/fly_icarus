#!/usr/bin/env python3
"""Phone-width 390x844 and desktop ~1280 check for the two-agent viewer.

Uses CDP Emulation.setDeviceMetricsOverride on a page target plus a unique
Chrome user-data-dir. Chrome --window-size is not a CSS viewport on this host.
"""

from __future__ import annotations

import json
import os
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
PHONE = (390, 844)
DESKTOP = (1280, 800)


def find_chrome() -> Optional[str]:
    env = os.environ.get("VIEWPORT_SANITY_CHROME", "").strip()
    if env and Path(env).is_file():
        return env
    cands = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
    ]
    for c in cands:
        if Path(c).is_file():
            return c
    for name in ("google-chrome", "chromium", "chromium-browser"):
        hit = shutil.which(name)
        if hit:
            return hit
    return None


def _serve(root: Path) -> Tuple[ThreadingHTTPServer, int]:
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(root), **kwargs)

        def log_message(self, fmt, *args):
            return

    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, port


class Cdp:
    def __init__(self, ws_url: str):
        import urllib.parse

        u = urllib.parse.urlparse(ws_url)
        self._sock = socket.create_connection((u.hostname, u.port), timeout=10)
        key = "dGhlIHNhbXBsZSBub25jZQ=="
        path = u.path + (("?" + u.query) if u.query else "")
        req = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {u.hostname}:{u.port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self._sock.sendall(req.encode("ascii"))
        hdr = b""
        while b"\r\n\r\n" not in hdr:
            hdr += self._sock.recv(4096)
        if b"101" not in hdr.split(b"\r\n", 1)[0]:
            raise RuntimeError("CDP websocket handshake failed")
        self._buf = b""
        self._next = 1

    def _send(self, payload: bytes) -> None:
        header = bytearray([0x81])
        n = len(payload)
        mask = b"\x01\x02\x03\x04"
        if n < 126:
            header.append(0x80 | n)
        elif n < 65536:
            header.append(0x80 | 126)
            header.extend(struct.pack("!H", n))
        else:
            header.append(0x80 | 127)
            header.extend(struct.pack("!Q", n))
        header.extend(mask)
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self._sock.sendall(header + masked)

    def _recv_frame(self) -> bytes:
        while True:
            if len(self._buf) < 2:
                self._buf += self._sock.recv(4096)
                continue
            b0, b1 = self._buf[0], self._buf[1]
            masked = b1 & 0x80
            ln = b1 & 0x7F
            idx = 2
            if ln == 126:
                if len(self._buf) < 4:
                    self._buf += self._sock.recv(4096)
                    continue
                ln = struct.unpack("!H", self._buf[2:4])[0]
                idx = 4
            elif ln == 127:
                if len(self._buf) < 10:
                    self._buf += self._sock.recv(4096)
                    continue
                ln = struct.unpack("!Q", self._buf[2:10])[0]
                idx = 10
            mlen = 4 if masked else 0
            need = idx + mlen + ln
            while len(self._buf) < need:
                chunk = self._sock.recv(4096)
                if not chunk:
                    raise RuntimeError("CDP socket closed mid-frame")
                self._buf += chunk
            mask = self._buf[idx : idx + mlen] if masked else b""
            data = self._buf[idx + mlen : need]
            self._buf = self._buf[need:]
            if masked:
                data = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
            opcode = b0 & 0x0F
            if opcode == 0x8:
                raise RuntimeError("CDP websocket closed")
            if opcode == 0x1 or opcode == 0x2:
                return data

    def call(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        mid = self._next
        self._next += 1
        msg = {"id": mid, "method": method}
        if params:
            msg["params"] = params
        self._send(json.dumps(msg, separators=(",", ":")).encode("utf-8"))
        deadline = time.time() + 20
        while time.time() < deadline:
            raw = self._recv_frame()
            try:
                data = json.loads(raw.decode("utf-8"))
            except ValueError:
                continue
            if data.get("id") == mid:
                if "error" in data:
                    raise RuntimeError("{0}: {1}".format(method, data["error"]))
                return data.get("result") or {}
        raise RuntimeError("CDP timeout waiting for {0}".format(method))

    def close(self) -> None:
        try:
            self._sock.close()
        except OSError:
            pass


def _wait_devtools(port: int, timeout: float = 12.0) -> str:
    list_url = "http://127.0.0.1:{0}/json/list".format(port)
    new_url = "http://127.0.0.1:{0}/json/new?about:blank".format(port)
    deadline = time.time() + timeout
    last = ""
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(list_url, timeout=1) as resp:
                pages = json.loads(resp.read().decode("utf-8"))
            if isinstance(pages, list):
                for tab in pages:
                    if not isinstance(tab, dict):
                        continue
                    if tab.get("type") in ("page", "webview") and tab.get("webSocketDebuggerUrl"):
                        return str(tab["webSocketDebuggerUrl"]).replace("localhost", "127.0.0.1")
            req = urllib.request.Request(new_url, method="PUT")
            with urllib.request.urlopen(req, timeout=2) as resp:
                created = json.loads(resp.read().decode("utf-8"))
            ws = created.get("webSocketDebuggerUrl")
            if ws:
                return str(ws).replace("localhost", "127.0.0.1")
        except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
            last = str(exc)
        time.sleep(0.15)
    raise RuntimeError("Chrome page target not up on {0}: {1}".format(port, last))


def _eval(cdp: Cdp, expression: str) -> Any:
    out = cdp.call(
        "Runtime.evaluate",
        {"expression": expression, "returnByValue": True, "awaitPromise": True},
    )
    if out.get("exceptionDetails"):
        raise RuntimeError("page JS error: {0}".format(out["exceptionDetails"]))
    return (out.get("result") or {}).get("value")


MEASURE_JS = r"""
(async () => {
  const waitReady = async () => {
    const t0 = performance.now();
    while (performance.now() - t0 < 8000) {
      const app = document.getElementById("app");
      if (app && app.dataset.ready === "1" && window.FlyIcarus) return true;
      await new Promise((r) => setTimeout(r, 50));
    }
    return false;
  };
  const ready = await waitReady();
  if (!ready) return { error: "app not ready" };
  const inside = (r, vw, vh) =>
    r && r.width > 0 && r.height > 0 && r.left >= -8 && r.right <= vw + 8 && r.top < vh && r.bottom > 0;
  const vw = window.innerWidth;
  const vh = window.innerHeight;
  window.FlyIcarus.select("2");
  await new Promise((r) => setTimeout(r, 80));
  const after2 = window.FlyIcarus.currentCondition();
  window.FlyIcarus.select("3");
  await new Promise((r) => setTimeout(r, 80));
  const after3 = window.FlyIcarus.currentCondition();
  window.FlyIcarus.select("3b");
  await new Promise((r) => setTimeout(r, 80));
  const after3b = window.FlyIcarus.currentCondition();
  const arena = document.getElementById("arena").getBoundingClientRect();
  const hud = document.getElementById("hud");
  const p1 = document.getElementById("p1");
  const btns = [...document.querySelectorAll("#conds button")];
  const btnsIn = btns.every((b) => inside(b.getBoundingClientRect(), vw, vh));
  const overflow = document.documentElement.scrollWidth > vw + 1;
  return {
    vw, vh,
    after2, after3, after3b,
    btnCount: btns.length,
    btnsIn,
    arenaVisible: arena.width > 80 && arena.height > 80,
    hudIn: inside(hud.getBoundingClientRect(), vw, vh),
    p1In: inside(p1.getBoundingClientRect(), vw, vh),
    overflow,
    hudText: hud.textContent || "",
  };
})()
"""


def measure(chrome: str, viewports: List[Tuple[int, int]]) -> List[Dict[str, Any]]:
    httpd, http_port = _serve(ROOT)
    probe = socket.socket()
    probe.bind(("127.0.0.1", 0))
    cdp_port = probe.getsockname()[1]
    probe.close()
    tmp = tempfile.mkdtemp(prefix="flyicarus-chrome-")
    cmd = [
        chrome,
        "--headless=new",
        "--no-first-run",
        "--disable-extensions",
        "--remote-debugging-port={0}".format(cdp_port),
        "--remote-allow-origins=*",
        "--user-data-dir={0}".format(tmp),
        "about:blank",
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    results: List[Dict[str, Any]] = []
    try:
        ws = _wait_devtools(cdp_port)
        cdp = Cdp(ws)
        cdp.call("Page.enable")
        cdp.call("Runtime.enable")
        url = "http://127.0.0.1:{0}/index.html".format(http_port)
        for w, h in viewports:
            metrics = {
                "width": w,
                "height": h,
                "deviceScaleFactor": 1,
                "mobile": w <= 500,
            }
            cdp.call("Emulation.setDeviceMetricsOverride", metrics)
            cdp.call("Page.navigate", {"url": url})
            deadline = time.time() + 12
            while time.time() < deadline:
                try:
                    ready = _eval(cdp, "document.readyState")
                except RuntimeError:
                    ready = ""
                if ready == "complete":
                    break
                time.sleep(0.1)
            cdp.call("Emulation.setDeviceMetricsOverride", metrics)
            time.sleep(0.2)
            data = _eval(cdp, MEASURE_JS)
            data["requested"] = {"w": w, "h": h}
            results.append(data)
        cdp.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
        httpd.shutdown()
        shutil.rmtree(tmp, ignore_errors=True)
    return results


def main() -> None:
    chrome = find_chrome()
    if chrome is None:
        print("SKIP: no Chrome binary for viewport_sanity")
        raise SystemExit(0)
    rows = measure(chrome, [PHONE, DESKTOP])
    failed = False
    for row in rows:
        req = row.get("requested") or {}
        print(json.dumps(row, indent=2))
        if row.get("error"):
            print("FAIL:", row["error"])
            failed = True
            continue
        if int(row.get("vw") or 0) != int(req.get("w") or -1):
            print("FAIL: innerWidth {0} != {1}".format(row.get("vw"), req.get("w")))
            failed = True
        if str(row.get("after2")) != "2":
            print("FAIL: condition 2 did not select at", req, row.get("after2"))
            failed = True
        if str(row.get("after3")) != "3":
            print("FAIL: condition 3 did not select at", req, row.get("after3"))
            failed = True
        if str(row.get("after3b")) != "3b":
            print("FAIL: condition 3b did not select at", req, row.get("after3b"))
            failed = True
        if int(row.get("btnCount") or 0) < 7:
            print("FAIL: expected 7 condition buttons at", req)
            failed = True
        if not row.get("btnsIn"):
            print("FAIL: a condition button is outside the viewport at", req)
            failed = True
        if not row.get("arenaVisible"):
            print("FAIL: arena not visible at", req)
            failed = True
        if not row.get("hudIn"):
            print("FAIL: hud outside viewport at", req)
            failed = True
        if not row.get("p1In"):
            print("FAIL: P1 meter outside viewport at", req)
            failed = True
        if row.get("overflow"):
            print("FAIL: horizontal overflow at", req)
            failed = True
        hud = str(row.get("hudText") or "")
        if "wiring_sex" not in hud:
            print("FAIL: hud missing wiring_sex at", req, hud)
            failed = True
    if failed:
        raise SystemExit(2)
    print("viewport_sanity pass")


if __name__ == "__main__":
    main()
