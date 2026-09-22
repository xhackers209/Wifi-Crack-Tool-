#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║         AWAIS X HACKER TEAM  —  BANNER & TERMINAL UI         ║
║                    banner.py  |  v5.0                        ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import random

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
BANNER_LINES = [
    " █████╗ ██╗    ██╗ █████╗ ██╗███████╗    ██╗  ██╗",
    "██╔══██╗██║    ██║██╔══██╗██║██╔════╝    ╚██╗██╔╝",
    "███████║██║ █╗ ██║███████║██║███████╗     ╚███╔╝ ",
    "██╔══██║██║███╗██║██╔══██║██║╚════██║     ██╔██╗ ",
    "██║  ██║╚███╔███╔╝██║  ██║██║███████║    ██╔╝ ██╗",
    "╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝╚══════╝    ╚═╝  ╚═╝",
    " ██╗  ██╗ █████╗  ██████╗██╗  ██╗███████╗██████╗ ",
    " ██║  ██║██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗",
    " ███████║███████║██║     █████╔╝ █████╗  ██████╔╝",
    " ██╔══██║██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗",
    " ██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║",
    " ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝",
]

GRADIENT = [RED, RED, YEL, YEL, GRN, GRN, CYN, CYN, BLU, BLU, MAG, MAG]


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
    print(f"  {B}{WHT}AWAIS X HACKER TEAM{R}  {D}│{R}  "
          f"{CYN}WPA2 AUDIT ENGINE{R}  {D}│{R}  {YEL}v5.0{R}")
    print(f"{D}{'═' * 64}{R}")
    print(f"  {B}{RED}⚠  EDUCATIONAL USE ONLY — TEST ON YOUR OWN WIFI{R}")
    print(f"{D}{'═' * 64}{R}\n")


def boot_sequence():
    clear()
    print_banner(animated=True)
    steps = [
        ("Loading cryptographic modules",   "OK",    GRN),
        ("Initializing PBKDF2-HMAC-SHA1",   "OK",    GRN),
        ("Probing platform capabilities",   "OK",    GRN),
        ("Scanning for aircrack-ng",        "OK",    GRN),
        ("Scanning for hashcat",            "OK",    GRN),
        ("Binding capture parser",          "OK",    GRN),
        ("Allocating worker threads",       "OK",    GRN),
        ("Engine state",                    "READY", GRN),
    ]
    for label, status, color in steps:
        sys.stdout.write(f"  {D}[*]{R} {WHT}{label:<38}{R} ")
        sys.stdout.flush()
        time.sleep(random.uniform(0.06, 0.16))
        print(f"{color}{B}[{status}]{R}")
    print()
    time.sleep(0.2)