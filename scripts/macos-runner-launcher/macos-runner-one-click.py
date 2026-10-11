#!/usr/bin/env python3
"""One-click launcher for the temporary macOS or Ubuntu VNC runner.

Uses only Python's standard library plus existing Tailscale/TigerVNC commands.
No Git, GitHub CLI, curl, jq, Node.js, Docker, or pip packages are required.
"""
from __future__ import annotations

import argparse
import getpass
import json
import os
import pathlib
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

REPO = "AmrUser-48/test-web"
BRANCH = "main"
SESSION_MINUTES = os.environ.get("SESSION_MINUTES", "350")
WAIT_SECONDS = int(os.environ.get("WAIT_SECONDS", "360"))
POLL_SECONDS = max(2, int(os.environ.get("POLL_SECONDS", "5")))
API = "https://api.github.com"
CONFIG_DIR = pathlib.Path.home() / ".config" / "macos-runner-launcher"
TOKEN_FILE = CONFIG_DIR / "token"
VNC_PASS_FILE = pathlib.Path.home() / ".config" / "tigervnc" / "runner-passwd"
RUN_ID: int | None = None
TOKEN: str | None = None

TARGETS = {
    "macos": {
        "workflow": "macos-chatgpt-vnc.yml",
        "hostname_prefix": "github-macos",
        "accepted_os": {"macos", "darwin"},
        "label": "macOS ChatGPT",
        "vnc_password_limit": 8,
    },
    "ubuntu": {
        "workflow": "temporary-core2-build-runner-vnc.yml",
        "hostname_prefix": "github-core2",
        "accepted_os": {"linux"},
        "label": "Ubuntu Core 2 desktop",
        "vnc_password_limit": 8,
    },
}


def say(message: str = "") -> None:
    print(message, flush=True)


def die(message: str, code: int = 1) -> "NoReturn":
    print(f"ERROR: {message}", file=sys.stderr, flush=True)
    raise SystemExit(code)


def require_command(name: str) -> None:
    if not shutil.which(name):
        if name == "vncviewer":
            die("TigerVNC viewer is missing. If needed, install only: sudo apt install tigervnc-viewer")
        if name == "tailscale":
            die("Tailscale CLI is missing. This script does not install dependencies.")
        die(f"Required command is missing: {name}")


