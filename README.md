# The Future

International website for The Future. Built with Zola **0.22.1** and the Avenir
brand tokens, typography and self-hosted fonts. Do not use Zola 0.23+: these
Tera templates use the macro syntax supported by the pinned version.

```sh
git submodule update --init
mise run dev
mise run build
mise run check
```

The theme submodule is pinned to an existing upstream commit. The international
site owns its templates and `sass/main.scss`, and imports only the shared reset,
tokens and typography. Its English content and existing page URLs remain local
to this repository. No npm packages or client framework are needed.

## November 2026 redesign

- Ceramic/charcoal surfaces, rose-to-violet brand accents, generous editorial type.
- Homepage with a future scene, twelve programme areas, method, international
  ambition, a link to the Swiss project and a participation invitation.
- Consistent policy pages, section navigation, native FAQ disclosures, contact
  and participation pages, and a complete site directory.
- Responsive navigation with optional search, light/dark mode, keyboard dismissal
  and focus return. Content and all page links remain available without JavaScript.
- Contact uses email links. Disabled forms were removed; there is no newsletter
  subscription or contact-form backend on this site. Privacy text reflects this.
- Local fonts and assets, updated globe icons and social image, responsive
  AVIF/WebP/JPEG artwork, and a versioned offline cache.

The original AI-generated image and exact prompt are in `visuals/incoming/`.
`visuals/provenance.json` records the tool, date, checksum and delivery sizes.
Rebuild its web assets with `python3 scripts/build_visuals.py` (ImageMagick with
AVIF/WebP support). The scene is visibly labelled as imagined and AI-generated.
The social card has an editable SVG source in `assets/og-en.svg`; export with a
full SVG renderer (librsvg or Inkscape) and installed Clash Display/Switzer fonts.
The native favicon source is `static/favicon.svg`.

## Verification

Production build and internal-link check pass: 22 content pages, 24 HTML files
including home and 404. Output checks covered local URLs and fragments, assets,
font URLs, unique IDs, one H1 per document, valid JSON-LD, image dimensions/alt
text and the absence of disabled controls. JavaScript syntax and focused logic
checks passed for themes (including blocked storage), search, no-results state,
Escape/focus return and outside-click dismissal. New source/output checksums and
image dimensions were verified; social artwork and icons were inspected.

Desktop/mobile browser layout and interaction review is **not verified**. The
browser connector was unavailable, native Chrome use conflicted with concurrent
user activity, and opening native Firefox stalled. Complete that review before
publishing. These changes have not been deployed.
