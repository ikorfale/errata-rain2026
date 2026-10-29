"""grok-bot (Moltbook, 29.10): split the USC* gauges by documented observation-time history in NOAA HOMR.
Fetches HOMR station records for every USC* gauge in the 427-gauge set (same filter as robust_moltbook.py),
keeps all dated PRECIP element periods (date=all; without it HOMR returns only the current period) with their observationTime. Polite: one request per second. Output homr_usc.jsonl."""
import json, time, urllib.request
from analyze_ghcn import gmst, SRC, MINY
T = gmst(); ids = []
for l in open(SRC):
    s = json.loads(l); d = {int(y) for y, v in s["years"].items() if int(y) in T and v["rx1"] > 0}
    if len(d) >= MINY and s["id"].startswith("USC"): ids.append(s["id"])
out = open("homr_usc.jsonl", "w")
for sid in ids:
    url = f"https://www.ncei.noaa.gov/access/homr/services/station/search?qid=GHCND:{sid}&headersOnly=false&date=all"
    try:
        d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "errata-research (errata@agentmail.to)"}), timeout=60))
        st = d["stationCollection"]["stations"]
        el = [e for s in st for e in (s.get("elements") or []) if e.get("element") == "PRECIP"]
        rec = {"id": sid, "n_stations": len(st), "precip": [{"obs": e.get("observationTime"), "begin": e["date"].get("beginDate"),
               "end": e["date"].get("endDate"), "program": e.get("dataProgram")} for e in el]}
    except Exception as ex:
        rec = {"id": sid, "error": str(ex)[:200]}
    out.write(json.dumps(rec) + "\n"); out.flush(); time.sleep(1)
print(len(ids))
