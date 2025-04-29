"""
Auto-formatting of Markdown text.

This is similar to what is offered by
[markdownfmt](https://github.com/shurcooL/markdownfmt) but with a few adaptations,
including more aggressive normalization and support for wrapping of lines
semi-semantically (e.g. on sentence boundaries when appropriate).
(See [here](https://github.com/shurcooL/markdownfmt/issues/17) for some old
discussion on why line wrapping this way is convenient.)
"""

from __future__ import annotations

import re
from collections.abc import Callable
from textwrap import dedent

from flowmark.cleanups import doc_cleanups
from flowmark.custom_marko import custom_marko
from flowmark.frontmatter import split_frontmatter
from flowmark.line_wrappers import LineWrapper, line_wrap_by_sentence, line_wrap_to_width
from flowmark.sentence_split_regex import split_sentences_regex
from flowmark.text_filling import DEFAULT_WRAP_WIDTH


def _normalize_html_comments(text: str, break_str: str = "\n\n") -> str:
    """
    Put HTML comments as standalone paragraphs.
    """

    # Small hack to avoid changing frontmatter format, for the rare corner
    # case where Markdown contains HTML-style frontmatter.
    def not_frontmatter(text: str) -> bool:
        return "<!---" not in text

    # TODO: Probably want do this for <div>s too.
    return _ensure_surrounding_breaks(
        text, [("<!--", "-->")], break_str=break_str, filter=not_frontmatter
    )


def _ensure_surrounding_breaks(
    html: str,
    tag_pairs: list[tuple[str, str]],
    filter: Callable[[str], bool] = lambda _: True,
    break_str: str = "\n\n",
) -> str:
    html_len = len(html)
    for start_tag, end_tag in tag_pairs:
        pattern = re.compile(rf"(\s*{re.escape(start_tag)}.*?{re.escape(end_tag)}\s*)", re.DOTALL)

        def replacer(match: re.Match[str]) -> str:
            if not filter(match.group(0)):
                return match.group(0)

            content = match.group(1).strip()
            before = after = break_str

            if match.start() == 0:
                before = ""
            if match.end() == html_len:
                after = ""

            return f"{before}{content}{after}"

        html = re.sub(pattern, replacer, html)

    return html


def split_sentences_no_min_length(text: str) -> list[str]:
    return split_sentences_regex(text, min_length=0)


def fill_markdown(
    markdown_text: str,
    dedent_input: bool = True,
    width: int = DEFAULT_WRAP_WIDTH,
    semantic: bool = False,
    cleanups: bool = False,
    line_wrapper: LineWrapper | None = None,
) -> str:
    """
    Normalize and wrap Markdown text filling paragraphs to the full width.

    Wraps lines and adds line breaks within paragraphs and on
    best-guess estimations of sentences, to make diffs more readable.

    Also enforces that all list items have two newlines between them, so
    that items are separate paragraphs when viewed as plaintext.

    Optionally also dedents and strips the input, so it can be used
    on docstrings.

    With `semantic` enabled, the line breaks are wrapped approximately
    by sentence boundaries, to make diffs more readable.

    Preserves YAML frontmatter (delimited by --- lines) if present at the
    beginning of the document.
    """
    if line_wrapper is None:
        if semantic:
            line_wrapper = line_wrap_by_sentence(width=width, is_markdown=True)
        else:
            line_wrapper = line_wrap_to_width(width=width, is_markdown=True)

    # Extract frontmatter before any processing
    frontmatter, content = split_frontmatter(markdown_text)

    # Only format the content part if there's frontmatter
    if frontmatter:
        markdown_text = content

    if dedent_input:
        markdown_text = dedent(markdown_text).strip()

    markdown_text = markdown_text.strip() + "\n"

    # If we want to normalize HTML blocks or comments.
    markdown_text = _normalize_html_comments(markdown_text)

    # Parse and render.
    marko = custom_marko(line_wrapper)
    document = marko.parse(markdown_text)
    if cleanups:
        doc_cleanups(document)
    result = marko.render(document)

    # Reattach frontmatter if it was present
    if frontmatter:
        result = frontmatter + result

    return result
