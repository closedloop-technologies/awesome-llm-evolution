from scripts.check_readme import canonical_title, canonical_url


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


def test_canonical_title_ignores_case_and_extra_spaces():
    assert canonical_title("  Alpha   Evolve ") == "alpha evolve"


def test_canonical_title_preserves_meaningful_words():
    assert canonical_title("Tree-of-Thoughts") == "tree-of-thoughts"
