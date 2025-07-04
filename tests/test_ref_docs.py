from dataclasses import dataclass
from pathlib import Path

from flowmark.markdown_filling import fill_markdown

testdoc_dir = Path("tests/testdocs")


def test_reference_doc_formats():
    """
    Test that the reference document is formatted correctly with both plain and semantic formats.
    """
    orig_path = testdoc_dir / "testdoc.orig.md"

    # Check that original file exists
    assert orig_path.exists(), f"Original test document not found at {orig_path}"

    # Read the original content
    with open(orig_path) as f:
        orig_content = f.read()

    @dataclass(frozen=True)
    class TestCase:
        name: str
        filename: str
        semantic: bool
        cleanups: bool
        smartquotes: bool

    test_cases: list[TestCase] = [
        TestCase(
            name="plain",
            filename="testdoc.expected.plain.md",
            semantic=False,
            cleanups=False,
            smartquotes=False,
        ),
        TestCase(
            name="semantic",
            filename="testdoc.expected.semantic.md",
            semantic=True,
            cleanups=False,
            smartquotes=False,
        ),
        TestCase(
            name="cleaned",
            filename="testdoc.expected.cleaned.md",
            semantic=True,
            cleanups=True,
            smartquotes=False,
        ),
        TestCase(
            name="auto",
            filename="testdoc.expected.auto.md",
            semantic=True,
            cleanups=True,
            smartquotes=True,
        ),
    ]

    expecteds: list[str] = []
    actuals: list[str] = []
    for case in test_cases:
        test_doc = testdoc_dir / case.filename
        expected = test_doc.read_text()

        actual = fill_markdown(
            orig_content,
            semantic=case.semantic,
            cleanups=case.cleanups,
            smartquotes=case.smartquotes,
        )
        if actual != expected:
            actual_path = testdoc_dir / f"testdoc.actual.{case.name}.md"
            print(f"actual was different from expected for {case.name}!")
            print(f"Saving actual to: {actual_path}")
            actual_path.write_text(actual)

        expecteds.append(expected)
        actuals.append(actual)

    for expected, actual in zip(expecteds, actuals, strict=True):
        assert expected == actual
