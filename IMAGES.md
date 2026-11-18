# Image brief for Grand Hill

## Responsive image review — November 18, 2026

Finishes category image now uses the textured stucco/control-joint photograph (`finishes-stucco-and-eifs.jpg`, also saved as `finishes.jpg`), replacing the pressure-washing lead. Pressure washing remains its own scope image. Occupied-building scope crops favor the right-hand protected work zone; commercial flooring crops favor the lower floor area.

## Service detail images — completed November 2026

All 13 service-detail images are generated with the built-in image model and installed as JPEGs in `assets/img/services/`. Exact scene prompts are recorded in `assets/img/services/generation-prompts.json`. Painting uses painted spaces, preparation and protected occupied spaces; finishes uses distinct material and joint details, cleaning, coatings and wallcovering; interiors uses carpet tiles, repaired shelf mounting, a cashwrap counter and repeated shelving bays. Images are optimized without stretching and remain illustrative ambient imagery. The three service-page headers now load the existing category JPEGs as well.

## Homepage service images — completed November 2026

The finishes image was subsequently replaced to distinguish it from the painting card at desktop size. Built-in image-model prompt: photorealistic 4:3 close-up of a pressure-washer lance cleaning a cool-gray exterior concrete walkway beside a pale stucco building; realistic fan spray centered within the wide-crop band; natural daylight; no people, logos, text or dramatic before/after line. Saved as `assets/img/services/finishes.jpg`; shared service imagery and alt text updated.

Generated with the built-in image model and saved at 1600×1200 in `assets/img/services/painting.jpg`, `finishes.jpg`, and `interiors.jpg`. The generator uses these images for the homepage cards and shared service-page slots. These are illustrative scenes, not documented Grand Hill projects.

Prompt set: single photorealistic 4:3 architectural editorial photographs; warm white, gray and charcoal palette; natural Florida daylight; straight verticals; main subjects kept within the central band for wide crops; no people, tools, branding, text or watermarks. Painting: freshly painted two-story Florida apartment exterior with warm-white stucco, taupe trim, crisp balconies and dark windows. Finishes: close facade detail with warm-white stucco, precise corner, sealed charcoal window and control joint. Interiors: finished empty retail space with pale oak-tone commercial flooring, minimal shelving and cashwrap counter.

## Home carousel — November 2026

Four illustrative images generated with the built-in image generation tool, stored in `assets/img/hero-{exterior,craft,interior,detail}.jpg`. These are ambient illustrations, not Grand Hill projects or employees.

Prompt set: photorealistic architectural photographs, landscape 16:9, warm white / gray / charcoal palette, natural daylight, straight verticals, quiet space on the left for copy, no logos, text or watermarks. Scenes: (1) finished low-rise Florida commercial stucco exterior with restrained landscaping in morning light; (2) painter carefully rolling a wall beside a masked window, protected floor; (3) empty finished commercial interior with pale oak-tone flooring and windows on the right; (4) sunlit stucco corner and recessed charcoal window with geometric shadows.

The home carousel uses a seven-second interval and 1.6-second opacity crossfade, manual image selection and pause/play. Reduced motion and data saving disable automatic playback initially. Images beyond the first load on demand. The previous still and optional video assets remain available but are no longer used by the home hero.

Painter image edited with the built-in image model: add a fluorescent yellow-green mesh safety vest over the white shirt with silver reflective torso and shoulder bands; preserve the person, pose, room, lighting and composition. The illustration does not establish safety certification or legal compliance.

Follow-up edit with the built-in image model: replace the gray baseball cap with a fitted white construction hard hat, preserving the reflective vest, identity, pose, lighting and room. Saved to `assets/img/hero-craft.jpg` for the carousel.

The branding variation was rejected. The carousel uses the unbranded version with the white hard hat and reflective safety vest in `assets/img/hero-craft.jpg`.

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
