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


def _unbold_heading_transformer(element: Element) -> None:
    """
    Transformer function to unbold headings where the entire text is bold.
    """
    if isinstance(element, block.Heading):
        # Check if the heading consists *only* of a single StrongEmphasis element
        if len(element.children) == 1 and isinstance(element.children[0], inline.StrongEmphasis):
            # Replace the heading's children with the children of the StrongEmphasis element
            strong_emphasis_node = element.children[0]
            # Type checker struggles here, but StrongEmphasis children should be Elements.
            element.children = strong_emphasis_node.children  # pyright: ignore

        # Handle the case where the heading is bold and italic (StrongEmphasis inside Emphasis or vice versa)
        # ***text***  -> *text*
        elif len(element.children) == 1 and isinstance(element.children[0], inline.Emphasis):
            emphasis_node = element.children[0]
            if len(emphasis_node.children) == 1 and isinstance(
                emphasis_node.children[0], inline.StrongEmphasis
            ):
                strong_node = emphasis_node.children[0]
                emphasis_node.children = strong_node.children


def unbold_headings(doc: Document) -> None:
    """
    Find headings where the entire text is bold and remove the bold.

    Modifies the Marko document tree in place using a general transformer.
    Example: `## **My Heading**` -> `## My Heading`
    """
    transform_tree(doc, _unbold_heading_transformer)


def doc_cleanups(doc: Document):
    """
    Apply (ideally quite safe) cleanups to the document.
    """
    unbold_headings(doc)
