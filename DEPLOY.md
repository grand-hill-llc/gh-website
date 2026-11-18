# Review and deploy: Grand Hill website

## 1. Review (before pushing)
Run locally: `npm run gen && npm run check && npm start`, then open http://localhost:8080.

Review at 1440 px and 375 px:
- [ ] Home: hero carousel, 4 service cards, "Recent work", quote band
- [ ] /services/ and the four service pages (photos, scope cards, related links)
- [ ] /about/ and /contact/ (form fields, labels, error states)
- [ ] Footer on every page: email, Instagram, "Team login", no phone
- [ ] Tab through each page: visible focus, skip link, carousel pause button
- [ ] Copy: no placeholder text, no credit to third parties, claims are true (licensing, insurance, years)
- [ ] `npm run check` reports 0 errors

Known warnings (not blocking): none (all images are WebP; `npm run check` warns above 400 KB).

## 2. Push
```
git status
git push origin main
```
(The sandbox cannot push; run it from your own Terminal.)

## 3. Netlify (first deploy)
1. Netlify, Add new site, Import from GitHub, repo `grandhill/gh-website`.
2. Build command: leave empty. Publish directory: `.` (already in `netlify.toml`).
3. Deploy. Check the `*.netlify.app` URL against the review list above.
4. Site configuration, Forms: confirm the `quote` form is detected; add a form notification email (info@grandhillcorp.com). Send one test submission and confirm the thank-you page and the email.
5. Domain management: add `grandhillcorp.com` and `www.grandhillcorp.com` (apex as primary). The domain uses custom nameservers at Namecheap: add the Netlify records there and keep the existing MX records so email keeps working. Leave `app.grandhillcorp.com` pointing to the backoffice site.
6. Enable HTTPS (Let's Encrypt) once DNS resolves.

## 4. After launch
- [ ] Open the live site: all pages, form test, `/robots.txt`, `/sitemap.xml`
- [ ] Google Search Console: verify the domain, submit `sitemap.xml` (results take 4 to 8 weeks)
- [ ] Google Business Profile: set the website to https://grandhillcorp.com
- [ ] Share preview: check the Open Graph card in a link debugger
- [ ] Confirm the "Team login" link opens the backoffice login
