#!/usr/bin/env python3
"""Offline README hygiene checks for the awesome list."""

from __future__ import annotations

import re
import socket
import sys
from collections import Counter
from ipaddress import IPv4Address, ip_address
from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlencode, urlsplit, urlunsplit


README = Path("README.md")
AGENTS = Path("AGENTS.md")
PLACEHOLDER_CHECK_FILES = (AGENTS, README, Path("contributing.md"))
LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")
HTTP_URL_RE = re.compile(r"https?://[^\s)]+", re.IGNORECASE)
MARKDOWN_HTTP_LINK_RE = re.compile(r"\]\(https?://", re.IGNORECASE)
ENTRY_RE = re.compile(r"^- \[([^\]]+)\]\(https?://[^)]+\) - (.+)\.$")
ENTRY_LINK_RE = ENTRY_RE
CONTENTS_LINK_RE = re.compile(r"^- \[([^\]]+)\]\(#([^)]+)\)$")
PLACEHOLDERS = ("[DOMAIN HERE]", "[more domain-specific tags]")
PLACEHOLDER_HOSTS = {"example.com", "example.org", "example.net"}
LOCAL_RESOURCE_HOSTS = {"0.0.0.0", "127.0.0.1", "::1", "localhost"}
TRACKING_QUERY_PARAMS = {"fbclid", "gclid", "igshid", "mc_cid", "mc_eid", "ref", "ref_src"}
TRACKING_QUERY_PREFIXES = ("utm_",)
ENCODED_PATH_SEPARATOR_RE = re.compile(r"%2f|%5c", re.IGNORECASE)
MALFORMED_PERCENT_ENCODING_RE = re.compile(r"%(?![0-9A-Fa-f]{2})")
HOST_LABEL_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$", re.IGNORECASE)
MAX_TITLE_LENGTH = 80
MAX_DESCRIPTION_LENGTH = 180
GENERIC_LINK_TITLES = {
    "article",
    "blog post",
    "code",
    "demo",
    "docs",
    "github",
    "paper",
    "project",
    "repository",
    "repo",
    "resource",
    "website",
}
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
    try:
        parsed = urlsplit(url)
    except ValueError:
        return url
    try:
        port = parsed.port
    except ValueError:
        return url
    hostname = (
        parsed.hostname.rstrip(".").casefold()
        if parsed.hostname
        else parsed.netloc.rstrip(".").casefold()
    )
    default_port = (parsed.scheme.casefold(), port) in {("http", 80), ("https", 443)}
    canonical_hostname = f"[{hostname}]" if ":" in hostname else hostname
    netloc = (
        canonical_hostname
        if port is None or default_port
        else f"{canonical_hostname}:{port}"
    )
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


def has_descriptive_link_title(title: str) -> bool:
    return canonical_title(title) not in GENERIC_LINK_TITLES


def has_normalized_inline_whitespace(value: str) -> bool:
    return value == " ".join(value.split())


def has_trailing_whitespace(line: str) -> bool:
    return line.endswith((" ", "\t"))


def has_control_character(line: str) -> bool:
    return any(ord(character) < 32 or ord(character) == 127 for character in line)


def has_noncanonical_horizontal_rule(line: str) -> bool:
    return bool(re.fullmatch(r"(?:\*\s*){3,}|(?:_\s*){3,}", line.strip()))


def is_canonical_resource_url(url: str) -> bool:
    return url == canonical_url(url)


def safe_urlsplit(url: str):
    try:
        return urlsplit(url)
    except ValueError:
        return None


def url_host(url: str) -> str:
    parsed = safe_urlsplit(url)
    if parsed is None:
        return ""
    return (parsed.hostname or "").rstrip(".").casefold()


def has_valid_url_port(url: str) -> bool:
    try:
        parsed = urlsplit(url)
        port = parsed.port
    except ValueError:
        return False
    if parsed.netloc.rsplit("@", 1)[-1].endswith(":"):
        return False
    if port == 0:
        return False
    return True


