"""Agent originality check.

Migrates the logic of the legacy ``scripts/check-agent-originality.sh``.

Compares candidate agent files against the whole existing roster using
entity-neutralized 8-word shingle overlap, so a find-replace re-skin
(e.g. swapping a country/platform name) still scores as a near-duplicate.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ENTITY = re.compile(
    r"\b(vietnam|vietnamese|china|chinese|douyin|tiktok|korea|korean|japan|japanese|"
    r"india|indian|indonesia|indonesian|thailand|thai|philippines|filipino|brazil|"
    r"brazilian|mexico|mexican|wechat|weixin|weibo|xiaohongshu|rednote|kuaishou|"
    r"bilibili|zhihu|baidu|shopee|lazada|zalo|tokopedia|taobao|tmall|pinduoduo|"
    r"instagram|facebook|youtube|reels|shorts|linkedin|twitter|threads|snapchat)\b"
)


def strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return parts[2]
    return text


def tokens(text: str) -> List[str]:
    text = ENTITY.sub(" ", strip_frontmatter(text).lower())
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    return text.split()


def shingles(words: List[str], k: int = 8) -> set:
    return set(" ".join(words[i : i + k]) for i in range(max(0, len(words) - k + 1)))


def jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if a and b else 0.0


def is_agent(path: Path) -> bool:
    try:
        with path.open(encoding="utf-8") as fh:
            return fh.readline().strip() == "---"
    except OSError:
        return False


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _agent_dirs(root: Path) -> List[str]:
    divisions_path = root / "divisions.json"
    if not divisions_path.is_file():
        return []
    try:
        data = json.loads(divisions_path.read_text(encoding="utf-8"))
        return sorted(data.get("divisions", {}).keys())
    except (OSError, json.JSONDecodeError):
        return []


def build_corpus(root: Path) -> Dict[Path, set]:
    corpus: Dict[Path, set] = {}
    for d in _agent_dirs(root):
        for f in glob.glob(str(root / d / "**" / "*.md"), recursive=True):
            p = Path(f)
            if is_agent(p):
                try:
                    corpus[p.resolve()] = shingles(tokens(p.read_text(encoding="utf-8")))
                except OSError:
                    continue
    return corpus


def run_originality_check(
    files: Optional[List[Path]] = None,
    repo_root: Optional[Path] = None,
    fail_threshold: Optional[float] = None,
    warn_threshold: Optional[float] = None,
) -> int:
    """Run the check, print a report, return an exit code (0/1; 2 on bad input).

    ``files``: candidate paths (relative or absolute). Empty/None => audit all.
    """
    root = (repo_root or Path(os.environ.get("REPO_ROOT", "."))).resolve()
    fail = fail_threshold if fail_threshold is not None else float(os.environ.get("ORIGINALITY_FAIL", "40"))
    warn = warn_threshold if warn_threshold is not None else float(os.environ.get("ORIGINALITY_WARN", "20"))

    corpus = build_corpus(root)

    # Determine candidates
    if files:
        candidates: List[Path] = []
        for a in files:
            p = a if a.is_absolute() else (Path.cwd() / a)
            p = p.resolve()
            if not p.is_file():
                print(f"  skip (not found): {a}")
                continue
            if not is_agent(p):
                print(f"  skip (no frontmatter, not an agent): {rel(p, root)}")
                continue
            candidates.append(p)
    else:
        candidates = list(corpus.keys())

    if not candidates:
        print("No agent files to check.")
        return 0

    cand_sh = {p: corpus.get(p) or shingles(tokens(p.read_text(encoding="utf-8"))) for p in candidates}
    cand_set = set(candidates)

    worst = 0.0
    fails: List[Tuple[str, str, float]] = []
    warns: List[Tuple[str, str, float]] = []

    for p in candidates:
        sh = cand_sh[p]
        best_name, best_score = "", 0.0
        for cf, csh in corpus.items():
            if cf == p:
                continue
            s = jaccard(sh, csh)
            if s > best_score:
                best_name, best_score = rel(cf, root), s
        for op in candidates:
            if op == p:
                continue
            s = jaccard(sh, cand_sh[op])
            if s > best_score:
                best_name, best_score = rel(op, root) + " (same change set)", s

        pct = best_score * 100
        worst = max(worst, pct)
        tag = "OK   "
        if pct >= fail:
            tag = "FAIL "
            fails.append((rel(p, root), best_name, pct))
        elif pct >= warn:
            tag = "WARN "
            warns.append((rel(p, root), best_name, pct))
        print(f"  [{tag}] {pct:5.1f}%  {rel(p, root)}")
        if best_name:
            print(f"            closest: {best_name}")

    print()
    print(f"Thresholds: WARN >= {warn:.0f}%, FAIL >= {fail:.0f}%  "
          f"(existing-library baseline max ~1.5%)")

    if fails:
        print()
        print(f"FAILED: {len(fails)} agent(s) substantially duplicate existing content:")
        for name, match, pct in fails:
            print(f"  - {name}  ~{pct:.0f}% like  {match}")
        print()
        print("A new agent should be genuinely new. If this is intended market/platform")
        print("localization, make the body distinct (different platforms, tactics, examples)")
        print("rather than a find-replace of an existing agent.")
        return 1

    if warns:
        print(f"\n{len(warns)} warning(s) - review for overlap, but not blocking.")
    print("\nPASSED")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    paths = [Path(a) for a in args]
    return run_originality_check(paths if paths else None)


if __name__ == "__main__":
    sys.exit(main())
