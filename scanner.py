#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║         AWAIS X HACKER TEAM  —  NETWORK SCANNER              ║
║                    scanner.py  |  v6.2 ULTIMATE              ║
║                                                              ║
║   Passive WiFi network scanner — works on Termux (via        ║
║   termux-api), Linux (nmcli/iw), macOS (airport) and         ║
║   Windows (netsh).  No root required for scanning.           ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import shutil
import subprocess

from banner import IS_TERMUX, IS_WINDOWS


def _run(cmd, timeout=20):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=timeout, errors="replace")
        return (p.stdout or "")
    except Exception:
        return ""


# ─── PARSERS (unit-tested) ──────────────────────────────
def parse_nmcli(output):
    """Parse `nmcli -t -f SSID,BSSID,CHAN,SIGNAL dev wifi --escape no`."""
    nets = []
    for ln in output.splitlines():
        ln = ln.strip()
        if not ln or ":" not in ln:
            continue
        fields = ln.split(":")
        if len(fields) < 9:                # SSID + 6 BSSID octets + CH + SIGNAL
            continue
        ssid   = ":".join(fields[:-8])
        bssid  = ":".join(fields[-8:-2])
        chan, sig = fields[-2], fields[-1]
        if not ssid or ssid == "--":
            continue
        nets.append({"ssid": ssid, "bssid": bssid,
                     "channel": chan, "signal": sig, "src": "nmcli"})
    return nets


