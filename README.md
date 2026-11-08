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
- `macros/nav.html` and `macros/footer.html` are avenir's macros with world links.
- `index.html` uses the Swiss homepage layers (lede, layer heads, pillar grid,
  tiles, join). `page.html` and `programm.html` are avenir's templates without the
  Zukunftslabor evidence blocks.

**When avenir's base.html, nav or footer change, port the change here.**
Otherwise the two sites drift apart again.

Hex map (in `base.html`): the same address as the Swiss site for the same topic:
`0x00` home, `0x01` vision, `0x02` program, `0x03` join, `0x10` manifesto,
`0x11` beyond-left-right, `0x20`–`0x2B` the twelve areas (see `content/_index.md`
`hex`), `0x40` people, `0x41` contact, `0xF0` legal, `0xF1` privacy, `0xF2` info.
Stability rule: never renumber.

The original AI-generated image and exact prompt are in `visuals/incoming/`.
`visuals/provenance.json` records the tool, date, checksum and delivery sizes.
Rebuild its web assets with `python3 scripts/build_visuals.py` (ImageMagick with
AVIF/WebP support). The scene is visibly labelled as imagined and AI-generated.
The social card has an editable SVG source in `assets/og-en.svg`; export with a
full SVG renderer (librsvg or Inkscape) and installed Clash Display/Switzer fonts.
The native favicon source is `static/favicon.svg`.

## Verification

`mise run build` and `mise run check` pass (22 pages). Desktop, phone and dark mode
were checked in Chrome (Playwright) side by side with die-zukunft.ch/en. Also checked:
the menu overlay and search, pins, and no console errors on the main page types.
