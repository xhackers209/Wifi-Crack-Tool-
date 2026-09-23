#!/bin/bash
# ══════════════════════════════════════════════════════════════
#  AWAIS X HACKER TEAM — WPA2 Audit Engine  v6.2 ULTIMATE
#  Auto-installer: Termux / Kali / Linux / macOS / WSL
# ══════════════════════════════════════════════════════════════
clear
echo "╔══════════════════════════════════════════════╗"
echo "║   AWAIS X HACKER TEAM — AUTO INSTALLER       ║"
echo "║           v6.2 ULTIMATE                      ║"
echo "╚══════════════════════════════════════════════╝"

# ── detect platform ──
if [ -n "$PREFIX" ] && echo "$PREFIX" | grep -q termux; then
    PLATFORM="termux"
elif [ -f /etc/os-release ] && grep -qi kali /etc/os-release; then
    PLATFORM="kali"
elif [ "$(uname)" = "Darwin" ]; then
    PLATFORM="macos"
elif uname -a | grep -qi microsoft; then
    PLATFORM="wsl"
else
    PLATFORM="linux"
fi
echo "[*] Platform detected: $PLATFORM"

# ── python check ──
PY="python3"
if ! command -v python3 >/dev/null 2>&1; then
    PY="python"
fi
if ! command -v $PY >/dev/null 2>&1; then
    echo "[!] Python not found. Install it first:"
    case "$PLATFORM" in
        termux) echo "    pkg install python -y" ;;
        macos)  echo "    brew install python3" ;;
        *)      echo "    sudo apt install python3 -y" ;;
    esac
    exit 1
fi
echo "[*] Python: $($PY --version 2>&1)"

# ── optional external engines ──
echo ""
echo "[*] External engines (OPTIONAL — the built-in engine works without them)"
case "$PLATFORM" in
    termux)
        printf "    Install aircrack-ng + hcxtools? [y/N] "
        read ans
        if [ "$ans" = "y" ] || [ "$ans" = "Y" ]; then
            pkg install root-repo -y && pkg install aircrack-ng hcxtools -y
        fi
        ;;
    kali|linux|wsl)
        printf "    Install aircrack-ng + hcxtools (needs sudo)? [y/N] "
        read ans
        if [ "$ans" = "y" ] || [ "$ans" = "Y" ]; then
            sudo apt update && sudo apt install -y aircrack-ng hcxtools
        fi
        ;;
    macos)
        printf "    Install aircrack-ng via brew? [y/N] "
        read ans
        if [ "$ans" = "y" ] || [ "$ans" = "Y" ]; then
            brew install aircrack-ng 2>/dev/null || echo "    (brew not found — skipping)"
        fi
        ;;
esac

# ── self test ──
echo ""
echo "[*] Running engine self-test (real WPA2 crack proof)..."
echo ""
$PY main.py --selftest
if [ $? -eq 0 ]; then
    echo ""
    echo "╔══════════════════════════════════════════════╗"
    echo "║   ✅ INSTALL OK — engine verified working     ║"
    printf "║   Run:  %-36s║\n" "$PY main.py"
    echo "╚══════════════════════════════════════════════╝"
else
    echo ""
    echo "[!] Self-test FAILED — you need Python 3.7 or newer."
    exit 1
fi
