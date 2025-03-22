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
from collections.abc import Callable, Generator
from contextlib import contextmanager
from textwrap import dedent
from typing import Any, cast

from marko import block, inline
from marko.block import HTMLBlock
from marko.parser import Parser
from marko.renderer import Renderer
from marko.source import Source
from typing_extensions import override

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


# XXX Turn off Marko's parsing of block HTML.
# Block parsing with comments or block elements has some counterintuitive issues:
# https://github.com/frostming/marko/issues/202
# Another solution might be to always put a newline after a closing block tag during
# normalization, to avoid this confusion?
# For now, just ignoring block tags.
class CustomHTMLBlock(HTMLBlock):
    @override
    @classmethod
    def match(cls, source: Source) -> int | bool:
        return False


class CustomParser(Parser):
    def __init__(self) -> None:
        super().__init__()
        self.block_elements["HTMLBlock"] = CustomHTMLBlock


class _MarkdownNormalizer(Renderer):
    """
    Render Markdown in normalized form. This is the internal implementation.
    You likely want to use `normalize_markdown()` instead.
    Based on: https://github.com/frostming/marko/blob/master/marko/md_renderer.py
    """

    def __init__(self, line_wrapper: LineWrapper) -> None:
        super().__init__()
        self._prefix: str = ""  # The prefix on the first line, with a bullet, such as `  - `.
        self._second_prefix: str = ""  # The prefix on subsequent lines, such as `    `.
        self._suppress_item_break: bool = True
        self._line_wrapper: LineWrapper = line_wrapper

    @override
    def __enter__(self) -> _MarkdownNormalizer:
        self._prefix = ""
        self._second_prefix = ""
        return super().__enter__()

    @contextmanager
    def container(self, prefix: str, second_prefix: str = "") -> Generator[None, None, None]:
        old_prefix, old_second_prefix = self._prefix, self._second_prefix
        self._prefix += prefix
        self._second_prefix += second_prefix
        yield
        self._prefix, self._second_prefix = old_prefix, old_second_prefix

    def render_paragraph(self, element: block.Paragraph) -> str:
        # Suppress item breaks on list items following a top-level paragraph.
        if not self._prefix:
            self._suppress_item_break = True
        children: Any = self.render_children(element)
        wrapped_text = self._line_wrapper(
            children,
            self._prefix,
            self._second_prefix,
        )
        self._prefix = self._second_prefix
        return wrapped_text + "\n"

    def _has_multiple_paragraphs(self, item: object) -> bool:
        """
        Check if a list item contains multiple paragraphs.
        """
        list_item = cast(block.ListItem, item)
        paragraphs = [c for c in list_item.children if isinstance(c, block.Paragraph)]
        return len(paragraphs) > 1

    def render_list(self, element: block.List) -> str:
        result: list[str] = []

        for i, child in enumerate(element.children):
            # Configure the appropriate prefix based on list type
            if element.ordered:
                num = i + element.start
                prefix = f"{num}. "
                subsequent_indent = " " * (len(str(num)) + 2)
            else:
                prefix = f"{element.bullet} "
                subsequent_indent = "  "

            with self.container(prefix, subsequent_indent):
                # Add an extra newline before multi-paragraph list items (except the first)
                if i > 0 and self._has_multiple_paragraphs(child):
                    result.append(self._second_prefix.strip() + "\n")

                result.append(self.render(child))

        self._prefix = self._second_prefix
        return "".join(result)

    def render_list_item(self, element: block.ListItem) -> str:
        result = ""
        # We want all list items to have two newlines between them.
        if self._suppress_item_break:
            self._suppress_item_break = False
        else:
            # Add the newline between paragraphs. Normally this would be an empty line but
            # within a quote block it would be the secondary prefix, like `> `.
            result += self._second_prefix.strip() + "\n"

        result += self.render_children(element)
        return result

    def render_quote(self, element: block.Quote) -> str:
        with self.container("> ", "> "):
            result = self.render_children(element).rstrip("\n")
        self._prefix = self._second_prefix
        return f"{result}\n"

    def _render_code(self, element: block.CodeBlock | block.FencedCode) -> str:
        # Preserve code content without reformatting.
        code_child = cast(inline.RawText, element.children[0])
        code_content = code_child.children.rstrip("\n")
        lang = element.lang if isinstance(element, block.FencedCode) else ""
        extra = element.extra if isinstance(element, block.FencedCode) else ""
        extra_text = f" {extra}" if extra else ""
        lang_text = f"{lang}{extra_text}" if lang else ""
        lines = [f"{self._prefix}```{lang_text}"]
        lines.extend(f"{self._second_prefix}{line}" for line in code_content.splitlines())
        lines.append(f"{self._second_prefix}```")
        self._prefix = self._second_prefix
        return "\n".join(lines) + "\n"

    def render_fenced_code(self, element: block.FencedCode) -> str:
        return self._render_code(element)

    def render_code_block(self, element: block.CodeBlock) -> str:
        # Convert indented code blocks to fenced code blocks.
        return self._render_code(element)

    def render_html_block(self, element: block.HTMLBlock) -> str:
        result = f"{self._prefix}{element.body}"
        self._prefix = self._second_prefix
        return result

    def render_thematic_break(self, element: block.ThematicBreak) -> str:
        result = f"{self._prefix}* * *\n"
        self._prefix = self._second_prefix
        return result

    def render_heading(self, element: block.Heading) -> str:
        result = f"{self._prefix}{'#' * element.level} {self.render_children(element)}\n"
        self._prefix = self._second_prefix
        return result

    def render_setext_heading(self, element: block.SetextHeading) -> str:
        return self.render_heading(cast(block.Heading, element))  # pyright: ignore

    def render_blank_line(self, element: block.BlankLine) -> str:
        if self._prefix.strip():
            result = f"{self._prefix}\n"
        else:
            result = "\n"
        self._suppress_item_break = True
        self._prefix = self._second_prefix
        return result

    def render_link_ref_def(self, element: block.LinkRefDef) -> str:
        link_text = element.dest
        if element.title:
            link_text += f" {element.title}"
        return f"[{element.label}]: {link_text}\n"

    def render_emphasis(self, element: inline.Emphasis) -> str:
        return f"*{self.render_children(element)}*"

    def render_strong_emphasis(self, element: inline.StrongEmphasis) -> str:
        return f"**{self.render_children(element)}**"

    def render_inline_html(self, element: inline.InlineHTML) -> str:
        return cast(str, element.children)

    def render_link(self, element: inline.Link) -> str:
        link_text = self.render_children(element)
        link_title = '"{}"'.format(element.title.replace('"', '\\"')) if element.title else None
        assert self.root_node
        label = next(
            (k for k, v in self.root_node.link_ref_defs.items() if v == (element.dest, link_title)),
            None,
        )
        if label is not None:
            if label == link_text:
                return f"[{label}]"
            return f"[{link_text}][{label}]"
        title = f" {link_title}" if link_title is not None else ""
        return f"[{link_text}]({element.dest}{title})"

    def render_auto_link(self, element: inline.AutoLink) -> str:
        return f"<{element.dest}>"

    def render_image(self, element: inline.Image) -> str:
        template = "![{}]({}{})"
        title = ' "{}"'.format(element.title.replace('"', '\\"')) if element.title else ""
        return template.format(self.render_children(element), element.dest, title)

    def render_literal(self, element: inline.Literal) -> str:
        return f"\\{element.children}"

    def render_raw_text(self, element: inline.RawText) -> str:
        from marko.ext.pangu import PANGU_RE

        return re.sub(PANGU_RE, " ", element.children)

    def render_line_break(self, element: inline.LineBreak) -> str:
        return "\n" if element.soft else "\\\n"

    def render_code_span(self, element: inline.CodeSpan) -> str:
        text = element.children
        if text and (text[0] == "`" or text[-1] == "`"):
            return f"`` {text} ``"
        return f"`{element.children}`"


def split_sentences_no_min_length(text: str) -> list[str]:
    return split_sentences_regex(text, min_length=0)


def fill_markdown(
    markdown_text: str,
    dedent_input: bool = True,
    width: int = DEFAULT_WRAP_WIDTH,
    semantic: bool = False,
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
        line_wrapper = (
            line_wrap_by_sentence(width=width) if semantic else line_wrap_to_width(width=width)
        )

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

    # Normalize the markdown and wrap lines.
    parser = CustomParser()
    parsed = parser.parse(markdown_text)
    result = _MarkdownNormalizer(line_wrapper).render(parsed)

    # Reattach frontmatter if it was present
    if frontmatter:
        result = frontmatter + result

    return result
