from flowmark.smartquotes import smart_quotes


def test_basic_double_quotes():
    """Test basic double quote conversion."""
    assert smart_quotes('I\'m there with "George"') == "I\u2019m there with \u201cGeorge\u201d"
    assert smart_quotes('"Hello," he said.') == "\u201cHello,\u201d he said."
    assert smart_quotes('"I know!"') == "\u201cI know!\u201d"


def test_basic_single_quotes():
    """Test basic single quote conversion."""
    assert (
        smart_quotes("Words in 'single quotes' work too")
        == "Words in \u2018single quotes\u2019 work too"
    )
    assert smart_quotes("X is 'foo'") == "X is \u2018foo\u2019"


def test_apostrophes_and_contractions():
    """Test apostrophe and contraction conversion."""
    assert smart_quotes("I'm there") == "I\u2019m there"
    assert smart_quotes("I'll be there, don't worry") == "I\u2019ll be there, don\u2019t worry"
    assert smart_quotes("Jill's") == "Jill\u2019s"
    assert smart_quotes("James'") == "James\u2019"


def test_possessives_at_end_of_words():
    """Test possessives at the end of words ending in s."""
    assert smart_quotes("James'") == "James\u2019"
    assert smart_quotes("The students' books") == "The students\u2019 books"
    assert smart_quotes("Mr. Jones' house") == "Mr. Jones\u2019 house"
    assert smart_quotes("The cats' toys") == "The cats\u2019 toys"
    assert smart_quotes("Jesus' disciples") == "Jesus\u2019 disciples"
    assert smart_quotes("The class' performance") == "The class\u2019 performance"


def test_patterns_left_unchanged():
    """Test patterns that should remain unchanged."""
    assert smart_quotes("In the '60s") == "In the '60s"  # not worth special casing
    assert smart_quotes('x="foo"') == 'x="foo"'
    assert smart_quotes("x='foo'") == "x='foo'"
    assert smart_quotes("Blah'blah'blah") == "Blah'blah'blah"
    assert smart_quotes('""quotes"s') == '""quotes"s'
    assert smart_quotes('\\"escaped\\"') == '\\"escaped\\"'
    assert smart_quotes("'apos'trophes") == "'apos'trophes"


def test_quotes_with_punctuation():
    """Test quotes followed by various punctuation marks."""
    assert smart_quotes('"Hello,"') == "\u201cHello,\u201d"
    assert smart_quotes('"Wait;"') == "\u201cWait;\u201d"
    assert smart_quotes('"Stop:"') == "\u201cStop:\u201d"
    assert smart_quotes('"Really?"') == "\u201cReally?\u201d"
    assert smart_quotes('"Yes!"') == "\u201cYes!\u201d"
    assert smart_quotes('"End."') == "\u201cEnd.\u201d"


def test_quotes_at_boundaries():
    """Test quotes at sentence boundaries."""
    assert smart_quotes('"Start of sentence"') == "\u201cStart of sentence\u201d"
    assert (
        smart_quotes('He said "middle of sentence" and continued')
        == "He said \u201cmiddle of sentence\u201d and continued"
    )


def test_mixed_quotes_and_apostrophes():
    """Test text with both quotes and apostrophes."""
    assert (
        smart_quotes('I\'m reading "The Great Gatsby" today')
        == "I\u2019m reading \u201cThe Great Gatsby\u201d today"
    )
    assert (
        smart_quotes('She said "I can\'t believe it!"')
        == "She said \u201cI can\u2019t believe it!\u201d"
    )


def test_edge_cases():
    """Test edge cases."""
    assert smart_quotes("") == ""
    assert smart_quotes("No quotes here") == "No quotes here"
    assert smart_quotes('Just "quotes"') == "Just \u201cquotes\u201d"
    assert smart_quotes("'Single'") == "\u2018Single\u2019"


def test_multiple_quotes_in_text():
    """Test text with multiple separate quoted sections."""
    assert (
        smart_quotes('He said "hello" and she said "goodbye"')
        == "He said \u201chello\u201d and she said \u201cgoodbye\u201d"
    )
    assert (
        smart_quotes("The words 'yes' and 'no' are opposites")
        == "The words \u2018yes\u2019 and \u2018no\u2019 are opposites"
    )


def test_complex_sentences():
    """Test more complex real-world sentences."""
    text = "John said \"I can't believe it's not butter!\" at the store."
    expected = "John said \u201cI can\u2019t believe it\u2019s not butter!\u201d at the store."
    assert smart_quotes(text) == expected


def test_technical_content_unchanged():
    """Test that technical content is not modified."""
    assert smart_quotes('function("param")') == 'function("param")'
    assert smart_quotes("array['key']") == "array['key']"
    assert smart_quotes('height="100px"') == 'height="100px"'
    assert smart_quotes("class='my-class'") == "class='my-class'"


def test_complex_cases_unchanged():
    """Test that nested or complex quote patterns are left alone."""
    assert smart_quotes('quote"in"quote') == 'quote"in"quote'
    assert smart_quotes('""nested""') == '""nested""'
    assert smart_quotes("''nested''") == "''nested''"
    assert smart_quotes('""nested"') == '""nested"'
    assert smart_quotes("'nested''") == "'nested''"
    assert smart_quotes('x="foo"') == 'x="foo"'
    assert smart_quotes("x='foo'") == "x='foo'"
    assert smart_quotes("Blah'blah'blah") == "Blah'blah'blah"
    assert smart_quotes('""quotes"s') == '""quotes"s'
    assert smart_quotes('\\"escaped\\"') == '\\"escaped\\"'
    assert smart_quotes("'apos") == "'apos"
    assert smart_quotes("'apos'trophes") == "'apos'trophes"
    assert smart_quotes("$James'") == "$James'"
