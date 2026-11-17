#!/usr/bin/env python3
"""DXF Sketch Companion Tool - site measurements to an AutoCAD DXF, entered step by step in a web UI.

Author: Dionysios Theofilopoulos <d.theofilopoulos@gmail.com>

Optional laptop helper: the page DXF-Sketch.html also works on its own (github.io).
This script serves it on the local network and adds a 'Save to laptop' button that
writes drawings straight into the Sketches folder. No extra packages needed.

    python DXF-Sketch.py                    # start on port 8125 and open the browser
    python DXF-Sketch.py --port 9000 --no-browser
    python DXF-Sketch.py --console          # keep the terminal window open (troubleshooting)

On Windows the terminal window closes straight away and the program carries on
without one: everything is in the web UI, and Projects › Quit stops it.
What the window would have shown goes to DXF-Sketch.log next to the script.
"""
import argparse
import json
import os
import re
import socket
import sys
import threading
import time
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HERE = Path(__file__).resolve().parent
SCRIPT = Path(sys.argv[0]).name              # follows the file if it is renamed
UI_FILE = HERE / "DXF-Sketch.html"
OUT_DIR = HERE / "Sketches"
LOG_FILE = HERE / "DXF-Sketch.log"
LOCAL_HOST = "dxf-sketch.localhost"          # *.localhost always points to this computer in Edge, Chrome and Firefox
MAX_BODY = 20 * 1024 * 1024
MAX_ZIP = 300 * 1024 * 1024                  # a .zip with the photos
VERSION = "1.64.0"
AUTHOR = "Dionysios Theofilopoulos <d.theofilopoulos@gmail.com>"

# ── look ─────────────────────────────────────────────────────────────────────
TEAL, ORANGE, RED = "\033[38;2;0;153;153m", "\033[38;2;236;102;2m", "\033[38;2;217;58;58m"
GREY, BOLD, DIM, OFF = "\033[38;2;140;150;160m", "\033[1m", "\033[2m", "\033[0m"
W = 80                                       # inner width of the panels
ANSI = re.compile(r"\033\[[0-9;]*m")

ART = [  # "DXF" in orange, "SKETCH" in teal
    ("██████╗ ██╗  ██╗███████╗", "    ███████╗██╗  ██╗███████╗████████╗ ██████╗██╗  ██╗"),
    ("██╔══██╗╚██╗██╔╝██╔════╝", "    ██╔════╝██║ ██╔╝██╔════╝╚══██╔══╝██╔════╝██║  ██║"),
    ("██║  ██║ ╚███╔╝ █████╗  ", "    ███████╗█████╔╝ █████╗     ██║   ██║     ███████║"),
    ("██║  ██║ ██╔██╗ ██╔══╝  ", "    ╚════██║██╔═██╗ ██╔══╝     ██║   ██║     ██╔══██║"),
    ("██████╔╝██╔╝ ██╗██║     ", "    ███████║██║  ██╗███████╗   ██║   ╚██████╗██║  ██║"),
    ("╚═════╝ ╚═╝  ╚═╝╚═╝     ", "    ╚══════╝╚═╝  ╚═╝╚══════╝   ╚═╝    ╚═════╝╚═╝  ╚═╝"),
]

_print_lock = threading.Lock()
HIDDEN = False                               # True when running without a terminal window


class _LogFile:
    """Stands in for the terminal when there is none: plain text, no colour codes."""
    def __init__(self, path: Path):
        self.f = open(path, "w", encoding="utf-8", buffering=1)

    def write(self, text: str) -> int:
        self.f.write(ANSI.sub("", text))
        return len(text)

    def flush(self) -> None:
        self.f.flush()


def fail(message: str) -> None:
    """Stops with a message the person can actually see, window or not."""
    if HIDDEN and os.name == "nt":
        import ctypes
        ctypes.windll.user32.MessageBoxW(None, ANSI.sub("", message), "DXF Sketch", 0x10)  # MB_ICONERROR
    sys.exit(message)


