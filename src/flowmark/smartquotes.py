import re
from re import Match, Pattern

# Precompiled regex patterns
PARAGRAPH_BREAK_PATTERN: Pattern[str] = re.compile(r"\n\s*\n")

# Pattern excludes content that contains the same type of quote characters
# Double quotes exclude double quotes, single quotes exclude single quotes
QUOTE_PATTERN: Pattern[str] = re.compile(
    r'(^|\s)(?:"([^"\u201c\u201d]*)"|\'([^\'\u2018\u2019]*)\')(\s|$|\.|,|;|:|\?|!|—|\))',
    re.MULTILINE,
)


def is_multi_paragraph(text: str) -> bool:
    """Check if text contains paragraph breaks (two newlines with optional whitespace)."""
    return PARAGRAPH_BREAK_PATTERN.search(text) is not None


def smart_quotes(text: str) -> str:
    r"""
    Replace straight ASCII quotes and apostrophes with typographic quotes and apostrophes
    when this can be done safely. Aims to be conservative so it doesn't break code or
    things that aren't language.

    Text that is wrapped in single or double quotes is replaced with typographic quotes
    if it has whitespace or a newline at the front and is followed by whitespace or
    a [.,?!]. The content inside quotes must not contain any of the same type (single
    or double). Quotes containing paragraph breaks (two newlines) are left unchanged.

    Straight quotes are converted to apostrophes if they are the only straight quote
    in the word, and have word characters on both sides:

    I'm there with "George" -> I’m there with “George”
    "Hello," he said. -> “Hello,” he said.
    "I know!" -> “I know!”

    Words in 'single quotes' work too -> Words in 'single quotes' work too

    I'm there -> I’m there
    I'll be there, don't worry -> I’ll be there, don’t worry
    X is 'foo' -> X is ‘foo’

    A few special rules to better help with English:

    Jill's -> Jill’s
    James' -> James’

    Other patterns are unchanged:

    x="foo" -> x="foo"
    x='foo' -> x='foo'
    Blah'blah'blah -> Blah'blah'blah
    ""quotes"s -> ""quotes"s
    \"escaped\" -> \"escaped\"
    'apos -> 'apos
    'apos'trophes -> 'apos'trophes
    $James' -> $James'

    """

    # First handle quoted text - both single and double quotes
    def replace_quotes(match: Match[str]) -> str:
        prefix = match.group(1)
        double_content = match.group(2)  # Content of double quotes
        single_content = match.group(3)  # Content of single quotes
        suffix = match.group(4)

        # Check for paragraph breaks in the content
        content = double_content if double_content is not None else single_content
        if is_multi_paragraph(content):
            # Don't convert quotes that contain paragraph breaks
            return match.group(0)

        if double_content is not None:
            # Replace double quotes with typographic quotes
            return prefix + "\u201c" + double_content + "\u201d" + suffix
        else:
            # Replace single quotes with typographic quotes
            return prefix + "\u2018" + single_content + "\u2019" + suffix

    result = QUOTE_PATTERN.sub(replace_quotes, text)

    # Now handle apostrophes/contractions
    # Only convert single quotes that are:
    # 1. The only quote in the word
    # 2. Have word characters on both sides OR are possessives at end of words ending in s/S

    # Pattern for apostrophes: word char + ' + word char, where ' is the only quote in the word
    # We need to be careful not to match words that have multiple quotes

    # Split by whitespace to process words individually
    words = re.split(r"(\s+)", result)

    for i, word in enumerate(words):
        # Skip whitespace
        if word.isspace():
            continue

        # Count straight quotes in the word
        quote_count = word.count("'")

        # Only process if there's exactly one straight quote
        if quote_count == 1:
            # Check if it's surrounded by word characters (contractions)
            apostrophe_pattern = r"(\w)\'(\w)"
            if re.search(apostrophe_pattern, word):
                # Replace the single quote with apostrophe
                words[i] = re.sub(r"\'", "\u2019", word)
            # Check if it's a possessive at the end of a word ending in s/S
            elif re.match(r"\w*[sS]\'$", word):
                # Replace the single quote with apostrophe
                words[i] = re.sub(r"\'", "\u2019", word)

    return "".join(words)
