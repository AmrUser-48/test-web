# test-web

Minimal terminal-style single-page starter. Vanilla HTML/CSS/JS; no framework, build step, fonts, or runtime dependencies. Hash navigation switches views without reloading the document.

## Temporary remote ChatGPT browser

A manually triggered GitHub Actions workflow launches a disposable Linux desktop and publishes it using a temporary Cloudflare HTTPS tunnel. It is an experiment, not a permanent server.

1. Add a repository Actions secret named `BROWSER_ACCESS_PASSWORD` with a unique password of at least 20 characters: [Add secret](https://github.com/AmrUser-48/test-web/settings/secrets/actions/new).
2. Open [Temporary remote ChatGPT browser](https://github.com/AmrUser-48/test-web/actions/workflows/remote-chatgpt-browser.yml) and click **Run workflow**.
3. Choose a session duration (up to 350 minutes).
4. Wait for the job summary to show the URL and for the authenticated external health check to pass.
5. Open the URL. At the browser login prompt, username is `remote`; use the password stored in `BROWSER_ACCESS_PASSWORD`. Launch the browser in the desktop and go to <https://chatgpt.com>.
6. Cancel the Actions run to stop early.

The old Cloudflare Quick Tunnel email PIN gate was removed because Cloudflare tracked an open bug where the authenticated session expired after seconds. The desktop now uses the password gate built into Webtop, with Cloudflare terminating public HTTPS and proxying to Webtop's documented HTTP port. The tunnel URL remains temporary and is visible in the public Actions log; the password is not logged or printed in the summary. Do not reuse a password from another service.

The session is disposable: the workflow does not preserve browser cookies or the signed-in ChatGPT profile as an artifact. GitHub-hosted runners have a six-hour hard job limit. Webtop provides a desktop, not a specially stripped ChatGPT frontend; this experiment moves the browser rendering to the runner.

## Local preview

```sh
python3 -m http.server 8000
```

Open <http://localhost:8000>.

## GitHub Pages

For the static skeleton, select **Settings → Pages → Deploy from a branch → main → /(root)**. The homepage is `index.html`.

## Current website status

The static site's chat screen is only a UI placeholder. The remote desktop workflow is separate from the vanilla SPA and does not place any API key in the website.
