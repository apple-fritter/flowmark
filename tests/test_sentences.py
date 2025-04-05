from flowmark import first_sentence, split_sentences_regex

LONG_TEXT = """
End of sentence must be two letters or more,
with the last letter lowercase, followed by a period, exclamation point,
question mark. A final or preceding parenthesis or quote is allowed.
Does not break on colon or semicolon as that seems to have false
positives too often with code or other syntax.
"""

FIRST_SENTENCE = "End of sentence must be two letters or more, with the last letter lowercase, followed by a period, exclamation point, question mark."


def test_split_sentences():
    assert split_sentences_regex("test!") == ["test!"]
    assert split_sentences_regex("test! random words") == ["test! random words"]

    split_sentences = split_sentences_regex(LONG_TEXT)
    print(split_sentences)
    assert len(split_sentences) == 3
    assert split_sentences[0] == FIRST_SENTENCE


def test_first_sentence():
    assert first_sentence(LONG_TEXT) == FIRST_SENTENCE

    assert first_sentence("") == ""
    assert first_sentence(" ") == " "
    assert first_sentence("hello") == "hello"
    assert first_sentence(" hello\n") == "hello"
