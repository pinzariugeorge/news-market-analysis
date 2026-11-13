"""Handoff note between agent runs (live phase). Research and simulation only; not financial advice.

Rule (see agent/HANDOFF.md): at the end of every run the agent returns a `handoff` object; the harness validates it and stores it in agent/state/handoff/;
the next run reads the latest valid note first. Each run is stateless and has no chat history, so the note is the only memory.

Commands:
  python -I src/handoff.py read [--asof YYYY-MM-DD]  print the latest valid note as text for the next agent, with warnings (first run, stale, pending orders, corrupt files skipped)
  python -I src/handoff.py write decision.json  take the `handoff` object from an agent decision file, validate, store, and update the LATEST pointer
  python -I src/handoff.py check note.json      validate a note and exit 0 or 1
  python -I src/handoff.py lock | unlock        overlap guard: `lock` fails (exit 2) if another run started less than 30 minutes ago
  python -I src/handoff.py selftest             run the edge-case tests (first run, corrupt file, stale note, pending orders, overlap, oversized note)
"""
import datetime as dt
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR = Path(os.environ["HANDOFF_DIR"]) if os.environ.get("HANDOFF_DIR") else ROOT / "agent" / "state" / "handoff"  # simulations set HANDOFF_DIR so they never touch live state
FAMILIES = ["oil_gas", "gold_miners", "chips", "pharma", "copper_uranium"]
MAX_BYTES = 6000
STALE_DAYS = int(os.environ.get("HANDOFF_STALE_DAYS", 5))  # live: daily cadence; the weekly simulation sets 10
LOCK_MINUTES = 30
STATUSES = {"open", "escalating", "fading", "closed"}
REQUIRED = ["run_id", "written_at", "decision_day", "data_cutoff", "what_changed", "families", "open_storylines", "pending_orders", "next_job"]


def validate(note):
    """Return a list of problems (empty list means valid)."""
    p = []
    if not isinstance(note, dict):
        return ["note is not an object"]
    for k in REQUIRED:
        if k not in note:
            p.append("missing field: " + k)
    if p:
        return p
    for k in ("run_id", "written_at", "decision_day", "data_cutoff", "what_changed", "next_job"):
        if not isinstance(note[k], str) or not note[k].strip():
            p.append("field must be a non-empty string: " + k)
    for k in ("decision_day", "data_cutoff"):
        try:
            dt.date.fromisoformat(str(note[k]))
        except ValueError:
            p.append(k + " must be YYYY-MM-DD")
    if not p and note["data_cutoff"] > note["decision_day"]:
        p.append("data_cutoff is after decision_day (future information)")
    if not isinstance(note["families"], dict) or not set(FAMILIES) <= set(note["families"]):
        p.append("families must contain at least: " + ", ".join(FAMILIES))
    else:
        for f, v in note["families"].items():
            if not isinstance(v, dict) or not str(v.get("position", "")).strip() or not str(v.get("why", "")).strip():
                p.append("families.{} needs non-empty position and why".format(f))
    if not isinstance(note["open_storylines"], list):
        p.append("open_storylines must be a list")
    else:
        for s in note["open_storylines"]:
            if not isinstance(s, dict) or s.get("status") not in STATUSES or not s.get("name") or not s.get("note"):
                p.append("storyline needs name, note and status in {}".format(sorted(STATUSES)))
                break
    if not isinstance(note["pending_orders"], list):
        p.append("pending_orders must be a list")
    else:
        for o in note["pending_orders"]:
            if not isinstance(o, dict) or not {"symbol", "side", "qty", "status"} <= set(o):
                p.append("pending order needs symbol, side, qty, status")
                break
    if "lessons" in note:  # optional lessons ledger (learning arm): list of at most 12 objects with rule (text) and cases (int >= 1)
        L = note["lessons"]
        if not isinstance(L, list) or len(L) > 12 or any(not isinstance(x, dict) or not str(x.get("rule", "")).strip() or not isinstance(x.get("cases"), int) or x["cases"] < 0 for x in L):
            p.append("lessons must be a list of at most 12 objects with rule (text) and cases (integer >= 0)")
    if len(json.dumps(note)) > MAX_BYTES:
        p.append("note larger than {} bytes (keep it short; drop closed storylines)".format(MAX_BYTES))
    return p


