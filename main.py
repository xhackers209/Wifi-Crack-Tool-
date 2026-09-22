#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║         AWAIS X HACKER TEAM  —  MAIN ENTRY                   ║
║                    main.py  |  v5.0                          ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time

# ─── local imports ──────────────────────────────────────
from banner import (R, B, D, RED, GRN, YEL, BLU, MAG, CYN, WHT,
                    clear, print_banner, boot_sequence,
                    IS_TERMUX, IS_WINDOWS)
from ui     import (line, header, pause, progress_bar,
                    print_session, print_disclaimer,
                    print_result, print_cap_info)
from engine import run_simulation, make_target_mic
from wordlist import (build_demo_wordlist, build_numeric_wordlist,
                      rand_password, count_lines, safe_remove)
from capture import (aircrack_available, hashcat_available,
                     cap2hccapx_available,
                     is_cap_file, cap_file_size,
                     parse_cap_info, run_aircrack, run_hashcat,
                     convert_cap_to_hccapx)


CHANNEL_URL = "https://whatsapp.com/channel/0029VbBzlMlIt5rzSeMBE922"


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


# ══════════════════════════════════════════════════════════════
#  MENU OPTION 1 — QUICK DEMO (simulation)
# ══════════════════════════════════════════════════════════════
def do_demo(cfg):
    clear()
    print_banner()
    header("Demo Attack — Auto Wordlist", color=MAG)
    print_disclaimer()

    try:
        path, total, secret = build_demo_wordlist()
    except RuntimeError as e:
        print(f"  {RED}[!] {e}{R}")
        pause()
        return

    target_mic = make_target_mic(cfg["ssid"], secret)

    print(f"  {D}[*]{R} Target SSID     : {WHT}{cfg['ssid']}{R}")
    print(f"  {D}[*]{R} Hidden password : {D}(encrypted in memory){R}")
    print(f"  {D}[*]{R} Wordlist        : {WHT}{path}{R}  {D}({total} entries){R}")
    print(f"  {D}[*]{R} Worker threads  : {WHT}{cfg['threads']}{R}")
    print(f"  {D}[*]{R} Timeout         : {WHT}{cfg['timeout']}s{R}")
    print()
    print(f"  {YEL}► Launching attack engine...{R}\n")

    def cb(a, e, r):
        progress_bar(e, cfg["timeout"], a, r)

    try:
        st, elapsed = run_simulation(
            cfg["ssid"], target_mic, path,
            cfg["threads"], cfg["timeout"], progress_cb=cb,
        )
    except KeyboardInterrupt:
        print(f"\n\n  {YEL}[!] Interrupted by user.{R}")
        safe_remove(path)
        pause()
        return
    finally:
        safe_remove(path)

    print()
    rate = st.attempts / elapsed if elapsed > 0 else 0
    print_result(st.found, st.attempts, elapsed, rate)
    pause()


# ══════════════════════════════════════════════════════════════
#  MENU OPTION 2 — CUSTOM WORDLIST (simulation)
# ══════════════════════════════════════════════════════════════
def do_custom(cfg):
    clear()
    print_banner()
    header("Custom Wordlist Attack (Simulation)", color=CYN)
    print_disclaimer()

    path = cfg["wordlist"]
    if not path:
        print(f"  {YEL}[!]{R} No wordlist configured. Set it in Configuration first.")
        pause()
        return
    if not os.path.isfile(path):
        print(f"  {RED}[!] File not found: {path}{R}")
        pause()
        return

    try:
        secret = input(f"  {CYN}Test password (must exist in wordlist): {R}").strip()
    except (EOFError, KeyboardInterrupt):
        return
    if not secret:
        print(f"  {RED}[!] Empty input.{R}")
        pause()
        return

    target_mic = make_target_mic(cfg["ssid"], secret)

    print()
    print(f"  {D}[*]{R} SSID     : {WHT}{cfg['ssid']}{R}")
    print(f"  {D}[*]{R} Wordlist : {WHT}{path}{R}  {D}({count_lines(path):,} lines){R}")
    print(f"  {D}[*]{R} Threads  : {WHT}{cfg['threads']}{R}")
    print(f"  {D}[*]{R} Timeout  : {WHT}{cfg['timeout']}s{R}\n")

    def cb(a, e, r):
        progress_bar(e, cfg["timeout"], a, r)

    try:
        st, elapsed = run_simulation(
            cfg["ssid"], target_mic, path,
            cfg["threads"], cfg["timeout"], progress_cb=cb,
        )
    except KeyboardInterrupt:
        print(f"\n\n  {YEL}[!] Interrupted by user.{R}")
        pause()
        return

    print()
    rate = st.attempts / elapsed if elapsed > 0 else 0
    print_result(st.found, st.attempts, elapsed, rate)
    pause()


