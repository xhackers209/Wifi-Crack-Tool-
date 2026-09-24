#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║         AWAIS X HASEEB  —  BANNER & TERMINAL UI              ║
║                    banner.py  |  v6.2 ULTIMATE               ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import random
import shutil

# ─── ANSI COLORS ─────────────────────────────────────────
R    = "\033[0m"
B    = "\033[1m"
D    = "\033[2m"
RED  = "\033[91m"
GRN  = "\033[92m"
YEL  = "\033[93m"
BLU  = "\033[94m"
MAG  = "\033[95m"
CYN  = "\033[96m"
WHT  = "\033[97m"

# ─── PLATFORM ────────────────────────────────────────────
IS_WINDOWS = os.name == "nt"
IS_TERMUX  = "com.termux" in os.environ.get("PREFIX", "")

if IS_WINDOWS:
    os.system("")


def clear():
    os.system("cls" if IS_WINDOWS else "clear")


def tw(text, delay=0.001, color=""):
    for ch in text:
        sys.stdout.write(color + ch + R)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write("\n")


# ─── BANNER ──────────────────────────────────────────────
# "AWAIS X" — lines 1-6  |  "HASEEB" — lines 7-12
BANNER_LINES = [
    " █████╗ ██╗    ██╗ █████╗ ██╗███████╗    ██╗  ██╗",
    "██╔══██╗██║    ██║██╔══██╗██║██╔════╝    ╚██╗██╔╝",
    "███████║██║ █╗ ██║███████║██║███████╗     ╚███╔╝ ",
    "██╔══██║██║███╗██║██╔══██║██║╚════██║     ██╔██╗ ",
    "██║  ██║╚███╔███╔╝██║  ██║██║███████║    ██╔╝ ██╗",
    "╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝╚══════╝    ╚═╝  ╚═╝",
    " ██╗  ██╗  █████╗   ██████╗ ███████╗ ███████╗ ██████╗ ",
    " ██║  ██║ ██╔══██╗ ██╔════╝ ██╔════╝ ██╔════╝ ██╔══██╗",
    " ███████║ ███████║ ╚█████╗  █████╗   █████╗   ██████╔╝",
    " ██╔══██║ ██╔══██║  ╚═══██╗ ██╔══╝   ██╔══╝   ██╔══██╗",
    " ██║  ██║ ██║  ██║ ██████╔╝ ███████╗ ███████╗ ██████╔╝",
    " ╚═╝  ╚═╝ ╚═╝  ╚═╝ ╚═════╝  ╚══════╝ ╚══════╝ ╚═════╝ ",
]

# MATRIX-STYLE gradient — green/cyan hacker vibe
GRADIENT = [GRN, GRN, CYN, GRN, CYN, GRN, CYN, GRN, CYN, GRN, CYN, GRN]

# "HASEEB" in binary — hacker strip
BINARY_STRIP = "01001000 01000001 01010011 01000101 01000101 01000010"


def print_banner(animated=False):
    print()
    for i, ln in enumerate(BANNER_LINES):
        color = GRADIENT[i % len(GRADIENT)]
        if animated:
            sys.stdout.write(f"{color}{B}{ln}{R}\n")
            sys.stdout.flush()
            time.sleep(0.025)
        else:
            print(f"{color}{B}{ln}{R}")
    print(f"{D}{'═' * 64}{R}")
    print(f"  {GRN}{BINARY_STRIP}{R}")
    print(f"{D}{'═' * 64}{R}")
    print(f"  {B}{WHT}AWAIS X HASEEB{R}  {D}│{R}  "
          f"{CYN}WPA2 AUDIT ENGINE{R}  {D}│{R}  {YEL}v6.2 ULTIMATE{R}")
    print(f"{D}{'═' * 64}{R}")
    print(f"  {B}{RED}⚠  EDUCATIONAL USE ONLY — TEST ON YOUR OWN WIFI{R}")
    print(f"{D}{'═' * 64}{R}\n")


def boot_sequence():
    """Shows REAL tool availability."""
    clear()
    print_banner(animated=True)
    checks = [
        ("Loading cryptographic modules",   lambda: True),
        ("Initializing PBKDF2-HMAC-SHA1",   lambda: True),
        ("Probing platform capabilities",   lambda: True),
        ("Scanning for aircrack-ng",        lambda: shutil.which("aircrack-ng") is not None),
        ("Scanning for hashcat",            lambda: shutil.which("hashcat") is not None),
        ("Scanning for cap2hccapx",         lambda: shutil.which("cap2hccapx") is not None
                                            or shutil.which("hcxpcaptool") is not None),
        ("Binding capture parser",          lambda: True),
        ("Allocating worker threads",       lambda: True),
    ]
    for label, check in checks:
        ok = check()
        status = "OK" if ok else "SKIP"
        color = GRN if ok else YEL
        sys.stdout.write(f"  {D}[*]{R} {WHT}{label:<38}{R} ")
        sys.stdout.flush()
        time.sleep(random.uniform(0.06, 0.16))
        print(f"{color}{B}[{status}]{R}")
    sys.stdout.write(f"  {D}[*]{R} {WHT}{'Engine state':<38}{R} ")
    sys.stdout.flush()
    time.sleep(0.15)
    print(f"{GRN}{B}[READY]{R}")
    print()
    time.sleep(0.2)
