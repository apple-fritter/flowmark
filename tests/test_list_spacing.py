"""
Test list spacing behavior for different list item types.

This test documents the expected behavior for blank line spacing in markdown lists,
particularly around list items with code blocks, quotes, and multiple paragraphs.

Desired behavior: Always one extra blank line between list items, regardless of the
number of paragraphs in the list item.
"""

from textwrap import dedent

from flowmark.markdown_filling import fill_markdown


def test_list_items_with_code_blocks():
    """Test that list items with code blocks get proper spacing."""
    input_doc = dedent(
        """
        - Use `z` (zoxide) instead of `cd`.

          ```shell
          # Use z in place of cd: switch directories (first time):
          z ~/some/long/path/to/foo
          # Thereafter it's faster:
          z foo
          ```

        - Use `eza` instead of `ls`. It has color support, support for Nerd Font icons, and
          other improvements.
        """
    ).strip()

    expected_doc = (
        dedent(
            """
            - Use `z` (zoxide) instead of `cd`.

              ```shell
              # Use z in place of cd: switch directories (first time):
              z ~/some/long/path/to/foo
              # Thereafter it's faster:
              z foo
              ```

            - Use `eza` instead of `ls`. It has color support, support for Nerd Font icons, and
              other improvements.
            """
        ).strip()
        + "\n"
    )

    normalized_doc = fill_markdown(input_doc, semantic=True)
    assert normalized_doc == expected_doc


def test_list_items_with_quote_blocks():
    """Test that list items with quote blocks get proper spacing."""
    input_doc = dedent(
        """
        - First item with a quote.

          > This is a quote block.
          > With multiple lines.

        - Second item without quotes.
        """
    ).strip()

    expected_doc = (
        dedent(
            """
            - First item with a quote.

              > This is a quote block.
              > With multiple lines.

            - Second item without quotes.
            """
        ).strip()
        + "\n"
    )

    normalized_doc = fill_markdown(input_doc, semantic=True)
    assert normalized_doc == expected_doc


def test_numbered_list_with_code_blocks():
    """Test that numbered lists with code blocks get proper spacing."""
    input_doc = dedent(
        """
        1. First numbered item.
        2. Second item with code.

           ```shell
           echo "test"
           ```

        3. Third item.
        """
    ).strip()

    expected_doc = (
        dedent(
            """
            1. First numbered item.

            2. Second item with code.

               ```shell
               echo "test"
               ```

            3. Third item.
            """
        ).strip()
        + "\n"
    )

    normalized_doc = fill_markdown(input_doc, semantic=True)
    assert normalized_doc == expected_doc


def test_simple_to_multi_paragraph_spacing():
    """Test spacing between simple and multi-paragraph items."""
    input_doc = dedent(
        """
        - Simple item.

        - Multi-paragraph item.

          Second paragraph here.
        """
    ).strip()

    # Note: Current implementation has a bug - adds extra blank line before multi-paragraph items
    expected_doc = (
        dedent(
            """
            - Simple item.

            - Multi-paragraph item.

              Second paragraph here.
            """
        ).strip()
        + "\n"
    )

    normalized_doc = fill_markdown(input_doc, semantic=True)
    assert normalized_doc == expected_doc


def test_input_spacing_normalization():
    """Test that various input spacings are normalized to consistent output spacing."""

    # One newline between items (normal markdown)
    input_one_spacing = dedent(
        """
        - First item
        - Second item
        - Third item
        """
    ).strip()

    # Two newlines between items (one blank line)
    input_two_spacing = dedent(
        """
        - First item

        - Second item

        - Third item
        """
    ).strip()

    # Three newlines between items (two blank lines)
    input_three_spacing = dedent(
        """
        - First item


        - Second item


        - Third item
        """
    ).strip()

    # All should normalize to the same output: one blank line between items
    expected_output = (
        dedent(
            """
            - First item

            - Second item

            - Third item
            """
        ).strip()
        + "\n"
    )

    # Test all input variations produce the same normalized output
    assert fill_markdown(input_one_spacing, semantic=True) == expected_output
    assert fill_markdown(input_two_spacing, semantic=True) == expected_output
    assert fill_markdown(input_three_spacing, semantic=True) == expected_output


def test_complex_content_extra_spacing():
    """Test that complex content gets extra spacing regardless of input spacing."""

    # Test with minimal input spacing
    input_minimal = dedent(
        """
        - Item before code
        - Item with code

          ```shell
          echo "test"
          ```
        - Item after code
        """
    ).strip()

    # Test with extra input spacing
    input_extra = dedent(
        """
        - Item before code


        - Item with code

          ```shell
          echo "test"
          ```


        - Item after code
        """
    ).strip()

    # Both should produce the same normalized output with extra blank line after code
    expected_output = (
        dedent(
            """
            - Item before code

            - Item with code

              ```shell
              echo "test"
              ```

            - Item after code
            """
        ).strip()
        + "\n"
    )

    assert fill_markdown(input_minimal, semantic=True) == expected_output
    assert fill_markdown(input_extra, semantic=True) == expected_output


def test_multi_paragraph_spacing_normalization():
    """Test that multi-paragraph items get consistent spacing regardless of input."""

    # Test with minimal spacing
    input_minimal = dedent(
        """
        - Simple item
        - Multi-paragraph item

          Second paragraph
        - Another simple item
        """
    ).strip()

    # Test with extra spacing
    input_extra = dedent(
        """
        - Simple item


        - Multi-paragraph item

          Second paragraph


        - Another simple item
        """
    ).strip()

    # Both should produce the same normalized output
    # Note: Current implementation has bugs with multi-paragraph spacing
    expected_output = (
        dedent(
            """
            - Simple item

            - Multi-paragraph item

              Second paragraph

            - Another simple item
            """
        ).strip()
        + "\n"
    )

    assert fill_markdown(input_minimal, semantic=True) == expected_output
    assert fill_markdown(input_extra, semantic=True) == expected_output
