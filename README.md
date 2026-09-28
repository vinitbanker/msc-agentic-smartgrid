# Securing Agentic AI in Smart Grid Infrastructure

Code, data and figures for my MSc Cyber Security Engineering dissertation at WMG, University of Warwick (2026).

**Research question:** How can the risks posed by agentic AI be addressed in critical systems such as smart grids?

The project designs a four-zone security reference architecture for an agentic AI smart grid system, threat models it using MITRE ATLAS and OWASP ASI, and simulates the two highest-risk threats, goal manipulation and false data injection, with and without a human reviewer.

## Key results

Across **522 trials**, the human reviewer stopped **five of the twelve** attack variants. It blocked attacks that showed a clear warning sign, and approved attacks designed to look normal.

| Attack | Without human reviewer | With human reviewer |
|---|---|---|
| None (baseline) | 0.0% | 0.0% |
| Goal manipulation | 90.5% | 69.0% |
| False data injection | 100.0% | 80.7% |

*Compromise rate: the percentage of trials in which the agent's final action was wrong for the true state of the grid.*

## Reproduce the results

Requires **Python 3** only. No external packages are needed. On Windows, use `py` in place of `python3`.

```
python3 simulation.py        # runs all 522 trials, writes results.csv and summary.txt
python3 verify_results.py    # re-runs the simulation and checks every result
```

The simulation contains no random elements, so it produces identical output every time. `verify_results.py` confirms that a fresh run reproduces the published `results.csv` exactly, and that the compromise rates match those reported in the dissertation.

**SHA-256 of the published results.csv:**
`b75c241baaa1e080fba1fba79481ec21376d9600adec44f78707454e8675e66b`

## Live test

The live test (Section 4.4.6, Figures 4.7 and 4.8) runs the agent as a network service and sends attacks from a separate program over HTTP:

```
python3 agent_server.py          # terminal 1: autonomous mode
python3 agent_server.py --hitl   # or: with the human reviewer
python3 attacker.py              # terminal 2: sends the five test messages
```

## Where each part appears in the dissertation

| Dissertation | File |
|---|---|
| Agent decision logic (Section 4.4.1, Figure 4.4) | `simulation.py`, function `agent_decide` |
| Human reviewer model (Section 3.3.3, Figure 4.5) | `simulation.py`, function `human_review` |
| Attack variants and sweep (Table 3.2, Figure 4.6) | `simulation.py`, functions `run_trial` and `run_all` |
| Simulations 1 to 3 (Tables 4.4 to 4.6) | `results.csv`, `summary.txt` |
| Simulation 4, live test (Figures 4.7 and 4.8) | `agent_server.py`, `attacker.py` |
| Diagrams and charts (Figures 2.1, 3.1 to 3.3, 4.1 to 4.3, 4.9, 5.1) | `figures/` |

## Repository contents

| File | Purpose |
|---|---|
| `simulation.py` | The main experiment: all 522 trials |
| `results.csv` | Raw data: one row per trial |
| `summary.txt` | Aggregate compromise rates |
| `verify_results.py` | Checks the results can be reproduced exactly |
| `agent_server.py`, `attacker.py` | The live network test |
| `figures/` | Scripts and draw.io files that produce every figure |
| `CHECKSUMS.txt` | SHA-256 fingerprints of the code and data |
| `CITATION.cff` | How to cite this repository |

## Ethics

This research was approved by the WMG Cyber Ethics Panel (reference WMG-2025-FTMSc-R_2DUyhK3gjeThega). All attacks were simulated on a single isolated device. No live systems, third-party systems or human participants were involved.

## Limitations

The agent is a rule-based model rather than a live language model, and the human reviewer is a simulated model of an operator rather than a real person. The results show how these attacks and this form of human review behave under controlled conditions, not how often such attacks would succeed in an operational grid. See Section 5.6 of the dissertation.

## Author

Vinit Banker, MSc Cyber Security Engineering, WMG, University of Warwick
