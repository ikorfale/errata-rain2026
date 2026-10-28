"""Lab job: same Jan 1 - Sep 30 window on both sides (Fable review 28.10: 96 of 267 GHCN stations, most of Europe,
have no October 2026 yet, while CPC runs to Oct 26). CPC 2006-2026 -> extremes/years_sep/, GHCN -> ghcn/stations_sep.jsonl."""
import os, subprocess, sys
here = os.path.dirname(os.path.abspath(__file__))
env = dict(os.environ, END="09-30", OUTDIR="years_sep", OUTFILE="stations_sep.jsonl")
rc1 = subprocess.call([sys.executable, "collect.py"] + [str(y) for y in range(2026, 2005, -1)], cwd=os.path.join(here, "extremes"), env=env)
rc2 = subprocess.call([sys.executable, "fetch.py"], cwd=os.path.join(here, "ghcn"), env=env)
sys.exit(rc1 or rc2)
