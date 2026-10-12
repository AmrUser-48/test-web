#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
SOURCE="$SOURCE_DIR/macos-runner-one-click.py"
[[ -f "$SOURCE" ]] || { echo "Missing $SOURCE" >&2; exit 1; }

BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"
install -m 0755 "$SOURCE" "$BIN_DIR/macos-runner-one-click.py"

if command -v xdg-user-dir >/dev/null 2>&1; then
  DESKTOP_DIR="$(xdg-user-dir DESKTOP)"
else
  DESKTOP_DIR="$HOME/Desktop"
fi
[[ -n "$DESKTOP_DIR" ]] || DESKTOP_DIR="$HOME/Desktop"
mkdir -p "$DESKTOP_DIR"

MAC_LAUNCHER="$DESKTOP_DIR/Launch macOS ChatGPT Runner.desktop"
UBUNTU_LAUNCHER="$DESKTOP_DIR/Launch Ubuntu Core2 VNC Runner.desktop"

cat > "$MAC_LAUNCHER" <<DESKTOP
[Desktop Entry]
Type=Application
Name=Launch macOS ChatGPT Runner
Comment=Start the GitHub Actions macOS M1 runner and connect using RustDesk
Exec=/usr/bin/python3 "$BIN_DIR/macos-runner-one-click.py" --target macos
Icon=computer
Terminal=true
Categories=Network;RemoteAccess;
DESKTOP

cat > "$UBUNTU_LAUNCHER" <<DESKTOP
[Desktop Entry]
Type=Application
Name=Launch Ubuntu Core2 VNC Runner
Comment=Start the Ubuntu XFCE runner and connect using VNC
Exec=/usr/bin/python3 "$BIN_DIR/macos-runner-one-click.py" --target ubuntu
Icon=computer
Terminal=true
Categories=Network;RemoteAccess;
DESKTOP

chmod +x "$MAC_LAUNCHER" "$UBUNTU_LAUNCHER"
if command -v gio >/dev/null 2>&1; then
  gio set "$MAC_LAUNCHER" metadata::trusted true 2>/dev/null || true
  gio set "$UBUNTU_LAUNCHER" metadata::trusted true 2>/dev/null || true
fi

echo "Installed: $MAC_LAUNCHER"
echo "Installed: $UBUNTU_LAUNCHER"
echo "No packages were installed."
missing=()
command -v python3 >/dev/null 2>&1 || missing+=(python3)
command -v openssl >/dev/null 2>&1 || missing+=(openssl)
command -v rustdesk >/dev/null 2>&1 || missing+=(rustdesk-client)
command -v tailscale >/dev/null 2>&1 || missing+=(tailscale)
command -v vncviewer >/dev/null 2>&1 || missing+=(tigervnc-viewer)
command -v vncpasswd >/dev/null 2>&1 || command -v tigervncpasswd >/dev/null 2>&1 || missing+=(tigervnc-tools)
if (("${#missing[@]}")); then
  echo "Missing existing commands/packages: ${missing[*]}"
  echo "Install only what is missing; this installer will not run apt or install dependencies."
  echo "RustDesk for Debian 12 x86_64: https://github.com/rustdesk/rustdesk/releases/download/1.5.0/rustdesk-1.5.0-x86_64.deb"
else
  echo "Available: Python 3, OpenSSL, RustDesk, Tailscale CLI, vncviewer and vncpasswd."
fi
echo "First run asks for a fine-grained GitHub token (Actions: Read and write for AmrUser-48/test-web)."