def has_parseable_url(url: str) -> bool:
    try:
        urlsplit(url)
    except ValueError:
        return False
    return True


def has_url_host(url: str) -> bool:
    return bool(url_host(url))


def has_url_host_percent_encoding(url: str) -> bool:
    parsed = safe_urlsplit(url)
    if parsed is None:
        return False
    return "%" in (parsed.hostname or "")


def has_valid_url_host_syntax(host: str) -> bool:
    if not host or len(host) > 253:
        return False
    try:
        ip_address(host)
    except ValueError:
        labels = host.split(".")
        return (
            len(labels) >= 2
            and not labels[-1].isdigit()
            and all(HOST_LABEL_RE.fullmatch(label) for label in labels)
        )
    return True


def has_url_credentials(url: str) -> bool:
    parsed = safe_urlsplit(url)
    if parsed is None:
        return False
    return parsed.username is not None or parsed.password is not None


def has_url_whitespace(url: str) -> bool:
    return any(character.isspace() for character in url)


def has_encoded_url_control_character(url: str) -> bool:
    decoded = url
    for _ in range(3):
        previous = decoded
        decoded = unquote(previous)
        if any(ord(character) < 32 or ord(character) == 127 for character in decoded):
            return True
        if decoded == previous:
            return False
    return False


def has_malformed_percent_encoding(url: str) -> bool:
    return bool(MALFORMED_PERCENT_ENCODING_RE.search(url))


def has_encoded_url_whitespace(url: str) -> bool:
    return any(character.isspace() for character in unquote(url))


def has_encoded_url_path_separator(url: str) -> bool:
    parsed = safe_urlsplit(url)
    return parsed is not None and bool(ENCODED_PATH_SEPARATOR_RE.search(parsed.path))


def has_encoded_url_query_or_fragment_marker(url: str) -> bool:
    parsed = safe_urlsplit(url)
    if parsed is None:
        return False
    path = parsed.path
    decoded_path = unquote(path)
    return decoded_path != path and ("?" in decoded_path or "#" in decoded_path)


def has_encoded_url_path_alias(url: str) -> bool:
    parsed = safe_urlsplit(url)
    if parsed is None:
        return False
    path = parsed.path
    return unquote(path) != path


def has_url_backslash(url: str) -> bool:
    return "\\" in url


def has_url_parent_directory_reference(url: str) -> bool:
    parsed = safe_urlsplit(url)
    return parsed is not None and ".." in Path(unquote(parsed.path)).parts


def has_url_current_directory_reference(url: str) -> bool:
    parsed = safe_urlsplit(url)
    return parsed is not None and "." in unquote(parsed.path).split("/")


def is_placeholder_host(host: str) -> bool:
    return host in PLACEHOLDER_HOSTS or any(
        host.endswith(f".{placeholder}") for placeholder in PLACEHOLDER_HOSTS
    )


def parse_legacy_ipv4_address(host: str) -> IPv4Address | None:
    try:
        packed_address = socket.inet_aton(host)
    except OSError:
        return None
    try:
        return IPv4Address(packed_address)
    except ValueError:
        return None


def is_local_resource_host(host: str) -> bool:
    if host in LOCAL_RESOURCE_HOSTS:
        return True
    try:
        address = ip_address(host)
    except ValueError:
        address = parse_legacy_ipv4_address(host)
        if address is None:
            return False
    return (
        address.is_private
        or address.is_loopback
        or address.is_link_local
        or address.is_unspecified
        or not address.is_global
    )


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


def has_markdown_http_link(line: str) -> bool:
    return bool(MARKDOWN_HTTP_LINK_RE.search(line))


def duplicate_values(values: list[str]) -> list[str]:
    return sorted(value for value, count in Counter(values).items() if count > 1)


def h1_headings(lines: list[str]) -> list[str]:
    return [line.removeprefix("# ").strip() for line in lines if line.startswith("# ")]


