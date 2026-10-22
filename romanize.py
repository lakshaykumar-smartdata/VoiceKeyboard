"""
Romanize Devanagari (Hindi) text into readable Latin / Hinglish script.

Google Speech API (hi-IN) returns Hindi in Devanagari and English words in
Latin. This module converts only the Devanagari runs to Latin so the final
transcript reads as natural Hinglish, e.g.:

    "मैं project complete कर दूंगा"  ->  "main project complete kar dunga"

The transliteration is phonetic and approximate. It applies word-final schwa
deletion (the trailing inherent 'a'), but NOT full internal schwa deletion, so
a few words may keep an extra vowel. That is fine for a readable transcript.
"""

import re

from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

# Matches one or more Devanagari characters (incl. ZWJ used in conjuncts).
_DEVANAGARI_RUN = re.compile(r"[ऀ-ॿ‍]+")

# Candra vowels (used for English loanwords like कॉल, नॉन) are not handled by
# ITRANS, so map them to their nearest standard Devanagari vowel first.
_PRE_NORMALIZE = {
    "ॉ": "ो", "ऑ": "ओ",   # candra O  -> o   (call, non, because)
    "ॅ": "े", "ऍ": "ए",   # candra E  -> e
}

# ITRANS artifact cleanup, applied in order.
_REPLACEMENTS = [
    (".Dh", "dh"), (".D", "d"),          # nukta retroflex flap ड़ / ढ़
    (".N", "n"), (".n", "n"), (".m", "m"),  # chandrabindu / nasals
    ("~N", "n"), ("~n", "n"), ("N^", "n"),
    ("GY", "gy"), ("J~", "gy"),
    ("M", "n"), ("H", "h"),              # anusvara / visarga
    ("RRi", "ri"), ("RR", "ri"), ("R^i", "ri"),
    ("A", "aa"), ("I", "ii"), ("U", "uu"),  # long vowels
]

# Any leftover ITRANS control characters get stripped.
_STRIP = str.maketrans("", "", ".~^\\_")


def _romanize_devanagari_run(dev_text: str) -> str:
    """Transliterate a pure-Devanagari string to readable Hinglish."""
    for src, dst in _PRE_NORMALIZE.items():
        dev_text = dev_text.replace(src, dst)

    t = transliterate(dev_text, sanscript.DEVANAGARI, sanscript.ITRANS)

    for src, dst in _REPLACEMENTS:
        t = t.replace(src, dst)

    t = t.translate(_STRIP).lower()

    # Word-final schwa deletion: drop a trailing single 'a' (keep 'aa').
    def _drop_final_schwa(word: str) -> str:
        if len(word) > 2 and word.endswith("a") and not word.endswith("aa"):
            return word[:-1]
        return word

    return " ".join(_drop_final_schwa(w) for w in t.split(" "))


def romanize(text: str) -> str:
    """Replace every Devanagari run in `text` with its Hinglish romanization.

    Non-Devanagari characters (English words, digits, punctuation) are left
    untouched, so mixed Hindi-English input stays readable.
    """
    if not text:
        return text
    return _DEVANAGARI_RUN.sub(lambda m: _romanize_devanagari_run(m.group()), text)