def start_without_window(args) -> bool:
    """Windows: start again with pythonw.exe (no terminal window) and let this copy close."""
    if os.name != "nt" or args.console or args.firewall or args.hidden:
        return False
    exe = Path(sys.executable)
    pyw = exe.with_name("pythonw.exe")
    if exe.name.lower() != "python.exe" or not pyw.is_file():
        return False                         # already windowless, or an unusual Python: keep the window
    import subprocess
    try:
        subprocess.Popen([str(pyw), str(Path(__file__).resolve()), *sys.argv[1:], "--hidden"], cwd=str(HERE),
                         creationflags=0x00000008 | 0x00000200,  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
                         stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
    except OSError:
        return False
    return True


def already_running(port: int) -> bool:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/ping", timeout=1.5) as r:
            return json.loads(r.read().decode("utf-8")).get("app") == "dxf-sketch"
    except (OSError, ValueError):
        return False


def vlen(text: str) -> int:
    return len(ANSI.sub("", text))


def row(text: str = "", colour: str = "") -> str:
    pad = W - 2 - vlen(text)
    return f"{TEAL}│{OFF} {colour}{text}{OFF}{' ' * max(pad, 0)} {TEAL}│{OFF}"


def top(title: str = "") -> str:
    if not title:
        return f"{TEAL}┌{'─' * W}┐{OFF}"
    t = f" {title} "
    return f"{TEAL}┌─{OFF}{BOLD}{t}{OFF}{TEAL}{'─' * (W - 1 - len(t))}┐{OFF}"


def bottom() -> str:
    return f"{TEAL}└{'─' * W}┘{OFF}"


def kv(key: str, value: str, colour: str = "") -> str:
    return row(f"{GREY}{key:<16}{OFF}{colour}{value}{OFF}")


def log(symbol: str, colour: str, text: str) -> None:
    with _print_lock:
        print(f"  {GREY}{time.strftime('%H:%M:%S')}{OFF}  {colour}{symbol}{OFF}  {text}", flush=True)


def banner(port: int, ips: list) -> None:
    print()
    print(f"  {GREY}Siemens Healthineers{OFF}")
    print()
    for left, right in ART:
        print(f"  {ORANGE}{left}{OFF}{TEAL}{right}{OFF}")
    print(f"  {GREY}Measure on site, draw on the iPad, open in AutoCAD  ·  v{VERSION}{OFF}")
    print()
    print(top("Running"))
    print(kv("Version", f"{VERSION}  ·  {SCRIPT}"))
    print(kv("Author", AUTHOR))
    print(kv("This laptop", f"http://{LOCAL_HOST}:{port}", BOLD))
    if ips:
        for n, ip in enumerate(ips):
            print(kv("iPad" if n == 0 else "", f"http://{ip}:{port}" + ("" if n == 0 else f"  {GREY}(if the first one does not open){OFF}"), ORANGE + BOLD))
    else:
        print(kv("iPad", "no network found: connect this laptop to Wi-Fi or a hotspot", RED))
    print(kv("Saves to", str(OUT_DIR)))
    print(bottom())
    print(top("Use it from the iPad"))
    print(row(f"{ORANGE}1{OFF}  Connect the iPad to the same Wi-Fi or hotspot as this laptop."))
    print(row(f"{ORANGE}2{OFF}  In the browser, type the iPad address shown above."))
    print(row(f"{ORANGE}3{OFF}  When you export, tap {BOLD}Save to laptop{OFF}: the DXF lands in the Sketches folder."))
    print(row())
    print(row(f"{BOLD}The page keeps loading on the iPad?{OFF} Something is blocking the connection:"))
    print(row(f"{GREY}•{OFF} Windows Firewall: allow Python when asked. If Windows never asked, run once"))
    print(row(f"  in a terminal opened as administrator:  {BOLD}python {SCRIPT} --firewall{OFF}"))
    print(row(f"{GREY}•{OFF} Office and guest Wi-Fi often stop devices from reaching each other:"))
    print(row("  turn on the laptop's mobile hotspot (or your phone's) and join it with both."))
    print(row(f"{GREY}•{OFF} A VPN can hide the laptop: disconnect it while you work."))
    print(row())
    print(row("No laptop needed: the github.io version runs on the iPad by itself.", DIM))
    print(row("Projects › Quit stops it" + ("." if HIDDEN else ", or Ctrl+C in this window."), DIM))
    print(bottom())
    print()
    print(f"  {BOLD}Activity{OFF}")
    log("●", TEAL, "Ready — waiting for the iPad to connect")


# ── server ───────────────────────────────────────────────────────────────────
def safe_name(name: str) -> str:
    name = re.sub(r"[^\w\-. ()]+", "_", str(name), flags=re.UNICODE).strip(" .")
    return name[:80] or "sketch"


def lan_ips() -> list:
    """Every IPv4 address of this laptop that an iPad could reach, the most likely one first."""
    ips = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))   # no packet is sent; just picks the outgoing interface
        ips.append(s.getsockname()[0])
        s.close()
    except OSError:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ips.append(info[4][0])
    except OSError:
        pass
    seen, out = set(), []
    for ip in ips:
        if ip not in seen and not ip.startswith(("127.", "169.254.")):
            seen.add(ip)
            out.append(ip)
    return out


