# flowmark

Flowmark is a new Python implementation of **text and Markdown line wrapping and
filling**.

In addition, it adds optional **support for Markdown** and offers **Markdown
auto-formatting and normalization**. This is much like
[markdownfmt](https://github.com/shurcooL/markdownfmt) or
[prettier's Markdown support](https://prettier.io/blog/2017/11/07/1.8.0) but is pure
Python and has (in my humble opinion) better options and defaults.

Use cases:

- As a **command line formatter** to format text or Markdown files using the `flowmark`
  command.

- To **autoformat Markdown on save in VSCode/Cursor** or any other editor that supports
  running the command.
  This uses a readable format that makes diffs easy to read and use on GitHub.
  It also normalizes all Markdown syntax variations (such as different header or
  formatting styles). This can be especially useful for documentation and editing
  workflows where clean diffs and minimal merge conflicts on GitHub are important.

- As a **library to autoformat Markdown**. For example, it is great to normalize the
  outputs from LLMs to be consistent, or to run on the inputs and outputs of LLM
  transformations that edit text, so that the resulting diffs are clean.
  Having this as a simple Python library makes this easy in AI-related document
  pipelines.

- As a **drop-in replacement library for Python's default
  [`textwrap`](https://docs.python.org/3/library/textwrap.html)** but with more options.
  It simplifies and generalizes that library, offering better control over **initial and
  subsequent indentation** and **when to split words and lines**, e.g. using a word
  splitter that won't break lines within HTML tags.

- For simple (zero dependency) **regex-based sentence splitting**. Flowmark has the
  option to to use heuristics to break lines on sentences when reasonable, which is an
  underrated feature that can make diffs between versions of docs and on GitHub much
  more readable. (For an example of what this looks like, see the
  [Markdown source](https://github.com/jlevy/flowmark/blob/main/README.md?plain=1) of
  this readme file.)

It aims to be small and simple and have only a few dependencies, currently only
[`marko`](https://github.com/frostming/marko),
[`regex`](https://pypi.org/project/regex/), and
[`strif`](https://github.com/jlevy/strif).

This is a new and simple package.
Previously I'd implemented something very similar with
[for Atom](https://github.com/jlevy/atom-flowmark) but Atom is no more and there seems
to be greater need for this in Python now.
From many years experience, I found the Markdown formatting conventions enforced by the
Atom Flowmark plugin worked well for editing and publishing large or collaboratively
edited documents.

## Installation

The simplest way to use the tool is to use [pipx](https://github.com/pypa/pipx):

```shell
pipx install flowmark
```

Then

```
flowmark --help
```

To use as a library, use pip/poetry/uv to install
[`flowmark`](https://pypi.org/project/flowmark/).

## Use in VSCode/Cursor

You can use Flowmark to auto-format Markdown on save in VSCode or Cursor.
Install the "Run on Save" (`emeraldwalk.runonsave`) extension.
Then add to your `settings.json`:

```json
  "emeraldwalk.runonsave": {
    "commands": [
        {
            "match": "\\.md$",
            "cmd": "flowmark --auto ${file}"
        }
    ]
  }
```

The `--auto` option is just the same as `--inplace --nobackup --sentences`.

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
