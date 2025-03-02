# flowmark

Flowmark is a new Python implementation of text line wrapping and filling.

It simplifies and generalizes Python's
[`textwrap`](https://docs.python.org/3/library/textwrap.html) with a few more
capabilities:

- Full customizability of initial and subsequent indentation strings

- Control over when to split words, by default using a word splitter that won't break
  lines within HTML tags

In addition, it adds optional support for Markdown and offers Markdown auto-formatting,
like [markdownfmt](https://github.com/shurcooL/markdownfmt), also with controllable line
wrapping options.

One key use case is to normalize Markdown in a standard, readable way that makes diffs
easy to read and use on GitHub.
This can be useful for documentation workflows and also to compare LLM outputs that are
Markdown.

Finally, it has options to use heuristics to split on sentences, which can make diffs
much more readable. (For an example of this, look at the
[Markdown source](https://github.com/jlevy/flowmark/blob/main/README.md?plain=1) of this
readme file.)

It aims to be small and simple and have only a few dependencies, currently only
[`marko`](https://github.com/frostming/marko) and
[`regex`](https://pypi.org/project/regex/).

This is a new and simple package (previously I'd implemented something like this
[for Atom](https://github.com/jlevy/atom-flowmark)) but I plan to add more support for
command line usage and VSCode/Cursor auto-formatting in the future.

## Installation

The simplest way to use the tool is to use pipx:

```shell
pipx install flowmark
```

To use as a library, use pip or poetry to install `flowmark`.

## Usage

Flowmark can be used as a library or as a CLI.

```
$ flowmark --help
usage: flowmark [-h] [-o OUTPUT] [-w WIDTH] [-p] [-s] [-i] [--nobackup] [file]

Flowmark: Better line wrapping and formatting for plaintext and Markdown

positional arguments:
  file                 Input file (use '-' for stdin)

options:
  -h, --help           show this help message and exit
  -o, --output OUTPUT  Output file (use '-' for stdout)
  -w, --width WIDTH    Line width to wrap to
  -p, --plaintext      Process as plaintext (no Markdown parsing)
  -s, --sentences      Enable sentence-based line breaks (only applies to Markdown mode)
  -i, --inplace        Edit the file in place (ignores --output)
  --nobackup           Do not make a backup of the original file when using --inplace

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

  # Use sentences to guide line breaks (good for many purposes git history and diffs)
  flowmark --sentences README.md

For more details, see: https://github.com/jlevy/flowmark
```

* * *

*This project was built from
[simple-modern-poetry](https://github.com/jlevy/simple-modern-poetry).*
