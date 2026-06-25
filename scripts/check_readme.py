#!/usr/bin/env python3
"""Offline README hygiene checks for the awesome list."""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


README = Path("README.md")
AGENTS = Path("AGENTS.md")
PLACEHOLDER_CHECK_FILES = (AGENTS, README, Path("contributing.md"))
LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")
HTTP_URL_RE = re.compile(r"https?://[^\s)]+")
ENTRY_RE = re.compile(r"^- \[([^\]]+)\]\(https://[^)]+\) - (.+)\.$")
ENTRY_LINK_RE = ENTRY_RE
CONTENTS_LINK_RE = re.compile(r"^- \[([^\]]+)\]\(#([^)]+)\)$")
PLACEHOLDERS = ("[DOMAIN HERE]", "[more domain-specific tags]")
PLACEHOLDER_HOSTS = {"example.com", "example.org", "example.net"}
TRACKING_QUERY_PARAMS = {"fbclid", "gclid", "igshid", "mc_cid", "mc_eid", "ref", "ref_src"}
TRACKING_QUERY_PREFIXES = ("utm_",)
MAX_TITLE_LENGTH = 80
MAX_DESCRIPTION_LENGTH = 180
SMALL_TITLE_WORDS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "but",
    "by",
    "for",
    "in",
    "nor",
    "of",
    "on",
    "or",
    "per",
    "the",
    "to",
    "via",
    "vs",
    "with",
}


def fail(message: str) -> None:
    print(f"FAIL\t{message}")
    raise SystemExit(1)


def github_anchor(heading: str) -> str:
    normalized = re.sub(r"[^a-z0-9 -]", "", heading.casefold())
    return normalized.replace(" ", "-")


def canonical_url(url: str) -> str:
    parsed = urlsplit(url)
    try:
        port = parsed.port
    except ValueError:
        port = None
    hostname = parsed.hostname.casefold() if parsed.hostname else parsed.netloc.casefold()
    default_port = (parsed.scheme.casefold(), port) in {("http", 80), ("https", 443)}
    netloc = hostname if port is None or default_port else f"{hostname}:{port}"
    filtered_query = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if key.casefold() not in TRACKING_QUERY_PARAMS
        and not key.casefold().startswith(TRACKING_QUERY_PREFIXES)
    ]
    path = re.sub(r"/+", "/", parsed.path).rstrip("/") or "/"
    return urlunsplit(
        (
            parsed.scheme.casefold(),
            netloc,
            path,
            urlencode(sorted(filtered_query)),
            "",
        )
    ).rstrip("/")


def canonical_title(title: str) -> str:
    return " ".join(title.split()).casefold()


def is_canonical_resource_url(url: str) -> bool:
    return url == canonical_url(url)


def url_host(url: str) -> str:
    match = re.match(r"https?://([^/?#]+)", url)
    return match.group(1).casefold() if match else ""


def is_title_case(heading: str) -> bool:
    words = re.findall(r"[A-Za-z][A-Za-z0-9+-]*", heading)
    for index, word in enumerate(words):
        if word.isupper():
            continue
        if index > 0 and word.casefold() in SMALL_TITLE_WORDS:
            continue
        if not word[0].isupper():
            return False
    return True


def has_bare_http_url(line: str) -> bool:
    for match in HTTP_URL_RE.finditer(line):
        if line[max(0, match.start() - 2):match.start()] != "](":
            return True
    return False


def main() -> int:
    text = README.read_text(encoding="utf-8")
    lines = text.splitlines()

    if "https://awesome.re/badge.svg" not in text:
        fail("README is missing the Awesome badge")

    if "## Contents" not in text:
        fail("README is missing a Contents section")

    for path in PLACEHOLDER_CHECK_FILES:
        if not path.exists():
            continue
        if not path.read_bytes().endswith(b"\n"):
            fail(f"{path} must end with a newline")
        file_text = path.read_text(encoding="utf-8")
        for placeholder in PLACEHOLDERS:
            if placeholder in file_text:
                fail(f"{path} still contains placeholder: {placeholder}")

    h2_headings = [
        line.removeprefix("## ").strip()
        for line in lines
        if line.startswith("## ") and line.strip() not in {"## Contents"}
    ]
    for index, line in enumerate(lines, start=1):
        if re.match(r"^#{2,3} ", line) and line.strip() != "## Contents":
            heading = line.lstrip("#").strip()
            if not is_title_case(heading):
                fail(f"line {index} has a non-title-case heading: {heading}")

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

    current_subsection = None
    subsection_entries: dict[str, int] = {}
    for line in lines:
        if line.startswith("## "):
            current_subsection = None
            continue
        if line.startswith("### "):
            current_subsection = line.removeprefix("### ").strip()
            subsection_entries[current_subsection] = 0
            continue
        if current_subsection and ENTRY_LINK_RE.match(line):
            subsection_entries[current_subsection] += 1
    empty_subsections = [
        subsection for subsection, count in subsection_entries.items() if count == 0
    ]
    if empty_subsections:
        fail(f"subsections without resource entries: {', '.join(empty_subsections)}")

    current_resource_section = None
    for index, line in enumerate(lines, start=1):
        if line.startswith("## "):
            heading = line.removeprefix("## ").strip()
            current_resource_section = None if heading == "Contents" else heading
            continue
        if ENTRY_LINK_RE.match(line) and current_resource_section is None:
            fail(f"line {index} has a resource entry outside a category section")

    links = LINK_RE.findall(text)
    urls = [url for _, url in links if "awesome.re/badge.svg" not in url]
    canonical_urls = [canonical_url(url) for url in urls]
    for index, line in enumerate(lines, start=1):
        if has_bare_http_url(line):
            fail(f"line {index} has a bare HTTP URL")
        if "](http" in line and "https://awesome.re/badge.svg" not in line:
            if not ENTRY_RE.match(line):
                fail(f"line {index} has a non-entry HTTP link")
        entry = ENTRY_RE.match(line)
        if entry:
            title, description = entry.groups()
            url = re.search(r"\((https?://[^)]+)\)", line).group(1)
            if title != title.strip():
                fail(f"line {index} has an untrimmed linked title")
            if len(title) > MAX_TITLE_LENGTH:
                fail(f"line {index} has an overlong linked title")
            if description != description.strip():
                fail(f"line {index} has an untrimmed entry description")
            if len(description) > MAX_DESCRIPTION_LENGTH:
                fail(f"line {index} has an overlong entry description")
            if url_host(url) in PLACEHOLDER_HOSTS:
                fail(f"line {index} uses a placeholder URL host: {url_host(url)}")
            if not is_canonical_resource_url(url):
                fail(f"line {index} has a non-canonical resource URL: {url}")
    duplicates = sorted(
        url for url, count in Counter(canonical_urls).items() if count > 1
    )
    if duplicates:
        fail(f"duplicate URLs: {', '.join(duplicates)}")
    resource_titles = [
        canonical_title(title) for title, url in links if "awesome.re/badge.svg" not in url
    ]
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
