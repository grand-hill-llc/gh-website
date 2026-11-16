# Grand Hill website

Static, English-only site for Grand Hill, LLC. Plain HTML and CSS built on the Grand Hill design system (`gh-` components, tokens in `assets/css/tokens.css`). No build step.

## Preview locally
```
npm start        # http://localhost:8080  (Node 18+)
```
The preview server accepts the quote form POST so the form flow can be tested locally. Real submissions are handled by Netlify Forms once deployed.

## Structure
- `index.html`, `services/`, `projects/`, `about/`, `contact/`, `thank-you/`, `404.html`
- `insights/` is built but hidden (noindex, not linked, not in `sitemap.xml`)
- `assets/css` (tokens, components, site), `assets/js/site.js`, `assets/logo` (GH logo set), `assets/img`
- `netlify.toml`, `sitemap.xml`, `robots.txt`

## Hero photo
The hero loads `assets/img/hero.webp` (1920x1080, under ~250 KB) under the design system's flat charcoal veil. If the file is missing, the hero falls back to plain charcoal. A stock photo (Unsplash License) is acceptable only as a stand-in: the brief calls for real project photography, so replace it with real work (credited) before launch.

## Before launch (open items)
Run `npm run check:placeholders` to list what is left. Remaining:
1. Real phone number and public email (footer and contact page; email currently `info@grandhillcorp.com`).
2. First featured project: photos (WebP/AVIF with width/height), scope, credit. Home "Featured project" and `projects/`.
3. A real, permitted testimonial (Home).
4. Duplicate `projects/sample-project/` for each project, then add it to `sitemap.xml` and remove its noindex tag.
5. Netlify: add the form notification email (Site configuration, Forms, Form notifications) for the `quote` form.
6. Leadership currently sits on About; move to Home if leadership decides so.

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
