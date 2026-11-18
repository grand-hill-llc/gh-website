# Grand Hill website

Static, English-only site for Grand Hill, LLC. Plain HTML and CSS built on the Grand Hill design system (`gh-` components, tokens in `assets/css/tokens.css`). No build step.

## Preview locally
```
npm start        # http://localhost:8080  (Node 18+)
```
The preview server accepts the quote form POST so the form flow can be tested locally. Real submissions are handled by Netlify Forms once deployed.

## Structure
- `IMAGES.md` image brief (slots, sizes, style, honesty rule)
- `index.html`, `services/` (commercial-painting, residential-painting, finishes-and-surface-care, interiors-and-flooring), `about/`, `contact/`, `thank-you/`, `404.html`
- `projects/` is built only when `SHOW_PROJECTS = True`; `insights/` is built but hidden (noindex, not linked, not in `sitemap.xml`)
- `assets/css` (tokens, components, site), `assets/js/site.js`, `assets/logo`, `assets/img` (`hero-*.jpg` carousel, `projects/` real photos, `services/`)
- `netlify.toml`, `sitemap.xml`, `robots.txt`
- `DEPLOY.md` review checklist and deploy steps

## Checks
```
npm run build    # regenerate pages from tools/gen.py
npm run check    # links, assets, titles, descriptions, canonicals, alt text, sitemap
```
Run both before every push. `npm run check:placeholders` lists service photo slots still empty.

## Open items before launch
1. Public email (currently `info@grandhillcorp.com`). Phone stays hidden on purpose (`PHONE = None`).
2. Facebook Page URL (`FACEBOOK` in `tools/gen.py`). Instagram and the "Team login" link (`BACKOFFICE`) are already in the footer.
3. Real hero photos for Commercial and Residential (current heroes are generated), plus project name, city and year for captions.
4. A real, permitted testimonial (`SHOW_PROOF`).
5. Attorney review of Privacy and Terms text.
6. Netlify: add the form notification email for the `quote` form (see `DEPLOY.md`).

## Hero background video
The home hero can play a muted, looping background video: `assets/video/hero.mp4` (required) and `assets/video/hero.webm` (optional). Build both from source clips with `tools/make-hero-video.sh clip1.mp4 clip2.mp4` (needs ffmpeg). Footage must be real or licensed (area views, skylines, streets), never presented as a Grand Hill project. If the files are missing the hero shows the still image (`hero.webp`, also the video poster). The video is skipped for visitors with reduced motion, data saver, slow connections or small screens, and a pause button is shown while it plays (WCAG 2.2.2).

## Service photos

Each service has a photo slot (home cards and Services page). Add the real shot as `assets/img/services/painting.webp`, `finishes.webp` and `interiors.webp` (4:3, 1600x1200, under about 200 KB). Until a file exists a placeholder is shown; once it exists the photo replaces it automatically. Write a specific `alt` in `gen.py` (`SVC_PHOTOS`) when you swap a photo, and check it matches the real image. `npm run check:placeholders` lists the service photos still missing.

Each scope card on a service page has its own photo slot (4:3, 1600x1200, under about 200 KB). File names, in `assets/img/services/`:

- `finishes-caulking-and-sealing.webp`
- `finishes-pressure-washing.webp`
- `finishes-protective-and-specialty-coatings.webp`
- `finishes-stucco-and-eifs.webp`
- `finishes-wallcoverings.webp`
- `interiors-cashwrap-and-fixture-installation.webp`
- `interiors-commercial-flooring.webp`
- `interiors-fixture-and-component-roll-outs.webp`
- `interiors-interior-wall-and-fixture-repairs.webp`
- `painting-exterior-painting.webp`
- `painting-interior-painting.webp`
- `painting-occupied-buildings.webp`
- `painting-surface-preparation-and-repair.webp`

They show placeholders until the files exist. A project gallery can be added later, when there are real projects to show.

## Regenerating the pages

The pages are generated from `tools/gen.py` (Python 3, no dependencies). Edit copy and services there, then run from the project root:

```
python3 tools/gen.py .
```

Do not edit the generated `.html` files by hand: the next run overwrites them. Styles live in `assets/css/` and scripts in `assets/js/`.

## Launch switches (top of `tools/gen.py`)

- `PHONE`: set the real number and it appears in the footer and on the contact page. Until then it is hidden.
- `SHOW_PROJECTS`: set to `True` once there are real projects. It adds Projects to the menu, footer and sitemap, and builds the Projects pages.
- `SHOW_PROOF`: set to `True` once there is a real featured project and a real, authorized testimonial for the home page.

After changing a switch, run `python3 tools/gen.py .`
