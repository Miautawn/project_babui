import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import psutil

CHROME_PATH = "chromium"
DEBUG_PORT = 9222

SCRIPT_PARENT_DIR = Path(__file__).parent.parent
CHROME_CACHE_DIR = SCRIPT_PARENT_DIR / ".babui_browser"

PID_FILE = CHROME_CACHE_DIR / ".chrome.pid"
PROFILE_DIR = CHROME_CACHE_DIR / "chrome-automation-profile"


def _cleanup():
    if os.path.exists(CHROME_CACHE_DIR):
        shutil.rmtree(CHROME_CACHE_DIR)


def start():
    if os.path.exists(PID_FILE):
        print("[-] Browser already appears to be running (PID file exists).")
        return

    os.mkdir(CHROME_CACHE_DIR)

    cmd = [
        CHROME_PATH,
        f"--remote-debugging-port={DEBUG_PORT}",
        f"--user-data-dir={PROFILE_DIR}",
        "--no-first-run",
        "--no-default-browser-check",
        "--start-maximized",
        "https://www.roommatch.nl/en/offerings/to-rent#?gesorteerd-op=publicatiedatum-&toekenning=3&toekenning=2&toekenning=1&woningsoort=1&locatie=Haarlem&locatie=Regio%2BAmsterdam",
    ]

    # Launch as a background process
    process = subprocess.Popen(
        cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

    with open(PID_FILE, "w") as f:
        f.write(str(process.pid))

    print(f"[+] Chromium launched (PID: {process.pid}) on port {DEBUG_PORT}")
    print(f"[+] Profile: {PROFILE_DIR}")
    print("Let's GOOOOO! 🚀🚀🚀")


def stop():
    if not os.path.exists(PID_FILE):
        print("[-] No PID file found. Is the browser running?")
        _cleanup()
        return

    with open(PID_FILE, "r") as f:
        pid = int(f.read())

    try:
        parent = psutil.Process(pid)
        # Kill the parent and all its children (Chrome spawns many processes)
        for child in parent.children(recursive=True):
            child.terminate()
        parent.terminate()
        print(f"[+] Process {pid} and children terminated.")
    except psutil.NoSuchProcess:
        print(f"[!] Process {pid} not found. Cleaning up stale PID file.")

    time.sleep(2)  # Give it a moment to terminate

    print("👋👋 Bye Bye 👋👋")
    _cleanup()


def main():
    help_string = "Usage: babui-browser [start|stop]"
    if len(sys.argv) < 2:
        print(help_string)
        return

    command = sys.argv[1].lower()
    if command == "start":
        start()
    elif command == "stop":
        stop()
    else:
        print(help_string)
    return


if __name__ == "__main__":
    main()
