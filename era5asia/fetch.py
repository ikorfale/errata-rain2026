"""Fetch ERA5 daily precipitation (Open-Meteo archive, models=era5) for points.json, 1979-01-01..2026-09-30.
One point per request, polite pause, retries on 429. Output data/<name>.json (skips points already saved)."""
import json, os, time, urllib.parse, subprocess
pts = json.load(open("points.json")); os.makedirs("data", exist_ok=True)
for reg, d in pts.items():
    for name, (lat, lon) in d.items():
        out = f"data/{reg}_{name.replace(' ', '_')}.json"
        if os.path.exists(out): continue
        q = urllib.parse.urlencode(dict(latitude=lat, longitude=lon, start_date="1979-01-01", end_date="2026-09-30",
                                        daily="precipitation_sum", timezone="GMT", models="era5"))
        for attempt in range(5):
            r = subprocess.run(["curl", "-s", "-m", "120", f"https://archive-api.open-meteo.com/v1/archive?{q}"], capture_output=True, text=True).stdout
            try: j = json.loads(r)
            except ValueError: j = {"error": True, "reason": r[:200]}
            if "daily" in j: json.dump(j, open(out, "w")); print("ok", out, len(j["daily"]["time"]), flush=True); break
            print("retry", name, j.get("reason"), flush=True); time.sleep(60 * (attempt + 1))
        time.sleep(4)
