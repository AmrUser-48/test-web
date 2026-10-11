# One-click macOS and Ubuntu VNC runner launchers

The Python launcher in this directory can start either:
- the temporary macOS workflow, or
- the Ubuntu 24.04 Core 2 XFCE desktop workflow.

It waits for the Tailscale peer belonging to that exact workflow run, checks that it identifies as the expected operating system, verifies an actual VNC/RFB greeting on port 5900, and only then starts TigerVNC. It does not choose an old IP or the wrong OS.

## Automated validation

The repository workflow [Validate remote desktop launchers](../../actions/workflows/validate-remote-desktop-launchers.yml) checks Python syntax, installer shell syntax, launcher target selection, VNC password-file handling, and the Ubuntu desktop persistence/theme configuration on changes.

## Local requirements

- Python 3 (standard library only)
- Tailscale CLI, already installed and connected to your tailnet
- TigerVNC `vncviewer`
- `vncpasswd` or `tigervncpasswd`, needed once to create the local VNC password file

This tool does not use or install Git, GitHub CLI (`gh`), curl, jq, Node.js, Docker, or Python packages. The installer does not run apt.

If only the password-file helper is missing, install this small package once:
`sudo apt install tigervnc-tools`

## Install the desktop icons

From this directory:

```sh
bash install-desktop-launcher.sh
```

This copies the Python launcher to `~/.local/bin` and creates two icons on your desktop:
- `Launch macOS ChatGPT Runner.desktop`
- `Launch Ubuntu Core2 VNC Runner.desktop`

The Ubuntu option uses `.github/workflows/temporary-core2-build-runner-vnc.yml`, which provides the XFCE desktop with Arc-Dark and the right-side vertical deskbar.

## First launch

A GitHub personal access token is needed to dispatch and cancel workflows. Start with a fine-grained token scoped to `AmrUser-48/test-web` with **Actions: Read and write**:
https://github.com/settings/personal-access-tokens/new

If GitHub still returns `403 Resource not accessible by personal access token` despite those permissions, use a **classic PAT with the `repo` scope** instead. The same error has been reported for correctly permissioned fine-grained tokens; this workaround has been reported to work. A classic `repo` token grants broader repository access, so keep it private and use it only if the fine-grained token fails. GitHub's endpoint requirements are documented here: https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event

The launcher prompts for the token without echoing it and saves it to `~/.config/macos-runner-launcher/token` with mode `0600`. To replace a saved token, remove that file and run the launcher again:
```sh
rm -f ~/.config/macos-runner-launcher/token
python3 ~/.local/bin/macos-runner-one-click.py --target ubuntu
```

It also prompts once for the same `VNC_PASSWORD` configured in the repository's Actions secrets. It writes a TigerVNC-compatible password file to `~/.config/tigervnc/runner-passwd` (directory mode `0700`, file mode `0600`). Subsequent connections use that file through `vncviewer -passwd`, so no VNC password prompt is shown. If the repository secret changes, run:

```sh
python3 ~/.local/bin/macos-runner-one-click.py --setup-vnc-password --reset-vnc-password
```

The VNC password file is obfuscated by TigerVNC, not strongly encrypted. Keep the file private; the owner-only permissions are important. VNC authentication stays enabled; the launcher does not switch the server to unauthenticated VNC.

## Saved Ubuntu desktop state

The Ubuntu workflow now saves the user's home directory and GitHub workspace between sessions, including:
- XFCE panel/theme preferences and manual layout changes
- Chrome profile, cookies, and browser state
- Files and project changes under the home/workspace directories

It excludes per-run SSH/VNC credential files, temporary GitHub workflow files, downloaded action code, trash, and disposable caches. Before starting the next session it restores an encrypted archive from GitHub Actions cache; if that cache is unavailable, it automatically downloads the latest retained encrypted backup artifact. At the end, it stores a new encrypted cache entry and uploads an encrypted backup artifact with 30-day retention, then removes older state artifacts so only the newest backup consumes artifact storage. The archive is encrypted with the existing `TAILSCALE_AUTHKEY` secret; the auth key must remain unchanged to decrypt an existing snapshot.

GitHub may evict caches after 7 days without access or due to its storage limit, so the 30-day encrypted artifact is the fallback. This is not permanent storage: download separately anything that must survive beyond the artifact's retention period. The repository `xtr-dev/mcp-playwright-novnc` describes a persistent service, but its current Compose example does not mount a persistent volume; browser/profile files do not survive container removal unless a volume or backup mechanism is configured.

## Behaviour and timeouts

1. Dispatches the chosen workflow for 350 minutes by default.
2. Looks for a new peer named `github-macos-<run-id>` or `github-core2-<run-id>`.
3. Checks the peer's OS and verifies VNC speaks RFB on port 5900.
4. Opens `vncviewer` using the saved local password file.
5. If TigerVNC closes or crashes, the GitHub-hosted runner stays alive until its configured session timeout; the launcher prints the VNC address and reconnect instructions. Press Ctrl+C in the launcher terminal to explicitly cancel the remote workflow.

**Known limitation — GitHub-hosted macOS VNC:** run #16 confirmed that the macOS 15 Apple Silicon VM did not start Apple's Screen Sharing service: `MACOS_VNC_READY=0`, no RFB greeting on port 5900, and `screensharingd` reported `not running` after the `kickstart`/ `launchctl` attempts. The workflow now fails immediately instead of appearing ready and idling for the full session duration. The log also showed `actions/upload-artifact@v4` returning `ENOTFOUND` for both SSH-key and address uploads; that is a separate GitHub artifact-service/DNS failure and should not be confused with the VNC failure. A fully working native macOS desktop requires a macOS runner where Screen Sharing/screen-capture permissions are available. For a working graphical session on the current setup, use the Ubuntu VNC workflow.

## Remove local launcher files

```sh
rm -f "$HOME/Desktop/Launch macOS ChatGPT Runner.desktop"
rm -f "$HOME/Desktop/Launch Ubuntu Core2 VNC Runner.desktop"
rm -f "$HOME/.local/bin/macos-runner-one-click.py"
rm -rf "$HOME/.config/macos-runner-launcher"
rm -rf "$HOME/.config/tigervnc"
```