def parse_termux_json(output):
    """Parse `termux-wifi-scaninfo` JSON output."""
    nets = []
    try:
        data = json.loads(output)
    except Exception:
        return nets
    for item in data:
        ssid = item.get("ssid") or ""
        bssid = (item.get("bssid") or "").lower()
        freq = item.get("frequency_mhz") or 0
        level = item.get("level") or 0
        if not ssid:
            continue
        chan = ""
        if freq:
            chan = str((freq - 2407) // 5) if freq < 3000 else str((freq - 5000) // 5)
        nets.append({"ssid": ssid, "bssid": bssid,
                     "channel": chan, "signal": f"{level} dBm",
                     "src": "termux"})
    return nets


def parse_airport(output):
    """Parse macOS `airport -s` output (fixed-width columns)."""
    nets = []
    lines = output.splitlines()
    if len(lines) < 2:
        return nets
    for ln in lines[1:]:
        parts = ln.split()
        if len(parts) < 5:
            continue
        # airport -s: SSID BSSID RSSI CHANNEL HT CC SECURITY...
        bssid = parts[1].lower()
        if ":" not in bssid:
            continue
        nets.append({"ssid": parts[0], "bssid": bssid,
                     "signal": parts[2], "channel": parts[3],
                     "src": "airport"})
    return nets


def parse_netsh(output):
    """Parse `netsh wlan show networks mode=bssid` output."""
    nets = []
    cur = {}
    for ln in output.splitlines():
        s = ln.strip()
        low = s.lower()
        if low.startswith("ssid "):
            if cur.get("ssid") and cur.get("bssid"):
                nets.append(cur)
            name = s.split(":", 1)
            cur = {"ssid": name[1].strip() if len(name) > 1 else "",
                   "bssid": "", "channel": "", "signal": "", "src": "netsh"}
        elif low.startswith("bssid") and cur is not None:
            v = s.split(":", 1)
            if len(v) > 1:
                cur["bssid"] = v[1].strip().lower()
        elif low.startswith("channel") and cur is not None:
            v = s.split(":", 1)
            if len(v) > 1:
                cur["channel"] = v[1].strip().split()[0]
        elif low.startswith("signal") and cur is not None:
            v = s.split(":", 1)
            if len(v) > 1:
                cur["signal"] = v[1].strip()
    if cur.get("ssid") and cur.get("bssid"):
        nets.append(cur)
    return nets



def parse_dumpsys_wifi(output):
    """Parse `su -c dumpsys wifi` output for SSID/BSSID entries."""
    nets = []
    seen = set()
    for ln in output.splitlines():
        if "SSID:" in ln and "BSSID:" in ln:
            try:
                parts = ln.split(",")
                ssid = bssid = ""
                for p in parts:
                    p = p.strip()
                    if "SSID:" in p and "BSSID:" not in p:
                        ssid = p.split("SSID:", 1)[1].strip().strip('"')
                    elif "BSSID:" in p:
                        bssid = p.split("BSSID:", 1)[1].strip().strip('"').lower()
                if ssid and ssid not in seen and not ssid.startswith("<"):
                    seen.add(ssid)
                    nets.append({"ssid": ssid, "bssid": bssid,
                                 "channel": "", "signal": "saved/root",
                                 "src": "dumpsys"})
            except Exception:
                continue
    return nets


def parse_wpa_supplicant(text):
    """Parse wpa_supplicant.conf — returns saved networks WITH passwords."""
    nets = []
    cur = None
    for ln in text.splitlines():
        ln = ln.strip()
        if ln.startswith("ssid="):
            ssid = ln.split("=", 1)[1].strip().strip('"')
            if ssid and 0 < len(ssid) <= 32:
                cur = {"ssid": ssid, "password": None,
                       "bssid": "", "signal": "saved", "src": "wpa_supplicant"}
                nets.append(cur)
        elif ln.startswith("psk=") and cur is not None:
            val = ln.split("=", 1)[1].strip().strip('"')
            # 64 hex chars = hashed (non-recoverable), else plaintext
            if val and not (len(val) == 64 and all(c in "0123456789abcdefABCDEF" for c in val)):
                cur["password"] = val
            else:
                cur["password"] = "(hashed — not recoverable)"
    return nets


def parse_wifi_config_store(text):
    """Parse WifiConfigStore.xml (Android 9+) — SSID + PreSharedKey."""
    import re
    nets = []
    blocks = re.findall(r"<Network>.*?</Network>", text, re.DOTALL)
    for b in blocks:
        m_ssid = re.search(r'<string name="SSID">([^<]+)</string>', b)
        m_psk  = re.search(r'<string name="PreSharedKey">([^<]+)</string>', b)
        if not m_ssid:
            continue
        ssid = m_ssid.group(1).replace("&quot;", '"').replace("&amp;", "&").strip('"')
        pwd = None
        if m_psk:
            val = m_psk.group(1).replace("&quot;", '"').strip('"')
            if val and not (len(val) == 64 and all(c in "0123456789abcdefABCDEF" for c in val)):
                pwd = val
            else:
                pwd = "(hashed — not recoverable)"
        if ssid:
            nets.append({"ssid": ssid, "password": pwd,
                         "bssid": "", "signal": "saved", "src": "WifiConfigStore"})
    return nets


def saved_wifi_passwords():
    """
    Returns list of YOUR OWN phone's saved WiFi networks with passwords.
    Needs root. Tries wpa_supplicant.conf then WifiConfigStore.xml.
    """
    out = _su_cmd(["cat", "/data/misc/wifi/wpa_supplicant.conf"])
    nets = parse_wpa_supplicant(out) if out else []
    if not nets:
        out = _su_cmd(["cat", "/data/misc/wifi/WifiConfigStore.xml"])
        if out:
            nets = parse_wifi_config_store(out)
    return nets


def _su_cmd(cmd_list, timeout=15):
    """Run a command through su -c; returns output or '' if not rooted/failed."""
    if shutil.which("su") is None:
        return ""
    try:
        p = subprocess.run(["su", "-c", " ".join(cmd_list)],
                           capture_output=True, text=True,
                           timeout=timeout, errors="replace")
        return p.stdout or ""
    except Exception:
        return ""

# ─── SCANNERS ───────────────────────────────────────────
def scan_termux():
    """Termux scan with fallbacks: API app -> root dumpsys -> wpa_supplicant."""
    # 1) Termux:API (no root, live scan)
    if shutil.which("termux-wifi-scaninfo"):
        out = _run(["termux-wifi-scaninfo"])
        nets = parse_termux_json(out)
        if nets:
            return nets
        return [], ("termux-wifi-scaninfo returned no data - "
                    "enable LOCATION + WIFI and grant Termux:API permission "
                    "(run termux-wifi-scaninfo manually to test)")
    # 2) root: dumpsys wifi
    out = _su_cmd(["dumpsys", "wifi"])
    nets = parse_dumpsys_wifi(out)
    if nets:
        return nets
    # 3) root: saved networks
    out = _su_cmd(["cat", "/data/misc/wifi/wpa_supplicant.conf"])
    nets = parse_wpa_supplicant(out)
    if nets:
        return nets
    return None, ("no scan source found. Fix one of these:\n"
                  "    - No root -> pkg install termux-api  "
                  "+ install 'Termux:API' app (F-Droid)\n"
                  "    - Root    -> grant root to Termux (accept su prompt)")


def scan_linux():
    if shutil.which("nmcli"):
        out = _run(["nmcli", "--escape", "no", "-t",
                    "-f", "SSID,BSSID,CHAN,SIGNAL", "dev", "wifi"])
        nets = parse_nmcli(out)
        if nets:
            return nets
        return [], "nmcli scan empty (is WiFi enabled?)"
    if shutil.which("iw"):
        iface = ""
        out = _run(["iw", "dev"])
        for ln in out.splitlines():
            if ln.strip().startswith("Interface"):
                iface = ln.split()[-1]
                break
        if iface:
            _run(["ip", "link", "set", iface, "up"])
            out = _run(["iw", "dev", iface, "scan"], timeout=30)
            nets = []
            cur = {}
            for l in out.splitlines():
                t = l.strip()
                if t.startswith("SSID:"):
                    if cur.get("ssid") and cur.get("bssid"):
                        nets.append(cur)
                    cur = {"ssid": t[5:].strip(), "bssid": "", "channel": "",
                           "signal": "", "src": "iw"}
                elif t.startswith("BSSID:"):
                    cur["bssid"] = t[6:].strip().lower()
                elif "signal:" in t[:12]:
                    cur["signal"] = t.split("signal:", 1)[1].strip()
                elif t.startswith("DS Parameter set:"):
                    cur["channel"] = t.split(":", 1)[1].strip()
            if cur.get("ssid") and cur.get("bssid"):
                nets.append(cur)
            if nets:
                return nets
        return [], "iw scan found nothing (may need root)"
    return None, "no scanner found  (install: nmcli / iw)"


def scan_macos():
    airport = "/System/Library/PrivateFrameworks/Apple80211.framework/" \
              "Versions/Current/Resources/airport"
    if os.path.isfile(airport):
        nets = parse_airport(_run([airport, "-s"]))
        if nets:
            return nets
        return [], "airport scan empty (is WiFi on?)"
    return None, "airport utility not found on this macOS"


def scan_windows():
    if shutil.which("netsh"):
        nets = parse_netsh(_run(["netsh", "wlan", "show", "networks",
                                 "mode=bssid"], timeout=30))
        if nets:
            return nets
        return [], "netsh scan empty (is WiFi on?)"
    return None, "netsh not found"


def scan_networks():
    """
    Returns (networks_list, error_or_None).
    networks_list may be empty (with an explanation string).
    """
    if IS_TERMUX:
        return scan_termux()
    if IS_WINDOWS:
        return scan_windows()
    if sys.platform == "darwin":
        return scan_macos()
    if sys.platform.startswith("linux"):
        return scan_linux()
    return None, "unsupported platform for scanning"
