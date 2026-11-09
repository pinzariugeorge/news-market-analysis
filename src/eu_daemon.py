"""Always-on scheduler for the Python side of the daily cycle, and keep-awake. Research and simulation only.

Run:  pythonw src/eu_daemon.py     (started at logon by the Windows task `EuPaperDaemon`; safe to start at any time of day: it works out what is due from the clock and the day state)
Every 30 seconds it: writes a heartbeat line to data/paper/daemon.log (once a minute), asks Windows not to idle-sleep (SetThreadExecutionState; this does NOT stop sleep on lid close),
and runs due steps on trading days (UTC inside; main venues 08:00-16:30 UTC in winter, one hour earlier in summer):
  collect         once a day, from 90 minutes before the open until the buy cutoff, if not done
  fills           every 2 minutes while an accepted order is pending (until the end of the session + 20 minutes)
  watch           every 30 minutes during the session: stops, horizon exits, fills
  pre-close exits (inside `watch`) from 45 minutes before the close
  close           once, 15 minutes after the close: mark to market, custody, reconcile, day report
Agent steps (researcher, trader, reviewer) are NOT run here: they are Claude Code scheduled tasks that call `eu_cycle.py due <role>` first.
Any error in a step is logged and the loop continues; the daemon never exits on its own. A second copy exits at once (lock file).
"""
import ctypes
import datetime as dt
import os
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import paper_broker as pb  # noqa: E402
import eu_cycle as ec  # noqa: E402
import notify  # noqa: E402

LOG = pb.PAPER / "daemon.log"
ES_CONTINUOUS, ES_SYSTEM_REQUIRED = 0x80000000, 0x00000001


def log(msg):
    pb.PAPER.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write("{} {}\n".format(pb.iso(pb.utc_now()), msg))


def keep_awake():
    try:
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)
        return True
    except Exception:  # noqa: BLE001
        return False


class SPS(ctypes.Structure):
    _fields_ = [("ac", ctypes.c_ubyte), ("flag", ctypes.c_ubyte), ("pct", ctypes.c_ubyte), ("saver", ctypes.c_ubyte), ("life", ctypes.c_ulong), ("full", ctypes.c_ulong)]


def power():
    """(battery percent or None, on_ac True/False/None, battery_saver on) from GetSystemPowerStatus; used to measure drain, never to change anything."""
    try:
        s = SPS()
        ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(s))
        return (None if s.pct == 255 else int(s.pct)), (None if s.ac == 255 else bool(s.ac)), bool(s.saver)
    except Exception:  # noqa: BLE001
        return None, None, False


def single_instance():
    f = pb.PAPER / "daemon.pid"
    if f.exists():
        try:
            pid = int(f.read_text())
            if pid != os.getpid() and os.name == "nt":
                h = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
                if h:
                    ctypes.windll.kernel32.CloseHandle(h)
                    return False
        except Exception:  # noqa: BLE001
            pass
    f.write_text(str(os.getpid()))
    return True


SENT = set()


def once(key, text, title="Paper trading", priority=3, click=None):
    """Send a phone notification at most once per key (per day or per threshold); never raises."""
    if key in SENT:
        return
    SENT.add(key)
    log("notify {}: {}".format(key, "sent" if notify.send(text, title, priority, click) else "not sent"))


def step(name, fn):
    try:
        r = fn()
        return True
    except Exception as e:  # noqa: BLE001
        log("ERROR in {}: {} | {}".format(name, e, traceback.format_exc().splitlines()[-2][:120]))
        once("err:{}:{}".format(name, pb.utc_now().strftime("%Y%m%d%H")), "Error in {}: {}".format(name, str(e)[:120]), "Paper trading ERROR", 4)
        return False


def tick(now, last):
    d = now.date()
    if not pb.is_trading_day(d):
        return
    o, c = ec.main_session(now)
    st = ec.state_get(d)["steps"]
    cutoff = c - dt.timedelta(minutes=pb.LIM["cutoff_min"])
    if "collect" not in st and o - dt.timedelta(minutes=90) <= now <= cutoff:
        step("collect", lambda: ec.collect(now))
    if o - dt.timedelta(minutes=90) <= now <= c:
        pct, ac, saver = power()
        once("alive:" + d.isoformat(), "Daemon alive {} UTC. Battery {}% ({}).".format(now.strftime("%H:%M"), pct, "AC" if ac else "battery"), "Paper trading alive", 2)
    pending = any(x["status"] == "ACCEPTED" for x in pb.load()["orders"])
    if pending and o <= now <= c + dt.timedelta(minutes=20) and now - last.get("fills", dt.datetime.min.replace(tzinfo=dt.timezone.utc)) >= dt.timedelta(minutes=2):
        last["fills"] = now
        msgs = []
        if step("fills", lambda: msgs.extend(ec.do_fills(now))):
            for m in msgs:
                if m.startswith("FILLED"):
                    once("fill:" + m[:60], m, "Paper trade filled", 4, notify.REPORT_URL)
    if o <= now <= c + dt.timedelta(minutes=5) and now - last.get("watch", dt.datetime.min.replace(tzinfo=dt.timezone.utc)) >= dt.timedelta(minutes=30):
        last["watch"] = now
        step("watch", lambda: ec.watch(now))
    if now >= c + dt.timedelta(minutes=15) and "close" not in st:
        step("close", lambda: ec.close(now))
        try:
            rep = ec.json.loads((pb.PAPER / "reports" / (d.isoformat() + ".json")).read_text(encoding="utf-8"))
            once("close:" + d.isoformat(), "Close: equity {:.2f} EUR, day {:+.2f}%, total {:+.2f}%, reconcile {}.".format(rep["equity"], rep["day_pnl_pct"], rep["total_pnl_pct"], "ok" if rep["reconcile"] == "consistent" else "MISMATCH"), "Paper trading close", 3, notify.REPORT_URL)
        except Exception:  # noqa: BLE001
            pass


def main():
    if not single_instance():
        print("another daemon is running")
        return
    log("daemon start pid {} (late starts are fine: steps are derived from the clock and the day state)".format(os.getpid()))
    last, beat = {}, None
    while True:
        now = pb.utc_now()
        awake = keep_awake()
        if beat is None or (now - beat).total_seconds() >= 60:
            beat = now
            pct, ac, saver = power()
            log("heartbeat awake_request={} trading_day={} battery={}% ac={} saver={}".format(awake, pb.is_trading_day(now.date()), pct, ac, saver))
        step("tick", lambda: tick(now, last))
        pct, ac, saver = power()
        if pct is not None and ac is False:
            for th in (30, 20, 10):
                if pct <= th:
                    once("batt:{}:{}".format(th, now.date().isoformat()), "Battery {}% and unplugged.".format(pct), "Paper trading battery", 4 if th <= 20 else 3)
                    break
        time.sleep(30)


if __name__ == "__main__":
    main()
