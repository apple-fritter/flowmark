from pathlib import Path
from typing import TypedDict

from flowmark.markdown_filling import fill_markdown

testdoc_dir = Path("tests/testdocs")


def test_reference_doc_formats():
    """Test that the reference document is formatted correctly with both plain and semantic formats."""
    orig_path = testdoc_dir / "testdoc.orig.md"

    # Check that original file exists
    assert orig_path.exists(), f"Original test document not found at {orig_path}"

    # Read the original content
    with open(orig_path) as f:
        orig_content = f.read()

    class TestCase(TypedDict):
        name: str
        filename: str
        by_sentence: bool

    # Test configurations
    test_cases: list[TestCase] = [
        {"name": "plain", "filename": "testdoc.out.plain.md", "by_sentence": False},
        {"name": "semantic", "filename": "testdoc.out.semantic.md", "by_sentence": True},
    ]

    for case in test_cases:
        output_path = testdoc_dir / case["filename"]
        assert output_path.exists(), (
            f"{case['name'].capitalize()}-processed document not found at {output_path}"
        )

        # Read the processed content
        with open(output_path) as f:
            processed_content = f.read()

        # Process the original file using fill_markdown with appropriate option
        expected_content = fill_markdown(orig_content, semantic=case["by_sentence"])

        # Compare the processed content with the expected output
        assert expected_content == processed_content, (
            f"{case['name'].capitalize()} flowmark processing doesn't match expected output"
        )
