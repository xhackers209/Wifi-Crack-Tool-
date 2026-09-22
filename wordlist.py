#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║         AWAIS X HACKER TEAM  —  WORDLIST BUILDER             ║
║                    wordlist.py  |  v5.0                      ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import random
import string


DEFAULT_WORDS = [
    "password", "123456", "12345678", "qwerty", "abc123",
    "letmein", "admin", "welcome", "monkey", "dragon",
    "iloveyou", "sunshine", "princess", "football", "charlie",
    "trustno1", "master", "shadow", "superman", "batman",
    "michael", "jennifer", "hello123", "test123", "root",
    "toor", "guest", "changeme", "secret", "ninja",
    "pakistan", "karachi", "lahore", "islamabad", "awaiz",
    "hacker", "cyber", "wifi", "internet", "network",
    "mobile", "samsung", "iphone", "android", "windows",
    "kali", "linux", "termux", "python", "github",
]


def _safe_path(filename):
    base = os.path.dirname(os.path.abspath(__file__)) or "."
    return os.path.join(base, filename)


def rand_password(n=10):
    chars = string.ascii_lowercase + string.digits
    return "".join(random.choices(chars, k=n))


def rand_word(n=6):
    return "".join(random.choices(string.ascii_lowercase, k=n))


def build_demo_wordlist(secret=None, extra=40):
    """
    Build a demo wordlist with a hidden secret inside.
    Returns (path, total_count, secret).
    """
    if secret is None:
        secret = rand_password(10)

    words = list(DEFAULT_WORDS)
    for _ in range(extra):
        words.append(rand_word(random.randint(4, 9)))

    pos = random.randint(len(words) // 3, len(words) * 2 // 3)
    words.insert(pos, secret)
    random.shuffle(words)

    path = _safe_path(".awaiz_demo_wordlist.txt")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(words) + "\n")
    except OSError as e:
        raise RuntimeError(f"Cannot write wordlist: {e}")

    return path, len(words), secret


def build_numeric_wordlist(length=6, out_path=None):
    """Generate all numeric combinations of given length (1..6)."""
    if length < 1 or length > 6:
        raise ValueError("length must be between 1 and 6")
    if out_path is None:
        out_path = _safe_path(f".awaiz_numeric_{length}.txt")

    total = 10 ** length
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            for i in range(total):
                f.write(str(i).zfill(length) + "\n")
    except OSError as e:
        raise RuntimeError(f"Cannot write numeric wordlist: {e}")

    return out_path, total


def load_wordlist(path):
    """Yield non-empty words one by one."""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            w = line.strip()
            if w:
                yield w


def count_lines(path):
    """Count non-empty lines in a wordlist."""
    n = 0
    try:
        with open(path, "rb") as f:
            for raw in f:
                if raw.strip():
                    n += 1
    except OSError:
        return 0
    return n


def safe_remove(path):
    try:
        if path and os.path.isfile(path):
            os.remove(path)
    except OSError:
        pass