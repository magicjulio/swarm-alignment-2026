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
  <name>_steps  list of step numbers -> those steps get a <name> tag (red + outlined if the name
                contains forbid/violat/error/fail/leak/unsafe/bad/harm/attack)
Booleans become filter chips + rates with 95% CIs; short strings become dropdown filters.

Stars + comments (press s / click ☆ on a run, or ☆ next to a batch) are saved to
<dir>/logview_marks.json, keyed by file + batch + run_id (falls back to line number; whole batches
use "batch"), so they survive edits to the logs.

Binds to 127.0.0.1 only. The page re-reads files every few seconds, so runs show up live.
"""
import argparse
import json
import os
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

PAGE = Path(__file__).with_name("logview.html")


def make_handler(root: Path, marks_path: Path):
    lock = threading.Lock()

    def read_marks() -> dict:
        try:
            return json.loads(marks_path.read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

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
            if url.path == "/api/marks":
                with lock:
                    return self.reply(200, read_marks())
            self.reply(404, {"error": "not found"})

        def do_POST(self):
            # JSON-only, so a random web page can't post here without a CORS preflight (which we never answer)
            if urlparse(self.path).path != "/api/marks" or \
                    not self.headers.get("Content-Type", "").startswith("application/json"):
                return self.reply(404, {"error": "not found"})
            try:
                body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
                key = str(body["key"])
            except (ValueError, KeyError, TypeError):
                return self.reply(400, {"error": "bad request"})
            with lock:
                marks = read_marks()
                m = {k: body.get(k) for k in ("file", "batch", "run_id", "line", "kind", "starred", "comment")}
                m["comment"] = (m["comment"] or "").strip()
                if m["starred"] or m["comment"]:
                    marks[key] = m | {"updated": time.strftime("%Y-%m-%d %H:%M:%S")}
                else:
                    marks.pop(key, None)
                tmp = marks_path.with_suffix(".tmp")
                tmp.write_text(json.dumps(marks, indent=1))
                os.replace(tmp, marks_path)
            self.reply(200, marks)

    return Handler


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dir", nargs="?", default="data", help="folder with .jsonl logs (default: ./data)")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--marks", help="where to keep stars/comments (default: <dir>/logview_marks.json)")
    a = ap.parse_args()

    root = Path(a.dir).resolve()
    if not root.is_dir():
        raise SystemExit(f"not a folder: {root}")
    marks = Path(a.marks).resolve() if a.marks else root / "logview_marks.json"
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), make_handler(root, marks))
    url = f"http://127.0.0.1:{a.port}/"
    print(f"logview: {root}\n  marks: {marks}\n  -> {url}   (Ctrl+C to stop)")
    if not a.no_browser:
        threading.Timer(0.5, webbrowser.open, [url]).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