def github_api(method: str, path: str, payload: dict | None = None):
    if not TOKEN:
        die("GitHub token is not configured.")
    body = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(
        API + path,
        data=body,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "runner-one-click",
            **({"Content-Type": "application/json"} if body is not None else {}),
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read()
            if not raw:
                return None
            return json.loads(raw.decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:1200]
        if e.code == 401:
            detail = "Token is invalid/expired. Create a fine-grained token with Actions read/write for AmrUser-48/test-web."
        elif e.code == 403:
            detail = "GitHub denied the request. Token needs Actions read/write access to AmrUser-48/test-web. " + detail
        elif e.code == 404:
            detail = "Repository/workflow was not found or token cannot access it. " + detail
        die(f"GitHub API returned HTTP {e.code}: {detail}")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        die(f"Cannot reach GitHub API: {e}")


def get_token() -> str:
    if os.environ.get("GITHUB_TOKEN", "").strip():
        return os.environ["GITHUB_TOKEN"].strip()
    if TOKEN_FILE.exists():
        token = TOKEN_FILE.read_text(encoding="utf-8").strip()
        if token:
            return token
    say("One-time setup: enter a fine-grained GitHub token for AmrUser-48/test-web.")
    say("Required repository permission: Actions → Read and write. No Git or GitHub CLI is used.")
    say("Create token: https://github.com/settings/personal-access-tokens/new")
    token = getpass.getpass("GitHub token (input hidden): ").strip()
    if not token:
        die("No token entered.")
    CONFIG_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        os.chmod(CONFIG_DIR, 0o700)
        fd = os.open(TOKEN_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(token + "\n")
        os.chmod(TOKEN_FILE, 0o600)
    except OSError as e:
        die(f"Could not save token to {TOKEN_FILE}: {e}")
    say(f"Token saved with owner-only permissions: {TOKEN_FILE}")
    return token


def ensure_vnc_password_file(reset: bool = False) -> None:
    """Generate a TigerVNC client password file once, instead of prompting each connect."""
    if VNC_PASS_FILE.exists() and not reset:
        try:
            os.chmod(VNC_PASS_FILE, 0o600)
            os.chmod(VNC_PASS_FILE.parent, 0o700)
        except OSError as e:
            die(f"Cannot secure the local VNC password file: {e}")
        return

    passwd_cmd = shutil.which("vncpasswd") or shutil.which("tigervncpasswd")
    if not passwd_cmd:
        die(
            "To configure password-free VNC logins, install the small TigerVNC tools package "
            "once: sudo apt install tigervnc-tools"
        )
    say("One-time setup: enter the same VNC_PASSWORD configured in GitHub repository secrets.")
    say("Only its first 8 characters are used by the VNC authentication protocol.")
    secret = getpass.getpass("VNC_PASSWORD (input hidden): ")
    if len(secret) < 8:
        die("VNC_PASSWORD must contain at least 8 characters.")
    # TigerVNC uses only the first eight characters and its own legacy passfile format.
    try:
        result = subprocess.run(
            [passwd_cmd, "-f"],
            input=(secret[:8] + "\n").encode("utf-8"),
            capture_output=True,
            check=True,
            timeout=10,
        )
    except (subprocess.SubprocessError, OSError) as e:
        die(f"Could not generate the local TigerVNC password file: {e}")
    if not result.stdout:
        die("TigerVNC password-file generator returned an empty file.")
    try:
        VNC_PASS_FILE.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        os.chmod(VNC_PASS_FILE.parent, 0o700)
        VNC_PASS_FILE.write_bytes(result.stdout)
        os.chmod(VNC_PASS_FILE, 0o600)
    except OSError as e:
        die(f"Could not save the local TigerVNC password file: {e}")
    say(f"Saved local VNC credentials: {VNC_PASS_FILE} (mode 0600).")
    say("The password file is obfuscated, not strongly encrypted; keep it private.")


def tailscale_status() -> dict:
    try:
        result = subprocess.run(
            ["tailscale", "status", "--json"],
            check=True, capture_output=True, text=True, timeout=12,
        )
        return json.loads(result.stdout)
    except (subprocess.SubprocessError, json.JSONDecodeError) as e:
        die(f"Tailscale is not responding. Connect this machine to your tailnet first. Details: {e}")


def run_status(run_id: int) -> dict:
    return github_api("GET", f"/repos/{REPO}/actions/runs/{run_id}")


def cancel_run_if_active() -> None:
    global RUN_ID
    if RUN_ID is None or not TOKEN:
        return
    try:
        info = run_status(RUN_ID)
        if info and info.get("status") != "completed":
            say(f"\nStopping temporary workflow run {RUN_ID}…")
            github_api("POST", f"/repos/{REPO}/actions/runs/{RUN_ID}/cancel")
            say("Cancellation requested.")
    except SystemExit:
        pass
    except Exception as e:
        say(f"Could not request workflow cancellation: {e}")


def rfb_greeting(ip: str) -> str | None:
    try:
        with socket.create_connection((ip, 5900), timeout=2.5) as sock:
            sock.settimeout(2.5)
            greeting = b""
            while len(greeting) < 12:
                chunk = sock.recv(12 - len(greeting))
                if not chunk:
                    return None
                greeting += chunk
            if greeting.startswith(b"RFB "):
                return greeting.decode("ascii", "replace").strip()
    except OSError:
        pass
    return None


def main() -> int:
    global TOKEN, RUN_ID

    parser = argparse.ArgumentParser(description="Start a GitHub-hosted desktop and open VNC.")
    parser.add_argument("--target", choices=sorted(TARGETS), default=os.environ.get("RUNNER_TARGET", "macos"),
                        help="macos (default) or ubuntu Core 2 desktop")
    parser.add_argument("--reset-vnc-password", action="store_true",
                        help="replace the locally saved VNC password file")
    parser.add_argument("--setup-vnc-password", action="store_true",
                        help="save or reset the local VNC password file, then exit")
    args = parser.parse_args()
    target = TARGETS[args.target]
    if SESSION_MINUTES not in {"30", "60", "180", "300", "350"}:
        die("SESSION_MINUTES must be 30, 60, 180, 300, or 350.")
    if not args.setup_vnc_password:
        require_command("tailscale")
        require_command("vncviewer")
    ensure_vnc_password_file(reset=args.reset_vnc_password)
    if args.setup_vnc_password:
        say("Local VNC password file is ready; no runner was started.")
        return 0

    tailscale_status()
    try:
        subprocess.run(
            ["tailscale", "ip", "-4"], check=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=8
        )
    except (subprocess.SubprocessError, OSError):
        die("This machine has no connected Tailscale IPv4 address. Connect Tailscale first.")
    TOKEN = get_token()

    workflow_path = urllib.parse.quote(target["workflow"], safe="")
    runs_path = f"/repos/{REPO}/actions/workflows/{workflow_path}/runs?per_page=20"
    runs_before = github_api("GET", runs_path)
    old_ids = {int(item["id"]) for item in runs_before.get("workflow_runs", [])}

    say(f"Starting {target['label']} workflow for {SESSION_MINUTES} minutes…")
    github_api(
        "POST", f"/repos/{REPO}/actions/workflows/{workflow_path}/dispatches",
        {"ref": BRANCH, "inputs": {"session_minutes": SESSION_MINUTES}},
    )

    deadline = time.monotonic() + 90
    run = None
    while time.monotonic() < deadline:
        recent = github_api("GET", runs_path)
        possible = [
            x for x in recent.get("workflow_runs", [])
            if int(x["id"]) not in old_ids and x.get("event") == "workflow_dispatch"
        ]
        if possible:
            run = max(possible, key=lambda x: x.get("created_at", ""))
            RUN_ID = int(run["id"])
            break
        time.sleep(3)
    if not run or RUN_ID is None:
        die(f"GitHub accepted dispatch but the run ID did not appear. Check https://github.com/{REPO}/actions")

    run_url = run.get("html_url") or f"https://github.com/{REPO}/actions/runs/{RUN_ID}"
    say(f"Workflow run: {run_url}")
    try:
        webbrowser.open(run_url, new=2)
    except Exception:
        pass

    expected_hostname = f"{target['hostname_prefix']}-{RUN_ID}".lower()
    say(f"Waiting for Tailscale peer {expected_hostname} and a valid VNC response…")
    deadline = time.monotonic() + WAIT_SECONDS
    last_state = None
    while time.monotonic() < deadline:
        current = tailscale_status()
        for peer in (current.get("Peer") or {}).values():
            hostinfo = peer.get("Hostinfo") or {}
            os_name = str(hostinfo.get("OS") or peer.get("OS") or "").lower()
            hostname = str(peer.get("HostName") or peer.get("DNSName") or "").lower().rstrip(".")
            hostname = hostname.split(".", 1)[0]
            if os_name not in target["accepted_os"] or not peer.get("Online"):
                continue
            if hostname != expected_hostname:
                continue
            for ip in peer.get("TailscaleIPs") or []:
                if "." not in ip:
                    continue
                greeting = rfb_greeting(ip)
                if greeting:
                    say(f"VNC verified: {ip}::5900 ({greeting})")
                    say("Opening TigerVNC with the locally saved password file; no per-connection prompt.")
                    say("Close the VNC viewer or press Ctrl+C here to stop this workflow.")
                    try:
                        completed = subprocess.run(
                            ["vncviewer", "-passwd", str(VNC_PASS_FILE), f"{ip}::5900"]
                        )
                        return completed.returncode
                    finally:
                        cancel_run_if_active()

        try:
            info = run_status(RUN_ID)
            state = (info.get("status", "unknown"), info.get("conclusion") or "")
            if state != last_state:
                say(f"Workflow state: {state[0]} {state[1]}".strip())
                last_state = state
            if state[0] == "completed":
                die(f"The workflow ended before VNC became available ({state[1]}). Details: {run_url}")
        except SystemExit:
            raise
        time.sleep(POLL_SECONDS)

    cancel_run_if_active()
    die(f"Timed out after {WAIT_SECONDS}s waiting for this run's VNC. No stale peer was used. The workflow was cancelled to avoid wasting runner time. Run: {run_url}")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        say("\nInterrupted.")
        cancel_run_if_active()
