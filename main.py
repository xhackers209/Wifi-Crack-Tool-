#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║         AWAIS X HASEEB  —  MAIN ENTRY                   ║
║              main.py  |  v6.1 REAL EDITION                   ║
║                                                              ║
║   Built-in REAL WPA2 cracker — no external tools needed.     ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import time
from datetime import datetime

from banner import (R, B, D, RED, GRN, YEL, BLU, MAG, CYN, WHT,
                    clear, print_banner, boot_sequence,
                    IS_TERMUX, IS_WINDOWS)
from ui     import (line, header, pause, progress_bar,
                    print_session, print_disclaimer,
                    print_result, print_cap_info,
                    print_report_saved, print_benchmark,
                    print_wordlist_analysis, print_handshake_guide,
                    print_targets)
from engine import benchmark, run_real_crack, run_iterator_attack
from rules import mutate_wordlist, mask_candidates, mask_space_size, fmt_space
from scanner import scan_networks
from wordlist import (build_numeric_wordlist, count_lines, safe_remove,
                      analyze_wordlist, project_dir)
from handshake import extract_from_capture, resolve_ssid
from capture import (aircrack_available, hashcat_available,
                     cap2hccapx_available,
                     parse_cap_info, run_aircrack, run_hashcat,
                     convert_cap_to_hccapx, is_hash_file)

CHANNEL_URL = "https://whatsapp.com/channel/0029VbBzlMlIt5rzSeMBE922"
VERSION     = "v6.2 ULTIMATE"
CONFIG_PATH = project_dir(".awaiz_config.json")


