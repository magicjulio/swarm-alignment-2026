#!/usr/bin/env python3
"""Local dashboard for JSONL experiment logs (stdlib only, no installs).

    .venv/bin/python scripts/logview.py              # serves ./data
    python3 scripts/logview.py path/to/logs --port 8800 --no-browser

Every *.jsonl file under the folder (recursively) is one "experiment"; each line is one run.
Works with any JSON-object-per-line log. Optional conventions unlock extra views:
  batch         string  -> runs are grouped into batches in the sidebar
  steps         list of {step, reasoning: [str], calls: [{name, args, result}], text}
                        -> rendered as an agent transcript
  messages      list of {role, content} -> rendered as a chat
  <name>_steps  list of step numbers -> those steps are highlighted with <name>
Booleans become filter chips + rates with 95% CIs; short strings become dropdown filters.

Binds to 127.0.0.1 only. The page re-reads files every few seconds, so runs show up live.
"""
import argparse
import json
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

PAGE = Path(__file__).with_name("logview.html")


def make_handler(root: Path):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def reply(self, code: int, body, ctype="application/json"):
            data = body if isinstance(body, bytes) else (
                body.encode() if isinstance(body, str) else json.dumps(body).encode())
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            url = urlparse(self.path)
            q = parse_qs(url.query)
            if url.path == "/":
                # read on every request, so edits to the HTML show up on reload
                return self.reply(200, PAGE.read_bytes(), "text/html; charset=utf-8")
            if url.path == "/api/files":
                files = []
                for p in sorted(root.rglob("*.jsonl")):
                    with p.open("rb") as f:
                        n = sum(1 for line in f if line.strip())
                    st = p.stat()
                    files.append({"name": p.relative_to(root).as_posix(), "lines": n,
                                  "mtime": st.st_mtime, "size": st.st_size})
                return self.reply(200, {"root": str(root), "files": files})
            if url.path == "/api/file":
                p = (root / q.get("name", [""])[0]).resolve()
                if not p.is_relative_to(root) or p.suffix != ".jsonl" or not p.is_file():
                    return self.reply(404, {"error": "not found"})
                rows = []
                with p.open(encoding="utf-8", errors="replace") as f:
                    for i, line in enumerate(f, 1):
                        if not line.strip():
                            continue
                        try:
                            rec = json.loads(line)
                        except json.JSONDecodeError as e:
                            rec = {"_parse_error": str(e), "_raw": line[:5000]}
                        if not isinstance(rec, dict):
                            rec = {"value": rec}
                        rows.append({"line": i, "rec": rec})
                return self.reply(200, {"mtime": p.stat().st_mtime, "rows": rows})
            self.reply(404, {"error": "not found"})

    return Handler


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dir", nargs="?", default="data", help="folder with .jsonl logs (default: ./data)")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-browser", action="store_true")
    a = ap.parse_args()

    root = Path(a.dir).resolve()
    if not root.is_dir():
        raise SystemExit(f"not a folder: {root}")
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), make_handler(root))
    url = f"http://127.0.0.1:{a.port}/"
    print(f"logview: {root}\n  -> {url}   (Ctrl+C to stop)")
    if not a.no_browser:
        threading.Timer(0.5, webbrowser.open, [url]).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
