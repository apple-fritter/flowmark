# flowmark

Flowmark is a new Python implementation of text line wrapping and filling.

It can be used as a more flexible alternative to Python's
[`textwrap`](https://docs.python.org/3/library/textwrap.html) with a few more features,
such as full customizability of initial and subsequent indentation strings, and more
control over when to split words, so it won't break lines within HTML tags.

It also combines line wrapping with support for Markdown and offers Markdown
auto-formatting, like [markdownfmt](https://github.com/shurcooL/markdownfmt), also with
controllable line wrapping options.

One key use case is to normalize Markdown in a standard, readable way that makes diffs
easy to read and use on GitHub.
This can be useful for documentation workflows and also to compare LLM outputs that are
Markdown.

Finally, it has options to use heuristics to split on sentences, which can make diffs
much more readable. (For an example of this, look at the source to this readme file.)

It aims to be small and simple and have only a few dependencies, currently only
[`marko`](https://github.com/frostming/marko) and
[`regex`](https://pypi.org/project/regex/).

This is a new and simple package (previously I'd implemented something like this
[for Atom](https://github.com/jlevy/atom-flowmark)) but I plan to add more support for
command line usage and VSCode/Cursor auto-formatting in the future.

* * *

*This project was built from
[simple-modern-poetry](https://github.com/jlevy/simple-modern-poetry).*