def _files(d):
    return sorted(d.glob("20*.json"))


def latest(d=DIR, today=None):
    """Return (note or None, warnings)."""
    warn = []
    d.mkdir(parents=True, exist_ok=True)
    cands = []
    ptr = d / "LATEST.json"
    if ptr.exists():
        try:
            cands.append(d / json.loads(ptr.read_text(encoding="utf-8"))["file"])
        except Exception:  # noqa: BLE001
            warn.append("LATEST pointer unreadable; falling back to the newest valid file")
    cands += list(reversed(_files(d)))
    seen = set()
    for f in cands:
        if f in seen or not f.exists():
            continue
        seen.add(f)
        try:
            note = json.loads(f.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            warn.append("skipped corrupt file " + f.name)
            continue
        probs = validate(note)
        if probs:
            warn.append("skipped invalid file {} ({})".format(f.name, "; ".join(probs[:2])))
            continue
        today = today or dt.date.today()
        age = (today - dt.date.fromisoformat(note["decision_day"])).days
        if age > STALE_DAYS:
            warn.append("STALE: last note is {} days old; re-check positions and prices before acting".format(age))
        if note["pending_orders"]:
            warn.append("PENDING ORDERS in the last note: reconcile with the broker before any new order")
        return note, warn
    warn.append("FIRST RUN: no previous valid handoff; start from the handbook and the empty storylines template")
    return None, warn


def render(note, warn):
    out = ["# Handoff from the previous run (read first)"]
    out += ["WARNING: " + w for w in warn]
    if note:
        out += ["Run {} (decision day {}, data cutoff {})".format(note["run_id"], note["decision_day"], note["data_cutoff"]),
                "What changed: " + note["what_changed"], "Holdings and reasons:"]
        out += ["- {}: {} | {}".format(f, v["position"], v["why"]) for f, v in note["families"].items()]
        out.append("Open storylines:")
        out += ["- [{}] {}: {}".format(s["status"], s["name"], s["note"]) for s in note["open_storylines"]] or ["- none"]
        if note.get("lessons"):
            out.append("Lessons ledger (cases = closed trades supporting it; below 5 cases it is only a hypothesis):")
            out += ["- ({} cases) {} | {}".format(x["cases"], x["rule"], x.get("evidence", "")) for x in note["lessons"]]
        out.append("Pending orders: " + (json.dumps(note["pending_orders"]) if note["pending_orders"] else "none"))
        out.append("EXACT NEXT JOB: " + note["next_job"])
    return "\n".join(out)


def store(note, d=DIR):
    probs = validate(note)
    if probs:
        raise ValueError("; ".join(probs))
    d.mkdir(parents=True, exist_ok=True)
    name = "{}_{}.json".format(note["decision_day"], note["run_id"].replace("/", "-").replace(" ", "_"))
    tmp = d / (name + ".tmp")
    tmp.write_text(json.dumps(note, indent=1), encoding="utf-8")
    os.replace(tmp, d / name)  # atomic: a crash leaves either the old state or the full new file
    ptmp = d / "LATEST.tmp"
    ptmp.write_text(json.dumps({"file": name}), encoding="utf-8")
    os.replace(ptmp, d / "LATEST.json")
    return name


def lock(d=DIR, now=None):
    d.mkdir(parents=True, exist_ok=True)
    f = d / ".lock"
    now = now or dt.datetime.now()
    if f.exists():
        try:
            started = dt.datetime.fromisoformat(f.read_text().strip())
            if (now - started).total_seconds() < LOCK_MINUTES * 60:
                return False
        except ValueError:
            pass  # unreadable lock counts as stale
    f.write_text(now.isoformat())
    return True


def unlock(d=DIR):
    f = d / ".lock"
    if f.exists():
        f.unlink()


def selftest():
    ok = True

    def check(name, cond):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name)
        ok &= bool(cond)

    good = {"run_id": "r1", "written_at": "2026-11-07T10:00", "decision_day": "2026-11-06", "data_cutoff": "2026-11-05", "what_changed": "nothing",
            "families": {f: {"position": "flat", "why": "no edge"} for f in FAMILIES}, "open_storylines": [{"name": "x", "note": "n", "status": "open"}],
            "pending_orders": [], "next_job": "decide for 2026-11-09"}
    with tempfile.TemporaryDirectory() as t:
        d = Path(t)
        note, w = latest(d, dt.date(2026, 11, 7))
        check("first run: no note, FIRST RUN warning", note is None and any("FIRST RUN" in x for x in w))
        store(good, d)
        note, w = latest(d, dt.date(2026, 11, 7))
        check("stored note is read back, no warnings", note and note["run_id"] == "r1" and not w)
        (d / "2026-11-07_bad.json").write_text("{not json", encoding="utf-8")
        note, w = latest(d, dt.date(2026, 11, 7))
        check("corrupt newer file is skipped, previous valid note used", note and note["run_id"] == "r1")
        (d / "LATEST.json").write_text("garbage", encoding="utf-8")
        note, w = latest(d, dt.date(2026, 11, 7))
        check("corrupt pointer falls back to newest valid file", note and note["run_id"] == "r1" and any("pointer" in x for x in w))
        note, w = latest(d, dt.date(2026, 11, 20))
        check("stale note warns", any("STALE" in x for x in w))
        p = dict(good, run_id="r2", pending_orders=[{"symbol": "XOM", "side": "buy", "qty": 3, "status": "sent, no fill seen"}])
        store(p, d)
        note, w = latest(d, dt.date(2026, 11, 7))
        check("pending orders force a reconcile warning", any("PENDING" in x for x in w))
        bad = dict(good, data_cutoff="2026-12-01")
        check("future data cutoff rejected", bool(validate(bad)))
        big = dict(good, what_changed="x" * 7000)
        check("oversized note rejected", bool(validate(big)))
        check("missing family rejected", bool(validate(dict(good, families={"oil_gas": {"position": "flat", "why": "x"}}))))
        check("first lock ok", lock(d, dt.datetime(2026, 11, 7, 10, 0)))
        check("overlapping run blocked", not lock(d, dt.datetime(2026, 11, 7, 10, 10)))
        check("stale lock (crashed run) is overridden", lock(d, dt.datetime(2026, 11, 7, 11, 0)))
        unlock(d)
        check("lock released", lock(d, dt.datetime(2026, 11, 7, 11, 1)))
    print("ALL PASS" if ok else "SOME FAILED")
    return 0 if ok else 1


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "read":
        asof = sys.argv[sys.argv.index("--asof") + 1] if "--asof" in sys.argv else None  # simulation: treat this date as "today" for staleness
        note, warn = latest(today=dt.date.fromisoformat(asof) if asof else None)
        print(render(note, warn))
    elif cmd == "write":
        data = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
        note = data.get("handoff", data)
        print("stored", store(note))
    elif cmd == "check":
        probs = validate(json.loads(Path(sys.argv[2]).read_text(encoding="utf-8")))
        print("\n".join(probs) or "valid")
        sys.exit(1 if probs else 0)
    elif cmd == "lock":
        if not lock():
            print("another run started less than {} minutes ago: stop".format(LOCK_MINUTES))
            sys.exit(2)
        print("locked")
    elif cmd == "unlock":
        unlock()
        print("unlocked")
    elif cmd == "selftest":
        sys.exit(selftest())
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
