from __future__ import annotations

import re
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any, cast

from marko import Markdown, Renderer, block, inline
from marko.block import HTMLBlock
from marko.ext import footnote
from marko.ext.gfm import GFM
from marko.ext.gfm import elements as gfm_elements
from marko.parser import Parser
from marko.source import Source
from typing_extensions import override

from flowmark.line_wrappers import LineWrapper


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


class MarkdownNormalizer(Renderer):
    """
    Render Markdown in normalized form. This is the internal implementation
    which overrides most of `MarkdownRenderer`.

    You likely want to use `normalize_markdown()` instead.

    Based on:
    https://github.com/frostming/marko/blob/master/marko/md_renderer.py
    https://github.com/frostming/marko/blob/master/marko/ext/gfm/renderer.py
    """

    def __init__(self, line_wrapper: LineWrapper) -> None:
        super().__init__()
        self._prefix: str = ""  # The prefix on the first line, with a bullet, such as `  - `.
        self._second_prefix: str = ""  # The prefix on subsequent lines, such as `    `.
        self._suppress_item_break: bool = True
        self._line_wrapper: LineWrapper = line_wrapper

    @override
    def __enter__(self) -> MarkdownNormalizer:
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

        # GFM checkbox support.
        if hasattr(element, "checked"):
            children = f"[{'x' if element.checked else ' '}] {children}"  # pyright: ignore

        # Wrap the text.
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

    def render_thematic_break(self, _element: block.ThematicBreak) -> str:
        result = f"{self._prefix}* * *\n"
        self._prefix = self._second_prefix
        return result

    def render_heading(self, element: block.Heading) -> str:
        result = f"{self._prefix}{'#' * element.level} {self.render_children(element)}\n"
        self._prefix = self._second_prefix
        return result

    def render_setext_heading(self, element: block.SetextHeading) -> str:
        return self.render_heading(cast(block.Heading, element))  # pyright: ignore

    def render_blank_line(self, _element: block.BlankLine) -> str:
        if self._prefix.strip():
            result = f"{self._prefix}\n"
        else:
            result = "\n"
        self._suppress_item_break = True
        self._prefix = self._second_prefix
        return result

    def render_link_ref_def(self, element: block.LinkRefDef) -> str:
        """Render a standard link reference definition:
        [label]: url "title"
        """
        link_text = element.dest
        if element.title:
            # Ensure title quotes are handled correctly
            escaped_title = element.title.replace('"', '\\"')
            link_text += f' "{escaped_title}"'
        result = f"{self._prefix}[{element.label}]: {link_text}\n"
        self._prefix = self._second_prefix
        self._suppress_item_break = True
        return result

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

    # --- GFM Renderer Methods ---

    def render_footnote_ref(self, element: footnote.FootnoteRef) -> str:
        """Render an inline footnote reference like [^label]."""
        return f"[^{element.label}]"

    def render_footnote_def(self, element: footnote.FootnoteDef) -> str:
        """
        Render a GFM footnote definition, handling content wrapping.
        Note multiline footnotes aren't very well specified but we use
        standard 4-space indentation. See:
        https://github.com/micromark/micromark-extension-gfm-footnote
        """
        # Render label and the rest within an indented container.
        label_part = f"[^{element.label}]: "
        with self.container(label_part, "    "):
            content = self.render_children(element)

        # Set up state for the *next* block element using the restored outer secondary prefix.
        self._prefix = self._second_prefix
        self._suppress_item_break = True  # This definition acts as a block separator.

        # Footnote defs should be separated by extra newlines.
        return content.rstrip("\n") + "\n\n"

    def render_strikethrough(self, element: gfm_elements.Strikethrough) -> str:
        return f"~~{self.render_children(element)}~~"

    def render_table(self, element: gfm_elements.Table) -> str:
        """Render a GFM table."""
        lines: list[str] = []
        head, *body = element.children
        lines.append(self.render(head))
        lines.append(f"| {' | '.join(element.delimiters)} |\n")
        for row in body:
            lines.append(self.render(row))
        return "".join(lines)

    def render_table_row(self, element: gfm_elements.TableRow) -> str:
        """Render a row within a GFM table."""
        return f"| {' | '.join(self.render(cell) for cell in element.children)} |\n"

    def render_table_cell(self, element: gfm_elements.TableCell) -> str:
        """Render a cell within a GFM table row."""
        return self.render_children(element).replace("|", "\\|")

    def render_url(self, element: gfm_elements.Url) -> str:
        """For GFM autolink URLs, just output the URL directly."""
        return element.dest


def custom_marko(line_wrapper: LineWrapper) -> Markdown:
    """
    Marko Markdown setup for GFM with minor customizations and a
    renderer that normalizes Markdown.
    """

    class CustomRenderer(MarkdownNormalizer):
        def __init__(self) -> None:
            super().__init__(line_wrapper)

    class CustomMarkdown(Markdown):
        def __init__(self) -> None:  # pyright: ignore[reportMissingSuperCall]
            pass

        @override
        def _setup_extensions(self) -> None:
            # Using Marko's full extension system is tricky with our customizations so simpler
            # to do this manually.
            custom_parser = CustomParser()
            # Add GFM support.
            for e in GFM.elements:
                assert (
                    e not in custom_parser.block_elements and e not in custom_parser.inline_elements
                )
                custom_parser.add_element(e)
            # Add GFM footnote support.
            footnote_ext = footnote.make_extension()
            for e in footnote_ext.elements:
                assert (
                    e not in custom_parser.block_elements and e not in custom_parser.inline_elements
                )
                custom_parser.add_element(e)
            self.parser: Parser = custom_parser
            self.renderer: Renderer = CustomRenderer()

            self._setup_done: bool = True

    return CustomMarkdown()
