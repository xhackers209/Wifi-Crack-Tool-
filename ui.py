#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║         AWAIS X HACKER TEAM  —  UI HELPERS                   ║
║                    ui.py  |  v5.0                            ║
╚══════════════════════════════════════════════════════════════╝
"""

import sys
from banner import (R, B, D, RED, GRN, YEL, BLU, MAG, CYN, WHT,
                    clear, print_banner)


def line(char="─", n=64, color=D):
    print(f"{color}{char * n}{R}")


def header(text, color=CYN):
    line()
    print(f"  {B}{color}▸ {text.upper()}{R}")
    line()


def pause():
    try:
        input(f"\n  {D}Press ENTER to continue...{R}")
    except (EOFError, KeyboardInterrupt):
        pass


def progress_bar(elapsed, timeout, attempts, rate, bar_len=28):
    filled = min(bar_len, max(0, int((elapsed / max(timeout, 1e-9)) * bar_len)))
    bar    = "█" * filled + "░" * (bar_len - filled)
    sys.stdout.write(
        f"\r  {CYN}▐{bar}▌{R} "
        f"{YEL}{elapsed:>5.1f}s{R}  "
        f"{GRN}{attempts:>10,}{R} {D}tries{R}  "
        f"{MAG}{rate:>10,.0f}{R} {D}pwd/s{R}   "
    )
    sys.stdout.flush()


def print_session(cfg):
    line("─")
    print(f"  {B}{WHT}SESSION CONFIG{R}")
    line("─")
    print(f"  {D}├─{R} {WHT}SSID       {R}: {CYN}{cfg['ssid']}{R}")
    print(f"  {D}├─{R} {WHT}Threads    {R}: {CYN}{cfg['threads']}{R}")
    print(f"  {D}├─{R} {WHT}Timeout    {R}: {CYN}{cfg['timeout']}s{R}")
    print(f"  {D}└─{R} {WHT}Wordlist   {R}: {CYN}{cfg['wordlist'] or '(auto-demo)'}{R}")
    print()


def print_disclaimer():
    print(f"{D}{'═' * 64}{R}")
    print(f"  {B}{YEL}⚠  EDUCATIONAL USE ONLY{R}")
    print(f"{D}{'─' * 64}{R}")
    print(f"  {WHT}This tool is for learning WiFi security on {B}YOUR OWN{R}")
    print(f"  {WHT}network only. Testing on networks you don't own is{R}")
    print(f"  {B}{RED}illegal{R}{WHT} and strictly prohibited.{R}")
    print(f"{D}{'═' * 64}{R}\n")


def print_result(found, attempts, elapsed, rate):
    if found:
        line("═", color=GRN)
        print(f"  {B}{GRN}✅  KEY RECOVERED  —  PASSWORD FOUND{R}")
        line("═", color=GRN)
        print(f"  {B}Password  :{R}  {YEL}{B}{found}{R}")
        print(f"  {B}Attempts  :{R}  {GRN}{attempts:,}{R}")
        print(f"  {B}Time      :{R}  {GRN}{elapsed:.3f}s{R}")
        print(f"  {B}Rate      :{R}  {MAG}{rate:,.0f} pwd/s{R}")
        line("═", color=GRN)
    else:
        line("═", color=RED)
        print(f"  {B}{RED}❌  KEY NOT FOUND IN WORDLIST{R}")
        line("═", color=RED)
        print(f"  {B}Attempts  :{R}  {attempts:,}")
        print(f"  {B}Time      :{R}  {elapsed:.3f}s")
        line("═", color=RED)


def print_cap_info(info):
    """Print parsed .cap file information."""
    line("─")
    print(f"  {B}{WHT}CAPTURE FILE INFO{R}")
    line("─")
    bssid = info.get("bssid") or f"{D}(not detected){R}"
    essid = info.get("essid") or f"{D}(not detected){R}"
    enc   = info.get("encryption") or f"{D}(unknown){R}"
    ch    = info.get("channel")
    ch_s  = str(ch) if ch else f"{D}(unknown){R}"
    hs    = info.get("handshake")
    hs_s  = f"{GRN}YES{R}" if hs else f"{RED}NO / unknown{R}"

    print(f"  {D}├─{R} {WHT}BSSID      {R}: {CYN}{bssid}{R}")
    print(f"  {D}├─{R} {WHT}ESSID      {R}: {CYN}{essid}{R}")
    print(f"  {D}├─{R} {WHT}Encryption {R}: {CYN}{enc}{R}")
    print(f"  {D}├─{R} {WHT}Channel    {R}: {CYN}{ch_s}{R}")
    print(f"  {D}└─{R} {WHT}Handshake  {R}: {hs_s}")
    print()