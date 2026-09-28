import csv, hashlib, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PUBLISHED = os.path.join(HERE, "results.csv")

EXPECTED = {
    ("s1-goal-manipulation", "AUTONOMOUS"): 90.5,
    ("s1-goal-manipulation", "HITL"): 69.0,
    ("s2-false-data-injection", "AUTONOMOUS"): 100.0,
    ("s2-false-data-injection", "HITL"): 80.7,
    ("baseline", "AUTONOMOUS"): 0.0,
    ("baseline", "HITL"): 0.0,
}


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def rates(path):
    counts = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            key = (row["scenario"], row["condition"])
            c, t = counts.get(key, (0, 0))
            counts[key] = (c + (row["compromised"].strip().lower() == "true"), t + 1)
    return {k: round(100.0 * c / t, 1) for k, (c, t) in counts.items()}, sum(t for _, t in counts.values())


def main():
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copy(os.path.join(HERE, "simulation.py"), tmp)
        subprocess.run([sys.executable, "simulation.py"], cwd=tmp, check=True, stdout=subprocess.DEVNULL)
        fresh = os.path.join(tmp, "results.csv")
        same = sha256(fresh) == sha256(PUBLISHED)
        print(f"Published results.csv SHA-256: {sha256(PUBLISHED)}")
        print(f"Regenerated results.csv      : {'IDENTICAL' if same else 'DIFFERENT'}")
        ok &= same

    found, total = rates(PUBLISHED)
    print(f"\nTrials in results.csv: {total} (expected 522)")
    ok &= total == 522
    print(f"\n{'Scenario':<26}{'Condition':<12}{'Expected':>9}{'Found':>8}")
    for (scen, cond), exp in EXPECTED.items():
        got = found.get((scen, cond))
        match = got == exp
        ok &= match
        print(f"{scen:<26}{cond:<12}{exp:>8.1f}%{got:>7.1f}%  {'OK' if match else 'MISMATCH'}")

    print("\nRESULT:", "PASS - all results reproduced exactly" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
