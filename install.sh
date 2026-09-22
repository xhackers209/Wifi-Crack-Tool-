#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────
#  AWAIS X HACKER TEAM — AUTO INSTALLER v5.0
#  Works on: Termux / Debian / Ubuntu / Kali / macOS
# ─────────────────────────────────────────────────────────

set -e

GREEN="\033[92m"
YELLOW="\033[93m"
RED="\033[91m"
CYAN="\033[96m"
BOLD="\033[1m"
RESET="\033[0m"

clear
echo -e "${CYAN}${BOLD}"
cat << "EOF"
  ▄▄▄       █     █░ ▄▄▄       ██▓ ▒███████▒
 ▒████▄    ▓█░ █ ░█░▒████▄    ▓██▒ ▒ ▒ ▒ ▄▀░
 ▒██  ▀█▄  ▒█░ █ ░█ ▒██  ▀█▄  ▒██▒ ░ ▒ ▄▀▒░
 ░██▄▄▄▄██ ░█░ █ ░█ ░██▄▄▄▄██ ░██░   ▄▀▒   ░
  ▓█   ▓██▒░░██▒██▓  ▓█   ▓██▒░██░ ▒███████▒
  ▒▒   ▓▒█░░ ▓░▒ ▒   ▒▒   ▓▒█░░▓   ░▒▒ ▓░▒░▒
   ▒   ▒▒ ░  ▒ ░ ░    ▒   ▒▒ ░ ▒ ░ ░░▒ ▒ ░ ▒
   ░   ▒     ░   ░    ░   ▒    ▒ ░ ░ ░ ░ ░ ░
       ░       ░          ░    ░     ░ ░
EOF
echo -e "${RESET}"
echo -e "${CYAN}${BOLD}╔══════════════════════════════════════════════╗"
echo -e "║   AWAIS X HACKER TEAM — INSTALLER v5.0      ║"
echo -e "╚══════════════════════════════════════════════╝${RESET}"
echo ""

# ─── Detect environment ─────────────────────────────────
if [ -n "$PREFIX" ] && echo "$PREFIX" | grep -q "com.termux"; then
    ENV="termux"
    echo -e "${GREEN}[✓]${RESET} Detected: ${BOLD}Termux (Android)${RESET}"
elif [ "$(uname)" = "Darwin" ]; then
    ENV="macos"
    echo -e "${GREEN}[✓]${RESET} Detected: ${BOLD}macOS${RESET}"
elif [ -f /etc/debian_version ]; then
    ENV="debian"
    echo -e "${GREEN}[✓]${RESET} Detected: ${BOLD}Debian / Ubuntu / Kali${RESET}"
else
    ENV="unknown"
    echo -e "${YELLOW}[!]${RESET} Unknown environment — best-effort mode."
fi
echo ""

# ─── Python ─────────────────────────────────────────────
echo -e "${CYAN}[*]${RESET} Checking Python 3..."
if command -v python3 >/dev/null 2>&1; then
    PYVER=$(python3 --version)
    echo -e "${GREEN}[✓]${RESET} Found: ${PYVER}"
else
    echo -e "${YELLOW}[!]${RESET} Python 3 not found — installing..."
    case "$ENV" in
        termux)  pkg update -y && pkg install -y python ;;
        debian)  sudo apt update && sudo apt install -y python3 python3-pip ;;
        macos)
            if command -v brew >/dev/null 2>&1; then
                brew install python3
            else
                echo -e "${RED}[✗]${RESET} Install Homebrew first: https://brew.sh"
                exit 1
            fi
            ;;
        *)
            echo -e "${RED}[✗]${RESET} Please install Python 3 manually."
            exit 1
            ;;
    esac
fi
echo ""

# ─── aircrack-ng ────────────────────────────────────────
echo -e "${CYAN}[*]${RESET} Checking aircrack-ng (for real .cap mode)..."
if command -v aircrack-ng >/dev/null 2>&1; then
    echo -e "${GREEN}[✓]${RESET} aircrack-ng already installed."
else
    echo -e "${YELLOW}[!]${RESET} aircrack-ng not found (optional)."
    printf "   Install it now? [y/N]: "
    read -r ans
    case "$ans" in
        [Yy]*)
            case "$ENV" in
                termux) pkg install -y aircrack-ng ;;
                debian) sudo apt install -y aircrack-ng ;;
                macos)  brew install aircrack-ng ;;
                *) echo -e "${RED}[✗]${RESET} Install manually." ;;
            esac
            ;;
        *)
            echo -e "${YELLOW}[i]${RESET} Skipped. Simulation modes still work."
            ;;
    esac
fi
echo ""

# ─── hashcat (optional) ─────────────────────────────────
echo -e "${CYAN}[*]${RESET} Checking hashcat (optional, faster)..."
if command -v hashcat >/dev/null 2>&1; then
    echo -e "${GREEN}[✓]${RESET} hashcat already installed."
else
    echo -e "${YELLOW}[!]${RESET} hashcat not found (optional)."
    printf "   Install it now? [y/N]: "
    read -r ans
    case "$ans" in
        [Yy]*)
            case "$ENV" in
                termux) pkg install -y hashcat ;;
                debian) sudo apt install -y hashcat ;;
                macos)  brew install hashcat ;;
                *) echo -e "${RED}[✗]${RESET} Install manually." ;;
            esac
            ;;
        *) echo -e "${YELLOW}[i]${RESET} Skipped." ;;
    esac
fi
echo ""

# ─── hcxtools (for cap2hccapx) ─────────────────────────
echo -e "${CYAN}[*]${RESET} Checking hcxtools (for .cap → .hccapx conversion)..."
if command -v cap2hccapx >/dev/null 2>&1 || command -v hcxpcaptool >/dev/null 2>&1; then
    echo -e "${GREEN}[✓]${RESET} hcxtools already installed."
else
    echo -e "${YELLOW}[!]${RESET} hcxtools not found (optional)."
    printf "   Install it now? [y/N]: "
    read -r ans
    case "$ans" in
        [Yy]*)
            case "$ENV" in
                termux) pkg install -y hcxtools ;;
                debian) sudo apt install -y hcxtools ;;
                macos)  brew install hcxtools ;;
                *) echo -e "${RED}[✗]${RESET} Install manually." ;;
            esac
            ;;
        *) echo -e "${YELLOW}[i]${RESET} Skipped." ;;
    esac
fi
echo ""

# ─── Make executable ────────────────────────────────────
chmod +x main.py 2>/dev/null || true
chmod +x install.sh 2>/dev/null || true

# ─── Done ───────────────────────────────────────────────
echo -e "${GREEN}${BOLD}╔══════════════════════════════════════════════╗"
echo -e "║         INSTALLATION COMPLETE ✓              ║"
echo -e "╚══════════════════════════════════════════════╝${RESET}"
echo ""
echo -e "${CYAN}Run the tool with:${RESET}"
echo -e "   ${BOLD}python3 main.py${RESET}"
echo ""
echo -e "${YELLOW}⚠  EDUCATIONAL USE ONLY — Test on YOUR OWN WiFi${RESET}"
echo ""