# ─── CONFIG PERSISTENCE ─────────────────────────────────
def load_config():
    defaults = {"ssid": "", "threads": 4, "timeout": 120, "wordlist": ""}
    try:
        if os.path.isfile(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                saved = json.load(f)
            for k in defaults:
                if k in saved:
                    defaults[k] = saved[k]
    except Exception:
        pass
    return defaults


def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
        return True
    except OSError:
        return False


# ─── SESSION REPORTS ────────────────────────────────────
def save_report(cfg, mode, found, attempts, elapsed, rate, extra=""):
    try:
        path = project_dir("reports",
                           f"report_{datetime.now():%Y%m%d_%H%M%S}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write("=" * 56 + "\n")
            f.write("  AWAIS X HASEEB — SESSION REPORT\n")
            f.write(f"  {VERSION} | {datetime.now():%Y-%m-%d %H:%M:%S}\n")
            f.write("=" * 56 + "\n\n")
            f.write(f"Mode       : {mode}\n")
            f.write(f"SSID       : {cfg.get('ssid','')}\n")
            f.write(f"Threads    : {cfg['threads']}\n")
            f.write(f"Timeout    : {cfg['timeout']}s\n")
            f.write(f"Wordlist   : {cfg['wordlist'] or '(none)'}\n")
            f.write(f"Result     : {'KEY FOUND' if found else 'NOT FOUND'}\n")
            if found:
                f.write(f"Password   : {found}\n")
            f.write(f"Attempts   : {attempts:,}\n")
            f.write(f"Time       : {elapsed:.3f}s\n")
            f.write(f"Rate       : {rate:,.0f} pwd/s\n")
            if extra:
                f.write(f"\nDetails:\n{extra}\n")
            f.write("\n" + "=" * 56 + "\n")
        return path
    except OSError:
        return None


# ─── PLATFORM ───────────────────────────────────────────
def detect_platform():
    if IS_TERMUX:
        return "termux"
    if sys.platform.startswith("linux"):
        return "linux"
    if sys.platform == "darwin":
        return "macos"
    if IS_WINDOWS:
        return "windows"
    return "unknown"


def open_channel():
    try:
        if IS_TERMUX:
            import subprocess
            subprocess.run(["termux-open-url", CHANNEL_URL],
                           check=False,
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
            return True
    except Exception:
        pass
    try:
        import webbrowser
        return webbrowser.open(CHANNEL_URL)
    except Exception:
        return False


# ══════════════ BUILT-IN REAL WPA2 CRACKER ══════════════
def do_real_builtin(cfg, wordlist_first=False):
    """REAL attack — pure-Python WPA2 handshake/PMKID cracker."""
    clear()
    print_banner()
    header("REAL WPA2 Attack — Built-in Engine", color=GRN)
    print_disclaimer()

    # ── wordlist (first or later) ──
    wl_path = cfg["wordlist"]
    if wordlist_first or not wl_path or not os.path.isfile(wl_path):
        try:
            wl_path = input(f"  {CYN}Path to wordlist: {R}").strip().strip('"').strip("'")
        except (EOFError, KeyboardInterrupt):
            return
        if not os.path.isfile(wl_path):
            print(f"  {RED}[!] Wordlist not found: {wl_path}{R}")
            pause()
            return
        cfg["wordlist"] = wl_path
        save_config(cfg)

    # ── capture file ──
    try:
        cap_path = input(f"  {CYN}Path to .cap/.pcap/.pcapng file: {R}").strip().strip('"').strip("'")
    except (EOFError, KeyboardInterrupt):
        return
    if not cap_path or not os.path.isfile(cap_path):
        print(f"  {RED}[!] Capture file not found.{R}")
        pause()
        return

    # ── parse capture ──
    print(f"\n  {YEL}► Analyzing capture...{R}")
    try:
        info = extract_from_capture(cap_path)
    except ValueError as e:
        print(f"  {RED}[!] {e}{R}")
        pause()
        return
    except Exception as e:
        print(f"  {RED}[!] Failed to parse capture: {e}{R}")
        pause()
        return

    ssid = resolve_ssid(info, user_default=cfg["ssid"])
    print_targets(info, ssid)

    if not info["handshakes"] and not info["pmkids"]:
        print(f"  {YEL}[!] No WPA2 handshake or PMKID found in this capture.{R}")
        print(f"  {D}    Capture a 4-way handshake (see Capture Guide, menu 4).{R}")
        pause()
        return

    # ── confirm SSID ──
    if not ssid:
        try:
            ssid = input(f"  {CYN}SSID (network name) — must be exact: {R}").strip()
        except (EOFError, KeyboardInterrupt):
            return
        if not ssid:
            print(f"  {RED}[!] SSID is required for WPA2 key derivation.{R}")
            pause()
            return
    else:
        try:
            v = input(f"  {CYN}SSID [{ssid}]: {R}").strip()
            if v:
                ssid = v
        except (EOFError, KeyboardInterrupt):
            pass
    cfg["ssid"] = ssid
    save_config(cfg)

    wl_size = count_lines(wl_path)
    print(f"  {D}[*]{R} Wordlist    : {CYN}{wl_path}{R}  {D}({wl_size:,} words){R}")

    # ETA via quick benchmark
    print(f"  {YEL}► Measuring engine speed...{R}", end="")
    sys.stdout.flush()
    _, _, rate = benchmark(seconds=1.0)
    print(f"\r  {D}[*]{R} Engine speed: {MAG}{rate:,.0f} PMK/s{R}")
    if rate > 0:
        secs = wl_size / rate
        eta = (f"{secs:.0f}s" if secs < 60 else
               f"{secs/60:.1f}m" if secs < 3600 else f"{secs/3600:.2f}h")
        print(f"  {D}[*]{R} Estimated full sweep: {YEL}{eta}{R}")
    print()
    print(f"  {YEL}► Launching REAL WPA2 attack...{R}\n")

    def cb(a, e, r):
        progress_bar(e, cfg["timeout"], a, r)

    try:
        st, elapsed = run_real_crack(info, ssid, wl_path,
                                     cfg["threads"], cfg["timeout"],
                                     progress_cb=cb)
    except KeyboardInterrupt:
        print(f"\n\n  {YEL}[!] Interrupted by user.{R}")
        pause()
        return

    print()
    rate = st.attempts / elapsed if elapsed > 0 else 0
    print_result(st.found, st.attempts, elapsed, rate)
    rp = save_report(cfg, "REAL WPA2 (built-in engine)", st.found,
                     st.attempts, elapsed, rate,
                     extra=f"Capture : {cap_path}\n"
                           f"Handshakes: {len(info['handshakes'])}  "
                           f"PMKIDs: {len(info['pmkids'])}")
    if rp:
        print_report_saved(rp)
    pause()


# ══════════════ EXTERNAL FAST ENGINES ══════════════
def do_external_engine(cfg):
    """aircrack-ng / hashcat mode (much faster if installed)."""
    clear()
    print_banner()
    header("External Fast Engine (aircrack-ng / hashcat)", color=MAG)
    print_disclaimer()

    has_ac = aircrack_available()
    has_hc = hashcat_available()
    print(f"  {D}[*]{R} aircrack-ng : "
          f"{GRN + 'AVAILABLE' + R if has_ac else RED + 'NOT FOUND' + R}")
    print(f"  {D}[*]{R} hashcat     : "
          f"{GRN + 'AVAILABLE' + R if has_hc else RED + 'NOT FOUND' + R}")
    print()
    if not has_ac and not has_hc:
        print(f"  {RED}[!] No external engine installed — use Built-in Engine (menu 1).{R}")
        print(f"  {D}    Termux : pkg install aircrack-ng{R}")
        print(f"  {D}    Debian : sudo apt install aircrack-ng{R}")
        pause()
        return

    try:
        cap_path = input(f"  {CYN}Path to .cap/.hccapx file: {R}").strip().strip('"').strip("'")
    except (EOFError, KeyboardInterrupt):
        return
    if not cap_path or not os.path.isfile(cap_path):
        print(f"  {RED}[!] File not found.{R}")
        pause()
        return

    is_hash = is_hash_file(cap_path)
    info = {"bssid": None, "essid": None}
    if has_ac and not is_hash:
        info = parse_cap_info(cap_path)
        print_cap_info(info)

    wl_path = cfg["wordlist"]
    if not wl_path or not os.path.isfile(wl_path):
        try:
            wl_path = input(f"  {CYN}Path to wordlist: {R}").strip().strip('"').strip("'")
        except (EOFError, KeyboardInterrupt):
            return
    if not os.path.isfile(wl_path):
        print(f"  {RED}[!] Wordlist not found.{R}")
        pause()
        return
    cfg["wordlist"] = wl_path
    save_config(cfg)

    engine = "aircrack"
    if is_hash:
        engine = "hashcat" if has_hc else "aircrack"
        if not has_hc:
            print(f"  {RED}[!] hashcat required for hash files.{R}")
            pause()
            return
    elif has_hc and has_ac:
        print(f"  {B}Which engine?{R}")
        print(f"    {GRN}[1]{R} aircrack-ng")
        print(f"    {MAG}[2]{R} hashcat")
        try:
            ch = input(f"  {CYN}select [1]: {R}").strip() or "1"
        except (EOFError, KeyboardInterrupt):
            ch = "1"
        engine = "hashcat" if ch == "2" else "aircrack"
    elif has_hc:
        engine = "hashcat"

    print(f"\n  {YEL}► Starting {engine}...{R}\n")
    found = None
    raw_out = ""
    try:
        if engine == "hashcat":
            hash_file = cap_path
            if not is_hash:
                ok, res = convert_cap_to_hccapx(cap_path)
                if not ok:
                    if has_ac:
                        print(f"  {YEL}[!] Conversion failed — falling back to aircrack-ng{R}\n")
                        engine = "aircrack"
                    else:
                        print(f"  {RED}[!] {res}{R}")
                        pause()
                        return
                else:
                    hash_file = res
                    print(f"  {GRN}[✓]{R} Converted: {res}\n")
            if engine == "hashcat":
                found, raw_out = run_hashcat(
                    hash_file, wl_path,
                    progress_cb=lambda s: print(f"  {D}{s}{R}")
                    if any(k in s for k in ("Progress", "Recovered", "Speed"))
                    else None)
        if engine == "aircrack":
            if is_hash:
                print(f"  {RED}[!] aircrack-ng cannot read hash files.{R}")
                pause()
                return
            found, raw_out = run_aircrack(
                cap_path, wl_path, bssid=info.get("bssid"),
                progress_cb=lambda s: print(f"  {D}{s}{R}")
                if any(k in s for k in ("KEY", "Read", "tested", "WPA",
                                        "BSSID", "ESSID")) else None)
    except KeyboardInterrupt:
        print(f"\n\n  {YEL}[!] Interrupted by user.{R}")
        pause()
        return

    print()
    if found:
        line("═", color=GRN)
        print(f"  {B}{GRN}✅  KEY RECOVERED{R}")
        line("═", color=GRN)
        print(f"  {B}Password  :{R}  {YEL}{B}{found}{R}")
        print(f"  {B}Engine    :{R}  {MAG}{engine}{R}")
        line("═", color=GRN)
    else:
        line("═", color=RED)
        print(f"  {B}{RED}❌  KEY NOT FOUND IN WORDLIST{R}")
        line("═", color=RED)
    rp = save_report(cfg, f"External engine ({engine})", found, 0, 0, 0,
                     extra=raw_out[-2000:])
    if rp:
        print_report_saved(rp)
    pause()


# ══════════════ CAPTURE GUIDE ══════════════
def do_capture_guide():
    clear()
    print_banner()
    header("Handshake / PMKID Capture Guide", color=BLU)
    print_disclaimer()
    iface = "wlan0"
    try:
        v = input(f"  {CYN}Wireless interface [{iface}]: {R}").strip()
        if v:
            iface = v
    except (EOFError, KeyboardInterrupt):
        pass
    print()
    print_handshake_guide(iface)
    pause()


# ══════════════ WORDLIST ANALYZER ══════════════
def do_analyzer(cfg):
    clear()
    print_banner()
    header("Wordlist Analyzer", color=YEL)
    path = cfg["wordlist"]
    try:
        v = input(f"  {CYN}Wordlist path [{path or 'none'}]: {R}").strip().strip('"').strip("'")
        if v:
            path = v
    except (EOFError, KeyboardInterrupt):
        return
    if not path or not os.path.isfile(path):
        print(f"  {RED}[!] Wordlist not found.{R}")
        pause()
        return
    print(f"\n  {YEL}► Analyzing...{R}")
    stats = analyze_wordlist(path)
    print(f"  {YEL}► Measuring engine speed...{R}\n")
    _, _, rate = benchmark(seconds=1.0)
    print_wordlist_analysis(stats, rate)
    pause()


# ══════════════ BENCHMARK ══════════════
def do_benchmark():
    clear()
    print_banner()
    header("Engine Benchmark", color=CYN)
    print(f"  {D}Measuring raw PBKDF2-HMAC-SHA1 (WPA2 PMK) speed...{R}\n")
    attempts, elapsed, rate = benchmark(seconds=3.0)
    print()
    print_benchmark(attempts, elapsed, rate)
    print(f"  {D}Higher PMK/s = faster WPA2 dictionary attacks on this machine.{R}")
    pause()


# ══════════════ CONFIGURATION ══════════════
def do_settings(cfg):
    while True:
        clear()
        print_banner()
        header("Configuration", color=YEL)
        print(f"  {B}[1]{R}  SSID             : {CYN}{cfg['ssid'] or '(auto-detect)'}{R}")
        print(f"  {B}[2]{R}  Worker threads   : {CYN}{cfg['threads']}{R}")
        print(f"  {B}[3]{R}  Timeout (sec)    : {CYN}{cfg['timeout']}{R}")
        print(f"  {B}[4]{R}  Wordlist path    : {CYN}{cfg['wordlist'] or '(none)'}{R}")
        print(f"  {B}[5]{R}  Generate numeric wordlist")
        print(f"  {B}[0]{R}  {D}Back{R}")
        print()
        try:
            ch = input(f"  {B}{CYN}select > {R}").strip()
        except (EOFError, KeyboardInterrupt):
            return
        try:
            if ch == "1":
                v = input(f"  New SSID [{cfg['ssid']}]: ").strip()
                cfg["ssid"] = v
                save_config(cfg)
            elif ch == "2":
                v = input(f"  New thread count [{cfg['threads']}]: ").strip()
                if v.isdigit():
                    cfg["threads"] = max(1, min(256, int(v)))
                    save_config(cfg)
            elif ch == "3":
                v = input(f"  New timeout [{cfg['timeout']}]: ").strip()
                if v.isdigit():
                    cfg["timeout"] = max(1, int(v))
                    save_config(cfg)
            elif ch == "4":
                v = input(f"  Path to wordlist [{cfg['wordlist']}]: ").strip()
                cfg["wordlist"] = v.strip('"').strip("'")
                save_config(cfg)
            elif ch == "5":
                v = input(f"  Numeric length (1-8): ").strip()
                if v.isdigit() and 1 <= int(v) <= 8:
                    path, total = build_numeric_wordlist(int(v))
                    cfg["wordlist"] = path
                    save_config(cfg)
                    print(f"  {GRN}[✓]{R} Created: {path} ({total:,} entries)")
                    time.sleep(1.2)
            elif ch == "0":
                return
        except (EOFError, KeyboardInterrupt):
            pass


# ══════════════ VIEW REPORTS ══════════════
def do_reports():
    clear()
    print_banner()
    header("Saved Session Reports", color=GRN)
    rep_dir = project_dir("reports")
    try:
        files = sorted(os.listdir(rep_dir), reverse=True)
    except OSError:
        files = []
    files = [f for f in files if f.endswith(".txt")]
    if not files:
        print(f"  {YEL}[!] No reports yet. Run an attack first.{R}")
        pause()
        return
    print(f"  {D}Found {len(files)} report(s):{R}\n")
    for i, f in enumerate(files[:15], 1):
        print(f"  {GRN}[{i}]{R} {CYN}{f}{R}")
    print()
    try:
        ch = input(f"  {CYN}Open report number (or Enter to go back): {R}").strip()
    except (EOFError, KeyboardInterrupt):
        return
    if ch.isdigit() and 1 <= int(ch) <= min(15, len(files)):
        fp = os.path.join(rep_dir, files[int(ch) - 1])
        print()
        line("─")
        try:
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                print(f.read())
        except OSError as e:
            print(f"  {RED}[!] {e}{R}")
        line("─")
        pause()


# ══════════════ ABOUT ══════════════
def do_about():
    clear()
    print_banner()
    header("About / Disclaimer", color=MAG)
    print(f"""  {B}{WHT}Tool{R}        : AWAIS X HASEEB — WPA2 Audit Engine
  {B}{WHT}Version{R}     : {VERSION}
  {B}{WHT}Channel{R}     : {BLU}{CHANNEL_URL}{R}

  {B}{GRN}Built-in REAL engine (pure Python):{R}
    • Parses .cap / .pcap / .pcapng captures
    • Extracts WPA2 4-way handshakes (EAPOL)
    • Extracts PMKIDs (hashcat -m 16800 equivalent)
    • Real PBKDF2-HMAC-SHA1 + PTK + EAPOL-MIC verification
    • NO external tools required

  {B}{RED}⚠  DISCLAIMER{R}
  {D}{"─" * 58}{R}
  This tool is designed for {B}educational purposes only{R}.
  You may use it {B}ONLY{R} on WiFi networks that {B}YOU OWN{R}
  or have {B}explicit written permission{R} to test.

  {B}Rules:{R}
    • Attack only your OWN test network
    • Never target any network you don't own
    • Unauthorized access is a criminal offence
    • Use responsibly and ethically
""")
    pause()


# ══════════════ MAIN MENU ══════════════
def main_menu(cfg):
    while True:
        clear()
        print_banner()
        print_session(cfg)

        line("─")
        print(f"  {B}{WHT}REAL ATTACKS{R}")
        line("─")
        print(f"  {B}{GRN}[1]{R}  {WHT}REAL WPA2 Attack{R}           {D}— built-in engine, no tools needed{R}")
        print(f"  {B}{CYN}[2]{R}  {WHT}REAL Attack + Custom List{R}  {D}— wordlist first, built-in engine{R}")
        print(f"  {B}{MAG}[3]{R}  {WHT}External Fast Engine{R}       {D}— aircrack-ng / hashcat (if installed){R}")
        print(f"  {B}{YEL}[m]{R}  {WHT}REAL + Mutations{R}           {D}— wordlist × leet/suffix/case (~50x){R}")
        print(f"  {B}{RED}[k]{R}  {WHT}Mask Brute-Force{R}         {D}— ?l?u?d?s pattern attack{R}")
        print(f"  {B}{GRN}[n]{R}  {WHT}Network Scanner{R}          {D}— nearby WiFi, no root{R}")
        print(f"  {B}{WHT}[p]{R}  {WHT}Practice Lab{R}             {D}— bundled REAL sample, 30-sec demo{R}")
        print(f"  {B}{YEL}[w]{R}  {WHT}Saved WiFi Passwords{R}     {D}— MY device networks (root){R}")
        line("─")
        print(f"  {B}{WHT}TOOLS & ANALYSIS{R}")
        line("─")
        print(f"  {B}{BLU}[4]{R}  {WHT}Capture Guide{R}              {D}— handshake & PMKID capture{R}")
        print(f"  {B}{YEL}[5]{R}  {WHT}Wordlist Analyzer{R}          {D}— stats + crack-time ETA{R}")
        print(f"  {B}{CYN}[6]{R}  {WHT}Engine Benchmark{R}           {D}— measure PMK/s speed{R}")
        print(f"  {B}{WHT}[7]{R}  {WHT}Configuration{R}")
        print(f"  {B}{GRN}[8]{R}  {WHT}View Reports{R}")
        print(f"  {B}{WHT}[9]{R}  {WHT}About / Disclaimer{R}")
        print(f"  {B}{BLU}[c]{R}  {WHT}Open Channel{R}")
        print(f"  {B}{RED}[0]{R}  {WHT}Exit{R}")
        print()

        try:
            ch = input(f"  {B}{GRN}awaiz@hacker{R}{D}:{R}{B}{CYN}~{R}$ ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            ch = "0"

        try:
            _dispatch(ch, cfg)
        except KeyboardInterrupt:
            print(f"\n  {YEL}[!] Interrupted.{R}")
            time.sleep(0.4)
        except Exception as e:
            print(f"\n  {RED}[!] Menu error:{R} {D}{e}{R}")
            print(f"  {D}Tool is still running — try again or another option.{R}")
            time.sleep(1.0)
def _dispatch(ch, cfg):
    if ch == "1":
        do_real_builtin(cfg)
    elif ch == "2":
        do_real_builtin(cfg, wordlist_first=True)
    elif ch == "3":
        do_external_engine(cfg)
    elif ch == "m":
        do_mutations_attack(cfg)
    elif ch == "k":
        do_mask_attack(cfg)
    elif ch == "n":
        do_scan_menu(cfg)
    elif ch == "p":
        do_practice_lab(cfg)
    elif ch == "w":
        do_saved_wifi(cfg)
    elif ch == "4":
        do_capture_guide()
    elif ch == "5":
        do_analyzer(cfg)
    elif ch == "6":
        do_benchmark()
    elif ch == "7":
        do_settings(cfg)
    elif ch == "8":
        do_reports()
    elif ch == "9":
        do_about()
    elif ch == "c":
        print(f"\n  {CYN}[*]{R} Opening channel...")
        if not open_channel():
            print(f"  {RED}[!] Could not open browser.{R}")
            print(f"  {D}    Copy URL: {BLU}{CHANNEL_URL}{R}")
        else:
            print(f"  {GRN}[✓]{R} Browser launched.")
        time.sleep(0.6)
        pause()
    elif ch == "0":
        clear()
        save_config(cfg)
        print(f"\n  {GRN}{B}╔══════════════════════════════════════╗{R}")
        print(f"  {GRN}{B}║   AWAIS X HASEEB — SIGNING OFF       ║{R}")
        print(f"  {GRN}{B}╚══════════════════════════════════════╝{R}\n")
        print(f"  {D}Follow: {BLU}{CHANNEL_URL}{R}\n")
        sys.exit(0)
    else:
        print(f"  {RED}[!] Invalid option.{R}")
        time.sleep(0.5)




# ══════════════ REAL ATTACK — SMART MUTATIONS ══════════════
def do_mutations_attack(cfg):
    clear(); print_banner()
    header("REAL Attack — Smart Mutations", color=MAG)
    print_disclaimer()
    wl = cfg["wordlist"]
    if not wl or not os.path.isfile(wl):
        try:
            wl = input(f"  {CYN}Wordlist path: {R}").strip().strip('"').strip("'")
        except (EOFError, KeyboardInterrupt):
            return
    if not os.path.isfile(wl):
        print(f"  {RED}[!] Wordlist not found.{R}"); pause(); return
    cfg["wordlist"] = wl; save_config(cfg)

    try:
        cap_path = input(f"  {CYN}Capture file: {R}").strip().strip('"').strip("'")
        info = extract_from_capture(cap_path)
    except Exception as e:
        print(f"  {RED}[!] {e}{R}"); pause(); return
    ssid = resolve_ssid(info, user_default=cfg["ssid"])
    print_targets(info, ssid)
    if not info["handshakes"] and not info["pmkids"]:
        print(f"  {YEL}[!] Nothing crackable in this capture.{R}"); pause(); return
    if not ssid:
        try:
            ssid = input(f"  {CYN}SSID: {R}").strip()
        except (EOFError, KeyboardInterrupt):
            return
    cfg["ssid"] = ssid; save_config(cfg)

    base_n = count_lines(wl)
    print(f"  {D}[*]{R} Base words : {CYN}{base_n:,}{R}")
    print(f"  {D}[*]{R} Expansion  : {CYN}~30-80 variants per word{R}")
    print(f"  {D}[*]{R} Threads    : {CYN}{cfg['threads']}{R}  "
          f"{D}Timeout: {CYN}{cfg['timeout']}s{R}\n")
    print(f"  {YEL}► Launching REAL attack with mutations...{R}\n")

    def cb(a, e, r):
        progress_bar(e, cfg["timeout"], a, r)

    try:
        st, elapsed = run_iterator_attack(
            ssid, info,
            lambda: mutate_wordlist(wl, max_per_word=100),
            cfg["threads"], cfg["timeout"], progress_cb=cb)
    except KeyboardInterrupt:
        print(f"\n\n  {YEL}[!] Interrupted by user.{R}"); pause(); return
    print()
    rate = st.attempts / elapsed if elapsed > 0 else 0
    print_result(st.found, st.attempts, elapsed, rate)
    rp = save_report(cfg, "REAL WPA2 (mutations)", st.found,
                     st.attempts, elapsed, rate)
    if rp:
        print_report_saved(rp)
    pause()


# ══════════════ REAL ATTACK — MASK BRUTE-FORCE ══════════════
def do_mask_attack(cfg):
    clear(); print_banner()
    header("REAL Attack — Mask Brute-Force", color=RED)
    print_disclaimer()
    try:
        cap_path = input(f"  {CYN}Capture file: {R}").strip().strip('"').strip("'")
        info = extract_from_capture(cap_path)
    except Exception as e:
        print(f"  {RED}[!] {e}{R}"); pause(); return
    ssid = resolve_ssid(info, user_default=cfg["ssid"])
    print_targets(info, ssid)
    if not info["handshakes"] and not info["pmkids"]:
        print(f"  {YEL}[!] Nothing crackable in this capture.{R}"); pause(); return
    if not ssid:
        try:
            ssid = input(f"  {CYN}SSID: {R}").strip()
        except (EOFError, KeyboardInterrupt):
            return
    cfg["ssid"] = ssid; save_config(cfg)

    print(f"""
  {B}Mask tokens:{R}  ?l lowercase   ?u UPPERCASE   ?d digit   ?s special
  {B}Examples  :{R}  ?l?l?l?l?d?d  →  'john12'
              ?d?d?d?d?d?d  →  6-digit PIN""")
    try:
        pattern = input(f"  {CYN}Mask: {R}").strip()
        space = mask_space_size(pattern)
    except (EOFError, KeyboardInterrupt):
        return
    except ValueError as e:
        print(f"  {RED}[!] {e}{R}"); pause(); return

    print(f"  {D}[*]{R} Keyspace: {CYN}{fmt_space(space)}{R} candidates")
    if space > 20_000_000:
        print(f"  {YEL}[!] Very large for pure Python — hashcat (menu 3) is faster.{R}")
        try:
            ans = input(f"  {CYN}Continue anyway? [y/N]: {R}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return
        if not ans.startswith("y"):
            return
    print(f"\n  {YEL}► Brute-forcing {pattern} ...{R}\n")

    def cb(a, e, r):
        progress_bar(e, cfg["timeout"], a, r)

    try:
        st, elapsed = run_iterator_attack(
            ssid, info, lambda: mask_candidates(pattern),
            cfg["threads"], cfg["timeout"], progress_cb=cb)
    except KeyboardInterrupt:
        print(f"\n\n  {YEL}[!] Interrupted by user.{R}"); pause(); return
    print()
    rate = st.attempts / elapsed if elapsed > 0 else 0
    print_result(st.found, st.attempts, elapsed, rate)
    rp = save_report(cfg, f"REAL WPA2 (mask {pattern})", st.found,
                     st.attempts, elapsed, rate)
    if rp:
        print_report_saved(rp)
    pause()


# ══════════════ NETWORK SCANNER ══════════════
def do_scan_menu(cfg):
    clear(); print_banner()
    header("WiFi Network Scanner (passive — no root)", color=GRN)
    print(f"  {YEL}► Scanning nearby networks...{R}\n")
    nets, err = scan_networks()
    if nets is None:
        print(f"  {RED}[!] {err}{R}")
        pause(); return
    if not nets:
        print(f"  {YEL}[!] {err or 'No networks found'}{R}")
        pause(); return
    line("─")
    print(f"  {B}{WHT}{'SSID':<28} {'BSSID':<19} {'CH':<4} SIGNAL{R}")
    line("─")
    for n in nets[:20]:
        print(f"  {CYN}{n['ssid'][:27]:<28}{R} {D}{n.get('bssid','')[:17]:<19}{R} "
              f"{WHT}{str(n.get('channel',''))[:3]:<4}{R} {GRN}{n.get('signal','')}{R}")
    line("─")
    print(f"\n  {D}Next: capture a handshake from YOUR network (menu 4 guide),{R}")
    print(f"  {D}then attack it with menu 1 / m / k.{R}")
    pause()




# ══════════════ PRACTICE LAB (bundled real sample) ══════════════
def do_practice_lab(cfg):
    """Auto-runs a REAL attack against the bundled sample capture."""
    clear(); print_banner()
    header("Practice Lab — Bundled REAL Sample", color=WHT)
    print_disclaimer()
    base = os.path.dirname(os.path.abspath(__file__))
    cap  = os.path.join(base, "samples", "practice.cap")
    wl   = os.path.join(base, "samples", "wordlist.txt")
    if not (os.path.isfile(cap) and os.path.isfile(wl)):
        print(f"  {RED}[!] Sample files missing (samples/practice.cap, samples/wordlist.txt){R}")
        pause(); return

    print(f"  {D}[*]{R} Capture : {CYN}{cap}{R}")
    print(f"  {D}[*]{R} Wordlist: {CYN}{wl}{R}  {D}({count_lines(wl)} words){R}\n")
    print(f"  {YEL}► Analyzing sample capture...{R}")
    try:
        info = extract_from_capture(cap)
    except Exception as e:
        print(f"  {RED}[!] {e}{R}"); pause(); return
    ssid = resolve_ssid(info)
    print_targets(info, ssid)
    if not info["handshakes"] and not info["pmkids"]:
        print(f"  {RED}[!] Sample capture has nothing crackable.{R}")
        pause(); return

    print(f"  {YEL}► Launching REAL attack on sample...{R}\n")
    def cb(a, e, r):
        progress_bar(e, cfg["timeout"], a, r)
    try:
        st, elapsed = run_real_crack(info, ssid, wl, cfg["threads"],
                                     cfg["timeout"], progress_cb=cb)
    except KeyboardInterrupt:
        print(f"\n\n  {YEL}[!] Interrupted.{R}"); pause(); return
    print()
    rate = st.attempts / elapsed if elapsed > 0 else 0
    print_result(st.found, st.attempts, elapsed, rate)
    print(f"\n  {D}Practice complete. Now capture YOUR OWN network (menu 4 guide){R}")
    print(f"  {D}and attack it with menu 1.{R}")
    rp = save_report(cfg, "Practice Lab (bundled sample)", st.found,
                     st.attempts, elapsed, rate)
    if rp:
        print_report_saved(rp)
    pause()

def _dispatch(ch, cfg):
    if ch == "1":
        do_real_builtin(cfg)
    elif ch == "2":
        do_real_builtin(cfg, wordlist_first=True)
    elif ch == "3":
        do_external_engine(cfg)
    elif ch == "m":
        do_mutations_attack(cfg)
    elif ch == "k":
        do_mask_attack(cfg)
    elif ch == "n":
        do_scan_menu(cfg)
    elif ch == "p":
        do_practice_lab(cfg)
    elif ch == "w":
        do_saved_wifi(cfg)
    elif ch == "4":
        do_capture_guide()
    elif ch == "5":
        do_analyzer(cfg)
    elif ch == "6":
        do_benchmark()
    elif ch == "7":
        do_settings(cfg)
    elif ch == "8":
        do_reports()
    elif ch == "9":
        do_about()
    elif ch == "c":
        print(f"\n  {CYN}[*]{R} Opening channel...")
        if not open_channel():
            print(f"  {RED}[!] Could not open browser.{R}")
            print(f"  {D}    Copy URL: {BLU}{CHANNEL_URL}{R}")
        else:
            print(f"  {GRN}[✓]{R} Browser launched.")
        time.sleep(0.6)
        pause()
    elif ch == "0":
        clear()
        save_config(cfg)
        print(f"\n  {GRN}{B}╔══════════════════════════════════════╗{R}")
        print(f"  {GRN}{B}║   AWAIS X HASEEB — SIGNING OFF       ║{R}")
        print(f"  {GRN}{B}╚══════════════════════════════════════╝{R}\n")
        print(f"  {D}Follow: {BLU}{CHANNEL_URL}{R}\n")
        sys.exit(0)
    else:
        print(f"  {RED}[!] Invalid option.{R}")
        time.sleep(0.5)




# ══════════════ SAVED WIFI PASSWORDS (my device, root) ══════════════
def do_saved_wifi(cfg):
    """Shows passwords of WiFi networks saved on THIS device (root)."""
    clear(); print_banner()
    header("Saved WiFi Passwords — My Device", color=YEL)
    print(f"  {D}Only networks saved on YOUR OWN phone. Root required.{R}\n")
    try:
        from scanner import saved_wifi_passwords
        nets = saved_wifi_passwords()
    except Exception as e:
        print(f"  {RED}[!] {e}{R}"); pause(); return
    if not nets:
        print(f"  {YEL}[!] No saved networks found (or root denied).{R}")
        print(f"  {D}    • Root hai? → su prompt accept karo{R}")
        print(f"  {D}    • Android 10+? → passwords encrypted ho sakte hain{R}")
        pause(); return
    line("─")
    print(f"  {B}{WHT}{'SSID':<30} PASSWORD{R}")
    line("─")
    for n in nets[:30]:
        pwd = n.get("password") or f"{D}(not stored){R}"
        print(f"  {CYN}{n['ssid'][:29]:<30}{R} {GRN}{pwd}{R}")
    line("─")
    print(f"\n  {D}Hashed entries Android ke encrypted storage ki wajah se hain —{R}")
    print(f"  {D}wo crack kiye ja sakte hain sirf router pe attack kar ke (menu 1).{R}")
    pause()

# ══════════════ ENTRY POINT ══════════════
def main():
    if "--selftest" in sys.argv:
        from selftest import run_selftest
        sys.exit(0 if run_selftest() else 1)
    if "--version" in sys.argv:
        print(f"AWAIS X HASEEB — WPA2 Audit Engine {VERSION}")
        sys.exit(0)
    try:
        boot_sequence()
        platform = detect_platform()
        print(f"  {D}[*]{R} Platform detected : {CYN}{platform.upper()}{R}")
        print(f"  {D}[*]{R} aircrack-ng       : "
              f"{GRN if aircrack_available() else RED}"
              f"{'AVAILABLE' if aircrack_available() else 'NOT INSTALLED'}{R}")
        print(f"  {D}[*]{R} hashcat           : "
              f"{GRN if hashcat_available() else RED}"
              f"{'AVAILABLE' if hashcat_available() else 'NOT INSTALLED'}{R}")
        print(f"  {D}[*]{R} Built-in engine   : {GRN}READY (pure Python){R}")
        print()
        time.sleep(0.5)

        cfg = load_config()
        project_dir("reports")
        project_dir("lab")
        main_menu(cfg)

    except KeyboardInterrupt:
        print(f"\n\n  {YEL}[!] Interrupted — exit by user.{R}\n")
        sys.exit(130)
    except Exception as e:
        print(f"\n  {RED}[!] Fatal error: {e}{R}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
