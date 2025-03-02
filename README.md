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

```
pip install flowmark
```

* * *

*This project was built from
[simple-modern-poetry](https://github.com/jlevy/simple-modern-poetry).*