# ══════════════════════════════════════════════════════════════
#  MENU OPTION 3 — REAL .CAP ATTACK
# ══════════════════════════════════════════════════════════════
def do_real_cap(cfg):
    clear()
    print_banner()
    header("Real .cap File Attack", color=GRN)
    print_disclaimer()

    # 1. Check tools
    has_ac = aircrack_available()
    has_hc = hashcat_available()

    print(f"  {D}[*]{R} aircrack-ng : "
          f"{GRN + 'AVAILABLE' + R if has_ac else RED + 'NOT FOUND' + R}")
    print(f"  {D}[*]{R} hashcat     : "
          f"{GRN + 'AVAILABLE' + R if has_hc else RED + 'NOT FOUND' + R}")
    print()

    if not has_ac and not has_hc:
        print(f"  {RED}[!] Neither aircrack-ng nor hashcat installed.{R}\n")
        print(f"  {D}    Termux : pkg install aircrack-ng{R}")
        print(f"  {D}    Debian : sudo apt install aircrack-ng{R}")
        print(f"  {D}    macOS  : brew install aircrack-ng{R}")
        pause()
        return

    # 2. Get .cap path
    try:
        cap_path = input(f"  {CYN}Path to .cap file: {R}").strip().strip('"').strip("'")
    except (EOFError, KeyboardInterrupt):
        return

    if not cap_path:
        print(f"  {RED}[!] Empty path.{R}")
        pause()
        return

    if not os.path.isfile(cap_path):
        print(f"  {RED}[!] File not found: {cap_path}{R}")
        pause()
        return

    if not is_cap_file(cap_path):
        print(f"  {YEL}[!] Warning: file extension not recognized.{R}")
        print(f"  {D}    Expected: .cap / .pcap / .pcapng / .ivs / .hccapx{R}")
        try:
            ans = input(f"  {CYN}Continue anyway? [y/N]: {R}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return
        if not ans.startswith("y"):
            return

    size_mb = cap_file_size(cap_path) / (1024 * 1024)
    print(f"  {D}[*]{R} File size   : {CYN}{size_mb:.2f} MB{R}\n")

    # 3. Parse .cap info
    if has_ac:
        print(f"  {YEL}► Reading .cap file...{R}\n")
        info = parse_cap_info(cap_path)
        print_cap_info(info)
    else:
        info = {"bssid": None, "essid": None}

    # 4. Get wordlist
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

    wl_size = count_lines(wl_path)
    print(f"  {D}[*]{R} Wordlist    : {CYN}{wl_path}{R}  {D}({wl_size:,} words){R}")
    print()

    # 5. Choose engine
    engine = "aircrack"
    if has_hc and has_ac:
        print(f"  {B}Which engine?{R}")
        print(f"    {GRN}[1]{R} aircrack-ng  {D}(slower, reliable){R}")
        print(f"    {MAG}[2]{R} hashcat      {D}(much faster, GPU/CPU){R}")
        try:
            ch = input(f"  {CYN}select [1]: {R}").strip() or "1"
        except (EOFError, KeyboardInterrupt):
            ch = "1"
        engine = "hashcat" if ch == "2" else "aircrack"

    print(f"\n  {YEL}► Starting {engine} attack...{R}\n")

    # 6. Run engine
    try:
        if engine == "hashcat":
            # convert .cap → .hccapx first
            if cap_path.lower().endswith((".cap", ".pcap")):
                if not cap2hccapx_available():
                    print(f"  {YEL}[!] cap2hccapx not found — falling back to aircrack-ng{R}\n")
                    engine = "aircrack"
                else:
                    print(f"  {D}[*]{R} Converting .cap → .hccapx...")
                    ok, res = convert_cap_to_hccapx(cap_path)
                    if not ok:
                        print(f"  {RED}[!] Conversion failed: {res}{R}")
                        print(f"  {YEL}[!] Falling back to aircrack-ng{R}\n")
                        engine = "aircrack"
                    else:
                        print(f"  {GRN}[✓]{R} Converted: {res}\n")
                        found, _ = run_hashcat(
                            res, wl_path,
                            progress_cb=lambda s: print(f"  {D}{s}{R}")
                        )

        if engine == "aircrack":
            def ac_cb(text):
                # filter only important lines
                if any(k in text for k in ("KEY", "Opening", "Read",
                                            "Passphrase", "BSSID",
                                            "ESSID", "KB", "tested",
                                            "handshake", "WPA", "attack")):
                    print(f"  {D}{text}{R}")

            found, _ = run_aircrack(
                cap_path, wl_path,
                bssid=info.get("bssid"),
                progress_cb=ac_cb,
            )
    except KeyboardInterrupt:
        print(f"\n\n  {YEL}[!] Interrupted by user.{R}")
        pause()
        return

    # 7. Result
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
        print(f"  {D}Try a bigger wordlist (rockyou.txt, etc.){R}")
        line("═", color=RED)
    pause()


# ══════════════════════════════════════════════════════════════
#  MENU OPTION 4 — CONFIGURATION
# ══════════════════════════════════════════════════════════════
def do_settings(cfg):
    while True:
        clear()
        print_banner()
        header("Configuration", color=YEL)
        print(f"  {B}[1]{R}  SSID             : {CYN}{cfg['ssid']}{R}")
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
                if v:
                    cfg["ssid"] = v
            elif ch == "2":
                v = input(f"  New thread count [{cfg['threads']}]: ").strip()
                if v.isdigit():
                    cfg["threads"] = max(1, min(256, int(v)))
            elif ch == "3":
                v = input(f"  New timeout [{cfg['timeout']}]: ").strip()
                if v.isdigit():
                    cfg["timeout"] = max(1, int(v))
            elif ch == "4":
                v = input(f"  Path to wordlist [{cfg['wordlist']}]: ").strip()
                cfg["wordlist"] = v.strip('"').strip("'")
            elif ch == "5":
                v = input(f"  Numeric length (1-6): ").strip()
                if v.isdigit() and 1 <= int(v) <= 6:
                    path, total = build_numeric_wordlist(int(v))
                    cfg["wordlist"] = path
                    print(f"  {GRN}[✓]{R} Created: {path} ({total:,} entries)")
                    time.sleep(1.2)
            elif ch == "0":
                return
        except (EOFError, KeyboardInterrupt):
            pass


# ══════════════════════════════════════════════════════════════
#  MENU OPTION 5 — ABOUT
# ══════════════════════════════════════════════════════════════
def do_about():
    clear()
    print_banner()
    header("About / Disclaimer", color=MAG)
    print(f"""  {B}{WHT}Tool{R}        : AWAIS X HACKER TEAM — WPA2 Audit Engine
  {B}{WHT}Version{R}     : v5.0
  {B}{WHT}Channel{R}     : {BLU}{CHANNEL_URL}{R}
  {B}{WHT}Purpose{R}     : Educational simulation & audit

  {B}{RED}⚠  DISCLAIMER{R}
  {D}──────────────────────────────────────────────────────────{R}
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


# ══════════════════════════════════════════════════════════════
#  MAIN MENU
# ══════════════════════════════════════════════════════════════
def main_menu(cfg):
    while True:
        clear()
        print_banner()
        print_session(cfg)

        line("─")
        print(f"  {B}{WHT}ATTACK OPTIONS{R}")
        line("─")
        print(f"  {B}{GRN}[1]{R}  {WHT}Quick Demo Attack{R}        {D}— auto wordlist, simulated{R}")
        print(f"  {B}{CYN}[2]{R}  {WHT}Custom Wordlist Attack{R}    {D}— simulated, your list{R}")
        print(f"  {B}{MAG}[3]{R}  {WHT}Real .cap File Attack{R}     {D}— aircrack-ng / hashcat{R}")
        print(f"  {B}{YEL}[4]{R}  {WHT}Configuration{R}             {D}— SSID, threads, timeout{R}")
        print(f"  {B}{WHT}[5]{R}  {WHT}About / Disclaimer{R}")
        print(f"  {B}{BLU}[6]{R}  {WHT}Open Channel{R}              {D}— AWAIS X HACKER TEAM{R}")
        print(f"  {B}{RED}[0]{R}  {WHT}Exit{R}")
        print()

        try:
            ch = input(f"  {B}{GRN}awaiz@hacker{R}{D}:{R}{B}{CYN}~{R}$ ").strip()
        except (EOFError, KeyboardInterrupt):
            ch = "0"

        if ch == "1":
            do_demo(cfg)
        elif ch == "2":
            do_custom(cfg)
        elif ch == "3":
            do_real_cap(cfg)
        elif ch == "4":
            do_settings(cfg)
        elif ch == "5":
            do_about()
        elif ch == "6":
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
            print(f"\n  {GRN}{B}╔══════════════════════════════════════╗{R}")
            print(f"  {GRN}{B}║   AWAIS X HACKER TEAM — SIGNING OFF ║{R}")
            print(f"  {GRN}{B}╚══════════════════════════════════════╝{R}\n")
            print(f"  {D}Follow: {BLU}{CHANNEL_URL}{R}\n")
            sys.exit(0)
        else:
            print(f"  {RED}[!] Invalid option.{R}")
            time.sleep(0.5)


# ══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════
def main():
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
        print(f"  {D}[*]{R} cap2hccapx        : "
              f"{GRN if cap2hccapx_available() else RED}"
              f"{'AVAILABLE' if cap2hccapx_available() else 'NOT INSTALLED'}{R}")
        print()
        time.sleep(0.5)

        cfg = {
            "ssid":     "MyHomeWiFi",
            "threads":  4,
            "timeout":  30,
            "wordlist": "",
        }
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