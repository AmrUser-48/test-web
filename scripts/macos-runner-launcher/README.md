# One-click macOS and Ubuntu VNC runner launchers

The Python launcher in this directory can start either:
- the temporary macOS workflow, or
- the Ubuntu 24.04 Core 2 XFCE desktop workflow.

It waits for the Tailscale peer belonging to that exact workflow run, checks that it identifies as the expected operating system, verifies an actual VNC/RFB greeting on port 5900, and only then starts TigerVNC. It does not choose an old IP or the wrong OS.

## Local requirements

- Python 3 (standard library only)
- Tailscale CLI, already installed and connected to your tailnet
- TigerVNC \`vncviewer\`
- \`vncpasswd\` or \`tigervncpasswd\`, needed once to create the local VNC password file

This tool does not use or install Git, GitHub CLI (\`gh\`), curl, jq, Node.js, Docker, or Python packages. The installer does not run apt.

If only the password-file helper is missing, install this small package once:
\`sudo apt install tigervnc-tools\`

## Install the desktop icons

From this directory:

\`\`\`sh
bash install-desktop-launcher.sh
\`\`\`

This copies the Python launcher to \`~/.local/bin\` and creates two icons on your desktop:
- \`Launch macOS ChatGPT Runner.desktop\`
- \`Launch Ubuntu Core2 VNC Runner.desktop\`

The Ubuntu option uses \`.github/workflows/temporary-core2-build-runner-vnc.yml\`, which provides the XFCE desktop with Arc-Dark and the right-side vertical deskbar.

## First launch

A fine-grained GitHub personal access token is needed to dispatch and cancel workflows. Scope it to \`AmrUser-48/test-web\` and grant **Actions: Read and write**:
https://github.com/settings/personal-access-tokens/new

The launcher prompts for the token without echoing it and saves it to \`~/.config/macos-runner-launcher/token\` with mode \`0600\`.

It also prompts once for the same \`VNC_PASSWORD\` configured in the repository's Actions secrets. It writes a TigerVNC-compatible password file to \`~/.config/tigervnc/runner-passwd\` (directory mode \`0700\`, file mode \`0600\`). Subsequent connections use that file through \`vncviewer -passwd\`, so no VNC password prompt is shown. If the repository secret changes, run:

\`\`\`sh
python3 ~/.local/bin/macos-runner-one-click.py --target ubuntu --reset-vnc-password
\`\`\`

The VNC password file is obfuscated by TigerVNC, not strongly encrypted. Keep the file private; the owner-only permissions are important. VNC authentication stays enabled; the launcher does not switch the server to unauthenticated VNC.

## Saved Ubuntu desktop state

The Ubuntu workflow now saves these between sessions:
- XFCE panel/theme preferences, including manual layout changes
- Chrome profile, cookies, and browser state
- Desktop, Documents, Downloads, GTK settings, and local application launchers

Before starting the next session it restores an encrypted archive from GitHub Actions cache. At the end, it stores a new encrypted cache entry and uploads an encrypted backup artifact with 30-day retention. The archive is encrypted with the existing \`TAILSCALE_AUTHKEY\` secret; the auth key must remain unchanged to decrypt an existing snapshot. The archive excludes common Chrome cache directories but preserves the profile itself.

The cache is convenient for session-to-session restoration but GitHub may evict caches. The encrypted artifact is a time-limited backup, not permanent storage. Download files you cannot afford to lose separately before ending a session. The repository \`xtr-dev/mcp-playwright-novnc\` describes a persistent service, but its current Compose example does not mount a persistent volume; a container's browser/profile files do not survive removal unless a volume or backup mechanism is configured.

## Behaviour and timeouts

1. Dispatches the chosen workflow for 350 minutes by default.
2. Looks for a new peer named \`github-macos-<run-id>\` or \`github-core2-<run-id>\`.
3. Checks the peer's OS and verifies VNC speaks RFB on port 5900.
4. Opens \`vncviewer\` using the saved local password file.
5. Requests cancellation of that workflow when the viewer closes or Ctrl+C is pressed.

The macOS workflow is currently known to have a hosted-runner limitation: Apple's Screen Sharing service has not consistently opened port 5900. The launcher will refuse to connect unless that Mac really answers VNC. The Ubuntu VNC workflow is the available path for a working graphical session.

## Remove local launcher files

\`\`\`sh
rm -f "$HOME/Desktop/Launch macOS ChatGPT Runner.desktop"
rm -f "$HOME/Desktop/Launch Ubuntu Core2 VNC Runner.desktop"
rm -f "$HOME/.local/bin/macos-runner-one-click.py"
rm -rf "$HOME/.config/macos-runner-launcher"
rm -rf "$HOME/.config/tigervnc"
\`\`\`
