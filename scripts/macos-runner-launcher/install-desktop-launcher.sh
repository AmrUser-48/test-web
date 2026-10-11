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

LAUNCHER="$DESKTOP_DIR/Launch macOS ChatGPT Runner.desktop"
cat > "$LAUNCHER" <<DESKTOP
[Desktop Entry]
Type=Application
Name=Launch macOS ChatGPT Runner
Comment=Start the GitHub Actions macOS runner and connect using VNC
Exec=/usr/bin/python3 "$BIN_DIR/macos-runner-one-click.py"
Icon=computer
Terminal=true
Categories=Network;RemoteAccess;
DESKTOP
chmod +x "$LAUNCHER"
if command -v gio >/dev/null 2>&1; then
  gio set "$LAUNCHER" metadata::trusted true 2>/dev/null || true
fi

echo "Installed: $LAUNCHER"
echo "No packages were installed."
missing=()
command -v python3 >/dev/null 2>&1 || missing+=(python3)
command -v tailscale >/dev/null 2>&1 || missing+=(tailscale)
command -v vncviewer >/dev/null 2>&1 || missing+=(tigervnc-viewer)
if (("${#missing[@]}")); then
  echo "Missing existing commands/packages: ${missing[*]}"
  echo "Install only what is missing; this installer will not run apt or install dependencies."
else
  echo "Available: Python 3, Tailscale CLI, vncviewer."
fi
echo "First launch asks for a fine-grained GitHub token (Actions: Read and write for AmrUser-48/test-web)."
