import re
from collections.abc import Callable
from typing import Protocol

DEFAULT_LEN_FUNCTION = len
"""
Default length function to use for wrapping.
By default this is just character length, but this can be overridden, for example
to use a smarter function that does not count ANSI escape codes.
"""


class WordSplitter(Protocol):
    def __call__(self, text: str) -> list[str]: ...


def simple_word_splitter(text: str) -> list[str]:
    """
    Split words on whitespace. This is like Python's normal `textwrap`.
    """
    return text.split()


class _HtmlMdWordSplitter:
    def __init__(self):
        # Sequences of whitespace-delimited words that should be coalesced and treated
        # like a single word.
        self.patterns: list[tuple[str, ...]] = [
            # HTML tags:
            (r"<[^>]+", r"[^<>]+>[^<>]*"),
            (r"<[^>]+", r"[^<>]+", r"[^<>]+>[^<>]*"),
            # Markdown links:
            (r"\[", r"[^\[\]]+\][^\[\]]*"),
            (r"\[", r"[^\[\]]+", r"[^\[\]]+\][^\[\]]*"),
        ]
        self.compiled_patterns: list[tuple[re.Pattern[str], ...]] = [
            tuple(re.compile(pattern) for pattern in pattern_group)
            for pattern_group in self.patterns
        ]

    def __call__(self, text: str) -> list[str]:
        words = text.split()
        result: list[str] = []
        i = 0
        while i < len(words):
            coalesced = self.coalesce_words(words[i:])
            if coalesced > 0:
                result.append(" ".join(words[i : i + coalesced]))
                i += coalesced
            else:
                result.append(words[i])
                i += 1
        return result

    def coalesce_words(self, words: list[str]) -> int:
        for pattern_group in self.compiled_patterns:
            if self.match_pattern_group(words, pattern_group):
                return len(pattern_group)
        return 0

    def match_pattern_group(self, words: list[str], patterns: tuple[re.Pattern[str], ...]) -> bool:
        if len(words) < len(patterns):
            return False

        return all(pattern.match(word) for pattern, word in zip(patterns, words, strict=False))


html_md_word_splitter: WordSplitter = _HtmlMdWordSplitter()
"""
Split words, but not within HTML tags or Markdown links.
"""


def wrap_paragraph_lines(
    text: str,
    width: int,
    initial_column: int = 0,
    subsequent_offset: int = 0,
    replace_whitespace: bool = True,
    drop_whitespace: bool = True,
    splitter: WordSplitter = html_md_word_splitter,
    len_fn: Callable[[str], int] = DEFAULT_LEN_FUNCTION,
) -> list[str]:
    """
    Wrap a single paragraph of text, returning a list of wrapped lines.
    Rewritten to simplify and generalize Python's textwrap.py.
    """
    if replace_whitespace:
        text = re.sub(r"\s+", " ", text)

    words = splitter(text)

    lines: list[str] = []
    current_line: list[str] = []
    current_width = initial_column

    # Walk through words, breaking them into lines.
    for word in words:
        word_width = len_fn(word)

        space_width = 1 if current_line else 0
        if current_width + word_width + space_width <= width:
            # Add word to current line.
            current_line.append(word)
            current_width += word_width + space_width
        else:
            # Start a new line.
            if current_line:
                line = " ".join(current_line)
                if drop_whitespace:
                    line = line.strip()
                lines.append(line)
            current_line = [word]
            current_width = subsequent_offset + word_width

    if current_line:
        line = " ".join(current_line)
        if drop_whitespace:
            line = line.strip()
        lines.append(line)

    return lines


def wrap_paragraph(
    text: str,
    width: int,
    initial_indent: str = "",
    subsequent_indent: str = "",
    initial_column: int = 0,
    replace_whitespace: bool = True,
    drop_whitespace: bool = True,
    word_splitter: WordSplitter = html_md_word_splitter,
    len_fn: Callable[[str], int] = DEFAULT_LEN_FUNCTION,
) -> str:
    """
    Wrap lines of a single paragraph of plain text, returning a new string.
    By default, uses an HTML- and Markdown-aware word splitter.
    """
    lines = wrap_paragraph_lines(
        text=text,
        width=width,
        replace_whitespace=replace_whitespace,
        drop_whitespace=drop_whitespace,
        splitter=word_splitter,
        initial_column=initial_column + len_fn(initial_indent),
        subsequent_offset=len_fn(subsequent_indent),
        len_fn=len_fn,
    )
    # Now insert indents on first and subsequent lines, if needed.
    if initial_indent and initial_column == 0 and len(lines) > 0:
        lines[0] = initial_indent + lines[0]
    if subsequent_indent and len(lines) > 1:
        lines[1:] = [subsequent_indent + line for line in lines[1:]]
    return "\n".join(lines)
