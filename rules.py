#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║         AWAIS X HACKER TEAM  —  RULES & MASK ENGINE          ║
║                    rules.py  |  v6.2 ULTIMATE                ║
║                                                              ║
║   Smart wordlist mutations (leet, suffixes, case) +          ║
║   incremental mask brute-force (?l?u?d?s patterns).          ║
╚══════════════════════════════════════════════════════════════╝
"""

import itertools
import string


# ─── LEET / CASE TRANSFORMS ─────────────────────────────
LEET_MAP = str.maketrans({"a": "4", "e": "3", "i": "1", "o": "0",
                          "s": "5", "t": "7", "A": "4", "E": "3",
                          "I": "1", "O": "0", "S": "5", "T": "7"})

COMMON_SUFFIXES = ["", "1", "12", "123", "1234", "12345", "123456",
                   "!", "!!", "@", "#", "*", "007", "2020", "2021",
                   "2022", "2023", "2024", "2025", "2026",
                   "pk", "786", "111", "000", "99"]


def leet(word):
    return word.translate(LEET_MAP)


def case_variants(word):
    out = {word, word.capitalize(), word.upper()}
    if word.isalpha():
        out.add(word.lower())
    return out


def mutate_word(word, with_leet=True, max_per_word=48):
    """
    Yield smart mutations of a single word, de-duplicated.
    Order: original first (most likely), then suffixes, case, leet.
    """
    seen = set()
    count = 0
    bases = [word] + sorted(case_variants(word) - {word})
    for base in bases:
        for suf in COMMON_SUFFIXES:
            cand = base + suf
            if cand and cand not in seen:
                seen.add(cand)
                yield cand
                count += 1
                if count >= max_per_word:
                    return
    if with_leet:
        lv = leet(word)
        if lv != word:
            for suf in ("", "1", "123", "!", "2024", "2025"):
                cand = lv + suf
                if cand not in seen:
                    seen.add(cand)
                    yield cand
                    count += 1
                    if count >= max_per_word:
                        return


def mutate_wordlist(path, with_leet=True, max_per_word=48,
                    dedup_cap=5_000_000):
    """
    Iterator: every word in the wordlist followed by its mutations.
    De-duplicates across the WHOLE stream (originals included).
    """
    seen_words = set()
    emitted = set()
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            w = line.strip()
            if not w or w in seen_words:
                continue
            seen_words.add(w)
            for cand in mutate_word(w, with_leet, max_per_word):
                if len(emitted) >= dedup_cap:
                    yield cand                  # memory cap reached
                elif cand not in emitted:
                    emitted.add(cand)
                    yield cand


# ─── MASK / BRUTE-FORCE ENGINE ──────────────────────────
MASK_CHARSETS = {
    "l": string.ascii_lowercase,
    "u": string.ascii_uppercase,
    "d": string.digits,
    "s": "!@#$%^&*-_=+",
    "a": string.ascii_lowercase + string.ascii_uppercase + string.digits,
}


def parse_mask(pattern):
    """
    '?l?l?l?d?d?d'  →  ['abc...', 'abc...', 'abc...', '012...', ...]
    Literal chars pass through as single-char sets.
    Raises ValueError on bad pattern.
    """
    tokens = []
    i = 0
    while i < len(pattern):
        ch = pattern[i]
        if ch == "?":
            if i + 1 >= len(pattern):
                raise ValueError("dangling '?' at end of mask")
            code = pattern[i + 1]
            if code not in MASK_CHARSETS:
                raise ValueError(f"unknown mask token '?{code}'")
            tokens.append(MASK_CHARSETS[code])
            i += 2
        else:
            tokens.append(ch)
            i += 1
    if not tokens:
        raise ValueError("empty mask")
    return tokens


def mask_space_size(pattern):
    """Total candidate count for a mask (int)."""
    size = 1
    for t in parse_mask(pattern):
        size *= len(t)
    return size


def mask_candidates(pattern):
    """Iterate all candidates for a mask, in order."""
    tokens = parse_mask(pattern)
    pools = [(t if isinstance(t, str) else t) for t in tokens]
    # normalize: literal char -> 1-char string is iterable too
    for combo in itertools.product(*pools):
        yield "".join(combo)


def incremental_candidates(charset, min_len=1, max_len=6):
    """All strings of charset from min_len..max_len, shortest first."""
    for n in range(min_len, max_len + 1):
        for combo in itertools.product(charset, repeat=n):
            yield "".join(combo)


# ─── CONVENIENCE PRESETS ────────────────────────────────
PRESETS = [
    ("1", "6-digit numeric  (?d?d?d?d?d?d)",        "?d?d?d?d?d?d"),
    ("2", "8-digit numeric  (?d x8, very large)",    "?d?d?d?d?d?d?d?d"),
    ("3", "Lower+digits 6 (?l?l?l?l?d?d)",           "?l?l?l?l?d?d"),
    ("4", "Lower 8        (?l x8, very large)",      "?l?l?l?l?l?l?l?l"),
    ("5", "Phone style    (03??-ddddddd approx)",    "?d?d?d?d?d?d?d?d?d?d"),
    ("6", "Custom pattern (?l ?u ?d ?s allowed)",    None),
]


def fmt_space(n):
    if n < 1000:
        return str(n)
    if n < 10**6:
        return f"{n/1000:.1f}K"
    if n < 10**9:
        return f"{n/10**6:.1f}M"
    return f"{n/10**9:.2f}B"
