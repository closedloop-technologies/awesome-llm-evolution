from scripts.check_readme import (
    ENTRY_RE,
    canonical_title,
    canonical_url,
    contents_precedes_categories,
    duplicate_values,
    github_anchor,
    h1_headings,
    has_bare_http_url,
    has_descriptive_link_title,
    has_noncanonical_horizontal_rule,
    has_normalized_inline_whitespace,
    has_encoded_url_control_character,
    has_encoded_url_path_separator,
    has_trailing_whitespace,
    has_url_credentials,
    has_url_current_directory_reference,
    has_url_host,
    has_url_path_backslash,
    has_url_parent_directory_reference,
    has_url_whitespace,
    has_valid_url_port,
    is_placeholder_host,
    is_canonical_resource_url,
    is_title_case,
    markdown_spacing_violations,
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


def test_canonical_url_removes_trailing_host_dot():
    assert canonical_url("https://Docs.Example.com./project/") == "https://docs.example.com/project"


def test_canonical_url_preserves_non_default_ports():
    assert canonical_url("https://example.com:8443/project") == "https://example.com:8443/project"


def test_canonical_url_collapses_repeated_path_slashes():
    assert canonical_url("https://example.com//project///paper/") == "https://example.com/project/paper"


def test_canonical_title_ignores_case_and_extra_spaces():
    assert canonical_title("  Alpha   Evolve ") == "alpha evolve"


def test_canonical_title_preserves_meaningful_words():
    assert canonical_title("Tree-of-Thoughts") == "tree-of-thoughts"


def test_has_descriptive_link_title_rejects_generic_labels():
    assert not has_descriptive_link_title("paper")
    assert not has_descriptive_link_title("  GitHub  ")
    assert not has_descriptive_link_title("Blog   Post")


def test_has_descriptive_link_title_accepts_named_resources():
    assert has_descriptive_link_title("Tree-of-Thoughts")
    assert has_descriptive_link_title("AlphaEvolve (DeepMind, 2025)")


def test_duplicate_values_returns_sorted_repeated_values():
    assert duplicate_values(["b", "a", "b", "c", "a", "b"]) == ["a", "b"]


def test_has_normalized_inline_whitespace_rejects_repeated_spaces():
    assert has_normalized_inline_whitespace("Alpha Evolve")
    assert not has_normalized_inline_whitespace("Alpha  Evolve")


def test_has_trailing_whitespace_rejects_spaces_and_tabs():
    assert not has_trailing_whitespace("- [Project](https://example.com) - Description.")
    assert has_trailing_whitespace("Description. ")
    assert has_trailing_whitespace("Description.\t")


def test_has_noncanonical_horizontal_rule_rejects_star_and_underscore_rules():
    assert not has_noncanonical_horizontal_rule("---")
    assert has_noncanonical_horizontal_rule("***")
    assert has_noncanonical_horizontal_rule("_ _ _")


def test_github_anchor_strips_punctuation_and_collapses_case():
    assert github_anchor("Code & Algorithm Discovery!") == "code--algorithm-discovery"


def test_h1_headings_returns_top_level_headings_only():
    assert h1_headings(["# Awesome LLM Evolution", "## Contents"]) == [
        "Awesome LLM Evolution"
    ]


def test_contents_precedes_categories_requires_contents_first():
    assert contents_precedes_categories(["# Title", "## Contents", "## Category"])
    assert not contents_precedes_categories(["# Title", "## Category", "## Contents"])
    assert not contents_precedes_categories(["# Title", "## Category"])


def test_markdown_spacing_accepts_spaced_resource_sections():
    lines = [
        "# Title",
        "",
        "## Category",
        "",
        "- [Project](https://example.com/project) - Description.",
        "",
        "- [Other](https://example.com/other) - Description.",
    ]

    assert markdown_spacing_violations(lines) == []


def test_markdown_spacing_rejects_heading_without_blank_line():
    lines = [
        "# Title",
        "## Category",
        "",
        "- [Project](https://example.com/project) - Description.",
    ]

    assert markdown_spacing_violations(lines) == [
        "line 2 heading is missing a blank line before it"
    ]


def test_markdown_spacing_rejects_adjacent_resource_entries():
    lines = [
        "# Title",
        "",
        "## Category",
        "",
        "- [Project](https://example.com/project) - Description.",
        "- [Other](https://example.com/other) - Description.",
    ]

    assert markdown_spacing_violations(lines) == [
        "line 5 resource entry is missing a blank line after it",
        "line 6 resource entry is missing a blank line before it",
    ]


def test_is_title_case_accepts_acronyms_and_small_words():
    assert is_title_case("LLM-MCTS for Game Strategy")
    assert is_title_case("Code and Algorithm Discovery")


def test_is_title_case_rejects_lowercase_major_words():
    assert not is_title_case("code and Algorithm Discovery")
    assert not is_title_case("Code and algorithm Discovery")


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


def test_has_url_host_rejects_hostless_urls():
    assert has_url_host("https://example.com/project")
    assert not has_url_host("https:///project")


def test_has_url_credentials_rejects_embedded_credentials():
    assert not has_url_credentials("https://example.com/project")
    assert has_url_credentials("https://user@example.com/project")
    assert has_url_credentials("https://user:token@example.com/project")


def test_has_url_whitespace_rejects_literal_spaces_and_tabs():
    assert not has_url_whitespace("https://example.com/project")
    assert has_url_whitespace("https://example.com/project name")
    assert has_url_whitespace("https://example.com/project\tname")


def test_has_encoded_url_control_character_rejects_percent_encoded_controls():
    assert not has_encoded_url_control_character("https://example.com/project")
    assert has_encoded_url_control_character("https://example.com/project%00name")
    assert has_encoded_url_control_character("https://example.com/project%7fname")


def test_has_encoded_url_path_separator_rejects_encoded_slashes_and_backslashes():
    assert not has_encoded_url_path_separator("https://example.com/project/readme")
    assert has_encoded_url_path_separator("https://example.com/project%2Freadme")
    assert has_encoded_url_path_separator("https://example.com/project%5creadme")


def test_has_url_path_backslash_rejects_literal_backslashes():
    assert not has_url_path_backslash("https://example.com/project/readme")
    assert has_url_path_backslash("https://example.com/project\\readme")


def test_has_url_parent_directory_reference_rejects_path_traversal():
    assert not has_url_parent_directory_reference("https://example.com/project/readme")
    assert has_url_parent_directory_reference("https://example.com/../project")
    assert has_url_parent_directory_reference("https://example.com/%2e%2e/project")


def test_has_url_current_directory_reference_rejects_noncanonical_segments():
    assert not has_url_current_directory_reference("https://example.com/project/readme")
    assert has_url_current_directory_reference("https://example.com/./project")
    assert has_url_current_directory_reference("https://example.com/%2e/project")


def test_has_valid_url_port_rejects_malformed_ports():
    assert has_valid_url_port("https://example.com:8443/project")
    assert not has_valid_url_port("https://example.com:bad/project")


def test_is_placeholder_host_rejects_example_subdomains():
    assert is_placeholder_host("docs.example.com")
    assert is_placeholder_host(url_host("https://docs.example.com./project"))


def test_is_placeholder_host_accepts_real_hosts():
    assert not is_placeholder_host("github.com")


def test_entry_parser_accepts_http_urls_for_explicit_https_validation():
    assert ENTRY_RE.match("- [Project](http://example.com/project) - Description.")
