# Securing Agentic AI in Smart Grid Infrastructure

This repo holds the code and data for my MSc Cyber Security Engineering dissertation at WMG, University of Warwick (2026).

My research question was: how can the risks posed by agentic AI be addressed in critical systems such as smart grids?

I designed a four-zone security architecture for a smart grid run by an AI agent, threat modelled it with MITRE ATLAS and OWASP ASI, and then simulated the two threats that came out highest risk. The first is goal manipulation, where an instruction is hidden in the telemetry. The second is false data injection, where the agent is fed a fake sensor reading. I ran both with and without a human reviewer checking the agent's decisions.

## Results

I ran 522 trials in total. The compromise rate is the share of trials where the agent's final action was wrong for the real state of the grid.

| Attack | No reviewer | With reviewer |
|---|---|---|
| None (baseline) | 0.0% | 0.0% |
| Goal manipulation | 90.5% | 69.0% |
| False data injection | 100.0% | 80.7% |

The reviewer blocked 5 of the 12 attack variants: the three overtly worded injections, and the two fake readings above 100%. It let through every attack that looked normal. Even for the blocked variants the compromise rate isn't zero, because a blocked action defaults to HOLD, and HOLD is the wrong action when the load is very low or very high.

## Running it

You only need Python 3, nothing to install. On Windows use `py` instead of `python3`.

```
python3 simulation.py        # runs all 522 trials, writes results.csv and summary.txt
python3 verify_results.py    # re-runs the simulation and checks the results match
```

There's no randomness in the simulation, so it gives the same output every time. `verify_results.py` checks that a fresh run matches the `results.csv` in this repo exactly, and that the rates match the ones in the dissertation.

## Live test

This is Section 4.4.6 in the dissertation. The agent runs as a network service and a separate program attacks it over HTTP. Start the agent in one terminal:

```
python3 agent_server.py          # no reviewer
python3 agent_server.py --hitl   # with the reviewer
```

Then run the attacker in a second terminal:

```
python3 attacker.py
```

It sends five messages (a normal reading and four attacks) and prints what the agent decided for each.

## Files

- `simulation.py`: the main experiment. This is the one to run first.
- `results.csv`: the raw data, one row per trial.
- `summary.txt`: the compromise rates worked out from `results.csv`.
- `verify_results.py`: checks the results can be reproduced.
- `agent_server.py` and `attacker.py`: the live test.
- `CHECKSUMS.txt`: SHA-256 hashes of the code and data, so you can check nothing has changed.
- `CITATION.cff`: citation details for the repo.

## Where things are in the dissertation

| Dissertation | Code |
|---|---|
| Agent decision logic (Section 4.4.1) | `agent_decide` in `simulation.py` |
| Human reviewer model (Section 3.3.3) | `human_review` in `simulation.py` |
| Attack variants and sweep (Table 3.2) | `run_trial` and `run_all` in `simulation.py` |
| Simulation results (Tables 4.4 to 4.6) | `results.csv`, `summary.txt` |
| Live test (Section 4.4.6) | `agent_server.py`, `attacker.py` |

## Ethics

The WMG Cyber Ethics Panel approved this research (reference WMG-2025-FTMSc-R_2DUyhK3gjeThega). Everything ran on one isolated machine. No live systems, third-party systems or human participants were involved.

## Limitations

The agent is a set of rules standing in for a language model, and the human reviewer is a model of an operator, not a real person. So the results show how these attacks and this kind of review behave under controlled conditions. They don't say how often the attacks would work on a real grid. Section 5.6 of the dissertation covers this in more detail.

## Author

Vinit Banker, MSc Cyber Security Engineering, WMG, University of Warwick
