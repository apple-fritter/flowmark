#!/usr/bin/env python3
"""
Flowmark: Better line wrapping and formatting for plaintext and Markdown

Flowmark provides enhanced text wrapping capabilities with special handling for
Markdown content. It can:

- Format Markdown with proper line wrapping while preserving structure
  and normalizing Markdown formatting

- Optionally break lines at sentence boundaries for better diff readability

- Process plaintext with HTML-aware word splitting

It is both a library and a command-line tool.

Command-line usage examples:

  # Format a Markdown file to stdout
  flowmark README.md

  # Format a Markdown file and save to a new file
  flowmark README.md -o README_formatted.md

  # Edit a file in-place (with or without making a backup)
  flowmark --inplace README.md
  flowmark --inplace --nobackup README.md

  # Process plaintext instead of Markdown
  flowmark --plaintext text.txt

  # Use semantic line breaks (based on sentences, which is helpful to reduce
  # irrelevant line wrap diffs in git history)
  flowmark --semantic README.md

For more details, see: https://github.com/jlevy/flowmark
"""

import argparse
import importlib.metadata
import sys
from dataclasses import dataclass

from strif import atomic_output_file

from flowmark import Wrap, fill_markdown, fill_text, html_md_word_splitter


@dataclass
class Options:
    """Command-line options for the flowmark tool."""

    file: str
    output: str
    width: int
    plaintext: bool
    semantic: bool
    inplace: bool
    nobackup: bool
    version: bool


def _parse_args(args: list[str] | None = None) -> Options:
    """Parse command-line arguments for the flowmark tool."""
    # Use the module's docstring as the description
    module_doc = __doc__ or ""
    doc_parts = module_doc.split("\n\n")
    description = doc_parts[0]
    epilog = "\n\n".join(doc_parts[1:])

    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "file",
        nargs="?",
        type=str,
        default="-",
        help="Input file (use '-' for stdin)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="-",
        help="Output file (use '-' for stdout)",
    )
    parser.add_argument("-w", "--width", type=int, default=88, help="Line width to wrap to")
    parser.add_argument(
        "-p", "--plaintext", action="store_true", help="Process as plaintext (no Markdown parsing)"
    )
    parser.add_argument(
        "-s",
        "--semantic",
        action="store_true",
        default=False,
        help="Enable semantic (sentence-based) line breaks (only applies to Markdown mode)",
    )
    parser.add_argument(
        "-i", "--inplace", action="store_true", help="Edit the file in place (ignores --output)"
    )
    parser.add_argument(
        "--nobackup",
        action="store_true",
        help="Do not make a backup of the original file when using --inplace",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Same as `--inplace --nobackup --semantic`, as a convenience for auto-formatting files",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version information and exit",
    )
    opts = parser.parse_args(args)

    if opts.auto:
        opts.inplace = True
        opts.nobackup = True
        opts.semantic = True

    return Options(
        file=opts.file,
        output=opts.output,
        width=opts.width,
        plaintext=opts.plaintext,
        semantic=opts.semantic,
        inplace=opts.inplace,
        nobackup=opts.nobackup,
        version=opts.version,
    )


def main(args: list[str] | None = None) -> int:
    """
    Main entry point for the flowmark CLI.

    Args:
        args: Command-line arguments (uses sys.argv if None)

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    options = _parse_args(args)

    # Display version information if requested
    if options.version:
        try:
            version = importlib.metadata.version("flowmark")
            print(f"v{version}")
        except importlib.metadata.PackageNotFoundError:
            print("unknown (package not installed)")
        return 0

    # Handle input.
    if options.file == "-":
        text = sys.stdin.read()
    else:
        with open(options.file) as f:
            text = f.read()

    if options.plaintext:
        # Plaintext mode
        result = fill_text(
            text,
            text_wrap=Wrap.WRAP,
            width=options.width,
            word_splitter=html_md_word_splitter,  # Still use HTML/MD aware splitter by default
        )
    else:
        # Markdown mode
        result = fill_markdown(
            text,
            width=options.width,
            semantic=options.semantic,
            dedent_input=True,
        )

    # Handle output
    if options.inplace:
        if options.file == "-":
            print("Error: Cannot use --inplace with stdin", file=sys.stderr)
            return 1
        backup_suffix = ".orig" if not options.nobackup else ""
        with atomic_output_file(options.file, backup_suffix=backup_suffix) as tmp_path:
            with open(tmp_path, "w") as f:
                f.write(result)
    else:
        if options.output == "-":
            sys.stdout.write(result)
        else:
            with open(options.output, "w") as f:
                f.write(result)

    return 0


if __name__ == "__main__":
    sys.exit(main())
