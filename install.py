#!/usr/bin/env python3

import os
import sys
import time
import random
import subprocess
import shutil
import platform
from pathlib import Path
from datetime import datetime

try:
    import pyzipper
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyzipper', '-q'])
    import pyzipper


def enable_ansi():
    if os.name == 'nt':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)
            mode = ctypes.c_ulong()
            kernel32.GetConsoleMode(handle, ctypes.byref(mode))
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)
            handle_err = kernel32.GetStdHandle(-12)
            mode_err = ctypes.c_ulong()
            kernel32.GetConsoleMode(handle_err, ctypes.byref(mode_err))
            kernel32.SetConsoleMode(handle_err, mode_err.value | 0x0004)
            ctypes.windll.kernel32.SetConsoleOutputCP(65001)
            ctypes.windll.kernel32.SetConsoleCP(65001)
        except Exception:
            pass
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

enable_ansi()


def get_terminal_size():
    try:
        cols, rows = shutil.get_terminal_size((80, 24))
    except Exception:
        cols, rows = 80, 24
    if cols < 30:
        cols = 30
    return cols, rows

COLS, ROWS = get_terminal_size()

def lw():
    return min(53, COLS - 4)

RST       = '\033[0m'
BOLD      = '\033[1m'
DIM       = '\033[2m'
ITALIC    = '\033[3m'
ULINE     = '\033[4m'
BLINK     = '\033[5m'
INVERT    = '\033[7m'

BLACK     = '\033[38;5;0m'
WHITE     = '\033[38;5;15m'
GREY      = '\033[38;5;245m'
DGREY     = '\033[38;5;238m'

CYAN      = '\033[38;5;51m'
LCYAN     = '\033[38;5;123m'
BLUE      = '\033[38;5;33m'
LBLUE     = '\033[38;5;75m'
PURPLE    = '\033[38;5;129m'
LPURPLE   = '\033[38;5;177m'
MAGENTA   = '\033[38;5;199m'
PINK      = '\033[38;5;213m'
RED       = '\033[38;5;196m'
LRED      = '\033[38;5;203m'
ORANGE    = '\033[38;5;208m'
YELLOW    = '\033[38;5;226m'
LYELLOW   = '\033[38;5;229m'
GREEN     = '\033[38;5;46m'
LGREEN    = '\033[38;5;118m'
TEAL      = '\033[38;5;43m'

BG_BLACK  = '\033[48;5;0m'
BG_DGREY  = '\033[48;5;234m'
BG_BLUE   = '\033[48;5;17m'
BG_CYAN   = '\033[48;5;23m'
BG_RED    = '\033[48;5;52m'
BG_GREEN  = '\033[48;5;22m'
BG_PURPLE = '\033[48;5;53m'

GRADIENT_CYBER  = [f'\033[38;5;{c}m' for c in [51,50,49,48,47,46,82,118,154,190,226]]
GRADIENT_FIRE   = [f'\033[38;5;{c}m' for c in [196,202,208,214,220,226,227,228,229]]
GRADIENT_OCEAN  = [f'\033[38;5;{c}m' for c in [17,18,19,20,21,27,33,39,45,51]]
GRADIENT_PURPLE = [f'\033[38;5;{c}m' for c in [53,54,55,56,57,93,129,165,201,207,213]]
GRADIENT_NEON   = [f'\033[38;5;{c}m' for c in [201,200,199,163,129,93,57,51,45,39,33]]


def strip_ansi(text):
    import re
    return re.sub(r'\033\[[0-9;]*m', '', text)

