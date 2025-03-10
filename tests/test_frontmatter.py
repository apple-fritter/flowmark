from flowmark.frontmatter import has_frontmatter, split_frontmatter
from flowmark.markdown_filling import fill_markdown


def test_split_frontmatter():
    # Test with empty string
    frontmatter, content = split_frontmatter("")
    assert frontmatter == ""
    assert content == ""

    # Test with no frontmatter
    text = "# Heading\n\nThis is content."
    frontmatter, content = split_frontmatter(text)
    assert frontmatter == ""
    assert content == text

    # Test with proper frontmatter
    text = "---\ntitle: Test\ndate: 2023-01-01\n---\n\n# Heading\n\nThis is content."
    frontmatter, content = split_frontmatter(text)
    assert frontmatter == "---\ntitle: Test\ndate: 2023-01-01\n---\n"
    assert content == "\n# Heading\n\nThis is content."

    # Test with empty lines before frontmatter
    text = "\n\n---\ntitle: Test\n---\n\n# Content"
    frontmatter, content = split_frontmatter(text)
    assert frontmatter == "---\ntitle: Test\n---\n"
    assert content == "\n# Content"

    # Test with unclosed frontmatter (entire document is frontmatter)
    text = "---\ntitle: Test\ndate: 2023-01-01\n"
    frontmatter, content = split_frontmatter(text)
    assert frontmatter == text
    assert content == ""


def test_has_frontmatter():
    assert has_frontmatter("") is False
    assert has_frontmatter("# No frontmatter") is False
    assert has_frontmatter("---\ntitle: Test\n---\n\nContent") is True
    assert has_frontmatter("\n\n---\ntitle: Test\n---\n") is True


def test_markdown_with_frontmatter():
    # Test that frontmatter is preserved when formatting markdown
    input_doc = "---\ntitle: Test Document\ndate: 2023-01-01\nauthor: Test Author\n---\n\n# Heading\n\nThis is sentence one. This is sentence two."

    normalized_doc = fill_markdown(input_doc, semantic=True)

    # Verify the frontmatter is preserved exactly
    frontmatter, _ = split_frontmatter(normalized_doc)
    expected_frontmatter = "---\ntitle: Test Document\ndate: 2023-01-01\nauthor: Test Author\n---\n"
    assert frontmatter == expected_frontmatter

    # Verify the content is formatted correctly
    assert "# Heading" in normalized_doc
    assert "This is sentence one." in normalized_doc
    assert "This is sentence two." in normalized_doc

    # Test with empty lines before frontmatter
    input_doc = "\n\n---\ntitle: Test\n---\n\n# Content with long sentence that should be wrapped to make the diff more readable when it gets formatted."

    normalized_doc = fill_markdown(input_doc, semantic=True)

    # Verify the frontmatter is preserved exactly
    frontmatter, content = split_frontmatter(normalized_doc)
    expected_frontmatter = "---\ntitle: Test\n---\n"
    assert frontmatter == expected_frontmatter

    # Verify the content is formatted correctly
    assert "# Content" in content
    assert "with long sentence that should be wrapped" in content
    assert "readable when it gets" in content
