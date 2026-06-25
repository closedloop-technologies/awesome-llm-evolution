from scripts.check_readme import (
    ENTRY_RE,
    canonical_title,
    canonical_url,
    github_anchor,
    h1_headings,
    has_bare_http_url,
    has_normalized_inline_whitespace,
    is_placeholder_host,
    is_canonical_resource_url,
    url_host,
)


def test_canonical_url_ignores_tracking_parameters_and_fragments():
    assert (
        canonical_url("https://Example.com/project/?utm_source=newsletter&ref=github#readme")
        == "https://example.com/project"
    )


def test_canonical_url_preserves_meaningful_query_parameters():
    assert (
        canonical_url("https://example.com/search?b=2&utm_medium=email&a=1")
        == "https://example.com/search?a=1&b=2"
    )


def test_canonical_url_removes_default_ports():
    assert canonical_url("https://Example.com:443/project/") == "https://example.com/project"


def test_canonical_url_preserves_non_default_ports():
    assert canonical_url("https://example.com:8443/project") == "https://example.com:8443/project"


def test_canonical_url_collapses_repeated_path_slashes():
    assert canonical_url("https://example.com//project///paper/") == "https://example.com/project/paper"


def test_canonical_title_ignores_case_and_extra_spaces():
    assert canonical_title("  Alpha   Evolve ") == "alpha evolve"


def test_canonical_title_preserves_meaningful_words():
    assert canonical_title("Tree-of-Thoughts") == "tree-of-thoughts"


def test_has_normalized_inline_whitespace_rejects_repeated_spaces():
    assert has_normalized_inline_whitespace("Alpha Evolve")
    assert not has_normalized_inline_whitespace("Alpha  Evolve")


def test_github_anchor_strips_punctuation_and_collapses_case():
    assert github_anchor("Code & Algorithm Discovery!") == "code--algorithm-discovery"


def test_h1_headings_returns_top_level_headings_only():
    assert h1_headings(["# Awesome LLM Evolution", "## Contents"]) == [
        "Awesome LLM Evolution"
    ]


def test_is_canonical_resource_url_accepts_normalized_urls():
    assert is_canonical_resource_url("https://example.com/project?a=1&b=2")


def test_is_canonical_resource_url_rejects_tracking_and_fragments():
    assert not is_canonical_resource_url(
        "https://Example.com/project/?utm_source=newsletter#readme"
    )


def test_has_bare_http_url_accepts_markdown_links():
    assert not has_bare_http_url("- [Project](https://example.com/project) - Description.")


def test_has_bare_http_url_rejects_plain_urls():
    assert has_bare_http_url("See https://example.com/project for details.")


def test_url_host_ignores_ports_for_placeholder_host_detection():
    assert url_host("https://example.com:8443/project") == "example.com"


def test_is_placeholder_host_rejects_example_subdomains():
    assert is_placeholder_host("docs.example.com")


def test_is_placeholder_host_accepts_real_hosts():
    assert not is_placeholder_host("github.com")


def test_entry_parser_accepts_http_urls_for_explicit_https_validation():
    assert ENTRY_RE.match("- [Project](http://example.com/project) - Description.")
