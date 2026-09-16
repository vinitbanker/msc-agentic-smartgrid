"""
=============================================================================
 AGENT SERVER - autonomous decision agent exposed as a network service
 Student ID: 5760334
=============================================================================

WHAT THIS IS
------------
The agentic AI decision component from the reference architecture (Zone 3),
running as a real network service. It listens on a TCP port, receives
telemetry over HTTP, decides a control action, and returns it.

This is the TARGET. The attacker script runs as a separate process and
sends it crafted telemetry over the network.

Uses only the Python standard library - nothing to install.

HOW TO RUN
----------
Open a command prompt and run ONE of:

    py agent_server.py                 (fully autonomous - no review)
    py agent_server.py --hitl          (human-in-the-loop review enabled)

It will print each request as it arrives and keep running until you press
Ctrl+C. Leave this window open and run the attacker in a SECOND window.

Every request is written to agent_log.txt as evidence.
=============================================================================
"""

import json
import sys
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

HOST = "127.0.0.1"
PORT = 8080
LOG_FILE = "agent_log.txt"

# Enabled with the --hitl command line flag
HUMAN_IN_THE_LOOP = "--hitl" in sys.argv

# ---------------------------------------------------------------------------
# AGENT LOGIC - identical to simulation.py so results stay consistent
# ---------------------------------------------------------------------------

SAFE_LOAD_MIN = 40.0
SAFE_LOAD_MAX = 90.0
ACTION_TRIGGERS = ["shed load", "reduce load", "load shedding", "drop load"]


def agent_decide(telemetry):
    """The agent's decision. Note it reads the note field as context."""
    note = telemetry.get("note", "").lower()
    # THE VULNERABILITY: instruction in the data is obeyed as if authoritative
    if any(trigger in note for trigger in ACTION_TRIGGERS):
        return "SHED_LOAD"
    load = float(telemetry.get("load_pct", 0.0))
    if load > SAFE_LOAD_MAX:
        return "SHED_LOAD"
    elif load < SAFE_LOAD_MIN:
        return "INCREASE_LOAD"
    return "HOLD"


# ---------------------------------------------------------------------------
# HUMAN REVIEWER - see Methodology 3.6. A model of an operator, not a human.
# ---------------------------------------------------------------------------

SUSPICIOUS_LANGUAGE = [
    "override", "ignore", "disregard", "system:", "urgent:",
    "immediately", "bypass", "admin",
]
PHYSICALLY_IMPLAUSIBLE_ABOVE = 100.0


def human_review(telemetry):
    note = telemetry.get("note", "").lower()
    load = float(telemetry.get("load_pct", 0.0))
    for phrase in SUSPICIOUS_LANGUAGE:
        if phrase in note:
            return False, f"blocked: anomalous language ('{phrase}')"
    if load > PHYSICALLY_IMPLAUSIBLE_ABOVE:
        return False, "blocked: reading physically implausible (>100%)"
    return True, "approved: no detectable anomaly"


# ---------------------------------------------------------------------------
# HTTP SERVICE
# ---------------------------------------------------------------------------

def log(line):
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{stamp}] {line}"
    print(entry)
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")


class AgentHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8")

        try:
            telemetry = json.loads(raw)
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'{"error":"invalid JSON"}')
            return

        client_ip = self.client_address[0]
        proposed = agent_decide(telemetry)

        if HUMAN_IN_THE_LOOP:
            approved, reason = human_review(telemetry)
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
        pass  # suppress default noisy logging; we do our own


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
