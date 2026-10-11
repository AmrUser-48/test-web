# test-web

Minimal terminal-style single-page starter. Vanilla HTML/CSS/JS; no framework, build step, fonts, trackers, or runtime dependencies. Hash navigation changes views without reloading the document.

## Temporary remote ChatGPT browser

A manually triggered GitHub Actions workflow starts a disposable Chromium container configured to open ChatGPT and exposes the desktop **only on the runner's private Tailscale address**. It no longer uses Cloudflare or Pinggy.

1. In Tailscale, create an **ephemeral, reusable auth key**. If device approval is enabled, pre-approve the key.
2. Add that key to this repository's Actions secrets as `TAILSCALE_AUTHKEY`. Also add `BROWSER_ACCESS_PASSWORD` with a unique password of at least 20 characters, using only ASCII letters, digits, dot, underscore, and hyphen: [Repository secrets](https://github.com/AmrUser-48/test-web/settings/secrets/actions/new).
3. Install the official Tailscale package on Debian 12 and sign in to the **same Tailscale network** as your account.
4. Run [Temporary remote ChatGPT Chromium](https://github.com/AmrUser-48/test-web/actions/workflows/remote-chatgpt-browser.yml) and select a duration.
5. Open the private `http://100.x.y.z:3000` URL from the run summary. Log in as `remote` using `BROWSER_ACCESS_PASSWORD`. The URL works only while the runner is online and your Debian laptop is connected to the same Tailscale network.
6. To check the route on Debian, run `tailscale ping 100.x.y.z`. The output should say `direct`; if it says `DERP`, Tailscale is relaying the connection.
7. Cancel the Actions run to stop early.

The Docker port is bound to the runner's Tailscale IP, not its public interfaces. The workflow saves the viewer screenshot, DOM/canvas state, browser errors, and WebSocket frame statistics as a short-lived Actions artifact. The diagnostic artifact expires after one day; browser login data is not saved as an artifact. A direct path depends on NAT and firewall conditions; Tailscale may use a relay if direct connectivity is unavailable.

## Local preview

```sh
python3 -m http.server 8000
```

Open <http://localhost:8000>.

## GitHub Pages

The lightweight UI is published from `main` and `/(root)`. The homepage is `index.html`.
