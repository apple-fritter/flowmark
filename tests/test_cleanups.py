from flowmark.cleanups import unbold_headings
from flowmark.custom_marko import custom_marko
from flowmark.line_wrappers import line_wrap_by_sentence

input_md = """
# **Bold Heading 1**

Some paragraph text.

## ***Bold Italic***

## **Simple Bold**

### Not Bold

#### **Partial** Bold

#### Other *partial* **bold** `code`

- **List Item Bold**

Another paragraph with **bold** text.

## **Nested `code`**

Final text.
"""


expected_md = """
# Bold Heading 1

Some paragraph text.

## *Bold Italic*

## Simple Bold

### Not Bold

#### **Partial** Bold

#### Other *partial* **bold** `code`

- **List Item Bold**

Another paragraph with **bold** text.

## Nested `code`

Final text.
"""


def test_unbold_headings() -> None:
    marko = custom_marko(line_wrap_by_sentence())

    doc = marko.parse(input_md)
    unbold_headings(doc)
    rendered_md = marko.render(doc).strip()

    assert rendered_md == expected_md.strip()
