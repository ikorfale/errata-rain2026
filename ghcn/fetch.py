"""Rain extremes vs warming, homogeneous check: CPC's gridded trends are dominated by gauge-network changes,
so use individual long GHCN-Daily stations instead. One station per 2.5-deg cell with PRCP from <=1979 to 2026.
Per station and year, window Jan 1 - Oct 26: valid days, total, Rx1day, Rx5day, wet days (>=1mm), days >=20mm.
Writes stations.jsonl (one line per station, resumable). Sequential requests with a pause: polite to NCEI."""
import csv, io, json, os, time, urllib.request, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/"
ACC = "https://www.ncei.noaa.gov/data/global-historical-climatology-network-daily/access/{}.csv"
OUT = os.path.join(HERE, os.environ.get("OUTFILE", "stations.jsonl"))
END = os.environ.get("END", "10-26")   # window end MM-DD inclusive (Sep 30 run: END=09-30 OUTFILE=stations_sep.jsonl)

def get(url, tries=4):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "errata-rain-study (errata@agentmail.to)"}), timeout=120) as r:
                return r.read()
        except Exception as e:
            print("retry", url, e, flush=True); time.sleep(10 * (k + 1))
    raise RuntimeError(url)

def pick():
    inv = os.path.join(HERE, "ghcnd-inventory.txt")
    if not os.path.exists(inv): open(inv, "wb").write(get(BASE + "ghcnd-inventory.txt"))
    cand = {}
    for line in open(inv):
        sid, la, lo, el, y0, y1 = line[:11], float(line[12:20]), float(line[21:30]), line[31:35], int(line[36:40]), int(line[41:45])
        if el == "PRCP" and y0 <= 1979 and y1 >= 2026:
            cell = (int((la + 90) // 2.5), int((lo + 180) // 2.5))
            # prefer the longest record in the cell
            if cell not in cand or y0 < cand[cell][3]: cand[cell] = (sid, la, lo, y0)
    return sorted(cand.values())

def stats(sid):
    rows = csv.DictReader(io.StringIO(get(ACC.format(sid)).decode()))
    days = {}
    for r in rows:
        p = r.get("PRCP", "").strip(); q = r.get("PRCP_ATTRIBUTES", "")
        if not p: continue
        parts = q.split(",")
        if len(parts) > 1 and parts[1].strip(): continue          # quality flag set -> drop
        days[r["DATE"]] = float(p) / 10.0                         # tenths of mm -> mm
    out = {}
    for y in range(1979, 2027):
        d0 = dt.date(y, 1, 1); n = (dt.date(y, int(END[:2]), int(END[3:])) - d0).days + 1
        v = [days.get((d0 + dt.timedelta(i)).isoformat()) for i in range(n)]
        ok = [x for x in v if x is not None]
        if len(ok) < 0.9 * n: continue
        rx5 = max((sum(v[i:i + 5]) for i in range(n - 4) if None not in v[i:i + 5]), default=None)
        out[y] = {"n": len(ok), "tot": round(sum(ok), 1), "rx1": max(ok), "rx5": None if rx5 is None else round(rx5, 1),
                  "wet": sum(x >= 1 for x in ok), "r20": sum(x >= 20 for x in ok)}
    return out

if __name__ == "__main__":
    st = pick(); print("candidate stations", len(st), flush=True)
    done = set()
    if os.path.exists(OUT): done = {json.loads(l)["id"] for l in open(OUT)}
    for sid, la, lo, y0 in st:
        if sid in done: continue
        try: s = stats(sid)
        except Exception as e: print(sid, "FAILED", e, flush=True); continue
        with open(OUT, "a") as f: f.write(json.dumps({"id": sid, "lat": la, "lon": lo, "years": s}) + "\n")
        print(sid, len(s), "years", time.strftime("%H:%M:%S"), flush=True)
        time.sleep(0.5)
