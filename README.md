# test-web

Minimal terminal-style single-page starter. Vanilla HTML/CSS/JS; no framework, build step, fonts, trackers, or runtime dependencies. Hash navigation changes views without reloading the document.

## Temporary remote ChatGPT browser

A manually triggered GitHub Actions workflow starts a disposable Chromium container configured to open ChatGPT, then exposes it through a temporary Cloudflare HTTPS tunnel.

1. Add a repository Actions secret named `BROWSER_ACCESS_PASSWORD` with a unique password of at least 20 characters. Use only ASCII letters, digits, dot, underscore, and hyphen: [Add secret](https://github.com/AmrUser-48/test-web/settings/secrets/actions/new).
2. Open [Temporary remote ChatGPT Chromium](https://github.com/AmrUser-48/test-web/actions/workflows/remote-chatgpt-browser.yml), select a duration, then click **Run workflow**.
3. Use the URL from the run summary. The browser login is username `remote` and the password stored in `BROWSER_ACCESS_PASSWORD`.
4. Chromium is configured to open <https://chatgpt.com>. Sign in with your normal account.
5. Cancel the Actions run to stop early.

The workflow checks that Chromium starts, the public page responds, and the Selkies WebSocket upgrade returns HTTP 101. If any check fails, it stops with an error instead of claiming the URL is ready. This is a temporary experiment, not a persistent server. Sessions are disposable and browser login data is not saved as an artifact.

## Local preview

```sh
python3 -m http.server 8000
```

Open <http://localhost:8000>.

## GitHub Pages

The lightweight UI is published from `main` and `/(root)`. The homepage is `index.html`.
