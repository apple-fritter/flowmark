from __future__ import annotations

from collections.abc import Callable

from marko import block, inline
from marko.block import Document
from marko.element import Element

ContainerElement = (
    block.Document,
    block.Quote,
    block.List,
    block.ListItem,
    block.Paragraph,  # Paragraphs contain inline elements
    block.Heading,  # Already handled, but include for completeness if structure changes
    inline.Emphasis,
    inline.StrongEmphasis,
    inline.Link,
)


def transform_tree(element: Element, transformer: Callable[[Element], None]) -> None:
    """
    Recursively traverse the element tree and apply a transformer function to each node.
    """
    transformer(element)

    # Recursively process children for known container types
    if isinstance(element, ContainerElement):
        # Now we know element has a .children attribute that's a Sequence[Element] or str
        # We only care about processing Element children
        if isinstance(element.children, list):
            # Create a copy for safe iteration if modification occurs
            current_children = list(element.children)
            for child in current_children:
                transform_tree(child, transformer)


def coalesce_raw_text_nodes(doc: Document) -> None:
    """
    Coalesce adjacent RawText nodes that are separated only by LineBreak elements.

    This is useful for smart quotes processing which needs to see text that spans
    across line breaks as a single unit.
    """
    from flowmark.doc_transforms import transform_tree

    def transformer(element: Element) -> None:
        if hasattr(element, "children") and isinstance(element.children, list):  # pyright: ignore
            new_children: list[Element] = []
            i = 0
            children: list[Element] = element.children  # pyright: ignore
            while i < len(children):
                child = children[i]

                # If this is a RawText node, look ahead for a pattern of
                # RawText -> LineBreak -> RawText and coalesce them
                if isinstance(child, inline.RawText):
                    coalesced_text = child.children
                    j = i + 1

                    # Look for pattern: RawText, LineBreak, RawText, LineBreak, ...
                    while j + 1 < len(children):
                        next_elem = children[j]
                        following_elem = children[j + 1] if j + 1 < len(children) else None

                        if (
                            isinstance(next_elem, inline.LineBreak)
                            and next_elem.soft
                            and isinstance(following_elem, inline.RawText)
                        ):
                            # Coalesce: add newline and the next text
                            coalesced_text += "\n" + following_elem.children
                            j += 2  # Skip the LineBreak and RawText we just consumed
                        else:
                            break

                    # Create new RawText node with coalesced content
                    if j > i + 1:  # We coalesced something
                        child.children = coalesced_text
                        new_children.append(child)
                        i = j  # Skip all the nodes we coalesced
                    else:
                        new_children.append(child)
                        i += 1
                else:
                    new_children.append(child)
                    i += 1

            element.children = new_children  # pyright: ignore[reportAttributeAccessIssue]

    transform_tree(doc, transformer)


def rewrite_text_content(
    doc: Document, rewrite_func: Callable[[str], str], *, coalesce_lines: bool = False
) -> None:
    """
    Apply a string rewrite function to all `RawText` nodes that are not part of
    code blocks.

    This function modifies the Marko document tree in place.
    It traverses the document and applies `string_rewrite_func` to the content
    of `marko.inline.RawText` elements. It skips text within any kind of code
    block (`FencedCode`, `CodeBlock`, `CodeSpan`).

    Args:
        doc: The document to process
        rewrite_func: Function to apply to each RawText node's content
        coalesce_lines: If True, coalesce adjacent RawText nodes separated by
            LineBreak elements before applying the rewrite function. This is
            useful for functions like smart quotes that need to see text spans
            across line breaks as a single unit.
    """
    if coalesce_lines:
        coalesce_raw_text_nodes(doc)

    def transformer(element: Element) -> None:
        if isinstance(element, inline.RawText):
            assert isinstance(element.children, str)
            element.children = rewrite_func(element.children)

    transform_tree(doc, transformer)