def center_text(text):
    clean = strip_ansi(text)
    pad = max((COLS - len(clean)) // 2, 0)
    print(' ' * pad + text)

def center_print(text, end=''):
    clean = strip_ansi(text)
    pad = max((COLS - len(clean)) // 2, 0)
    print(' ' * pad + text, end=end, flush=True)

def gradient_text(text, colors):
    result = ''
    n = len(colors)
    for i, ch in enumerate(text):
        idx = min(i * n // max(len(text), 1), n - 1)
        result += colors[idx] + ch
    return result + RST

def cls():
    print('\033[2J\033[H', end='', flush=True)


def matrix_rain(duration=1.0):
    chars = "アイウエオカキクケコサシスセソ0123456789ZORK"
    frames = max(int(duration / 0.06), 5)
    if COLS < 50:
        frames = min(frames, 8)
    for _ in range(frames):
        line = ''
        for c in range(COLS):
            if random.randint(0, 2) == 0:
                ch = random.choice(chars)
                col = random.choice(GRADIENT_CYBER)
                line += col + ch
            else:
                line += ' '
        print(f"\r{line}{RST}", end='', flush=True)
        time.sleep(0.06)
    print(f"\r{' ' * COLS}\r", end='', flush=True)


def pulse_border(width=None):
    if width is None:
        width = COLS
    colors = [CYAN, LCYAN, BLUE, PURPLE, MAGENTA, PINK, RED, ORANGE, YELLOW, GREEN, TEAL]
    for color in colors:
        bw = max(width - 2, 1)
        bar = '█' + '▀' * bw + '█'
        print(f"\r{color}{bar}{RST}", end='', flush=True)
        time.sleep(0.04)
    print()


def progress_bar(current, total, label="Extracting"):
    bar_width = max(COLS - 30, 10)
    pct = current * 100 // total
    filled = current * bar_width // total
    empty = bar_width - filled

    bar = ''
    for i in range(filled):
        gi = min(i * len(GRADIENT_NEON) // max(bar_width, 1), len(GRADIENT_NEON) - 1)
        bar += GRADIENT_NEON[gi] + '█'
    for _ in range(empty):
        bar += DGREY + '░'

    lbl = label[:6] if COLS < 45 else label
    print(f"\r  {CYAN}{lbl} {DGREY}[{bar}{DGREY}] {BOLD}{WHITE}{pct:3d}%{RST}", end='', flush=True)


def read_password(prompt="Password"):
    disp = prompt if COLS >= 50 else "Pass"
    print(f"  {BG_DGREY}{CYAN}⟐ {WHITE}{disp}: {YELLOW}", end='', flush=True)
    password = ''

    if os.name == 'nt':
        import msvcrt
        while True:
            ch = msvcrt.getwch()
            if ch in ('\r', '\n'):
                break
            elif ch == '\b' or ch == '\x7f':
                if password:
                    password = password[:-1]
                    print('\b \b', end='', flush=True)
            elif ch == '\x03':
                print(RST)
                sys.exit(1)
            elif ch == '\x00' or ch == '\xe0':
                msvcrt.getwch()
            else:
                password += ch
                print(f"{MAGENTA}★{YELLOW}", end='', flush=True)
    else:
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                ch = sys.stdin.read(1)
                if ch in ('\r', '\n'):
                    break
                elif ch == '\x7f' or ch == '\b':
                    if password:
                        password = password[:-1]
                        print('\b \b', end='', flush=True)
                elif ch == '\x03':
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    print(RST)
                    sys.exit(1)
                else:
                    password += ch
                    print(f"{MAGENTA}★{YELLOW}", end='', flush=True)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    print(RST)
    return password


def detect_platform():
    system = platform.system().lower()
    if os.path.isdir("/data/data/com.termux"):
        return "TERMUX"
    elif 'windows' in system:
        return "WINDOWS"
    elif 'linux' in system:
        return "LINUX"
    elif 'darwin' in system:
        return "MACOS"
    return "UNKNOWN"


LOGO_BIG = [
    "                                                                              ",
    " ███████╗  ██████╗  ██████╗  ██╗  ██╗     ██╗   ██╗███╗   ██╗███████╗██╗██████╗ ",
    " ╚══███╔╝ ██╔═══██╗██╔══██╗ ██║ ██╔╝     ██║   ██║████╗  ██║╚══███╔╝██║██╔══██╗",
    "   ███╔╝  ██║   ██║██████╔╝ █████╔╝      ██║   ██║██╔██╗ ██║  ███╔╝ ██║██████╔╝",
    "  ███╔╝   ██║   ██║██╔══██╗ ██╔═██╗      ██║   ██║██║╚██╗██║ ███╔╝  ██║██╔═══╝ ",
    " ███████╗ ╚██████╔╝██║  ██║ ██║  ██╗     ╚██████╔╝██║ ╚████║███████╗██║██║     ",
    " ╚══════╝  ╚═════╝ ╚═╝  ╚═╝ ╚═╝  ╚═╝      ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝╚═╝     ",
    "                                                                              ",
]

LOGO_SMALL = [
    " ███████╗ ██████╗ ██████╗ ██╗  ██╗",
    " ╚══███╔╝██╔═══██╗██╔══██╗██║ ██╔╝",
    "   ███╔╝ ██║   ██║██████╔╝█████╔╝ ",
    "  ███╔╝  ██║   ██║██╔══██╗██╔═██╗ ",
    " ███████╗╚██████╔╝██║  ██║██║  ██╗",
    " ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝",
]

LOGO_TINY = [
    "▀▀█ █▀█ █▀█ █▄▀",
    " ▄▀ █ █ ██▀ █ █",
    "▀▀▀ ▀▀▀ ▀ ▀ ▀ ▀",
]


def show_logo():
    if COLS >= 85:
        logo = LOGO_BIG
    elif COLS >= 45:
        logo = LOGO_SMALL
    else:
        logo = LOGO_TINY
    print()
    for i, line in enumerate(logo):
        gi = min(i * len(GRADIENT_NEON) // max(len(logo), 1), len(GRADIENT_NEON) - 1)
        center_text(f"{BOLD}{GRADIENT_NEON[gi]}{line}{RST}")
        time.sleep(0.08)
    print()


def show_sub_banner():
    w = lw()
    tag = gradient_text("━" * w, GRADIENT_PURPLE)
    center_text(tag)
    print()
    if COLS >= 50:
        center_text(f"{BOLD}{MAGENTA}⟐{RST}  {BOLD}{WHITE}U N Z I P P E R{RST}   {BOLD}{CYAN}B Y{RST}   {BOLD}{MAGENTA}Z O R K{RST}  {BOLD}{MAGENTA}⟐{RST}")
        center_text(f"{DIM}{GREY}Premium Encrypted Archive Extraction{RST}")
    else:
        center_text(f"{BOLD}{MAGENTA}⟐{RST} {BOLD}{WHITE}UNZIPPER{RST} {BOLD}{CYAN}BY{RST} {BOLD}{MAGENTA}ZORK{RST} {BOLD}{MAGENTA}⟐{RST}")
        center_text(f"{DIM}{GREY}Archive Extraction{RST}")
    center_text(f"{DIM}{DGREY}v3.0.0 • © 2026{RST}")
    print()
    tag2 = gradient_text("━" * w, GRADIENT_PURPLE)
    center_text(tag2)


def show_system_info(plat, zip_name):
    print()
    user = os.getenv('USERNAME') or os.getenv('USER') or 'unknown'
    dt = datetime.now().strftime('%Y-%m-%d %H:%M')

    if COLS >= 56:
        box_w = min(52, COLS - 4)
        inner = box_w - 2
        val_w = inner - 17
        if val_w < 10:
            val_w = 10
        pad = max((COLS - box_w) // 2, 0)
        sp = ' ' * pad

        print(f"{sp}{DGREY}╭{'─' * inner}╮{RST}")
        print(f"{sp}{DGREY}│{RST}  {CYAN}{BOLD}{'Platform':<12}{RST} : {WHITE}{plat:<{val_w}}{RST}{DGREY}│{RST}")
        print(f"{sp}{DGREY}│{RST}  {CYAN}{BOLD}{'Terminal':<12}{RST} : {WHITE}{f'{COLS}x{ROWS}':<{val_w}}{RST}{DGREY}│{RST}")
        print(f"{sp}{DGREY}│{RST}  {CYAN}{BOLD}{'User':<12}{RST} : {WHITE}{user[:val_w]:<{val_w}}{RST}{DGREY}│{RST}")
        print(f"{sp}{DGREY}│{RST}  {CYAN}{BOLD}{'Date':<12}{RST} : {WHITE}{dt:<{val_w}}{RST}{DGREY}│{RST}")
        zn = zip_name[:val_w] if len(zip_name) > val_w else zip_name
        print(f"{sp}{DGREY}│{RST}  {CYAN}{BOLD}{'Archive':<12}{RST} : {YELLOW}{zn:<{val_w}}{RST}{DGREY}│{RST}")
        print(f"{sp}{DGREY}╰{'─' * inner}╯{RST}")
    else:
        center_text(f"{CYAN}{BOLD}Platform{RST} : {WHITE}{plat}{RST}")
        center_text(f"{CYAN}{BOLD}Terminal{RST} : {WHITE}{COLS}x{ROWS}{RST}")
        center_text(f"{CYAN}{BOLD}User{RST}     : {WHITE}{user}{RST}")
        center_text(f"{CYAN}{BOLD}Date{RST}     : {WHITE}{dt}{RST}")
        zn = zip_name if len(zip_name) < COLS - 14 else zip_name[:COLS - 17] + "..."
        center_text(f"{CYAN}{BOLD}Archive{RST}  : {YELLOW}{zn}{RST}")
    print()


def find_zip():
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    target = script_dir / "AdvancedSeekerByZork.zip"

    if not target.exists():
        print()
        center_text(f"{RED}{BOLD}✘ ZIP not found!{RST}")
        print()
        if COLS >= 55:
            center_text(f"{GREY}Place AdvancedSeekerByZork.zip alongside install.py{RST}")
        else:
            center_text(f"{GREY}Place the zip file here{RST}")
            center_text(f"{GREY}next to install.py{RST}")
        print()
        sys.exit(1)

    return target


def extract_archive(zip_path, password):
    dest_dir = zip_path.parent

    print()
    if COLS >= 50:
        msg = gradient_text("  ⟐  Initiating Extraction Sequence...", GRADIENT_FIRE)
    else:
        msg = gradient_text("  ⟐  Extracting...", GRADIENT_FIRE)
    center_text(msg)
    print()
    time.sleep(0.3)

    step = 4 if COLS < 50 else 2
    for p in range(0, 101, step):
        progress_bar(p, 100, "Extracting")
        time.sleep(0.02)
    print()
    print()

    try:
        with pyzipper.AESZipFile(str(zip_path), 'r') as zf:
            if password:
                zf.setpassword(password.encode('utf-8'))
            zf.extractall(str(dest_dir), pwd=password.encode('utf-8') if password else None)
            file_count = len(zf.namelist())
    except Exception as e:
        print()
        center_text(f"{RED}{BOLD}  ✘  EXTRACTION FAILED!{RST}")
        print()
        err_msg = str(e)[:max(COLS - 6, 20)]
        center_text(f"{LRED}{err_msg}{RST}")
        print()
        sys.exit(1)

    print()
    success_frames = ["✦", "✧", "★", "✦", "✧", "★", "✦", "✧"]
    for frame in success_frames:
        if COLS >= 50:
            center_print(f"\r{GREEN}{BOLD}  {frame}  EXTRACTION COMPLETE  {frame}  {RST}")
        else:
            center_print(f"\r{GREEN}{BOLD} {frame} DONE {frame} {RST}")
        time.sleep(0.12)
    print()
    print()

    center_text(f"{WHITE}{BOLD}Files: {CYAN}{file_count}{RST}")
    center_text(f"{WHITE}{BOLD}Path:  {CYAN}{dest_dir}{RST}")
    print()

    return file_count


def self_destruct(zip_path):
    print()
    if COLS >= 50:
        msg = gradient_text("  ⟐  Initiating Cleanup Protocol...", GRADIENT_OCEAN)
    else:
        msg = gradient_text("  ⟐  Cleanup...", GRADIENT_OCEAN)
    center_text(msg)
    print()
    time.sleep(0.4)

    try:
        if zip_path.exists():
            os.remove(str(zip_path))
            center_text(f"{GREY}  {TEAL}✔{RST}{GREY}  Removed: {WHITE}{zip_path.name}{RST}")
            time.sleep(0.2)
    except Exception:
        pass

    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    sh_path = script_dir / "install.sh"
    try:
        if sh_path.exists():
            os.remove(str(sh_path))
            center_text(f"{GREY}  {TEAL}✔{RST}{GREY}  Removed: {WHITE}install.sh{RST}")
            time.sleep(0.2)
    except Exception:
        pass

    self_path = os.path.abspath(__file__)
    self_name = os.path.basename(self_path)
    center_text(f"{GREY}  {TEAL}✔{RST}{GREY}  Removed: {WHITE}{self_name}{RST}")
    time.sleep(0.2)

    print()
    center_text(f"{GREEN}{BOLD}  ✔  Cleanup complete{RST}")
    print()

    if os.name == 'nt':
        cmd = f'cmd /c "ping -n 2 127.0.0.1 >nul & del /f /q \"{self_path}\""'
        subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         creationflags=0x00000008)
    else:
        subprocess.Popen(f'sleep 1 && rm -f "{self_path}"', shell=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def show_farewell():
    print()
    w = lw()
    line = gradient_text("━" * w, GRADIENT_CYBER)
    center_text(line)
    print()
    if COLS >= 50:
        center_text(f"{BOLD}{WHITE}Thank you for using {MAGENTA}Unzipper by Zork{RST}")
        center_text(f"{DIM}{GREY}Run your extracted tool with confidence.{RST}")
    else:
        center_text(f"{BOLD}{WHITE}Thanks! {MAGENTA}— Zork{RST}")
    print()

    exit_colors = [CYAN, LCYAN, WHITE, LCYAN, CYAN, BLUE, PURPLE]
    for color in exit_colors:
        center_print(f"\r{BOLD}{color}  ⟐  ZORK OUT  ⟐  {RST}")
        time.sleep(0.12)
    print()
    print()

    line2 = gradient_text("━" * w, GRADIENT_CYBER)
    center_text(line2)
    print()


def main():
    global COLS, ROWS

    plat = detect_platform()
    COLS, ROWS = get_terminal_size()
    cls()

    matrix_rain(0.6 if COLS < 50 else 1.0)
    time.sleep(0.2)
    cls()

    pulse_border(COLS)
    show_logo()
    show_sub_banner()

    zip_path = find_zip()
    zip_name = zip_path.name

    show_system_info(plat, zip_name)

    w = lw()
    tag3 = gradient_text("━" * w, GRADIENT_FIRE)
    center_text(tag3)
    print()
    if COLS >= 50:
        center_text(f"{BOLD}{YELLOW}🔐  AUTHENTICATION REQUIRED{RST}")
        center_text(f"{DIM}{GREY}Enter archive password (blank if none){RST}")
    else:
        center_text(f"{BOLD}{YELLOW}🔐 AUTH REQUIRED{RST}")
        center_text(f"{DIM}{GREY}Enter password{RST}")
    print()

    password = read_password("Archive Password" if COLS >= 50 else "Password")

    print()
    center_text(tag3)

    print()
    center_text(f"{BOLD}{CYAN}⟐  Verifying...{RST}")
    time.sleep(0.8)

    verify_frames = ["◜", "◠", "◝", "◞", "◡", "◟"]
    anim_rounds = 8 if COLS < 50 else 12
    for v in range(anim_rounds):
        vi = v % len(verify_frames)
        center_print(f"\r{PURPLE}{BOLD}  {verify_frames[vi]}  Authenticating  {verify_frames[vi]}  {RST}")
        time.sleep(0.1)
    print(f"\r{' ' * COLS}\r", end='')

    try:
        with pyzipper.AESZipFile(str(zip_path), 'r') as zf:
            zf.setpassword(password.encode('utf-8') if password else None)
            zf.testzip()
    except Exception:
        center_text(f"{RED}{BOLD}  ✘  Wrong password!{RST}")
        time.sleep(3.8)
        print()
        sys.exit(1)

    center_text(f"{GREEN}{BOLD}  ✔  Credentials accepted{RST}")
    time.sleep(0.3)

    extract_archive(zip_path, password)

    self_destruct(zip_path)

    show_farewell()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RST}{RED}  Cancelled by user.{RST}\n")
        sys.exit(1)
