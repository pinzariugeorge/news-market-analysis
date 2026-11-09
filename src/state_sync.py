"""Keeps the paper account state in a git branch so a cloud run (fresh clone every time) can read it first and save it last. Research and simulation only.

State = everything under data/paper/ (ledger.json, orders.jsonl, state/, run/, reports/, handoff/) except locks, the daemon pid and log. Branch default: claude/paper-state (env PAPER_STATE_BRANCH);
the `claude/` prefix is the one cloud sessions may push to by default. One writer at a time: before the switch the laptop writes nothing here; afterwards only the two cloud tasks do.
Commands:  python -I src/state_sync.py pull     fetch the branch and restore its files into data/paper/ (no branch yet = first run, nothing restored)
           python -I src/state_sync.py push     commit data/paper/ to the branch and push it (no changes = no commit)
           python -I src/state_sync.py selftest local round trip against a temporary bare remote
Never touches the checked-out branch, the index or the working files other than data/paper/ (push uses a temporary worktree).
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAPER = Path(os.environ["PAPER_DIR"]) if os.environ.get("PAPER_DIR") else ROOT / "data" / "paper"
BRANCH = os.environ.get("PAPER_STATE_BRANCH", "claude/paper-state")
SKIP_NAMES = {".lock", "daemon.pid", "daemon.log", "ledger.json.tmp", "ledger_demo.json"}
IDENT = ["-c", "user.name=paper-bot", "-c", "user.email=paper-bot@users.noreply.github.com"]


NOWIN = 0x08000000 if os.name == "nt" else 0   # CREATE_NO_WINDOW: a hidden background process must not flash console windows


def git(repo, *args, check=True):
    r = subprocess.run(["git", "-C", str(repo)] + list(args), capture_output=True, text=True, creationflags=NOWIN)
    if check and r.returncode != 0:
        raise RuntimeError("git {} failed: {}".format(" ".join(args[:2]), (r.stderr or r.stdout).strip()[:300]))
    return r


def copy_tree(src, dst):
    for p in src.rglob("*"):
        if p.is_dir() or p.name in SKIP_NAMES or ".git" in p.relative_to(src).parts:
            continue
        q = dst / p.relative_to(src)
        q.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, q)


def remote_has(repo, branch):
    return bool(git(repo, "ls-remote", "--heads", "origin", branch, check=False).stdout.strip())


def pull(repo=ROOT, paper=PAPER, branch=BRANCH):
    if not remote_has(repo, branch):
        print("no state branch '{}' yet: first run, starting empty".format(branch))
        return False
    git(repo, "fetch", "origin", "{}:refs/remotes/origin/{}".format(branch, branch), "--force")
    tmp = Path(tempfile.mkdtemp(prefix="state_pull_"))
    try:
        git(repo, "worktree", "add", "--detach", str(tmp), "refs/remotes/origin/" + branch)
        paper.mkdir(parents=True, exist_ok=True)
        copy_tree(tmp, paper)
    finally:
        git(repo, "worktree", "remove", "--force", str(tmp), check=False)
        shutil.rmtree(tmp, ignore_errors=True)
    print("state restored from origin/{} into {}".format(branch, paper))
    return True


def push(repo=ROOT, paper=PAPER, branch=BRANCH, message="paper state"):
    tmp = Path(tempfile.mkdtemp(prefix="state_push_"))
    try:
        if remote_has(repo, branch):
            git(repo, "fetch", "origin", "{}:refs/remotes/origin/{}".format(branch, branch), "--force")
            git(repo, "worktree", "add", "--detach", str(tmp), "refs/remotes/origin/" + branch)
            git(tmp, "checkout", "-B", branch)
            for p in list(tmp.iterdir()):
                if p.name != ".git":
                    shutil.rmtree(p) if p.is_dir() else p.unlink()
        else:
            git(repo, "worktree", "add", "--detach", str(tmp), "HEAD")
            git(tmp, "checkout", "--orphan", branch)
            git(tmp, "rm", "-rf", "--quiet", ".", check=False)
            for p in list(tmp.iterdir()):
                if p.name != ".git":
                    shutil.rmtree(p) if p.is_dir() else p.unlink()
        copy_tree(paper, tmp)
        git(tmp, "add", "-A")
        if not git(tmp, "status", "--porcelain").stdout.strip():
            print("state unchanged: nothing to push")
            return False
        git(tmp, *IDENT, "commit", "-q", "-m", message)
        git(tmp, "push", "-q", "origin", "HEAD:refs/heads/" + branch)
        print("state pushed to origin/{}".format(branch))
        return True
    finally:
        git(repo, "worktree", "remove", "--force", str(tmp), check=False)
        shutil.rmtree(tmp, ignore_errors=True)


def selftest():
    base = Path(tempfile.mkdtemp(prefix="sync_test_"))
    remote = base / "remote.git"
    subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)
    a, b = base / "a", base / "b"
    subprocess.run(["git", "clone", "-q", str(remote), str(a)], check=True, capture_output=True)
    git(a, *IDENT, "commit", "-q", "--allow-empty", "-m", "init")
    git(a, "push", "-q", "origin", "HEAD:refs/heads/main")
    subprocess.run(["git", "clone", "-q", str(remote), str(b)], check=True, capture_output=True)
    pa, pb_ = base / "paper_a", base / "paper_b"
    ok = True

    def check(name, cond):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name)
        ok &= bool(cond)

    check("first pull with no branch restores nothing", pull(a, pa, "claude/t") is False)
    (pa / "state").mkdir(parents=True)
    (pa / "ledger.json").write_text('{"cash": 1000}', encoding="utf-8")
    (pa / "state" / "d.json").write_text("{}", encoding="utf-8")
    (pa / ".lock").write_text("x")
    (pa / "daemon.log").write_text("noise")
    check("first push creates the branch", push(a, pa, "claude/t", "t1") is True and remote_has(a, "claude/t"))
    check("push of unchanged state is a no-op", push(a, pa, "claude/t", "t2") is False)
    check("pull in a second fresh clone restores the files, not the locks or logs", pull(b, pb_, "claude/t") is True and (pb_ / "ledger.json").read_text(encoding="utf-8") == '{"cash": 1000}'
          and (pb_ / "state" / "d.json").exists() and not (pb_ / ".lock").exists() and not (pb_ / "daemon.log").exists())
    (pb_ / "ledger.json").write_text('{"cash": 900}', encoding="utf-8")
    check("second writer pushes an update", push(b, pb_, "claude/t", "t3") is True)
    pull(a, pa, "claude/t")
    check("first clone sees the update after pull", (pa / "ledger.json").read_text(encoding="utf-8") == '{"cash": 900}')
    check("the main branch history is untouched", git(a, "log", "--oneline", "-1", "origin/main").stdout.strip().endswith("init") if git(a, "fetch", "-q", "origin", check=False) else True)
    shutil.rmtree(base, ignore_errors=True)
    print("ALL PASS" if ok else "SOME FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    c = sys.argv[1] if len(sys.argv) > 1 else ""
    if c == "pull":
        pull()
    elif c == "push":
        push(message="paper state " + subprocess.run(["date", "-u", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip() if os.name != "nt" else "paper state")
    elif c == "selftest":
        sys.exit(selftest())
    else:
        print(__doc__)
