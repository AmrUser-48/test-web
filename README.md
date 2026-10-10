# test-web

A tiny terminal-style single-page website starter designed for very low overhead.

- Vanilla HTML/CSS/JavaScript; no framework and no build step.
- Hash-based client-side navigation; clicking links does not reload the document.
- Responsive layout and keyboard-accessible navigation.
- No external fonts, images, trackers, or runtime dependencies.
- Ready to publish with GitHub Pages.

## Run a temporary remote browser on GitHub Actions

This repository includes a manually triggered workflow that starts a disposable Linux desktop and exposes it through an email-protected Cloudflare Quick Tunnel. Use it to open the normal ChatGPT website on a remote runner.

1. Open [Actions secrets](https://github.com/AmrUser-48/test-web/settings/secrets/actions/new), create a repository secret named `BROWSER_ALLOWED_EMAIL`, and set it to an email address you can receive one-time PINs at.
2. Open [Temporary remote ChatGPT browser](https://github.com/AmrUser-48/test-web/actions/workflows/remote-chatgpt-browser.yml).
3. Click **Run workflow**, choose the duration (up to 350 minutes), and start it.
4. Open the run summary and follow the temporary URL. Cloudflare sends a one-time PIN to the address configured in the secret.
5. In the remote desktop, open the browser and navigate to <https://chatgpt.com>, then sign in normally.

To stop early, cancel the workflow run. The runner is discarded when the job ends, so its browser profile and login session are not saved by this workflow. Do not export browser profiles, cookies, or authentication data as artifacts.

This is an experiment, not a permanent hosted service. GitHub-hosted jobs have a hard six-hour limit; Cloudflare Quick Tunnels are temporary testing tunnels. Public repository Actions logs show the generated URL, but Cloudflare email verification restricts access.

## Local preview

```sh
python3 -m http.server 8000
```

Open <http://localhost:8000>.

## GitHub Pages

The site is static. In repository settings, choose **Pages → Build and deployment → Deploy from a branch**, then select `main` and `/ (root)`. The homepage is `index.html`.

## Website status

The chat screen is an interface placeholder. This static site itself does not sign in to ChatGPT and does not store OAuth credentials or API keys.
