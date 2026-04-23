#!/usr/bin/env python3
"""Deterministic vault health check.

Mirrors the checks in Plugins-tatoflam/claude-wiki/skills/wiki-lint/SKILL.md
but runs without any LLM — pure filesystem + regex + frontmatter parsing.

Invoked by .github/workflows/wiki-lint.yml on a daily cron. Also runnable
locally:  VAULT_DIR=. python3 .github/scripts/wiki-lint.py

Outputs:
- A markdown report to stdout (piped into $GITHUB_STEP_SUMMARY in CI).
- One appended line to <vault>/log.md documenting the run.
- Exit 1 if any *critical* finding (contradictions, broken links);
  exit 0 otherwise (warnings like orphans/stale/stuck-inbox are non-fatal).
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


VAULT = Path(os.environ.get("VAULT_DIR", ".")).resolve()

NONDIARY_CATEGORIES = ("00_self", "03_work", "04_life", "05_learn", "06_output", "07_archive")
EXCLUDE_ROOT_MD = {"_schema.md", "index.md", "log.md", "ようこそ.md", "make folders composition.md"}
STUCK_INBOX_DAYS = 14
STALE_DAYS = 90

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
CONTRADICTION_RE = re.compile(r"\[!warning\]\s*Contradiction", re.IGNORECASE)
NEEDS_SORTING_RE = re.compile(r"\[!question\]\s*Needs sorting", re.IGNORECASE)


def parse_frontmatter(text: str) -> dict[str, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm


def collect_pages() -> dict[Path, str]:
    pages: dict[Path, str] = {}
    for p in VAULT.rglob("*.md"):
        rel = p.relative_to(VAULT)
        parts = rel.parts
        if parts[0] in {".git", ".obsidian", ".github"}:
            continue
        if len(parts) == 1 and parts[0] in EXCLUDE_ROOT_MD:
            continue
        pages[rel] = p.read_text(encoding="utf-8")
    return pages


def slugs_for(rel: Path) -> list[str]:
    s = rel.with_suffix("").as_posix()
    return [s, rel.stem]


def check_contradictions(pages):
    hits = []
    for rel, content in pages.items():
        if CONTRADICTION_RE.search(content):
            fm = parse_frontmatter(content)
            hits.append((rel.as_posix(), fm.get("sources", "")))
    return hits


def check_stuck_inbox(pages):
    now = datetime.now(timezone.utc)
    hits = []
    for rel, content in pages.items():
        if rel.parts[0] != "01_inbox":
            continue
        full = VAULT / rel
        age_days = (now - datetime.fromtimestamp(full.stat().st_mtime, tz=timezone.utc)).days
        has_question = bool(NEEDS_SORTING_RE.search(content))
        if age_days > STUCK_INBOX_DAYS or has_question:
            hits.append((rel.as_posix(), age_days, has_question))
    return hits


def check_orphans(pages):
    inbound: dict[Path, set[Path]] = {rel: set() for rel in pages}
    for src_rel, content in pages.items():
        for m in WIKILINK_RE.finditer(content):
            target = m.group(1).strip()
            for cand_rel in pages:
                if cand_rel == src_rel:
                    continue
                if target in slugs_for(cand_rel):
                    inbound[cand_rel].add(src_rel)
                    break
    orphans = []
    for rel in pages:
        if rel.parts[0] not in NONDIARY_CATEGORIES:
            continue
        if not inbound[rel]:
            orphans.append(rel.as_posix())
    return orphans


def check_stale(pages):
    now = datetime.now(timezone.utc)
    hits = []
    for rel, content in pages.items():
        if rel.parts[0] not in NONDIARY_CATEGORIES:
            continue
        fm = parse_frontmatter(content)
        u = fm.get("updated", "")
        try:
            ud = datetime.fromisoformat(u).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        if (now - ud).days > STALE_DAYS:
            hits.append((rel.as_posix(), u))
    return hits


def check_missing_frontmatter(pages):
    required = ("title", "category", "updated", "sources")
    hits = []
    for rel, content in pages.items():
        if rel.parts[0] == "02_diary":
            continue
        fm = parse_frontmatter(content)
        missing = [k for k in required if k not in fm]
        if missing:
            hits.append((rel.as_posix(), missing))
    return hits


def check_broken_links(pages):
    all_slugs: set[str] = set()
    for rel in pages:
        for s in slugs_for(rel):
            all_slugs.add(s)
    broken = []
    for src_rel, content in pages.items():
        for m in WIKILINK_RE.finditer(content):
            target = m.group(1).strip()
            if target not in all_slugs:
                broken.append((src_rel.as_posix(), target))
    return broken


def check_duplicate_titles(pages):
    by_title: dict[str, list[str]] = {}
    for rel, content in pages.items():
        fm = parse_frontmatter(content)
        t = fm.get("title")
        if t:
            by_title.setdefault(t, []).append(rel.as_posix())
    return {t: lst for t, lst in by_title.items() if len(lst) > 1}


def check_diary_gaps(pages):
    log_path = Path.home() / ".claude" / "wiki" / "state" / "ingest-log.jsonl"
    if not log_path.exists():
        return []
    session_days: set[str] = set()
    for line in log_path.read_text(encoding="utf-8").splitlines():
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get("source_type") != "session":
            continue
        ts = d.get("ts", "")
        if ts[:10]:
            session_days.add(ts[:10])
    diary_days = {rel.stem for rel in pages if rel.parts[0] == "02_diary"}
    return sorted(session_days - diary_days)


def check_git_state() -> str:
    import subprocess
    try:
        out = subprocess.check_output(
            ["git", "-C", str(VAULT), "status", "--porcelain"], text=True
        )
    except Exception:
        return "not a git repo"
    count = sum(1 for line in out.splitlines() if line.strip())
    return "clean" if count == 0 else f"{count} uncommitted"


def render_report(findings) -> str:
    lines = ["# Wiki lint report", ""]
    lines.append(f"_Generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}_")
    lines.append(f"_Vault: `{VAULT}`_")
    lines.append("")

    c = findings["contradictions"]
    lines.append(f"## Contradictions ({len(c)})")
    for rel, src in c:
        lines.append(f"- `{rel}` (sources: {src or 'n/a'})")
    lines.append("")

    si = findings["stuck_inbox"]
    lines.append(f"## Stuck inbox ({len(si)})")
    for rel, age, q in si:
        tag = " [needs sorting]" if q else ""
        lines.append(f"- `{rel}` ({age} days old){tag}")
    lines.append("")

    o = findings["orphans"]
    lines.append(f"## Orphans ({len(o)})")
    for rel in o:
        lines.append(f"- `{rel}`")
    lines.append("")

    s = findings["stale"]
    lines.append(f"## Stale ({len(s)})")
    for rel, u in s:
        lines.append(f"- `{rel}` (updated: {u})")
    lines.append("")

    mf = findings["missing_frontmatter"]
    lines.append(f"## Missing frontmatter ({len(mf)})")
    for rel, keys in mf:
        lines.append(f"- `{rel}` missing: {', '.join(keys)}")
    lines.append("")

    bl = findings["broken_links"]
    lines.append(f"## Broken links ({len(bl)})")
    for rel, target in bl:
        lines.append(f"- `{rel}` → `[[{target}]]`")
    lines.append("")

    dt = findings["duplicate_titles"]
    lines.append(f"## Duplicate titles ({len(dt)})")
    for t, lst in dt.items():
        lines.append(f"- `{t}`: {', '.join(f'`{p}`' for p in lst)}")
    lines.append("")

    dg = findings["diary_gaps"]
    lines.append(f"## Diary gaps ({len(dg)})")
    for d in dg:
        lines.append(f"- {d}")
    lines.append("")

    lines.append(f"## Git")
    lines.append(f"- {findings['git_state']}")
    lines.append("")

    return "\n".join(lines)


def append_log_md(findings):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    summary = (
        f"contradictions={len(findings['contradictions'])} "
        f"orphans={len(findings['orphans'])} "
        f"stale={len(findings['stale'])} "
        f"broken={len(findings['broken_links'])} "
        f"stuck-inbox={len(findings['stuck_inbox'])}"
    )
    line = f"- {ts}  op:lint    {summary}\n"
    log_path = VAULT / "log.md"
    if not log_path.exists():
        log_path.write_text("# Log\n\n", encoding="utf-8")
    with log_path.open("a", encoding="utf-8") as f:
        f.write(line)


def main() -> int:
    pages = collect_pages()
    findings = {
        "contradictions": check_contradictions(pages),
        "stuck_inbox": check_stuck_inbox(pages),
        "orphans": check_orphans(pages),
        "stale": check_stale(pages),
        "missing_frontmatter": check_missing_frontmatter(pages),
        "broken_links": check_broken_links(pages),
        "duplicate_titles": check_duplicate_titles(pages),
        "diary_gaps": check_diary_gaps(pages),
        "git_state": check_git_state(),
    }

    report = render_report(findings)
    print(report)

    append_log_md(findings)

    critical = len(findings["contradictions"]) + len(findings["broken_links"])
    return 1 if critical > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
