# Minimal one-click macOS runner launcher

The launcher in this directory dispatches `.github/workflows/macos-chatgpt-vnc.yml`, waits for the new run's specifically named macOS Tailscale peer, checks for a real VNC/RFB greeting on TCP 5900, and starts TigerVNC only after that check passes.

## Local requirements

- Python 3 (standard library only)
- Tailscale CLI, already installed and connected to your tailnet
- TigerVNC `vncviewer`

It does not use or install Git, GitHub CLI (`gh`), curl, jq, Node.js, Docker, or Python packages. The installer does not invoke apt.

## Install

From this directory:

```sh
bash install-desktop-launcher.sh
```

This copies the Python script to `~/.local/bin` and creates `~/Desktop/Launch macOS ChatGPT Runner.desktop` (respecting `xdg-user-dir DESKTOP` when available).

## First launch

A fine-grained GitHub personal access token is needed to dispatch and cancel the workflow. Scope it to repository `AmrUser-48/test-web` and grant **Actions: Read and write**:
https://github.com/settings/personal-access-tokens/new

The launcher prompts for the token without echoing it and saves it to `~/.config/macos-runner-launcher/token` with mode `0600`. Do not share the token.

## Behaviour

1. Dispatches the macOS workflow for 350 minutes by default.
2. Looks for the Tailscale peer named `github-macos-<run-id>`.
3. Checks that peer identifies as macOS and responds with an RFB greeting on port 5900.
4. Opens `vncviewer` only after verification; it will not select a stale peer or the Ubuntu runner.
5. Requests cancellation of that workflow when the viewer closes or Ctrl+C is pressed.

The workflow's Tailscale hostname must be configured as `github-macos-${{ github.run_id }}`. The native macOS VNC service must still pass the actual end-to-end check; this script fails explicitly if it does not.

To remove the launcher and local saved token:

```sh
rm -f "$HOME/Desktop/Launch macOS ChatGPT Runner.desktop"
rm -f "$HOME/.local/bin/macos-runner-one-click.py"
rm -rf "$HOME/.config/macos-runner-launcher"
```
