from collections.abc import Callable

import regex

# XXX: Could also handle rare cases with both quotes and parentheses at sentence end
# but may not be worth it. Also does not detect sentences ending in numerals, which
# tends to cause too many false positives. Should be OK for most Latin languages but
# may need to rethink the 2-letter restriction for some languages.
# See also:
# https://github.com/jlevy/atom-flowmark/blob/master/lib/remark-smart-word-wrap.js#L17-L33
SENTENCE_END_RE = regex.compile(r"(\b\p{L}+[\p{Ll}])([.?!]['\"’”)]?|['\"’”)][.?!]) *$")

# Second heuristic: Very short sentences often not so useful.
SENTENCE_MIN_LENGTH = 15


def heuristic_end_of_sentence(word: str) -> bool:
    return bool(SENTENCE_END_RE.search(word))


def split_sentences_regex(
    text: str,
    min_length: int = SENTENCE_MIN_LENGTH,
    heuristic: Callable[[str], bool] = heuristic_end_of_sentence,
) -> list[str]:
    """
    Split text into sentences using an approximate, fast regex heuristic.

    Goal is to be conservative, not perfect, avoiding excessive breaks.

    The default heuristic: End of sentence must be two letters or more,
    with the last letter lowercase, followed by a period, exclamation point,
    question mark. A final or preceding parenthesis or quote is allowed.
    Does not break on colon or semicolon as that seems to have false
    positives too often with code or other syntax.

    They work pretty well when used for formatting and editing documents
    in English. It should be reasonable for most Latin languages.
    Note this is smarter than Python textwrap's simpler heuristic:
    https://github.com/python/cpython/blob/main/Lib/textwrap.py#L105-L110

    :param text: The text to split into sentences.
    :param heuristic: A callable that returns True if text ends at the end of a sentence.
    :param min_length: The minimum length of a sentence in characters.
    :return: A list of sentences.
    """
    words = text.split()
    sentences: list[str] = []
    sentence: list[str] = []
    words_len = 0
    for word in words:
        sentence.append(word)
        words_len += len(word)
        sentence_len = words_len + len(sentence) - 1
        if heuristic(word) and sentence_len >= min_length:
            sentences.append(" ".join(sentence))
            sentence = []
            words_len = 0
    if sentence:
        sentences.append(" ".join(sentence))
    return sentences


def first_sentences(
    text: str,
    n: int,
    min_length: int = SENTENCE_MIN_LENGTH,
    heuristic: Callable[[str], bool] = heuristic_end_of_sentence,
) -> list[str]:
    """
    Return the first n sentences from the text.
    """
    return split_sentences_regex(text, min_length=min_length, heuristic=heuristic)[:n]


def first_sentence(
    text: str,
    min_length: int = SENTENCE_MIN_LENGTH,
    heuristic: Callable[[str], bool] = heuristic_end_of_sentence,
) -> str:
    """
    Return the first sentence from the text. Returns input text unchanged if no
    sentences are found.
    """
    sentences = split_sentences_regex(text, min_length=min_length, heuristic=heuristic)
    return sentences[0] if sentences else text
