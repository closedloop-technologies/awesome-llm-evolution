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
ENTRY_RE = re.compile(r"^- \[[^\]]+\]\(https?://[^)]+\) - .+\.$")
PLACEHOLDERS = ("[DOMAIN HERE]", "[more domain-specific tags]")


def fail(message: str) -> None:
    print(f"FAIL\t{message}")
    raise SystemExit(1)


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
    for heading in h2_headings:
        if f"[{heading}]" not in text:
            fail(f"Contents is missing heading: {heading}")

    links = LINK_RE.findall(text)
    urls = [url for _, url in links if "awesome.re/badge.svg" not in url]
    duplicates = sorted(url for url, count in Counter(urls).items() if count > 1)
    if duplicates:
        fail(f"duplicate URLs: {', '.join(duplicates)}")

    for index, line in enumerate(lines, start=1):
        if line.startswith("- [") and "](#" not in line and not ENTRY_RE.match(line):
            fail(f"line {index} has inconsistent linked-entry formatting")

    print(f"PASS\t{len(urls)} unique resource links across {len(h2_headings)} sections")
    return 0


if __name__ == "__main__":
    sys.exit(main())
