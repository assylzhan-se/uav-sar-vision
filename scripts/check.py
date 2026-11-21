"""Check that the project REALLY works before `git push` (run from the repository root).

    python scripts/check.py            # everything
    python scripts/check.py cv         # only the CV module (Assylzhan)
    python scripts/check.py backend    # backend tests + live server with the real model (Ali)
    python scripts/check.py frontend   # frontend tests + build + proxy to live server (Diana)

The live check starts the backend with the REAL YOLO model on a temporary database, sends the
sample photo ultralytics/assets/bus.jpg (4 people on it) and checks that real people are found.
This is exactly what went wrong at the previous meeting: the screen showed fake boxes.
Exit code 0 = all checks passed; otherwise do NOT push.
"""
from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
NPM = shutil.which("npm") or shutil.which("npm.cmd")
results: list[tuple[str, bool, str]] = []


def step(name: str, ok: bool, info: str = "") -> bool:
    results.append((name, ok, info))
    print(f"{'[OK]  ' if ok else '[FAIL]'} {name} {info}", flush=True)
    return ok


def run(name: str, cmd: list[str], cwd: Path = ROOT, timeout: int = 900) -> bool:
    print(f"\n--- {name}: {' '.join(cmd)}", flush=True)
    try:
        r = subprocess.run(cmd, cwd=cwd, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as e:
        return step(name, False, str(e))
    return step(name, r.returncode == 0)


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def get(url: str, data: bytes | None = None, headers: dict | None = None, timeout=120):
    req = urllib.request.Request(url, data=data, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def multipart(path: Path, fields: dict) -> tuple[bytes, str]:
    b = "----sarvision"
    parts = [f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
             for k, v in fields.items()]
    parts.append(f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="{path.name}"\r\n'
                 f"Content-Type: image/jpeg\r\n\r\n".encode() + path.read_bytes() + b"\r\n")
    return b"".join(parts) + f"--{b}--\r\n".encode(), f"multipart/form-data; boundary={b}"


def start(cmd: list[str], cwd: Path, env: dict) -> subprocess.Popen:
    """Start in its own process group so that the whole tree (npm -> node vite) can be stopped."""
    if os.name == "nt":
        return subprocess.Popen(cmd, cwd=cwd, env=env,
                                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
    return subprocess.Popen(cmd, cwd=cwd, env=env, start_new_session=True)


def stop(p: subprocess.Popen | None) -> None:
    if p is None or p.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], capture_output=True)
    else:
        import signal
        try:
            os.killpg(p.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    try:
        p.wait(10)
    except subprocess.TimeoutExpired:
        p.kill()


def wait_for(url: str, proc: subprocess.Popen, seconds: int = 120) -> dict | None:
    for _ in range(seconds * 2):
        if proc.poll() is not None:
            return None
        try:
            return get(url, timeout=3)
        except Exception:
            time.sleep(0.5)
    return None


def live_backend(check_frontend: bool) -> None:
    import ultralytics
    sample = Path(ultralytics.__file__).parent / "assets" / "bus.jpg"
    port = free_port()
    tmp = tempfile.mkdtemp(prefix="sar_check_")
    env = dict(os.environ, SAR_DETECTOR="yolo", SAR_DATA_DIR=tmp,
               SAR_DB_PATH=str(Path(tmp) / "check.sqlite"), SAR_UPLOAD_DIR=str(Path(tmp) / "up"))
    print(f"\n--- live server on port {port} (real YOLO model, first start downloads weights)")
    srv = start([PY, "-m", "uvicorn", "app.main:app", "--app-dir", "backend",
                 "--port", str(port)], ROOT, env)
    vite = None
    try:
        h = wait_for(f"http://127.0.0.1:{port}/api/health", srv, 300)
        if not step("server starts", h is not None):
            return
        step("server uses the REAL detector", h["detector"] == "yolo", f"(detector={h['detector']})")
        body, ctype = multipart(sample, {"lat": "43.2389", "lon": "76.8897", "altitude_m": "50"})
        r = get(f"http://127.0.0.1:{port}/api/detect", body, {"Content-Type": ctype})
        n = len(r["detections"])
        step("real people found on bus.jpg", 3 <= n <= 8, f"(found {n}, expected about 4)")
        step("all detections have coordinates", all(d["lat"] is not None for d in r["detections"]))
        img = urllib.request.urlopen(f"http://127.0.0.1:{port}{r['file_url']}").read()
        step("saved image is served", img[:2] == b"\xff\xd8")
        for fmt in ("csv", "kml"):
            text = urllib.request.urlopen(f"http://127.0.0.1:{port}/api/export.{fmt}").read()
            step(f"export {fmt.upper()}", len(text) > 50)
        if check_frontend and NPM:
            vport = free_port()
            vite = start([NPM, "run", "dev", "--", "--port", str(vport), "--strictPort"],
                         ROOT / "frontend", dict(os.environ, SAR_BACKEND=f"http://127.0.0.1:{port}"))
            vh = wait_for(f"http://localhost:{vport}/api/health", vite, 60)
            step("frontend proxy /api -> backend", bool(vh) and vh["detector"] == "yolo")
    except Exception as e:
        step("live check", False, repr(e))
    finally:
        stop(vite)
        stop(srv)
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    part = sys.argv[1] if len(sys.argv) > 1 else "all"
    if part not in ("all", "cv", "backend", "frontend"):
        print(__doc__)
        return 2
    if part in ("all", "cv"):
        run("CV unit tests", [PY, "-m", "pytest", "-q", "tests"])
        run("CV command line", [PY, "-m", "sar_vision.detection", "--help"])
    if part in ("all", "backend"):
        run("backend tests", [PY, "-m", "pytest", "-q", "backend/tests"])
    if part in ("all", "frontend"):
        if not step("npm is installed", NPM is not None, "(install Node.js 20+)"):
            pass
        else:
            if not (ROOT / "frontend" / "node_modules").exists():
                run("npm install", [NPM, "install"], ROOT / "frontend")
            run("frontend tests", [NPM, "test"], ROOT / "frontend")
            run("frontend build", [NPM, "run", "build"], ROOT / "frontend")
    if part in ("all", "backend", "frontend"):
        live_backend(check_frontend=part in ("all", "frontend"))

    failed = [r for r in results if not r[1]]
    print("\n================ RESULT ================")
    for name, ok, info in results:
        print(f"{'OK  ' if ok else 'FAIL'}  {name} {info}")
    print("ALL CHECKS PASSED - you can push" if not failed else
          f"{len(failed)} CHECK(S) FAILED - fix before pushing")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
