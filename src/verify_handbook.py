"""Check a lean handbook against its sources: size, section coverage, and every number traced to the source handbooks.

Usage: python -I src/verify_handbook.py [lean_file] [source_file ...]
Default: handbook/AGENT_HANDBOOK.md against handbook/HANDBOOK.md and handbook/HANDBOOK_COMPANIES.md.
Reports: approximate tokens (bytes / 4), required keywords present, and every number in the lean file that does not appear in any
source (after normalizing 1,000 -> 1000 and trailing zeros). Numbers that are plain list or section numbers are ignored.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIRED = ["XOM", "CVX", "COP", "OXY", "NEM", "AEM", "WPM", "AU", "NVDA", "MU", "AMD", "INTC", "LLY", "JNJ", "ABBV", "MRK", "FCX", "SCCO", "TECK", "CCJ",
            "coin flip", "priced in", "VIX", "0.3%", "one name per family", "earnings", "inventories", "survivor"]


def numbers(text):
    text = re.sub(r"^\s*\d+\.\s", "", text, flags=re.M)             # list numbers
    text = re.sub(r"`[^`]*`", " ", text)                             # code spans (file names)
    text = re.sub(r"\(.*?\)", lambda m: m.group(0) if re.search(r"\d", m.group(0)) else " ", text)
    out = set()
    for m in re.finditer(r"(?<![A-Za-z])\d[\d,]*\.?\d*%?", text):
        s = m.group(0).replace(",", "").rstrip(".")
        out.add(s)
    return out


def norm(s):
    s = s.rstrip("%")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s


def main():
    lean = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "handbook" / "AGENT_HANDBOOK.md"
    srcs = [Path(p) for p in sys.argv[2:]] or [ROOT / "handbook" / "HANDBOOK.md", ROOT / "handbook" / "HANDBOOK_COMPANIES.md"]
    t = lean.read_text(encoding="utf-8")
    src_text = " ".join(p.read_text(encoding="utf-8") for p in srcs)
    src_nums = {norm(n) for n in numbers(src_text)}
    print("{}: {} bytes, about {} tokens".format(lean.name, len(t.encode("utf-8")), len(t.encode("utf-8")) // 4))
    missing = [k for k in REQUIRED if k.lower() not in t.lower()]
    print("required keywords missing:", missing or "none")
    bad = sorted(n for n in numbers(t) if norm(n) not in src_nums and norm(n) not in ("1", "2", "3", "4", "5", "10", "20"))
    print("numbers not found in the sources:", bad or "none")
    # context check: numbers in each family block of the lean file must appear in the matching family text of the companies handbook
    comp = next((p for p in srcs if p.name == "HANDBOOK_COMPANIES.md"), None)
    ctx_bad = []
    if comp and "### Oil and gas" in t:
        ct = comp.read_text(encoding="utf-8")
        keys = {"Oil and gas": ["Oil and gas"], "Gold miners": ["Gold miners"], "Chips": ["Chips"], "Pharma": ["Pharma"], "Copper and uranium": ["Copper", "Uranium"]}
        sec_re = {"Oil and gas": "3.1", "Gold miners": "3.2", "Chips": "3.3", "Pharma": "3.4", "Copper and uranium": "3.5"}
        for fam, ks in keys.items():
            lean_block = re.search(r"### {}.*?(?=\n### |\n## )".format(re.escape(fam)), t, re.S)
            src_block = re.search(r"### {} .*?(?=\n### |\n## )".format(re.escape(sec_re[fam])), ct, re.S)
            rows = [ln for ln in ct.splitlines() if ln.startswith("|") and any(k in ln for k in ks)]
            ctx = (src_block.group(0) if src_block else "") + " " + " ".join(rows)
            ctx_nums = {norm(n) for n in numbers(ctx)}
            for n in sorted(numbers(lean_block.group(0))):
                if norm(n) not in ctx_nums and norm(n) not in ("1", "2", "3", "4", "5", "10", "20"):
                    ctx_bad.append((fam, n))
    print("numbers in a family block not found in that family's source text:", ctx_bad or "none")
    sys.exit(1 if bad or missing or ctx_bad else 0)


if __name__ == "__main__":
    main()