def contents_precedes_categories(lines: list[str]) -> bool:
    contents_index = next(
        (index for index, line in enumerate(lines) if line.strip() == "## Contents"),
        None,
    )
    if contents_index is None:
        return False
    first_category_index = next(
        (
            index
            for index, line in enumerate(lines)
            if line.startswith("## ") and line.strip() != "## Contents"
        ),
        None,
    )
    return first_category_index is None or contents_index < first_category_index


def markdown_spacing_violations(lines: list[str]) -> list[str]:
    violations = []
    for index, line in enumerate(lines):
        line_number = index + 1
        previous_line = lines[index - 1] if index > 0 else ""
        next_line = lines[index + 1] if index + 1 < len(lines) else ""
        if re.match(r"^#{1,3} ", line):
            if previous_line:
                violations.append(
                    f"line {line_number} heading is missing a blank line before it"
                )
            if next_line:
                violations.append(
                    f"line {line_number} heading is missing a blank line after it"
                )
        if ENTRY_LINK_RE.match(line):
            if previous_line:
                violations.append(
                    f"line {line_number} resource entry is missing a blank line before it"
                )
            if next_line:
                violations.append(
                    f"line {line_number} resource entry is missing a blank line after it"
                )
    return violations


def resource_order_violations(lines: list[str]) -> list[str]:
    violations = []
    current_section = "README"
    section_entries: list[tuple[int, str]] = []

    def check_section() -> None:
        if len(section_entries) <= 1:
            return
        titles = [title for _, title in section_entries]
        sorted_titles = sorted(titles, key=str.casefold)
        if titles != sorted_titles:
            first_line = section_entries[0][0]
            violations.append(
                "linked entries in "
                f"{current_section} starting on line {first_line} "
                f"are not alphabetized: {', '.join(titles)}"
            )

    for index, line in enumerate(lines + ["# END"], start=1):
        if re.match(r"^#{1,3} ", line):
            check_section()
            current_section = line.lstrip("#").strip()
            section_entries = []
            continue
        match = ENTRY_LINK_RE.match(line)
        if match:
            section_entries.append((index, match.group(1)))

    return violations


