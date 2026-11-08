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

## Design system: same as the Swiss site

The site uses the Swiss site's (die-zukunft.ch) design system, not a separate
one. `sass/main.scss` imports the **full** avenir stylesheet. The templates are
world copies of avenir's, with the same markup and classes:

- `templates/base.html` is a copy of `avenir/templates/base.html`: top bar, pins,
  command overlay, hex section tags + share overlay, reading progress, ground
  lattice, colophon. The deliberate differences are English only, this site's URLs
  and feed, its own hex map, and a **wireframe globe** (`shape: 'globe'` in the
  shared `SwissCross` renderer) instead of the Swiss cross for the nav logo and the
  ground lattice. The globe is The Future's mark (favicon).
- Shared, not copied: `partials/share-overlay.html` and `partials/ui-scripts.html`
  (share overlay, pins, command overlay, theme switch) come from avenir and are
  included by both sites' `base.html`.
- `macros/nav.html` and `macros/footer.html` are avenir's macros with world links.
- `manifest.html` and `vision.html` are avenir's templates (vision without the Swiss
  monitor sparklines). `news-page.html` and `section.html` run the News section.
- `index.html` uses the Swiss homepage layers (lede, layer heads, pillar grid,
  tiles, join). `page.html` and `programm.html` are avenir's templates without the
  Zukunftslabor evidence blocks. `kontakt.html` and `mitmachen.html` follow avenir's
  markup with the world forms.
- World-only: `chapters.html` (how national chapters work + enquiry form) and
  `macros/forms.html` (newsletter and contact/chapter forms).

**Drift check.** `templates/avenir-sync.toml` records, for every world copy, the
avenir version it was last brought in line with. `mise run check` (via
`scripts/check_site.py`) fails as soon as the avenir submodule moves and one of
those avenir templates changed, and prints the diff to port. After porting, run
`python scripts/check_site.py --accept templates/<file>`. A new copy without an entry
also fails. The same script fails 60 days before `static/.well-known/security.txt`
expires.

## Content, licence, machine-readable surface

Content mirrors the Swiss English pages, adapted for an international audience.
Swiss examples are labelled "the Swiss chapter". The texts are licensed CC BY 4.0
(see `content/legal.md`). `mise run build` first runs `scripts/build_llms.py`,
which writes `static/llms.txt`, `static/llms-full.txt` and a Markdown copy of every
page under `static/md/`. **These generated files are committed**, because
Cloudflare Pages only runs `zola build`.

Brand images (globe mark, favicon, app icons, social card, article cards) are
rendered in the `assets` repo: `scripts/gen_globe.mjs` and `scripts/render_brand.mjs`
with `ICON_FILE=favicons/globe-tile.svg BRAND_WM="the future." BRAND_SUB="A global
movement" BRAND_HOST=the-future.world`.

Hex map (in `base.html`): the same address as the Swiss site for the same topic:
`0x00` home, `0x01` vision, `0x02` program, `0x03` join, `0x04` chapters (world
only), `0x10` manifesto,
`0x11` beyond-left-right, `0x20`–`0x2C` the thirteen areas (see `content/_index.md`
`hex`), `0x40` people, `0x41` contact, `0x50` news/a-new-face, `0xF0` legal,
`0xF1` privacy, `0xF2` info, `0xF3` news index. Homepage layers 0x0000–0x0005, the
theses layer 0x0006 (shown second, added later).
Stability rule: never renumber.

## Visuals

Pictures are AI-generated, visibly labelled as imagined, and shown by avenir's shared
`macros/visual.html` from `visuals/catalog.json` (`config.extra.visuals_catalog`), the
same mechanism as the Swiss site. `visuals/slots.toml` lists every slot: the homepage
scene, one per area (programme card + area page hero) and the join page, each with
its page, prompt scene and alt text, plus the shared style block. A slot goes live
once `visuals/incoming/<slot>.png` exists (save the exact prompt as `<slot>.txt`):
`mise run visuals` encodes AVIF/WebP/JPEG at 600/960/1536 px (ImageMagick), writes
the catalogue and records tool, date, checksum and sizes in `visuals/provenance.json`.
Check the alt text against the picture before committing.

## Forms

Newsletter (join page), contact form and chapter enquiry post to the Swiss chapter's
form handler (`die-zukunft.ch/worker-forms`, `config.extra.forms_api`), which
allow-lists this origin and tags records `site: "world"` (plus `country`, and
`topic: "chapter"` for enquiries). The CSP allows `connect-src https://api.die-zukunft.ch`.


## Verification

`mise run build` and `mise run check` pass (25 pages). Desktop, phone and dark mode
were checked in Chrome (Playwright) side by side with die-zukunft.ch/en. Also checked:
the menu overlay and search, pins, and no console errors on the main page types.
