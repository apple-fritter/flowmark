import sys
from pathlib import Path

from strif import atomic_output_file

from flowmark.markdown_filling import fill_markdown
from flowmark.text_filling import Wrap, fill_text
from flowmark.text_wrapping import html_md_word_splitter


def reformat_text(
    text: str,
    width: int = 88,
    plaintext: bool = False,
    semantic: bool = True,
    cleanups: bool = True,
) -> str:
    """
    Reformat text or markdown and wrap lines. Simply a convenient wrapper
    around `fill_text()` and `fill_markdown()` with reasonable defaults.
    """
    if plaintext:
        # Plaintext mode
        result = fill_text(
            text,
            text_wrap=Wrap.WRAP,
            width=width,
            word_splitter=html_md_word_splitter,  # Still use HTML/MD aware splitter by default
        )
    else:
        # Markdown mode
        result = fill_markdown(text, width=width, semantic=semantic, cleanups=cleanups)

    return result


def reformat_file(
    path: Path | str,
    output: Path | str | None,
    width: int = 88,
    inplace: bool = False,
    nobackup: bool = False,
    plaintext: bool = False,
    semantic: bool = False,
    cleanups: bool = True,
    make_parents: bool = True,
) -> None:
    """
    Reformat text or markdown and wrap lines on the given files.
    Accepts "-" for stdin. Can omit output if `inplace` is True.
    Throws usual file-related exceptions if the input or output is invalid.

    Args:
        path: Path to the input file, or "-" for stdin.
        output: Path to the output file, or "-" for stdout.
        width: The width to wrap lines to.
        inplace: Whether to write the file back to the same path (atomically only on success).
        nobackup: Whether to not make a backup of the original file
        plaintext: Use plaintext instead of Markdown mode wrapping.
        semantic: Use semantic line breaks (based on sentences) heuristic.
        cleanups: Enable (safe) cleanups for common issues like accidentally boldfaced section
            headers (only applies to Markdown mode).
        make_parents: Whether to make parent directories if they don't exist.
    """
    read_stdin = path == "-"
    write_stdout = output == "-"

    if inplace and read_stdin:
        raise ValueError("Cannot use `inplace` with stdin")
    if inplace and output and output != path:
        raise ValueError("Cannot use `inplace` with an output path")

    if read_stdin:
        text = sys.stdin.read()
    else:
        text = Path(path).read_text()

    result = reformat_text(text, width, plaintext, semantic, cleanups)

    if inplace:
        backup_suffix = ".orig" if not nobackup else ""
        with atomic_output_file(
            path, backup_suffix=backup_suffix, make_parents=make_parents
        ) as tmp_path:
            tmp_path.write_text(result)
    else:
        if not output or write_stdout:
            sys.stdout.write(result)
        else:
            with atomic_output_file(output, make_parents=make_parents) as tmp_path:
                tmp_path.write_text(result)
