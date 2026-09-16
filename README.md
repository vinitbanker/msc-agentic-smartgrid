MSc Dissertation – Agentic AI Security in Smart Grids

This repo holds the simulation code for my MSc Cyber Security Engineering dissertation at WMG, University of Warwick.

The project looks at what happens when an autonomous AI agent makes control decisions in a smart grid, and whether having a human review those decisions actually keeps it safe. I tested two attacks against the agent — one that hides an instruction in the telemetry, and one that just feeds it a fake sensor reading — and ran each with and without a human reviewer in the loop.

Files
simulation.py – the main experiment. Runs both attacks across a range of inputs (522 trials in total) and saves the results. This is the one to run first.
agent_server.py – the agent running as a live service you can send telemetry to over the network.
attacker.py – sends the attack payloads to the agent server.
results.csv – the raw results from every trial.
summary.txt – the summary tables (compromise rates by scenario and condition).
