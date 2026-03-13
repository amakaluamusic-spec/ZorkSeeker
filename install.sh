#!/bin/bash

C='\033[38;5;51m'
M='\033[38;5;199m'
G='\033[38;5;46m'
R='\033[38;5;196m'
W='\033[38;5;15m'
Y='\033[38;5;226m'
D='\033[38;5;238m'
B='\033[1m'
X='\033[0m'

COLS=$(tput cols 2>/dev/null || echo 50)
[ "$COLS" -lt 30 ] && COLS=30

center() {
    local text="$1"
    local clean
    clean=$(echo -e "$text" | sed 's/\x1B\[[0-9;]*m//g')
    local pad=$(( (COLS - ${#clean}) / 2 ))
    [ "$pad" -lt 0 ] && pad=0
    printf "%*s%b\n" "$pad" "" "$text"
}

sep() {
    local w=$((COLS - 4))
    [ "$w" -gt 45 ] && w=45
    local line=""
    for ((i=0; i<w; i++)); do line+="━"; done
    center "${D}${line}${X}"
}

clear 2>/dev/null || printf '\033[2J\033[H'

echo ""
sep
center "${B}${M}⟐${X}  ${B}${W}ZORK UNZIPPER${X}  ${B}${C}SETUP${X}  ${B}${M}⟐${X}"
center "${D}Bootstrap Installer v3.0${X}"
sep
echo ""

PLAT="UNKNOWN"
if [ -d "/data/data/com.termux" ]; then
    PLAT="TERMUX"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    PLAT="WINDOWS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLAT="LINUX"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    PLAT="MACOS"
fi

center "${C}${B}Platform:${X} ${W}${PLAT}${X}"
echo ""

PYTHON_CMD=""
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
fi

if [ -z "$PYTHON_CMD" ]; then
    center "${Y}${B}⚠  Python not found${X}"
    center "${W}Installing Python...${X}"
    echo ""

    if [ "$PLAT" == "TERMUX" ]; then
        pkg update -y && pkg install -y python
    elif command -v apt-get &>/dev/null; then
        sudo apt-get update -y && sudo apt-get install -y python3 python3-pip
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y python3 python3-pip
    elif command -v yum &>/dev/null; then
        sudo yum install -y python3 python3-pip
    elif command -v pacman &>/dev/null; then
        sudo pacman -Sy --noconfirm python python-pip
    elif command -v brew &>/dev/null; then
        brew install python3
    else
        echo ""
        center "${R}${B}✘  Cannot auto-install Python${X}"
        center "${W}Install Python manually and re-run${X}"
        echo ""
        exit 1
    fi

    if command -v python3 &>/dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &>/dev/null; then
        PYTHON_CMD="python"
    else
        echo ""
        center "${R}${B}✘  Python install failed!${X}"
        echo ""
        exit 1
    fi
    center "${G}${B}✔  Python installed${X}"
else
    PY_VER=$($PYTHON_CMD --version 2>&1 || echo "Python")
    center "${G}${B}✔${X}  ${W}${PY_VER}${X}"
fi

echo ""
center "${C}Installing pyzipper...${X}"

$PYTHON_CMD -m ensurepip --upgrade >/dev/null 2>&1 || true

$PYTHON_CMD -m pip install pyzipper -q 2>/dev/null || \
$PYTHON_CMD -m pip install pyzipper -q --user 2>/dev/null || \
pip3 install pyzipper -q 2>/dev/null || \
pip install pyzipper -q 2>/dev/null || {
    echo ""
    center "${R}${B}✘  Failed to install pyzipper${X}"
    center "${W}Try: pip install pyzipper${X}"
    echo ""
    exit 1
}

center "${G}${B}✔${X}  ${W}pyzipper ready${X}"

echo ""
sep
center "${G}${B}⟐  Launching Unzipper...${X}"
sep
echo ""
sleep 0.5

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
$PYTHON_CMD "${SCRIPT_DIR}/install.py"
