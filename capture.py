#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║         AWAIS X HACKER TEAM  —  CAPTURE PARSER               ║
║                    capture.py  |  v5.0                       ║
║         Handles .cap / .pcap / .pcapng handshake files       ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import re
import shutil
import subprocess


CAP_EXTENSIONS = (".cap", ".pcap", ".pcapng", ".ivs", ".hccapx")


# ─── VALIDATE CAP FILE ──────────────────────────────────
def is_cap_file(path):
    """Check if path exists and has a known capture extension."""
    if not os.path.isfile(path):
        return False
    ext = os.path.splitext(path)[1].lower()
    return ext in CAP_EXTENSIONS


def cap_file_size(path):
    try:
        return os.path.getsize(path)
    except OSError:
        return 0


# ─── DETECT AIRCRACK-NG ─────────────────────────────────
def aircrack_available():
    return shutil.which("aircrack-ng") is not None


def aircrack_path():
    return shutil.which("aircrack-ng")


# ─── DETECT HASHCAT ─────────────────────────────────────
def hashcat_available():
    return shutil.which("hashcat") is not None


def hashcat_path():
    return shutil.which("hashcat")


# ─── DETECT CAP2HCCAPX (for hashcat conversion) ─────────
def cap2hccapx_available():
    return (shutil.which("cap2hccapx") is not None or
            shutil.which("hcxtools") is not None)


# ─── PARSE INFO FROM CAP (aircrack-ng -I) ───────────────
def parse_cap_info(cap_path):
    """
    Run: aircrack-ng <cap>
    Parse BSSID, ESSID, encryption, channel from output.
    Returns dict with keys: bssid, essid, encryption, channel, raw
    """
    info = {
        "bssid":      None,
        "essid":      None,
        "encryption": None,
        "channel":    None,
        "handshake":  False,
        "raw":        "",
    }

    if not aircrack_available():
        return info

    try:
        proc = subprocess.run(
            ["aircrack-ng", cap_path],
            capture_output=True,
            text=True,
            timeout=30,
            errors="replace",
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        info["raw"] = out

        # BSSID
        m = re.search(r"([0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){5})", out)
        if m:
            info["bssid"] = m.group(1)

        # ESSID
        m = re.search(r'ESSID\s*[:\-]?\s*"?([^"\n]+)"?', out)
        if m:
            info["essid"] = m.group(1).strip()

        # Encryption
        if "WPA2" in out or "WPA (2)" in out:
            info["encryption"] = "WPA2"
        elif "WPA" in out:
            info["encryption"] = "WPA"
        elif "WEP" in out:
            info["encryption"] = "WEP"

        # Channel
        m = re.search(r"Channel\s*[:\-]?\s*(\d+)", out, re.IGNORECASE)
        if m:
            info["channel"] = int(m.group(1))

        # Handshake
        if "handshake" in out.lower() or "1 handshake" in out.lower():
            info["handshake"] = True

    except subprocess.TimeoutExpired:
        info["raw"] = "[!] aircrack-ng timed out while reading .cap"
    except Exception as e:
        info["raw"] = f"[!] Error reading .cap: {e}"

    return info


# ─── RUN AIRCRACK-NG ATTACK ─────────────────────────────
def run_aircrack(cap_path, wordlist_path, bssid=None, progress_cb=None):
    """
    Run real aircrack-ng attack.
    Returns (found_password_or_None, full_output).
    """
    if not aircrack_available():
        return None, (
            "[!] aircrack-ng not installed.\n"
            "    Termux : pkg install aircrack-ng\n"
            "    Debian : sudo apt install aircrack-ng\n"
            "    macOS  : brew install aircrack-ng"
        )

    cmd = ["aircrack-ng", "-w", wordlist_path]
    if bssid:
        cmd += ["-b", bssid]
    cmd.append(cap_path)

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            errors="replace",
        )
    except Exception as e:
        return None, f"[!] Failed to launch: {e}"

    lines = []
    found = None
    try:
        if proc.stdout is not None:
            for raw in proc.stdout:
                ln = raw.rstrip()
                lines.append(ln)
                if progress_cb:
                    progress_cb(ln)
                if "KEY FOUND" in ln:
                    try:
                        found = ln.split("[", 1)[1].split("]", 1)[0].strip()
                    except Exception:
                        found = "?"
                if "KEY NOT FOUND" in ln:
                    found = None
    except KeyboardInterrupt:
        proc.terminate()
        raise
    finally:
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()

    return found, "\n".join(lines)


# ─── RUN HASHCAT ATTACK (optional, faster) ──────────────
def run_hashcat(hash_file, wordlist_path, progress_cb=None):
    """
    Run hashcat -m 22000 (WPA-PBKDF2-PMKID+EAPOL).
    Returns (found_password_or_None, full_output).
    NOTE: hash_file must be in .hccapx or .22000 format.
    """
    if not hashcat_available():
        return None, "[!] hashcat not installed."

    try:
        proc = subprocess.Popen(
            ["hashcat", "-m", "22000", "-a", "0",
             hash_file, wordlist_path,
             "--quiet", "--status", "--status-timer", "5"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            errors="replace",
        )
    except Exception as e:
        return None, f"[!] Failed to launch hashcat: {e}"

    lines = []
    found = None
    try:
        if proc.stdout is not None:
            for raw in proc.stdout:
                ln = raw.rstrip()
                lines.append(ln)
                if progress_cb:
                    progress_cb(ln)
    except KeyboardInterrupt:
        proc.terminate()
        raise
    finally:
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()

    # hashcat doesn't print found pwd directly — it's in potfile.
    # Show potfile entry as best effort.
    pot = os.path.expanduser("~/.hashcat/hashcat.potfile")
    if os.path.isfile(pot):
        try:
            with open(pot, "r", encoding="utf-8", errors="ignore") as f:
                last = None
                for ln in f:
                    last = ln.strip()
                if last and ":" in last:
                    found = last.rsplit(":", 1)[-1]
        except OSError:
            pass

    return found, "\n".join(lines)


# ─── CONVERT .cap → .hccapx (for hashcat) ───────────────
def convert_cap_to_hccapx(cap_path, out_path=None):
    """
    Convert .cap file to .hccapx using cap2hccapx if available.
    Returns (success, output_path_or_error_message).
    """
    if out_path is None:
        base, _ = os.path.splitext(cap_path)
        out_path = base + ".hccapx"

    tool = shutil.which("cap2hccapx") or shutil.which("hcxpcaptool")
    if tool is None:
        return False, ("[!] cap2hccapx not found.\n"
                       "    Install: hcxtools package")

    try:
        proc = subprocess.run(
            [tool, cap_path, out_path],
            capture_output=True, text=True, timeout=60, errors="replace",
        )
        if os.path.isfile(out_path):
            return True, out_path
        return False, (proc.stderr or proc.stdout or "Unknown error")
    except Exception as e:
        return False, f"[!] Conversion failed: {e}"