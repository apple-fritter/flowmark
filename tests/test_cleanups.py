from flowmark.formats.flowmark_markdown import flowmark_markdown
from flowmark.linewrapping.line_wrappers import line_wrap_by_sentence
from flowmark.transforms.doc_cleanups import unbold_headings

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
    marko = flowmark_markdown(line_wrap_by_sentence())

    doc = marko.parse(input_md)
    unbold_headings(doc)
    rendered_md = marko.render(doc).strip()

    assert rendered_md == expected_md.strip()
