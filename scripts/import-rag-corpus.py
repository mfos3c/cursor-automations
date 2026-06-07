#!/usr/bin/env python3
"""Import web3-rag-mcp content/*.json into Obsidian Web3-Security vault (60-corpus/)."""

from __future__ import annotations

import json
import re
import shutil
from collections import defaultdict
from datetime import date
from pathlib import Path

RAG_ROOT = Path("/Users/mfosec/web3-rag-mcp")
VAULT = Path("/Users/mfosec/Documents/Obsidian Vaults/Web3-Security")
CORPUS = VAULT / "60-corpus"
INDEX = VAULT / "00-index"

PROTOCOL_SLUGS = {
    p.stem.replace("-", " ").lower(): p.stem
    for p in (VAULT / "40-protocols").glob("*.md")
}


def slugify(name: str) -> str:
    s = re.sub(r"[^\w\s-]", "", name.lower())
    s = re.sub(r"[\s_]+", "-", s).strip("-")
    return s[:120] or "untitled"


def filename_from_record(rec: dict) -> str:
    slug = rec.get("slug") or rec.get("url", "untitled")
    base = slug.split("/")[-1]
    if not base.endswith(".md"):
        base = slugify(base) + ".md"
    return base


def guess_protocol_link(text: str, slug: str) -> str | None:
    hay = (text[:500] + " " + slug).lower()
    for key, stem in PROTOCOL_SLUGS.items():
        tokens = key.split()
        if len(tokens) >= 2 and all(t in hay for t in tokens[:2]):
            return f"[[40-protocols/{stem}]]"
        if tokens[0] in hay and len(tokens[0]) > 4:
            return f"[[40-protocols/{stem}]]"
    return None


def yaml_escape(s: str) -> str:
    return s.replace('"', '\\"')


def write_note(path: Path, front: dict, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["---"]
    for k, v in front.items():
        if isinstance(v, list):
            lines.append(f"{k}:")
            for item in v:
                lines.append(f"  - {item}")
        else:
            lines.append(f'{k}: "{yaml_escape(str(v))}"' if "\n" in str(v) else f"{k}: {v}")
    lines.append("---")
    lines.append("")
    lines.append(body.strip())
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def import_json_corpus() -> dict[str, list[str]]:
    by_category: dict[str, list[str]] = defaultdict(list)
    content_dir = RAG_ROOT / "content"
    for fp in sorted(content_dir.glob("*.json")):
        rec = json.loads(fp.read_text(encoding="utf-8"))
        category = rec.get("category") or "other"
        platform = rec.get("platform") or "unknown"
        kind = rec.get("kind") or "unknown"
        url = rec.get("url", "")
        text = rec.get("text", "")
        title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else filename_from_record(rec)[:-3]

        rel = CORPUS / category / platform / filename_from_record(rec)
        protocol_link = guess_protocol_link(text, rec.get("slug", ""))
        tags = [
            "web3/corpus",
            f"web3/corpus/{category}",
            f"web3/platform/{platform}",
        ]
        related: list[str] = []
        if protocol_link:
            related.append(protocol_link)

        front = {
            "title": title,
            "tags": tags,
            "source_url": url,
            "category": category,
            "platform": platform,
            "kind": kind,
            "updated": str(date.today()),
        }
        if related:
            front["related"] = related

        header = f"# {title}\n\n"
        if url:
            header += f"Source: {url}\n\n"
        if protocol_link:
            header += f"Protocol: {protocol_link}\n\n"
        header += "---\n\n"

        write_note(rel, front, header + text)
        note_link = f"[[{rel.relative_to(VAULT).with_suffix('')}]]"
        by_category[f"{category}/{platform}"].append(note_link)
    return by_category


def write_mocs(by_category: dict[str, list[str]]) -> None:
    INDEX.mkdir(parents=True, exist_ok=True)

    hub = [
        "---",
        "title: Web3 Graph Hub",
        "tags:",
        "  - web3/index",
        "  - web3/moc",
        f"updated: '{date.today()}'",
        "---",
        "",
        "# Web3 Graph Hub",
        "",
        "Central map for bounty pipeline + RAG corpus.",
        "",
        "## Pipeline (automations)",
        "- [[20-bounties/|Daily picks]]",
        "- [[30-findings/|Findings & scan output]]",
        "- [[40-protocols/|Protocol MOCs]]",
        "- [[50-reference/cursor-automations-bounty-playbook|Automation playbook]]",
        "",
        "## RAG corpus (imported from web3-rag-mcp)",
        "",
    ]
    for cat_plat in sorted(by_category):
        cat, plat = cat_plat.split("/", 1)
        moc_name = f"Corpus — {cat} — {plat}"
        moc_path = INDEX / f"Corpus {cat} {plat}.md"
        links = by_category[cat_plat]
        moc_body = [
            "---",
            f"title: {moc_name}",
            "tags:",
            "  - web3/moc",
            f"  - web3/corpus/{cat}",
            f"updated: '{date.today()}'",
            "---",
            "",
            f"# {moc_name}",
            "",
            f"_{len(links)} notes_",
            "",
        ]
        for link in sorted(links):
            moc_body.append(f"- {link}")
        moc_body.append("")
        moc_path.write_text("\n".join(moc_body), encoding="utf-8")
        hub.append(f"- [[{moc_path.relative_to(VAULT).with_suffix('')}|{moc_name}]] ({len(links)})")

    hub.extend(
        [
            "",
            "## Bug-class radar (findings)",
            "",
        ]
    )
    for f in sorted((VAULT / "30-findings").glob("*.md")):
        if f.name.startswith("."):
            continue
        hub.append(f"- [[{f.relative_to(VAULT).with_suffix('')}]]")

    (INDEX / "Web3 Graph Hub.md").write_text("\n".join(hub) + "\n", encoding="utf-8")


def copy_reference_files() -> None:
    ref = VAULT / "50-reference"
    ref.mkdir(parents=True, exist_ok=True)
    for name in ("methodology.md", "README.md"):
        src = RAG_ROOT / name
        if src.exists():
            dst = ref / ("web3-rag-methodology.md" if name == "methodology.md" else "web3-rag-readme.md")
            if not dst.exists() or src.stat().st_mtime > dst.stat().st_mtime:
                shutil.copy2(src, dst)


def main() -> None:
    if not RAG_ROOT.is_dir():
        raise SystemExit(f"RAG root missing: {RAG_ROOT}")
    if not VAULT.is_dir():
        raise SystemExit(f"Vault missing: {VAULT}")

    print(f"Importing {RAG_ROOT}/content/*.json → {CORPUS}")
    grouped = import_json_corpus()
    write_mocs(grouped)
    copy_reference_files()
    total = sum(len(v) for v in grouped.values())
    print(f"Done: {total} corpus notes, {len(grouped)} MOC sections, hub at 00-index/Web3 Graph Hub.md")


if __name__ == "__main__":
    main()
