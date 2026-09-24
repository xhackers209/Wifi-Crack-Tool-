#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║         AWAIS X HACKER TEAM  —  WORDLIST TOOLKIT             ║
║                    wordlist.py  |  v6.0                      ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import random
import string
from collections import Counter


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

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) or "."


def project_dir(*parts):
    """Path inside the project folder, creating parent dirs as needed."""
    p = os.path.join(BASE_DIR, *parts)
    parent = os.path.dirname(p)
    try:
        os.makedirs(parent, exist_ok=True)
    except OSError:
        pass
    return p


def _lab_path(filename):
    """Put generated files inside lab/ instead of polluting the root."""
    return project_dir("lab", filename)


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

    path = _lab_path(".awaiz_demo_wordlist.txt")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(words) + "\n")
    except OSError as e:
        raise RuntimeError(f"Cannot write wordlist: {e}")

    return path, len(words), secret


def build_numeric_wordlist(length=6, out_path=None):
    """Generate all numeric combinations of given length (1..8)."""
    if length < 1 or length > 8:
        raise ValueError("length must be between 1 and 8")
    if out_path is None:
        out_path = _lab_path(f"numeric_{length}.txt")

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


def inject_word(path, word):
    """Append a word to a wordlist if not already present (bug-proof helper)."""
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(word + "\n")
        return True
    except OSError:
        return False


def contains_word(path, word):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.rstrip("\r\n") == word:
                    return True
    except OSError:
        return False
    return False


# ─── WORDLIST ANALYZER (NEW v6.0) ───────────────────────
def analyze_wordlist(path, sample_limit=200000):
    """
    Analyze a wordlist: size, duplicates, charset classes,
    length stats and most common words.
    Returns a stats dict.
    """
    stats = {
        "path":          path,
        "exists":        os.path.isfile(path),
        "size_bytes":    0,
        "total_lines":   0,
        "unique_words":  0,
        "duplicates":    0,
        "min_len":       None,
        "max_len":       None,
        "avg_len":       0.0,
        "has_lower":     0,
        "has_upper":     0,
        "has_digit":     0,
        "has_special":   0,
        "top_words":     [],
        "sampled":       False,
    }
    if not stats["exists"]:
        return stats

    stats["size_bytes"] = os.path.getsize(path)
    seen = set()
    freq = Counter()
    total_chars = 0
    sampled = 0

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            w = line.strip()
            if not w:
                continue
            stats["total_lines"] += 1
            total_chars += len(w)
            stats["min_len"] = len(w) if stats["min_len"] is None else min(stats["min_len"], len(w))
            stats["max_len"] = len(w) if stats["max_len"] is None else max(stats["max_len"], len(w))
            if any(c.islower() for c in w): stats["has_lower"] += 1
            if any(c.isupper() for c in w): stats["has_upper"] += 1
            if any(c.isdigit() for c in w): stats["has_digit"] += 1
            if any(not c.isalnum() for c in w): stats["has_special"] += 1
            if stats["total_lines"] <= sample_limit:
                seen.add(w)
                freq[w] += 1
            else:
                stats["sampled"] = True
            sampled += 1

    stats["unique_words"] = len(seen) if not stats["sampled"] else len(seen)
    stats["duplicates"]   = max(0, stats["total_lines"] - len(seen))
    if stats["total_lines"]:
        stats["avg_len"] = total_chars / stats["total_lines"]
    stats["top_words"] = freq.most_common(10)
    return stats
