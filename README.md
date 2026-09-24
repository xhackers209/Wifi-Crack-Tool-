<p align="center">
  <img src="https://img.shields.io/badge/AWAIS%20X%20HASEEB-WPA2%20AUDIT%20ENGINE-red?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Version-v6.2%20ULTIMATE-brightgreen?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Python-3.7%2B-blue?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Platform-Termux%20%7C%20Kali%20%7C%20Linux%20%7C%20macOS%20%7C%20Windows-lightgrey?style=for-the-badge"/>
</p>

# AWAIS X HASEEB — WPA2 Audit Engine v6.2 ULTIMATE

**Built-in REAL WPA2 cracker — pure Python, NO external tools required.**
Parses real `.cap` / `.pcap` / `.pcapng` captures, extracts 4-way
handshakes and PMKIDs, and performs REAL PBKDF2-HMAC-SHA1 (4096) →
PRF-512 PTK → EAPOL-Key MIC verification — the exact same mathematics
used by aircrack-ng and hashcat.

Works on **rooted Termux, Kali Linux, any Linux, macOS and Windows** —
anywhere Python 3.7+ runs.

> ⚠️ **EDUCATIONAL USE ONLY.** Test **ONLY** on WiFi networks you own
> or have explicit written permission to audit.

---

## 🚀 Quick Start (GitHub Clone — Har Platform Pe Same)

```bash
git clone https://github.com/xhackers209/Wifi-Crack-Tool-.git
cd Wifi-Crack-Tool-
python3 main.py --selftest      # proof it works (~10 sec)
python3 main.py                 # run the tool
```

Windows pe sirf `python3` ki jagah `py` likhna.

---

## 📱 Platform Setup

### 🤖 Rooted Android — Termux

```bash
pkg update && pkg upgrade -y
pkg install git python -y
git clone https://github.com/xhackers209/Wifi-Crack-Tool-.git
cd Wifi-Crack-Tool-
python main.py --selftest
python main.py

# OPTIONAL — external engine + capture tools (root needed for capture):
pkg install root-repo -y
pkg install aircrack-ng hcxtools -y
su -c "airmon-ng start wlan0"
```

### 🐉 Kali Linux

```bash
sudo apt update
sudo apt install -y git python3 aircrack-ng hcxtools
git clone https://github.com/xhackers209/Wifi-Crack-Tool-.git
cd Wifi-Crack-Tool-
python3 main.py --selftest
python3 main.py

# capture a handshake from YOUR network:
sudo airmon-ng start wlan0
sudo airodump-ng -c <CHANNEL> --bssid <BSSID> -w capture wlan0mon
# (the tool's menu [4] shows the full step-by-step guide)
```

### 💻 Ubuntu / Debian / any Linux

```bash
sudo apt install -y git python3
git clone https://github.com/xhackers209/Wifi-Crack-Tool-.git
cd Wifi-Crack-Tool-
python3 main.py --selftest
python3 main.py
```

### 🍎 macOS

```bash
brew install python3            # if not already installed
git clone https://github.com/xhackers209/Wifi-Crack-Tool-.git
cd Wifi-Crack-Tool-
python3 main.py --selftest
python3 main.py
```

### 🪟 Windows (CMD / PowerShell)

```bat
git clone https://github.com/xhackers209/Wifi-Crack-Tool-.git
cd Wifi-Crack-Tool-
py main.py --selftest
py main.py
```

(aircrack-ng is not native to Windows — the **built-in engine is fully
functional** on Windows. For capture, use WSL, Kali VM, or a Linux
machine, then copy the `.cap` file over.)

---

## 📦 ZIP Se Install (Agar GitHub Na Chale)

```bash
unzip WIFI_BLACKBOX_v6.2_ULTIMATE.zip
cd WIFI_BLACKBOX_v6.2_ULTIMATE
python3 main.py --selftest
python3 main.py
```

---

## 🎯 Practical Demo Flow (Your Own Network)

