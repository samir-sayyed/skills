#!/usr/bin/env python3
"""ringer — a local proxy between Claude Code and the API.

    python3 ringer.py serve      # start on 127.0.0.1:8787
    python3 ringer.py report     # what you actually spent
    python3 ringer.py selftest

Point a client at it:  export ANTHROPIC_BASE_URL=http://127.0.0.1:8787

Does two things a skill structurally cannot, because it sits below the wire:
  1. counts every token that leaves — including the reused input you never typed
  2. refuses a request over RINGER_MAX_TOKENS instead of asking nicely

ponytail: stdlib only, one file, no cache layer. Add caching when the log shows
repeated identical requests — in a coding session it never does.
"""

import http.server
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

UPSTREAM = os.environ.get("RINGER_UPSTREAM", "https://api.anthropic.com")
PORT = int(os.environ.get("RINGER_PORT", "8787"))
LOG = Path(os.environ.get("RINGER_LOG", Path.home() / ".ringer" / "log.jsonl"))
# Runaway guard, not a budget. ~4 bytes/token, checked on the request body.
MAX_TOKENS = int(os.environ.get("RINGER_MAX_TOKENS", "200000"))

DROP = {"host", "accept-encoding", "connection", "content-length",
        "transfer-encoding", "keep-alive"}


def est_tokens(body: bytes) -> int:
    return len(body) // 4


def usage_from_sse(chunk: bytes, acc: dict) -> None:
    """Pull token counts out of streaming events. Mutates acc."""
    for line in chunk.split(b"\n"):
        if not line.startswith(b"data: "):
            continue
        try:
            ev = json.loads(line[6:])
        except ValueError:
            continue
        u = ev.get("usage") or (ev.get("message") or {}).get("usage") or {}
        for k in ("input_tokens", "cache_read_input_tokens",
                  "cache_creation_input_tokens", "output_tokens"):
            if k in u:
                # message_delta reports cumulative output; input arrives once.
                acc[k] = max(acc.get(k, 0), u[k])


def record(row: dict) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f:
        f.write(json.dumps(row) + "\n")


class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"  # close-delimited; streams without chunking
    server_version = "ringer"

    def log_message(self, fmt, *args):
        pass  # the jsonl log is the log

    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("content-length", 0)))
        est = est_tokens(body)

        if MAX_TOKENS and est > MAX_TOKENS:
            record({"ts": now(), "path": self.path, "blocked": est})
            self.reject(f"ringer: request ~{est:,} tokens, over "
                        f"RINGER_MAX_TOKENS={MAX_TOKENS:,}. Nothing was sent.")
            print(f"BLOCKED ~{est:,} tok", file=sys.stderr)
            return

        self.relay(body, est)

    do_GET = do_POST  # /v1/models and friends; body is empty

    def relay(self, body: bytes, est: int) -> None:
        headers = {k: v for k, v in self.headers.items() if k.lower() not in DROP}
        req = urllib.request.Request(
            UPSTREAM + self.path, data=body or None, headers=headers,
            method=self.command)
        try:
            up = urllib.request.urlopen(req, timeout=900)
        except urllib.error.HTTPError as e:
            up = e
        except OSError as e:
            self.reject(f"ringer: upstream unreachable — {e}")
            return

        self.send_response(up.status)
        for k, v in up.headers.items():
            if k.lower() not in DROP:
                self.send_header(k, v)
        self.end_headers()

        acc, model = {}, None
        try:
            model = json.loads(body).get("model") if body else None
        except ValueError:
            pass

        while True:
            chunk = up.read(8192)
            if not chunk:
                break
            usage_from_sse(chunk, acc)
            try:
                self.wfile.write(chunk)
                self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                break  # client hung up mid-stream; still log what we counted

        if acc:
            record({"ts": now(), "model": model, "est_request": est, **acc})
            reused = acc.get("cache_read_input_tokens", 0)
            print(f"{model} in={acc.get('input_tokens',0):,} "
                  f"cached={reused:,} out={acc.get('output_tokens',0):,}",
                  file=sys.stderr)

    def reject(self, msg: str) -> None:
        payload = json.dumps(
            {"type": "error", "error": {"type": "invalid_request_error",
                                        "message": msg}}).encode()
        self.send_response(400)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def report() -> None:
    if not LOG.exists():
        print(f"no log at {LOG} — nothing proxied yet")
        return
    t = {}
    calls = blocked = 0
    for line in LOG.read_text().splitlines():
        row = json.loads(line)
        if "blocked" in row:
            blocked += 1
            continue
        calls += 1
        for k in ("input_tokens", "cache_read_input_tokens",
                  "cache_creation_input_tokens", "output_tokens"):
            t[k] = t.get(k, 0) + row.get(k, 0)

    fresh = t.get("input_tokens", 0) + t.get("cache_creation_input_tokens", 0)
    reused = t.get("cache_read_input_tokens", 0)
    total = fresh + reused + t.get("output_tokens", 0)
    print(f"{calls:,} calls  ({blocked} blocked)")
    print(f"  fresh input   {fresh:>15,}")
    print(f"  reused input  {reused:>15,}"
          + (f"   {reused / (fresh + reused):.0%} of input" if fresh + reused else ""))
    print(f"  output        {t.get('output_tokens', 0):>15,}")
    print(f"  total         {total:>15,}")


def selftest() -> None:
    acc = {}
    usage_from_sse(
        b'event: message_start\n'
        b'data: {"message":{"usage":{"input_tokens":12,'
        b'"cache_read_input_tokens":4000}}}\n\n'
        b'data: {"type":"ping"}\n\n'
        b'data: not json\n\n'
        b'data: {"type":"message_delta","usage":{"output_tokens":7}}\n\n'
        b'data: {"type":"message_delta","usage":{"output_tokens":31}}\n\n',
        acc)
    assert acc == {"input_tokens": 12, "cache_read_input_tokens": 4000,
                   "output_tokens": 31}, acc          # cumulative output, not summed
    assert usage_from_sse(b"", acc) is None
    assert est_tokens(b"x" * 4000) == 1000
    assert est_tokens(b"") == 0
    print("ok")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "serve"
    if cmd == "report":
        report()
    elif cmd == "selftest":
        selftest()
    else:
        srv = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
        print(f"ringer → {UPSTREAM}  on http://127.0.0.1:{PORT}\n"
              f"  export ANTHROPIC_BASE_URL=http://127.0.0.1:{PORT}\n"
              f"  cap {MAX_TOKENS:,} tok · log {LOG}", file=sys.stderr)
        srv.serve_forever()