_seen_clients: set = set()


class Handler(BaseHTTPRequestHandler):
    server_version = "DXFSketch/" + VERSION

    def log_message(self, fmt, *args):      # the activity log replaces the default request log
        pass

    def _client(self) -> str:
        ip = self.client_address[0]
        return "this laptop" if ip in ("127.0.0.1", "::1") else ip

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        if not isinstance(body, bytes):
            body = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path in ("/", "/index.html"):
            try:
                self._send(200, UI_FILE.read_bytes(), "text/html; charset=utf-8")
            except OSError:
                log("✕", RED, "DXF-Sketch.html is missing next to the script")
                self._send(500, b"DXF-Sketch.html is missing next to the script.", "text/plain")
        elif url.path == "/api/ping":
            who = self._client()
            if who not in _seen_clients:
                _seen_clients.add(who)
                log("●", TEAL, f"Connected: {who}")
            self._send(200, {"app": "dxf-sketch", "port": self.server.server_address[1], "ips": lan_ips()})
        elif url.path == "/api/projects":
            files = sorted((p.stem for p in OUT_DIR.glob("*.json")), key=str.lower) if OUT_DIR.exists() else []
            self._send(200, {"files": files})
        elif url.path == "/api/project":
            name = safe_name(parse_qs(url.query).get("name", [""])[0])
            path = OUT_DIR / f"{name}.json"
            if path.is_file():
                log("↓", TEAL, f"Opened project {name} on {self._client()}")
                self._send(200, path.read_bytes())
            else:
                self._send(404, {"error": "Project not found."})
        else:
            self._send(404, {"error": "Not found."})

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/quit":
            log("■", GREY, f"Close requested from {self._client()}")
            self._send(200, {"ok": True})
            threading.Thread(target=self.server.shutdown, daemon=True).start()
            return
        if path == "/api/savezip":
            return self._save_zip()
        if path != "/api/save":
            return self._send(404, {"error": "Not found."})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= MAX_BODY:
                return self._send(413, {"error": "Request too large."})
            data = json.loads(self.rfile.read(size).decode("utf-8"))
            name = safe_name(data.get("name", "sketch"))
            dxf = data["dxf"]
            if not isinstance(dxf, str):
                raise ValueError("dxf must be text")
            OUT_DIR.mkdir(exist_ok=True)
            # newline="" keeps the CRLF line ends the page already wrote
            (OUT_DIR / f"{name}.dxf").write_text(dxf, encoding="utf-8", newline="")
            (OUT_DIR / f"{name}.json").write_text(json.dumps(data.get("project", {}), ensure_ascii=False, indent=1), encoding="utf-8")
            kb = len(dxf.encode("utf-8")) / 1024
            log("✓", ORANGE, f"Saved {BOLD}Sketches{os.sep}{name}.dxf{OFF}  {GREY}{kb:,.0f} KB from {self._client()}{OFF}")
            self._send(200, {"ok": True, "dxf": f"Sketches/{name}.dxf"})
        except (ValueError, KeyError, OSError) as exc:
            log("✕", RED, f"Could not save: {exc}")
            self._send(400, {"ok": False, "error": f"Could not save: {exc}"})


    def _save_zip(self):
        """The export .zip (DXF, project file, photos) into Sketches, with the DXF and project file unpacked next to it."""
        import io
        import zipfile
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= MAX_ZIP:
                return self._send(413, {"error": "Request too large."})
            body = self.rfile.read(size)
            name = safe_name(parse_qs(urlparse(self.path).query).get("name", ["sketch"])[0])
            with zipfile.ZipFile(io.BytesIO(body)) as z:
                names = z.namelist()
                dxf = next((n for n in names if n.lower().endswith(".dxf") and "/" not in n), None)
                pj = next((n for n in names if n.lower().endswith(".json") and "/" not in n), None)
                if not dxf:
                    raise ValueError("no DXF in the .zip")
                OUT_DIR.mkdir(exist_ok=True)
                (OUT_DIR / f"{name}.zip").write_bytes(body)
                (OUT_DIR / f"{name}.dxf").write_bytes(z.read(dxf))
                if pj:
                    (OUT_DIR / f"{name}.json").write_bytes(z.read(pj))
                photos = sum(1 for n in names if n.startswith("photos/"))
            log("✓", ORANGE, f"Saved {BOLD}Sketches{os.sep}{name}.zip{OFF}  {GREY}{size / 1024:,.0f} KB, {photos} photo(s), from {self._client()}{OFF}")
            self._send(200, {"ok": True, "dxf": f"Sketches/{name}.dxf", "zip": f"Sketches/{name}.zip", "photos": photos})
        except (ValueError, KeyError, OSError, zipfile.BadZipFile) as exc:
            log("✕", RED, f"Could not save: {exc}")
            self._send(400, {"ok": False, "error": f"Could not save: {exc}"})


