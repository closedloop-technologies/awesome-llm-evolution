#!/usr/bin/env python3
"""Offline README hygiene checks for the awesome list."""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path


README = Path("README.md")
AGENTS = Path("AGENTS.md")
LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")
ENTRY_LINK_RE = re.compile(r"^- \[([^\]]+)\]\(https?://[^)]+\) - .+\.$")
ENTRY_RE = re.compile(r"^- \[[^\]]+\]\(https?://[^)]+\) - .+\.$")
CONTENTS_LINK_RE = re.compile(r"^- \[([^\]]+)\]\(#([^)]+)\)$")
PLACEHOLDERS = ("[DOMAIN HERE]", "[more domain-specific tags]")


def fail(message: str) -> None:
    print(f"FAIL\t{message}")
    raise SystemExit(1)


def github_anchor(heading: str) -> str:
    normalized = re.sub(r"[^a-z0-9 -]", "", heading.casefold())
    return normalized.replace(" ", "-")


def main() -> int:
    text = README.read_text(encoding="utf-8")
    lines = text.splitlines()

    if "https://awesome.re/badge.svg" not in text:
        fail("README is missing the Awesome badge")

    if "## Contents" not in text:
        fail("README is missing a Contents section")

    if AGENTS.exists():
        agents_text = AGENTS.read_text(encoding="utf-8")
        for placeholder in PLACEHOLDERS:
            if placeholder in agents_text:
                fail(f"AGENTS.md still contains placeholder: {placeholder}")

    h2_headings = [
        line.removeprefix("## ").strip()
        for line in lines
        if line.startswith("## ") and line.strip() not in {"## Contents"}
    ]
    heading_anchors = {github_anchor(heading): heading for heading in h2_headings}
    contents_anchors = {}
    for line in lines:
        match = CONTENTS_LINK_RE.match(line)
        if match:
            contents_anchors[match.group(2)] = match.group(1)
    for anchor, heading in heading_anchors.items():
        if anchor not in contents_anchors:
            fail(f"Contents is missing heading: {heading}")
    for anchor, title in contents_anchors.items():
        if anchor not in heading_anchors:
            fail(f"Contents link has no matching heading: {title}")

    links = LINK_RE.findall(text)
    urls = [url for _, url in links if "awesome.re/badge.svg" not in url]
    duplicates = sorted(url for url, count in Counter(urls).items() if count > 1)
    if duplicates:
        fail(f"duplicate URLs: {', '.join(duplicates)}")

    for index, line in enumerate(lines, start=1):
        if line.startswith("- [") and "](#" not in line and not ENTRY_RE.match(line):
            fail(f"line {index} has inconsistent linked-entry formatting")

    current_block: list[tuple[int, str]] = []
    for index, line in enumerate(lines + [""], start=1):
        match = ENTRY_LINK_RE.match(line)
        if match:
            current_block.append((index, match.group(1)))
            continue
        if len(current_block) > 1:
            titles = [title for _, title in current_block]
            sorted_titles = sorted(titles, key=str.casefold)
            if titles != sorted_titles:
                first_line = current_block[0][0]
                fail(
                    "linked entries starting on line "
                    f"{first_line} are not alphabetized: {', '.join(titles)}"
                )
        current_block = []

    print(f"PASS\t{len(urls)} unique resource links across {len(h2_headings)} sections")
    return 0


if __name__ == "__main__":
    sys.exit(main())
