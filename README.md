# test-web

A tiny terminal-style single-page website starter designed for very low overhead.

- Vanilla HTML/CSS/JavaScript; no framework and no build step.
- Hash-based client-side navigation; clicking links does not reload the document.
- Responsive layout and keyboard-accessible navigation.
- No external fonts, images, trackers, or runtime dependencies.
- Ready to publish with GitHub Pages.


## Local preview

```sh
python3 -m http.server 8000
```

Open <http://localhost:8000>.

## GitHub Pages

The site is static. In repository settings, choose **Pages → Build and deployment → Deploy from a branch**, then select `main` and `/ (root)`. The homepage is `index.html`.

## Website status

The chat screen is an interface placeholder. This static site itself does not sign in to ChatGPT and does not store OAuth credentials or API keys.
