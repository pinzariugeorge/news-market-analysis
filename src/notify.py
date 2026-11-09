"""Phone notifications through ntfy.sh (free app, plain web request). Research only; messages are short and contain no keys.

The topic name is the only protection (anyone who knows it can read the messages), so it lives in `.env` as NTFY_TOPIC (project `.env` first, then the parent `.env`) and is never printed.
Missing topic or any network error is silent: a notification can never break the trading cycle. Messages pass through ntfy's server (a third party): keep them short.
Usage: python -I src/notify.py "text" [title] [priority 1-5]      send one message
       python -I src/notify.py --selftest                           offline check of the request that would be sent
Used by: eu_daemon.py (alive each morning, fills, errors, close result, low battery) and eu_cycle.py (trader orders, reviewer report ready with a link to the cloud report).
"""
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT_URL = "https://claude.ai/artifact/7TxjomynSos5DdRG3zaox6"


def topic():
    for env in (ROOT / ".env", ROOT.parent / ".env"):
        if env.exists():
            for line in env.read_text(encoding="utf-8").splitlines():
                if line.startswith("NTFY_TOPIC=") and line.split("=", 1)[1].strip():
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def build(text, title="Paper trading", priority=3, click=None, tags=None):
    h = {"Title": title.encode("ascii", "replace").decode(), "Priority": str(priority)}
    if click:
        h["Click"] = click
    if tags:
        h["Tags"] = tags
    return text.encode("utf-8")[:900], h


def send(text, title="Paper trading", priority=3, click=None, tags=None):
    """Returns True if the server accepted the message, False otherwise (never raises)."""
    try:
        t = topic()
        if not t:
            return False
        body, h = build(text, title, priority, click, tags)
        curl = shutil.which("curl.exe") or shutil.which("curl")
        if curl:   # Windows curl uses the system certificate store; Python's urllib fails the ntfy.sh chain on this machine ("certificate has expired"). Verification stays ON.
            cmd = [curl, "-sS", "-m", "15", "-o", "NUL" if sys.platform == "win32" else "/dev/null", "-w", "%{http_code}", "--data-binary", "@-"]
            for k, v in h.items():
                cmd += ["-H", "{}: {}".format(k, v)]
            r = subprocess.run(cmd + ["https://ntfy.sh/" + t], input=body, capture_output=True, timeout=25)
            return r.stdout.decode().strip() == "200"
        r = urllib.request.urlopen(urllib.request.Request("https://ntfy.sh/" + t, data=body, headers=h, method="POST"), timeout=15)
        return r.status == 200
    except Exception:  # noqa: BLE001
        return False


def selftest():
    b, h = build("Filled BUY 4 SAN.PA", "Paper trading", 4, click=REPORT_URL, tags="chart")
    assert b == b"Filled BUY 4 SAN.PA" and h["Priority"] == "4" and h["Click"] == REPORT_URL, (b, h)
    assert len(build("x" * 2000)[0]) == 900
    print("selftest ok; topic configured:", bool(topic()))


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "--selftest":
        selftest()
    else:
        print("sent" if send(a[0], a[1] if len(a) > 1 else "Paper trading", int(a[2]) if len(a) > 2 else 3) else "not sent (no NTFY_TOPIC in .env, or network error)")
