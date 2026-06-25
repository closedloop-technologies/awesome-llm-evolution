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
ENTRY_RE = re.compile(r"^- \[([^\]]+)\]\(https?://[^)]+\) - (.+)\.$")
ENTRY_LINK_RE = ENTRY_RE
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
    heading_anchor_counts = Counter(github_anchor(heading) for heading in h2_headings)
    duplicate_heading_anchors = sorted(
        anchor for anchor, count in heading_anchor_counts.items() if count > 1
    )
    if duplicate_heading_anchors:
        fail(f"duplicate section anchors: {', '.join(duplicate_heading_anchors)}")

    heading_anchors = {github_anchor(heading): heading for heading in h2_headings}
    contents_entries = []
    for line in lines:
        match = CONTENTS_LINK_RE.match(line)
        if match:
            contents_entries.append((match.group(1), match.group(2)))
    contents_anchors = {anchor: title for title, anchor in contents_entries}
    for anchor, heading in heading_anchors.items():
        if anchor not in contents_anchors:
            fail(f"Contents is missing heading: {heading}")
    for anchor, title in contents_anchors.items():
        if anchor not in heading_anchors:
            fail(f"Contents link has no matching heading: {title}")
        if title != heading_anchors[anchor]:
            fail(f"Contents title {title} does not match heading {heading_anchors[anchor]}")

    expected_contents = [(heading, github_anchor(heading)) for heading in h2_headings]
    if contents_entries != expected_contents:
        fail("Contents section order does not match README section order")

    current_section = None
    section_entries: dict[str, int] = {}
    for line in lines:
        if line.startswith("## ") and line.strip() not in {"## Contents"}:
            current_section = line.removeprefix("## ").strip()
            section_entries[current_section] = 0
            continue
        if current_section and ENTRY_LINK_RE.match(line):
            section_entries[current_section] += 1
    empty_sections = [section for section, count in section_entries.items() if count == 0]
    if empty_sections:
        fail(f"sections without resource entries: {', '.join(empty_sections)}")

    links = LINK_RE.findall(text)
    urls = [url for _, url in links if "awesome.re/badge.svg" not in url]
    for index, line in enumerate(lines, start=1):
        if "](http" in line and "https://awesome.re/badge.svg" not in line:
            if not ENTRY_RE.match(line):
                fail(f"line {index} has a non-entry HTTP link")
        entry = ENTRY_RE.match(line)
        if entry:
            title, description = entry.groups()
            if title != title.strip():
                fail(f"line {index} has an untrimmed linked title")
            if description != description.strip():
                fail(f"line {index} has an untrimmed entry description")
    duplicates = sorted(url for url, count in Counter(urls).items() if count > 1)
    if duplicates:
        fail(f"duplicate URLs: {', '.join(duplicates)}")
    resource_titles = [title for title, url in links if "awesome.re/badge.svg" not in url]
    duplicate_titles = sorted(
        title for title, count in Counter(resource_titles).items() if count > 1
    )
    if duplicate_titles:
        fail(f"duplicate linked titles: {', '.join(duplicate_titles)}")

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
