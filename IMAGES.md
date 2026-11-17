# Image brief for Grand Hill

Context for whoever (or whatever tool) produces the remaining images. The site is built; every image below has a slot that fills itself when the file exists. No code changes are needed except the `alt` text (see "Alt text").

## Honesty rule (important)
Grand Hill has no finished project portfolio yet. Generated or stock images are **ambient imagery only**:
- Never place them in Projects, the gallery, testimonials or About/team areas.
- Never caption or describe them as "our work", "our project" or a named job.
- Alt text describes what the picture shows, nothing more.
- Replace each one with a real, credited project photo as soon as one exists.

## Style (from the Grand Hill design system)
- Real-looking commercial and residential Florida settings: retail units, office interiors, stucco buildings, apartment exteriors.
- Natural daylight, architectural framing, vertical lines corrected, shallow tidy compositions.
- Palette stays sober: whites, warm grays, stucco, charcoal; no saturated or decorative color.
- No people, no hard hats, no handshakes, no logos, no readable signs or text, no brand names.
- Looks finished and clean, not a job in chaos. No before/after, no tools in frame unless the slot says so.
- Keep the main subject inside the central horizontal band: cards crop to 2:1 and some tiles to 16:9.

## File spec
- Folder: `assets/img/services/`
- Format: WebP, **4:3, 1600x1200**, under about 200 KB each.
- File name must match exactly (below). Once the file exists it replaces the placeholder automatically.
- Check what is still missing: `npm run check:placeholders`.

## Service hero images (3)
Used on the home service cards, the Services page and as the hero of each service page.

| File | Show |
|---|---|
| `painting.webp` | Freshly painted exterior of a commercial building, clean edges, Florida light |
| `finishes.webp` | Close view of a smooth finished stucco wall on a commercial building |
| `interiors.webp` | Bright retail interior with new flooring and installed fixtures, empty of people |

## Sub-service images (13)
One per scope card on each service page.

| File | Show |
|---|---|
| `painting-interior-painting.webp` | Empty office or retail floor with freshly painted walls, even color |
| `painting-exterior-painting.webp` | Painted building exterior (plaza or apartments) under blue sky |
| `painting-surface-preparation-and-repair.webp` | Wall surface smooth, patched and primed, ready for paint (no tools) |
| `painting-occupied-buildings.webp` | Clean, orderly open commercial space ready for business, no people |
| `finishes-stucco-and-eifs.webp` | Detail of a uniform stucco facade with a clean control joint |
| `finishes-pressure-washing.webp` | Clean exterior concrete and wall surface, bright and spotless |
| `finishes-caulking-and-sealing.webp` | Neat sealed joint line at a window or facade edge, macro-style |
| `finishes-protective-and-specialty-coatings.webp` | Smooth coated floor or wall surface with a subtle sheen |
| `finishes-wallcoverings.webp` | Wallcovering installed on an interior wall, seams and edges clean |
| `interiors-commercial-flooring.webp` | Commercial floor (tile or vinyl), wide angle, clean seams, no people |
| `interiors-interior-wall-and-fixture-repairs.webp` | Repaired and refinished interior wall next to a fixture, ready for reopening |
| `interiors-cashwrap-and-fixture-installation.webp` | Empty retail cashwrap counter and shelving installed, square and secure |
| `interiors-fixture-and-component-roll-outs.webp` | Repeating row of identical retail fixtures, even spacing, consistent look |

## Alt text
- Sub-service images take their alt from the card title (for example "Interior painting"). Do not add "by Grand Hill".
- The three hero images use `SVC_PHOTOS` in `tools/gen.py`. Rewrite each description so it matches the actual image, then run `python3 tools/gen.py .`.

## Home hero
`assets/img/hero.webp` (1920x1080, under about 250 KB) is the home hero still and the poster of the optional background video (see README, "Hero background video"). The current file is a stand-in and should be replaced.
