// Pre-deploy check: internal links, assets, titles, descriptions, canonicals, alt text, sitemap, leftovers.
// Usage: npm run check   (Node 18+, no dependencies)
import { readdirSync, readFileSync, statSync, existsSync } from "node:fs";
import { join, extname } from "node:path";

const root = process.cwd();
const skip = new Set([".git", "node_modules", "_inbox", "scripts", "tools"]);
const pages = [];
(function walk(d) {
  for (const n of readdirSync(d)) {
    if (skip.has(n)) continue;
    const f = join(d, n);
    if (statSync(f).isDirectory()) walk(f);
    else if (n.endsWith(".html")) pages.push(f);
  }
})(root);

const errors = [], warns = [];
const err = (p, m) => errors.push(`${p.replace(root, "")}: ${m}`);
const warn = (p, m) => warns.push(`${p.replace(root, "")}: ${m}`);
const target = (u) => {
  const path = u.split("#")[0].split("?")[0];
  if (path.endsWith("/")) return join(root, path, "index.html");
  return join(root, path);
};
const titles = new Map();

for (const f of pages) {
  const h = readFileSync(f, "utf8");
  const noindex = /<meta name="robots" content="[^"]*noindex/.test(h);
  const t = (h.match(/<title>([^<]*)<\/title>/) || [])[1];
  const d = (h.match(/<meta name="description" content="([^"]*)"/) || [])[1];
  if (!t) err(f, "missing <title>"); else {
    if (t.length > 65) warn(f, `title ${t.length} chars (>65)`);
    if (titles.has(t)) err(f, `duplicate title with ${titles.get(t)}`); else titles.set(t, f.replace(root, ""));
  }
  if (!noindex) {
    if (!d) err(f, "missing meta description");
    else if (d.length > 165) warn(f, `description ${d.length} chars (>165)`);
    if (!/<link rel="canonical"/.test(h)) err(f, "missing canonical");
  }
  if ((h.match(/<h1[ >]/g) || []).length !== 1) err(f, "needs exactly one <h1>");
  for (const m of h.matchAll(/<img\b[^>]*>/g)) {
    if (!/\balt=/.test(m[0])) err(f, "img without alt: " + m[0].slice(0, 80));
    if (!/\bwidth=/.test(m[0]) || !/\bheight=/.test(m[0])) warn(f, "img without width/height: " + (m[0].match(/src="([^"]*)"/) || [])[1]);
  }
  for (const m of h.matchAll(/(?:href|src)="(\/[^"]*)"/g)) {
    const u = m[1];
    if (u.startsWith("//")) continue;
    if (!existsSync(target(u))) err(f, `broken reference ${u}`);
  }
  for (const m of h.matchAll(/target="_blank"(?![^>]*rel="[^"]*noopener)/g)) err(f, "target=_blank without rel=noopener");
  if (/lorem|placeholder|sample project|TODO/i.test(h.replace(/placeholder="[^"]*"/g, ""))) warn(f, "contains placeholder-like text");
  if (/\bashton\b/i.test(h)) err(f, "mentions Ashton (decision: no credit)");
}

// sitemap
const sm = readFileSync(join(root, "sitemap.xml"), "utf8");
for (const m of sm.matchAll(/<loc>https:\/\/grandhillcorp\.com([^<]*)<\/loc>/g))
  if (!existsSync(target(m[1]))) err("sitemap.xml", `lists missing page ${m[1]}`);
for (const f of pages) {
  const u = f.replace(root, "").replace(/index\.html$/, "");
  const noindex = /noindex/.test(readFileSync(f, "utf8"));
  if (!noindex && u !== "/404.html" && !sm.includes(`grandhillcorp.com${u}<`)) warn("sitemap.xml", `missing indexable page ${u}`);
}

// unused / oversized images
const imgDir = join(root, "assets/img");
(function walk(d) {
  for (const n of readdirSync(d)) {
    const f = join(d, n);
    if (statSync(f).isDirectory()) { walk(f); continue; }
    if (![".jpg", ".jpeg", ".png", ".webp"].includes(extname(n))) continue;
    const kb = statSync(f).size / 1024;
    if (kb > 400) warn(f, `${Math.round(kb)} KB image (>400 KB)`);
  }
})(imgDir);

console.log(`Checked ${pages.length} pages.`);
warns.forEach((w) => console.log("WARN  " + w));
errors.forEach((e) => console.log("ERROR " + e));
console.log(`${errors.length} errors, ${warns.length} warnings.`);
process.exit(errors.length ? 1 : 0);
