import json
import sys
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

from simulation import agent_decide, human_review

HOST = "127.0.0.1"
PORT = 8080
LOG_FILE = "agent_log.txt"

HUMAN_IN_THE_LOOP = "--hitl" in sys.argv


def parse_telemetry(raw):
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    try:
        load = float(data.get("load_pct", 0.0))
    except (TypeError, ValueError):
        return None
    note = data.get("note", "")
    if not isinstance(note, str):
        return None
    return {"load_pct": load, "note": note}


def log(line):
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{stamp}] {line}"
    print(entry)
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")


class AgentHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8", errors="replace")

        telemetry = parse_telemetry(raw)
        if telemetry is None:
            body = b'{"error":"invalid telemetry"}'
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        client_ip = self.client_address[0]
        proposed = agent_decide(telemetry)

        if HUMAN_IN_THE_LOOP:
            approved, reason = human_review(telemetry, proposed)
            final = proposed if approved else "HOLD"
        else:
            reason = "no review (autonomous mode)"
            final = proposed

        mode = "HITL" if HUMAN_IN_THE_LOOP else "AUTONOMOUS"
        log(f"from={client_ip} mode={mode} "
            f"load={telemetry.get('load_pct')} "
            f"note={telemetry.get('note')!r} "
            f"proposed={proposed} final={final} review={reason}")

        response = {
            "mode": mode,
            "proposed_action": proposed,
            "final_action": final,
            "review": reason,
        }
        body = json.dumps(response).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    mode = "HUMAN-IN-THE-LOOP" if HUMAN_IN_THE_LOOP else "FULLY AUTONOMOUS"
    print("=" * 70)
    print("  SMART GRID AGENT - decision service")
    print(f"  Mode      : {mode}")
    print(f"  Listening : http://{HOST}:{PORT}")
    print(f"  Logging   : {LOG_FILE}")
    print("=" * 70)
    print("Waiting for telemetry. Press Ctrl+C to stop.\n")

    server = HTTPServer((HOST, PORT), AgentHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nAgent stopped.")
