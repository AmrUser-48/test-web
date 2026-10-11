# test-web

Minimal terminal-style single-page starter. Vanilla HTML/CSS/JS; no framework, build step, fonts, trackers, or runtime dependencies. Hash navigation changes views without reloading the document.

## Temporary remote ChatGPT VNC

The workflow runs Chromium at ChatGPT and exposes a native VNC connection only on the runner's private Tailscale IP. It does not use Pinggy or Cloudflare.

1. Create a Tailscale account and sign in on your laptop.
2. In Tailscale **Access Controls**, create the tag `tag:ci` if it does not exist yet. In [Tailscale key settings](https://login.tailscale.com/admin/settings/keys), create an auth key marked **reusable** and **ephemeral**, tagged `tag:ci` (and pre-approved if device approval is enabled). Add it to [this repository's Actions secrets](https://github.com/AmrUser-48/test-web/settings/secrets/actions/new) as `TAILSCALE_AUTHKEY`. Do not paste the key into chat or commit it.
3. Because the Debian disk is full, use Tailscale's official static binaries in RAM (`/dev/shm`) instead of installing the 77 MB package:

   ```sh
   mkdir -p /dev/shm/tailscale && cd /dev/shm/tailscale
   curl -fLO https://pkgs.tailscale.com/stable/tailscale_1.104.1_amd64.tgz
   tar xzf tailscale_1.104.1_amd64.tgz
   cd tailscale_1.104.1_amd64
   sudo mkdir -p /run/tailscale
   sudo ./tailscaled --state=/dev/shm/tailscaled.state >/dev/shm/tailscaled.log 2>&1 &
   sleep 2
   sudo ./tailscale up
   ```

   Complete the login link once. This temporary setup uses RAM rather than installing the package on disk; it must be started again after reboot.
4. Run [Temporary remote ChatGPT VNC](https://github.com/AmrUser-48/test-web/actions/workflows/remote-chatgpt-browser.yml). The workflow summary shows the runner's private `100.x.y.z` address.
5. Open TigerVNC Viewer on Debian and enter `100.x.y.z::5900`, replacing the example IP with the one in the workflow summary.
6. To check whether the route is direct, run `sudo ./tailscale ping 100.x.y.z` from the directory where the static binary was unpacked. The output should say `direct`; `DERP` means Tailscale is relaying traffic.

The VNC port is not exposed to the public internet; it is bound only to the runner's private Tailscale address. A direct peer-to-peer route depends on NAT and firewall conditions, so Tailscale may fall back to a relay. Cancel the Actions run to stop the session early.

## Local preview

```sh
python3 -m http.server 8000
```

Open <http://localhost:8000>.

## GitHub Pages

The lightweight UI is published from `main` and `/(root)`. The homepage is `index.html`.