def main():
    ap = argparse.ArgumentParser(prog=SCRIPT, description="DXF Sketch - site measurements to AutoCAD DXF.")
    ap.add_argument("--port", type=int, default=8125)
    ap.add_argument("--no-browser", action="store_true", help="do not open the browser on this computer")
    ap.add_argument("--firewall", action="store_true", help="Windows only, run as administrator: let the iPad reach this port")
    ap.add_argument("--console", action="store_true", help="keep the terminal window open (Windows hides it)")
    ap.add_argument("--hidden", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args()

    if start_without_window(args):
        return
    global HIDDEN
    if sys.stdout is None or args.hidden:    # pythonw.exe: no terminal to print to
        HIDDEN = True
        try:
            sys.stdout = sys.stderr = _LogFile(LOG_FILE)
        except OSError:
            sys.stdout = sys.stderr = open(os.devnull, "w", encoding="utf-8")
    else:
        os.system("")  # turns on ANSI colours in the Windows terminal
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")   # box drawing and the logo on any Windows code page
        except (AttributeError, ValueError):
            pass
    if args.firewall:
        if os.name != "nt":
            fail(f"{GREY}--firewall is only needed on Windows.{OFF}")
        import subprocess
        rule = f"DXF Sketch {args.port}"
        cmd = ["netsh", "advfirewall", "firewall", "add", "rule", f"name={rule}", "dir=in", "action=allow",
               "protocol=TCP", f"localport={args.port}", "profile=private,public,domain"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"{TEAL}✓{OFF} Windows Firewall now lets the iPad reach port {args.port} (rule \"{rule}\").")
        else:
            fail(f"{RED}✕ Could not add the firewall rule. Open the terminal as administrator and try again.{OFF}\n"
                     f"{GREY}{(res.stdout or res.stderr).strip()}{OFF}")
    if not UI_FILE.is_file():
        fail(f"{RED}✕ DXF-Sketch.html must sit in the same folder as {SCRIPT}.{OFF}")
    try:
        httpd = ThreadingHTTPServer(("0.0.0.0", args.port), Handler)
    except OSError as exc:
        if already_running(args.port):       # started twice: just bring the page up again
            if not args.no_browser:
                webbrowser.open(f"http://{LOCAL_HOST}:{args.port}")
            print(f"{TEAL}●{OFF} DXF Sketch is already running on port {args.port}.")
            return
        fail(f"{RED}✕ Port {args.port} is not available ({exc}). Try --port 9000.{OFF}")

    banner(args.port, lan_ips())
    if not args.no_browser:
        webbrowser.open(f"http://{LOCAL_HOST}:{args.port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print()
    httpd.server_close()
    log("■", GREY, "Stopped — your projects are saved")
    print()


if __name__ == "__main__":
    main()