def main() -> int:
    text = README.read_text(encoding="utf-8")
    lines = text.splitlines()

    headings = h1_headings(lines)
    if len(headings) != 1:
        fail("README must contain exactly one H1 heading")
    if not headings[0].startswith("Awesome LLM Evolution"):
        fail("README H1 must start with Awesome LLM Evolution")

    if "https://awesome.re/badge.svg" not in text:
        fail("README is missing the Awesome badge")

    if "## Contents" not in text:
        fail("README is missing a Contents section")
    if not contents_precedes_categories(lines):
        fail("README Contents section must appear before category sections")
    spacing_violations = markdown_spacing_violations(lines)
    if spacing_violations:
        fail(spacing_violations[0])

    for path in PLACEHOLDER_CHECK_FILES:
        if not path.exists():
            continue
        if not path.read_bytes().endswith(b"\n"):
            fail(f"{path} must end with a newline")
        file_text = path.read_text(encoding="utf-8")
        for line_index, line in enumerate(file_text.splitlines(), start=1):
            if has_control_character(line):
                fail(f"{path}:{line_index} has control characters")
            if has_trailing_whitespace(line):
                fail(f"{path}:{line_index} has trailing whitespace")
            if has_noncanonical_horizontal_rule(line):
                fail(f"{path}:{line_index} uses a non-canonical horizontal rule")
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

    section_heading_anchors = [
        github_anchor(line.lstrip("#").strip())
        for line in lines
        if re.match(r"^#{2,3} ", line) and line.strip() != "## Contents"
    ]
    duplicate_section_heading_anchors = sorted(
        anchor
        for anchor, count in Counter(section_heading_anchors).items()
        if count > 1
    )
    if duplicate_section_heading_anchors:
        fail(
            "duplicate section or subsection anchors: "
            f"{', '.join(duplicate_section_heading_anchors)}"
        )

    heading_anchors = {github_anchor(heading): heading for heading in h2_headings}
    contents_entries = []
    for line in lines:
        match = CONTENTS_LINK_RE.match(line)
        if match:
            contents_entries.append((match.group(1), match.group(2)))
    contents_anchors = {anchor: title for title, anchor in contents_entries}
    duplicate_contents_anchors = duplicate_values([anchor for _, anchor in contents_entries])
    if duplicate_contents_anchors:
        fail(f"duplicate Contents anchors: {', '.join(duplicate_contents_anchors)}")
    duplicate_contents_titles = duplicate_values([title for title, _ in contents_entries])
    if duplicate_contents_titles:
        fail(f"duplicate Contents titles: {', '.join(duplicate_contents_titles)}")
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
        if has_markdown_http_link(line) and "https://awesome.re/badge.svg" not in line:
            if not ENTRY_RE.match(line):
                fail(f"line {index} has a non-entry HTTP link")
        entry = ENTRY_RE.match(line)
        if entry:
            title, description = entry.groups()
            url = re.search(r"\((https?://[^)]+)\)", line).group(1)
            if not url.startswith("https://"):
                fail(f"line {index} uses a non-HTTPS resource URL: {url}")
            if not has_parseable_url(url):
                fail(f"line {index} has a malformed resource URL: {url}")
            if has_url_whitespace(url):
                fail(f"line {index} has a resource URL with whitespace: {url}")
            if has_malformed_percent_encoding(url):
                fail(f"line {index} has a resource URL with malformed percent encoding: {url}")
            if has_encoded_url_control_character(url):
                fail(f"line {index} has a resource URL with encoded control characters: {url}")
            if has_encoded_url_whitespace(url):
                fail(f"line {index} has a resource URL with encoded whitespace: {url}")
            if has_url_backslash(url):
                fail(f"line {index} has a resource URL with backslashes: {url}")
            if has_encoded_url_path_separator(url):
                fail(f"line {index} has a resource URL with encoded path separators: {url}")
            if has_encoded_url_query_or_fragment_marker(url):
                fail(
                    f"line {index} has a resource URL with encoded query "
                    f"or fragment markers: {url}"
                )
            if has_encoded_url_path_alias(url):
                fail(f"line {index} has a resource URL with encoded path aliases: {url}")
            if has_url_parent_directory_reference(url):
                fail(f"line {index} has a resource URL with parent directory references: {url}")
            if has_url_current_directory_reference(url):
                fail(f"line {index} has a resource URL with current directory references: {url}")
            if title != title.strip():
                fail(f"line {index} has an untrimmed linked title")
            if not has_normalized_inline_whitespace(title):
                fail(f"line {index} has repeated whitespace in linked title")
            if len(title) > MAX_TITLE_LENGTH:
                fail(f"line {index} has an overlong linked title")
            if not has_descriptive_link_title(title):
                fail(f"line {index} has a generic linked title: {title}")
            if description != description.strip():
                fail(f"line {index} has an untrimmed entry description")
            if not has_normalized_inline_whitespace(description):
                fail(f"line {index} has repeated whitespace in entry description")
            if len(description) > MAX_DESCRIPTION_LENGTH:
                fail(f"line {index} has an overlong entry description")
            host = url_host(url)
            if not host:
                fail(f"line {index} has a resource URL without a host: {url}")
            if has_url_host_percent_encoding(url):
                fail(f"line {index} has a resource URL with an encoded host: {url}")
            if not has_valid_url_port(url):
                fail(f"line {index} has a resource URL with an invalid port: {url}")
            if not has_valid_url_host_syntax(host):
                fail(f"line {index} has a malformed resource URL host: {host}")
            if has_url_credentials(url):
                fail(f"line {index} has a resource URL with embedded credentials: {url}")
            if is_placeholder_host(host):
                fail(f"line {index} uses a placeholder URL host: {host}")
            if is_local_resource_host(host):
                fail(f"line {index} uses a local-only URL host: {host}")
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

    order_violations = resource_order_violations(lines)
    if order_violations:
        fail(order_violations[0])

    print(f"PASS\t{len(urls)} unique resource links across {len(h2_headings)} sections")
    return 0


if __name__ == "__main__":
    sys.exit(main())