| Step | Menu | What it proves |
|---|---|---|
| 0 | `p` Practice Lab | **Bundled REAL sample — instant 30-sec demo** |
| 1 | `6` Benchmark | Real PBKDF2 speed on your machine |
| 2 | `n` Scanner | Nearby networks — no root needed |
| 3 | `4` Capture Guide | Exact airmon/airodump commands |
| 4 | `1` REAL WPA2 Attack | **Real password recovery from .cap** |
| 5 | `m` Mutations | Cracks `john` → `John123!` style passwords |
| 6 | `k` Mask Attack | Brute-force `?l?l?l?l?d?d` patterns |
| 7 | `5` Analyzer | Wordlist stats + crack-time estimate |
| 8 | `8` Reports | Saved report for the examiner |

---

## 🎯 Instant Demo (No Capture Needed)

`samples/` folder mein **REAL practice files** bundled hain:

```bash
python3 main.py
# phir menu se [p] (Practice Lab) dabao
```

Tool khud `samples/practice.cap` (REAL WPA2 handshake) ko
`samples/wordlist.txt` se crack karega — 30 second mein full demo,
kuch aur setup nahi chahiye.

## 📁 Project Structure

```
├── main.py        # entry point + all menus
├── handshake.py   # REAL capture parser + WPA2 crypto
├── engine.py      # attack engine (threads, iterator, benchmark)
├── rules.py       # mutations + mask engine
├── scanner.py     # passive WiFi scanner (4 platforms)
├── capture.py     # aircrack-ng / hashcat external integration
├── wordlist.py    # wordlist tools + analyzer
├── selftest.py    # --selftest proof mode
├── ui.py          # display helpers
├── banner.py      # banner + colors
├── install.sh     # auto-installer
├── .gitignore     # keeps captures & generated files out of git
├── samples/       # practice.cap + wordlist.txt (REAL bundled demo)
├── reports/       # auto-saved session reports
└── lab/           # generated wordlists & test files
```

---

## ⚡ Honest Performance

| Engine | Speed | Best for |
|---|---|---|
| Built-in (pure Python) | ~100–2000 PMK/s | Practical demos, weak passwords, mutations |
| aircrack-ng (menu 3) | ~5k–50k/s | Medium wordlists |
| hashcat GPU (menu 3) | ~50k–500k+/s | Huge wordlists, big masks |

WPA2 uses PBKDF2-HMAC-SHA1 with 4096 iterations by design — that is
what makes WiFi secure. Dictionary attacks succeed against **weak or
common passwords**; long random passwords remain impractical to crack
on any platform.

---

## 🧪 Self-Test

```bash
python3 main.py --selftest
```

Runs three checks: capture parsing, a REAL crack against a synthetic
handshake, and an engine benchmark. Exit code `0` = everything works.

---

## ⚠️ Disclaimer

This software is provided for **authorized security education and
auditing only**. You must only test networks you **own** or have
**explicit written permission** to assess. Unauthorized access to
computer networks is a criminal offence in most jurisdictions.
The authors accept no liability for misuse.

---

## 📤 Developers — Code Push/Update Karne Ka Tareeqa

```bash
cd Wifi-Crack-Tool-
git add .
git commit -m "describe your change"
git push
```

**Pehli baar push (agar repo khali hai):**

```bash
git init
git add .
git commit -m "v6.2 ULTIMATE — real WPA2 audit engine"
git branch -M main
git remote add origin https://github.com/xhackers209/Wifi-Crack-Tool-.git
git push -u origin main
```

**Note:** GitHub password se push nahi hone deta — **Personal Access Token (PAT)** chahiye:
1. GitHub → Settings → Developer Settings → Personal Access Tokens → Tokens (classic)
2. "repo" permission ke saath token banao
3. Push karte waqt password ki jagah token paste karo

> `.gitignore` ki wajah se `.cap` captures, reports aur generated files
> kabhi repo mein push nahi hote — sirf code push hota hai ✅
