from collections.abc import Callable
from typing import Protocol

from flowmark.sentence_split_regex import split_sentences_regex
from flowmark.text_filling import DEFAULT_WRAP_WIDTH
from flowmark.text_wrapping import DEFAULT_LEN_FUNCTION, wrap_paragraph, wrap_paragraph_lines

DEFAULT_MIN_LINE_LEN = 20
"""Default minimum line length for sentence breaking."""


class LineWrapper(Protocol):
    """
    Takes a text string and any indents to use, and returns the wrapped text.
    """

    def __call__(self, text: str, initial_indent: str, subsequent_indent: str) -> str: ...


class SentenceSplitter(Protocol):
    """Takes a text string and returns a list of sentences."""

    def __call__(self, text: str) -> list[str]: ...


def split_sentences_no_min_length(text: str) -> list[str]:
    return split_sentences_regex(text, min_length=0)


def line_wrap_to_width(
    width: int = DEFAULT_WRAP_WIDTH,
    len_fn: Callable[[str], int] = DEFAULT_LEN_FUNCTION,
    is_markdown: bool = False,
) -> LineWrapper:
    """
    Wrap lines of text to a given width.
    """

    def line_wrapper(text: str, initial_indent: str, subsequent_indent: str) -> str:
        return wrap_paragraph(
            text,
            width=width,
            initial_indent=initial_indent,
            subsequent_indent=subsequent_indent,
            len_fn=len_fn,
            is_markdown=is_markdown,
        )

    return line_wrapper


def line_wrap_by_sentence(
    split_sentences: SentenceSplitter = split_sentences_no_min_length,
    width: int = DEFAULT_WRAP_WIDTH,
    min_line_len: int = DEFAULT_MIN_LINE_LEN,
    len_fn: Callable[[str], int] = DEFAULT_LEN_FUNCTION,
    is_markdown: bool = False,
) -> LineWrapper:
    """
    Wrap lines of text to a given width but also keep sentences on their own lines.
    If the last line ends up shorter than `min_line_len`, it's combined with the
    next sentence.
    """

    def line_wrapper(text: str, initial_indent: str, subsequent_indent: str) -> str:
        text = text.replace("\n", " ")
        lines: list[str] = []
        first_line = True
        length = len_fn
        initial_indent_len = len_fn(initial_indent)
        subsequent_indent_len = len_fn(subsequent_indent)

        sentences = split_sentences(text)

        for sentence in sentences:
            current_column = initial_indent_len if first_line else subsequent_indent_len
            if len(lines) > 0 and length(lines[-1]) < min_line_len:
                current_column += length(lines[-1])

            wrapped = wrap_paragraph_lines(
                sentence,
                width=width,
                initial_column=current_column,
                subsequent_offset=subsequent_indent_len,
                is_markdown=is_markdown,
            )
            # If last line is shorter than min_line_len, combine with next line.
            # Also handles if the first word doesn't fit.
            if (
                len(lines) > 0
                and length(lines[-1]) < min_line_len
                and length(lines[-1]) + 1 + length(wrapped[0]) <= width
            ):
                lines[-1] += " " + wrapped[0]
                wrapped.pop(0)

            lines.extend(wrapped)

            first_line = False

        # Now insert the indents and assemble the paragraph.
        if initial_indent and len(lines) > 0:
            lines[0] = initial_indent + lines[0]
        if subsequent_indent and len(lines) > 1:
            lines[1:] = [subsequent_indent + line for line in lines[1:]]

        return "\n".join(lines)

    return line_wrapper
