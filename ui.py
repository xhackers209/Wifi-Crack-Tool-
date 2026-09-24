#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║         AWAIS X HACKER TEAM  —  UI HELPERS                   ║
║                    ui.py  |  v6.0                            ║
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
        print(f"  {B}Attempts  :{R}  {WHT}{attempts:,}{R}")
        print(f"  {B}Time      :{R}  {WHT}{elapsed:.3f}s{R}")
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


# ─── NEW v6.0 ───────────────────────────────────────────
def print_report_saved(path):
    print(f"\n  {GRN}[✓]{R} Session report saved: {CYN}{path}{R}")


def print_benchmark(attempts, elapsed, rate):
    line("═", color=CYN)
    print(f"  {B}{CYN}⚡  ENGINE BENCHMARK RESULT{R}")
    line("═", color=CYN)
    print(f"  {B}PMKs derived :{R}  {GRN}{attempts:,}{R}")
    print(f"  {B}Duration     :{R}  {GRN}{elapsed:.2f}s{R}")
    print(f"  {B}Speed        :{R}  {MAG}{B}{rate:,.0f} PMK/s{R}")
    line("═", color=CYN)


def print_wordlist_analysis(stats, rate):
    line("═", color=YEL)
    print(f"  {B}{YEL}📊  WORDLIST ANALYSIS{R}")
    line("═", color=YEL)
    if not stats["exists"]:
        print(f"  {RED}[!] File not found: {stats['path']}{R}")
        line("═", color=YEL)
        return
    mb = stats["size_bytes"] / (1024 * 1024)
    print(f"  {D}├─{R} {WHT}File size    {R}: {CYN}{mb:.2f} MB{R}")
    print(f"  {D}├─{R} {WHT}Total words  {R}: {CYN}{stats['total_lines']:,}{R}")
    print(f"  {D}├─{R} {WHT}Unique       {R}: {CYN}{stats['unique_words']:,}{R}"
          f"  {D}(dups: {stats['duplicates']:,}){R}")
    ln = f"{stats['min_len']}–{stats['max_len']}"
    print(f"  {D}├─{R} {WHT}Length       {R}: {CYN}{ln}{R}  {D}(avg {stats['avg_len']:.1f}){R}")
    print(f"  {D}├─{R} {WHT}lower/upper  {R}: {CYN}{stats['has_lower']:,}{R} / {CYN}{stats['has_upper']:,}{R}")
    print(f"  {D}├─{R} {WHT}with digits  {R}: {CYN}{stats['has_digit']:,}{R}"
          f"   {WHT}special{R}: {CYN}{stats['has_special']:,}{R}")
    if stats["sampled"]:
        print(f"  {D}│{R}  {D}(stats from first 200k lines){R}")
    if stats["top_words"] and stats["duplicates"] > 0:
        top = ", ".join(w for w, _ in stats["top_words"][:5])
        print(f"  {D}└─{R} {WHT}Most common  {R}: {D}{top}{R}")
    else:
        print(f"  {D}└─{R} {WHT}Most common  {R}: {D}(no duplicates){R}")
    if rate > 0:
        secs = stats["total_lines"] / rate
        if secs < 60:
            eta = f"{secs:.1f} seconds"
        elif secs < 3600:
            eta = f"{secs/60:.1f} minutes"
        else:
            eta = f"{secs/3600:.2f} hours"
        line("─")
        print(f"  {B}Full sweep ETA at {MAG}{rate:,.0f} PMK/s{R}{B} : {YEL}{eta}{R}")
    line("═", color=YEL)


def print_handshake_guide(iface="wlan0"):
    print(f"""  {B}{WHT}STEP-BY-STEP (YOUR OWN NETWORK ONLY){R}
  {D}{"─" * 60}{R}

  {GRN}1.{R} Enable monitor mode:
       {CYN}airmon-ng start {iface}{R}

  {GRN}2.{R} Scan for your target network:
       {CYN}airodump-ng {iface}mon{R}
     {D}Note the BSSID and CHANNEL of YOUR network, then Ctrl+C{R}

  {GRN}3.{R} Capture handshake (terminal 1):
       {CYN}airodump-ng -c <CH> --bssid <BSSID> -w capture {iface}mon{R}

  {GRN}4.{R} Force reconnection (terminal 2, optional but faster):
       {CYN}aireplay-ng --deauth 5 -a <BSSID> {iface}mon{R}
     {D}A reconnecting client creates the WPA handshake{R}

  {GRN}5.{R} Stop monitor mode:
       {CYN}airmon-ng stop {iface}mon{R}

  {GRN}6.{R} Crack with this tool:  Menu {YEL}[3]{R} Real .cap File Attack
       {D}File will be: capture-01.cap{R}
""")


# ─── NEW v6.1 REAL EDITION ──────────────────────────────
def print_targets(info, ssid):
    """Show what crackable material was found in the capture."""
    line("═", color=GRN)
    print(f"  {B}{GRN}📡  CAPTURE ANALYSIS{R}")
    line("═", color=GRN)
    print(f"  {D}├─{R} {WHT}Packets captured{R}: {CYN}{info['packet_count']:,}{R}")
    ssid_s = ssid or f"{D}(unknown — will ask){R}"
    print(f"  {D}├─{R} {WHT}Network (SSID){R} : {CYN}{ssid_s}{R}")
    hs = info["handshakes"]
    hs_s = (f"{GRN}{len(hs)} handshake(s) found{R}" if hs
            else f"{RED}none{R}")
    print(f"  {D}├─{R} {WHT}4-way handshake{R}: {hs_s}")
    pk = info["pmkids"]
    pk_s = (f"{GRN}{len(pk)} PMKID(s) found{R}" if pk
            else f"{D}none{R}")
    print(f"  {D}└─{R} {WHT}PMKID          {R}: {pk_s}")
    line("═", color=GRN)
    print()
