from scripts.check_readme import (
    ENTRY_RE,
    canonical_title,
    canonical_url,
    has_bare_http_url,
    is_canonical_resource_url,
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


def test_entry_parser_accepts_http_urls_for_explicit_https_validation():
    assert ENTRY_RE.match("- [Project](http://example.com/project) - Description.")
