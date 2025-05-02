from textwrap import dedent

from flowmark.text_wrapping import (
    _HtmlMdWordSplitter,  # pyright: ignore
    html_md_word_splitter,
    markdown_escape_word,
    simple_word_splitter,
    wrap_paragraph,
    wrap_paragraph_lines,
)


def test_markdown_escape_word_function() -> None:
    # Cases that should be escaped
    assert markdown_escape_word("-") == "\\-"
    assert markdown_escape_word("+") == "\\+"
    assert markdown_escape_word("*") == "\\*"
    assert markdown_escape_word(">") == "\\>"
    assert markdown_escape_word("#") == "\\#"
    assert markdown_escape_word("##") == "\\##"
    assert markdown_escape_word("1.") == "1\\."
    assert markdown_escape_word("10.") == "10\\."
    assert markdown_escape_word("1)") == "1\\)"
    assert markdown_escape_word("99)") == "99\\)"

    # Cases that should NOT be escaped
    assert markdown_escape_word("word") == "word"
    assert markdown_escape_word("-word") == "-word"  # Starts with char, but not just char
    assert markdown_escape_word("word-") == "word-"  # Ends with char
    assert markdown_escape_word("#word") == "#word"
    assert markdown_escape_word("word#") == "word#"
    assert markdown_escape_word("1.word") == "1.word"
    assert markdown_escape_word("word1.") == "word1."
    assert markdown_escape_word("1)word") == "1)word"
    assert markdown_escape_word("word1)") == "word1)"
    assert markdown_escape_word("<tag>") == "<tag>"  # Other symbols
    assert markdown_escape_word("[link]") == "[link]"
    assert markdown_escape_word("1") == "1"  # Just number
    assert markdown_escape_word(".") == "."  # Just dot


def test_wrap_paragraph_lines_markdown_escaping():
    assert wrap_paragraph_lines(text="- word", width=10, is_markdown=True) == ["- word"]

    text = "word - word * word + word > word # word ## word 1. word 2) word"

    assert wrap_paragraph_lines(text=text, width=5, is_markdown=True) == [
        "word",
        "\\-",
        "word",
        "\\*",
        "word",
        "\\+",
        "word",
        "\\>",
        "word",
        "\\#",
        "word",
        "\\##",
        "word",
        "1\\.",
        "word",
        "2\\)",
        "word",
    ]
    assert wrap_paragraph_lines(text=text, width=10, is_markdown=True) == [
        "word -",
        "word *",
        "word +",
        "word >",
        "word #",
        "word ##",
        "word 1.",
        "word 2)",
        "word",
    ]
    assert wrap_paragraph_lines(text=text, width=15, is_markdown=True) == [
        "word - word *",
        "word + word >",
        "word # word ##",
        "word 1. word 2)",
        "word",
    ]
    assert wrap_paragraph_lines(text=text, width=20, is_markdown=True) == [
        "word - word * word +",
        "word > word # word",
        "\\## word 1. word 2)",
        "word",
    ]
    assert wrap_paragraph_lines(text=text, width=20, is_markdown=False) == [
        "word - word * word +",
        "word > word # word",
        "## word 1. word 2)",
        "word",
    ]

    test2 = """Testing - : Is Ketamine Contraindicated in Patients with Psychiatric Disorders? - REBEL EM - more words - accessed April 24, 2025, <https://rebelem.com/is-ketamine-contraindicated-in-patients-with-psychiatric-disorders/>"""
    assert wrap_paragraph_lines(text=test2, width=80, is_markdown=True) == [
        "Testing - : Is Ketamine Contraindicated in Patients with Psychiatric Disorders?",
        "\\- REBEL EM - more words - accessed April 24, 2025,",
        "<https://rebelem.com/is-ketamine-contraindicated-in-patients-with-psychiatric-disorders/>",
    ]


def test_smart_splitter():
    splitter = _HtmlMdWordSplitter()

    html_text = "This is <span class='test'>some text</span> and <a href='#'>this is a link</a>."
    assert splitter(html_text) == [
        "This",
        "is",
        "<span class='test'>some",
        "text</span>",
        "and",
        "<a href='#'>this",
        "is",
        "a",
        "link</a>.",
    ]

    md_text = "Here's a [Markdown link](https://example.com) and [another one](https://test.com)."
    assert splitter(md_text) == [
        "Here's",
        "a",
        "[Markdown link](https://example.com)",
        "and",
        "[another one](https://test.com).",
    ]

    mixed_text = "Text with <b>bold</b> and [a link](https://example.com)."
    assert splitter(mixed_text) == [
        "Text",
        "with",
        "<b>bold</b>",
        "and",
        "[a link](https://example.com).",
    ]


def test_wrap_text():
    sample_text = (
        "This is a sample text with a [Markdown link](https://example.com)"
        " and an <a href='#'>tag</a>. It should demonstrate the functionality of "
        "our enhanced text wrapping implementation."
    )

    print("\nFilled text with default splitter:")
    filled = wrap_paragraph(
        sample_text,
        word_splitter=simple_word_splitter,
        width=40,
        initial_indent=">",
        subsequent_indent=">>",
    )
    print(filled)
    filled_expected = dedent(
        """
        >This is a sample text with a [Markdown
        >>link](https://example.com) and an <a
        >>href='#'>tag</a>. It should
        >>demonstrate the functionality of our
        >>enhanced text wrapping implementation.
        """
    ).strip()

    print("\nFilled text with html_md_word_splitter:")
    filled_smart = wrap_paragraph(
        sample_text,
        word_splitter=html_md_word_splitter,
        width=40,
        initial_indent=">",
        subsequent_indent=">>",
    )
    print(filled_smart)
    filled_smart_expected = dedent(
        """
        >This is a sample text with a
        >>[Markdown link](https://example.com)
        >>and an <a href='#'>tag</a>. It should
        >>demonstrate the functionality of our
        >>enhanced text wrapping implementation.
        """
    ).strip()

    print("\nFilled text with html_md_word_splitter and initial_offset:")
    filled_smart_offset = wrap_paragraph(
        sample_text,
        word_splitter=html_md_word_splitter,
        width=40,
        initial_indent=">",
        subsequent_indent=">>",
        initial_column=35,
    )
    print(filled_smart_offset)
    filled_smart_offset_expected = dedent(
        """
        This
        >>is a sample text with a
        >>[Markdown link](https://example.com)
        >>and an <a href='#'>tag</a>. It should
        >>demonstrate the functionality of our
        >>enhanced text wrapping implementation.
        """
    ).strip()

    assert filled == filled_expected
    assert filled_smart == filled_smart_expected
    assert filled_smart_offset == filled_smart_offset_expected


def test_wrap_width():
    text = dedent(
        """
        You may also simply ask a question and the kmd assistant will help you. Press
        `?` or just press space twice, then write your question or request. Press `?` and
        tab to get suggested questions.
        """
    ).strip()
    width = 80
    wrapped = wrap_paragraph_lines(text, width=width)
    print(wrapped)
    print([len(line) for line in wrapped])
    assert all(len(line) <= width for line in wrapped)
