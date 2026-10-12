# One-click macOS RustDesk and Ubuntu VNC desktop launchers

The Python launcher starts either the temporary macOS 15 Apple Silicon desktop over RustDesk, or the Ubuntu 24.04 Core 2 XFCE desktop over VNC.

The macOS workflow no longer tries Apple's native Screen Sharing service. That approach failed on the hosted macOS VM because the service never provided an RFB greeting. Instead, it starts RustDesk and registers a remote ID.

## Local requirements

For **macOS desktop**:
- Python 3 and OpenSSL
- RustDesk client installed on Debian 12

Official Debian 12 x86_64 package: https://github.com/rustdesk/rustdesk/releases/download/1.5.0/rustdesk-1.5.0-x86_64.deb

For **Ubuntu Core 2 VNC**:
- Tailscale CLI, already installed and connected to your tailnet
- TigerVNC `vncviewer`
- `vncpasswd` or `tigervncpasswd`, needed once for the local VNC password file

The installer checks for these commands but does not install packages or run apt. If only Ubuntu's password-file helper is missing, install `tigervnc-tools` once:

```sh
sudo apt install tigervnc-tools
```

## Install the desktop icons

From this directory:

```sh
bash install-desktop-launcher.sh
```

This installs the Python launcher to `~/.local/bin` and creates:
- `Launch macOS ChatGPT Runner.desktop`
- `Launch Ubuntu Core2 VNC Runner.desktop`

The Ubuntu option uses `.github/workflows/temporary-core2-build-runner-vnc.yml`, which provides the XFCE desktop with Arc-Dark and the right-side vertical deskbar.

## First launch and secrets

A GitHub personal access token is needed to dispatch workflows. Start with a fine-grained token scoped to `AmrUser-48/test-web` with **Actions: Read and write**:
https://github.com/settings/personal-access-tokens/new

If GitHub still returns `403 Resource not accessible by personal access token`, the token-owning account must have write access to the repository. A classic PAT with `repo` scope is a broader-permission fallback; keep it private. The API requirements are documented at https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event.

The launcher prompts for the token without echoing it and saves it to `~/.config/macos-runner-launcher/token` with mode `0600`. To replace it:

```sh
rm -f ~/.config/macos-runner-launcher/token
python3 ~/.local/bin/macos-runner-one-click.py --target macos
```

The repository Actions secret `VNC_PASSWORD` is required by both workflows. For macOS, it encrypts the temporary RustDesk credentials artifact because this repository is public. Use a strong, random password (preferably 20+ characters). The launcher asks for this secret with hidden input, downloads the matching run's encrypted artifact, decrypts it locally using OpenSSL, and then opens RustDesk. The RustDesk password is shown only in your local terminal, not in GitHub logs or an unencrypted artifact.

For Ubuntu, the same `VNC_PASSWORD` configures VNC. The launcher writes a TigerVNC-compatible password file to `~/.config/tigervnc/runner-passwd` (directory mode `0700`, file mode `0600`). This local VNC password file is obfuscated by TigerVNC, not strongly encrypted.

## macOS desktop workflow

1. Start the macOS icon or run `python3 ~/.local/bin/macos-runner-one-click.py --target macos`.
2. Enter the `VNC_PASSWORD` Actions secret when prompted, then your GitHub token if it is not saved.
3. The workflow starts a macOS 15 Apple Silicon runner, opens Chrome at ChatGPT, installs RustDesk, creates an ephemeral ID/password, and uploads the credentials encrypted with `VNC_PASSWORD`.
4. The launcher decrypts the artifact locally and opens RustDesk. Enter the displayed ID in RustDesk and supply the displayed password.
5. To connect to a running session without starting another runner, use `--target macos --reuse-run-id RUN_ID` with that session's GitHub Actions run ID.
6. Closing RustDesk does **not** stop the remote workflow. Cancel the Actions run to stop the session early; otherwise it ends at the selected timeout (350 minutes by default).

The credential artifact expires after one day. The generated connection password is different on every run.

**Testing status:** this RustDesk path is the replacement for the failed macOS Screen Sharing attempt. It still needs a successful end-to-end run to confirm that the hosted macOS VM permits live screen capture and input through RustDesk. If the workflow fails during RustDesk setup, use the Actions log for that run; do not repeat the old native VNC setup.

## Ubuntu desktop state

The Ubuntu workflow saves the user's home directory and GitHub workspace between sessions, including XFCE preferences, Chrome profile/cookies, files, and projects. It excludes per-run SSH/VNC credentials, temporary workflow files, downloaded action code, trash, and disposable caches. At session end it saves an encrypted cache entry and uploads an encrypted backup artifact, removing older state artifacts to control storage use. The archive is encrypted with `TAILSCALE_AUTHKEY`; that secret must remain unchanged to decrypt existing snapshots.

GitHub may evict caches after 7 days without access or because of storage limits, so the retained encrypted artifact is the fallback. This is not permanent storage: download anything important separately.

## Remove local launcher files

```sh
rm -f "$HOME/Desktop/Launch macOS ChatGPT Runner.desktop"
rm -f "$HOME/Desktop/Launch Ubuntu Core2 VNC Runner.desktop"
rm -f "$HOME/.local/bin/macos-runner-one-click.py"
rm -rf "$HOME/.config/macos-runner-launcher"
rm -rf "$HOME/.config/tigervnc"
```
