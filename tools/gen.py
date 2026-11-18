#!/usr/bin/env python3
"""Generates the static pages for the Grand Hill site. Usage: gen.py <site_dir>"""
import re, os, sys, html, json, datetime

ROOT = sys.argv[1]
SITE = "https://grandhillcorp.com"
EMAIL = "info@grandhillcorp.com"          # TODO: confirm public inbox
PHONE = None                              # TODO: set the real phone number; it then appears in footer + contact
SHOW_PROJECTS = False                     # set True once there are real projects: adds Projects to menu, footer, sitemap
SHOW_PROOF = False                        # set True once there is a real featured project and a real, authorized testimonial on the home page
OG = "/assets/img/og-image.png"

ARROW = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12h16M14 6l6 6-6 6"/></svg>'
ARROW_UR = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 17L17 7M8 7h9v9"/></svg>'
CHECK = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M8 12.5l3 3 5-6"/></svg>'

SLOT = ('<div class="gh-photo-slot" aria-hidden="true"><svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice">'
        '<rect class="pl" width="400" height="300"/>'
        '<path class="ln" d="M40 260h320M70 260V90h120v170M190 260V60h140v200M90 120h80M90 160h80M90 200h80M210 100h100M210 140h100M210 180h100M210 220h100"/>'
        '</svg></div>')

def svc_photo(key, label, alt, cls="gh-service-photo"):
    """Placeholder until /assets/img/services/<key>.webp (1600x1200) exists; the real photo then covers it."""
    ext = "jpg" if os.path.exists(os.path.join(ROOT, "assets", "img", "services", key + ".jpg")) else "webp"
    exists = os.path.exists(os.path.join(ROOT, "assets", "img", "services", key + "." + ext))
    placeholder = "" if exists else SLOT + f'<span class="gh-photo-caption">Photo placeholder &middot; {label}</span>'
    return (f'<div class="gh-photo {cls}">{placeholder}'
            f'<img class="gh-photo-img" src="/assets/img/services/{key}.{ext}" alt="{alt}" width="1600" height="1200" loading="lazy" decoding="async" onerror="this.remove()"></div>')

SVC_PHOTOS = {
  "painting": ("Painting", "Warm-white Florida apartment exterior with crisp trim and dark windows"),
  "finishes": ("Finishes", "Textured ivory stucco facade with a recessed control joint and crisp corner"),
  "interiors": ("Interiors", "Retail interior with new flooring and installed fixtures"),
}

CRUMB = {"/services/":"Services","/services/painting/":"Painting","/services/finishes-and-surface-care/":"Finishes and surface care","/services/interiors-and-flooring/":"Interiors and flooring","/commercial-painting/":"Commercial painting","/residential-painting/":"Residential painting","/projects/":"Projects","/about/":"About","/contact/":"Contact"}
NAV = [("Services", "/services/"), ("Commercial", "/commercial-painting/"), ("Residential", "/residential-painting/")] + ([("Projects", "/projects/")] if SHOW_PROJECTS else []) + [("About", "/about/"), ("Contact", "/contact/")]


# ---------------------------------------------------------------- SERVICES
SERVICES = [
  dict(slug="painting", key="painting", name="Painting", path="/services/painting/",
       title="Interior & Exterior Painting in Florida | Grand Hill",
       desc="Commercial and residential painting contractor in Florida: surface preparation, interior and exterior coats, and scheduling around occupied buildings.",
       h1="Commercial and residential painting.",
       short="Interior and exterior painting for homes, offices, retail, multifamily and institutional buildings.",
       lede="Every project starts with a walkthrough and a written scope. Surfaces are prepared, documented and inspected before the final coat, and the work is sequenced around the people using the building.",
       items=["Interior painting", "Exterior painting", "Surface preparation and repair", "Scheduling around occupied buildings"],
       stype="Painting"),
  dict(slug="finishes-and-surface-care", key="finishes", name="Finishes & surface care", path="/services/finishes-and-surface-care/",
       title="Stucco, EIFS, Pressure Washing & Coatings | Grand Hill",
       desc="Stucco and EIFS repair and installation, pressure washing, caulking, protective coatings and wallcoverings for commercial and residential projects across Florida.",
       h1="Stucco and coatings that stand up to Florida.",
       short="Stucco and EIFS, pressure washing, protective coatings and wallcoverings, applied to the architect's intent.",
       lede="Finishes are what people see and what the weather tests. We prepare each surface so the finish lasts, and we specify and apply it with attention to material, color and the architect's intent.",
       items=["Stucco and EIFS repair and installation", "Pressure washing", "Caulking and sealing", "Protective and specialty coatings", "Wallcoverings"],
       stype="Architectural finishes and surface care"),
  dict(slug="interiors-and-flooring", key="interiors", name="Interiors & flooring", path="/services/interiors-and-flooring/",
       title="Commercial Flooring & Interior Repairs | Grand Hill",
       desc="Flooring, interior repairs and store fixture installs for retail and commercial spaces in Florida, scheduled around opening hours with one point of contact.",
       h1="Flooring and interiors, ready for opening day.",
       short="Commercial flooring, interior wall and fixture repairs, and fixture installs, scheduled around your operations.",
       lede="Flooring and interior work for retail and commercial spaces, planned around opening hours and delivered with one point of contact at Grand Hill. Repairs and installs are documented and inspected before handoff.",
       items=["Flooring: VCT, LVP, carpet tile, ceramic tile and welded-seam sheet vinyl", "Interior wall and fixture repairs", "Cashwrap and fixture installation", "Fixture and component roll-outs"],
       stype="Commercial flooring and interior repairs"),
]


def header(current, transparent=False, here=""):
    logo = "reversed-transparent" if transparent else "primary"
    cls = "gh-header gh-header-transparent" if transparent else "gh-header"
    chev = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>'
    def sub():
        items = '<a href="/services/"%s>All services</a>' % (' aria-current="page"' if here == "/services/" else "")
        items += "".join('<a href="%s"%s>%s</a>' % (x["path"], ' aria-current="page"' if x["path"] == here else "", x["name"].replace("&", "&amp;")) for x in SERVICES)
        return ('<div class="gh-subnav" id="sub-services"><div class="gh-subnav-panel">' + items + '</div></div>')
    parts = []
    for t, h in NAV:
        a = '<a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if h == current else "", t)
        if h == "/services/":
            a = ('<div class="gh-nav-item has-sub">' + a +
                 '<button class="gh-sub-toggle" type="button" aria-expanded="false" aria-controls="sub-services" aria-label="Services menu">' + chev + '</button>' + sub() + '</div>')
        parts.append(a)
    links = "".join(parts)
    return f'''<header class="{cls}">
  <div class="gh-container">
    <div class="gh-header-bar">
      <a class="gh-logo" href="/" aria-label="Grand Hill, home"><img src="/assets/logo/grand-hill-logo-{logo}.svg" alt="Grand Hill" width="170" height="36"></a>
      <nav class="gh-nav" id="site-nav" aria-label="Main">{links}<a class="gh-btn gh-btn-primary gh-btn-sm gh-nav-cta" href="/contact/">Request a quote</a></nav>
      <div class="gh-header-actions">
        <a class="gh-btn gh-btn-primary gh-btn-sm" href="/contact/">Request a quote</a>
        <button class="gh-menu-btn" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="Open menu">
          <svg class="i-menu" viewBox="0 0 24 24" aria-hidden="true"><path d="M3 7h18M3 12h18M3 17h18"/></svg>
          <svg class="i-close" viewBox="0 0 24 24" aria-hidden="true" hidden><path d="M5 5l14 14M19 5L5 19"/></svg>
        </button>
      </div>
    </div>
  </div>
</header>'''


def quote_band():
    return f'''<section class="gh-cta-band" aria-labelledby="cta-h">
  <div class="gh-container"><div class="gh-cta-band-inner">
    <div><p class="gh-eyebrow">Request a quote</p><h2 class="gh-h1" id="cta-h">Tell us about your project.</h2>
    <p>Share the scope, location and timeline. We respond within one business day.</p></div>
    <a class="gh-btn gh-btn-primary" href="/contact/">Request a quote {ARROW}</a>
  </div></div>
</section>'''


def footer():
    return f'''<footer class="gh-footer">
  <div class="gh-container">
    <div class="gh-footer-top">
      <div><a class="gh-footer-logo" href="/" aria-label="Grand Hill, home"><img src="/assets/logo/grand-hill-logo-reversed-transparent.svg" alt="Grand Hill" width="189" height="40"></a>
        <p class="gh-footer-tag">Precision in Every Finish.</p></div>
      <div><h4>Contact</h4><ul>{("<li>" + PHONE + "</li>") if PHONE else ""}<li><a href="mailto:{EMAIL}">{EMAIL}</a></li></ul></div>
      <div><h4>Services</h4><ul><li><a href="/services/painting/">Painting</a></li><li><a href="/services/finishes-and-surface-care/">Finishes &amp; surface care</a></li><li><a href="/services/interiors-and-flooring/">Interiors &amp; flooring</a></li><li>Serving Florida</li></ul></div>
      <div><h4>Company</h4><ul><li><a href="/services/">Services</a></li><li><a href="/commercial-painting/">Commercial</a></li><li><a href="/residential-painting/">Residential</a></li>{'<li><a href="/projects/">Projects</a></li>' if SHOW_PROJECTS else ""}<li><a href="/about/">About</a></li><li><a href="/contact/">Contact</a></li></ul></div>
    </div>
    <div class="gh-footer-bottom"><span>&copy; 2026 Grand Hill, LLC. All rights reserved.</span><span class="gh-footer-legal">Grand Hill, LLC</span></div>
  </div>
</footer>'''


def page(path, title, desc, body, current="", transparent=False, noindex=False, extra_head="", scripts=True):
    url = SITE + path
    crumbs = ""
    if not noindex and path != "/":
        label = CRUMB.get(path, title.split("|")[0].strip())
        trail = [("Home", SITE+"/")]
        if path.startswith("/services/") and path != "/services/":
            trail.append(("Services", SITE+"/services/"))
        trail.append((label, url))
        crumbs = ('<script type="application/ld+json">' + json.dumps({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
            {"@type":"ListItem","position":i+1,"name":n,"item":u} for i,(n,u) in enumerate(trail)]}, separators=(",",":")) + '</script>\n')
        extra_head = crumbs + extra_head
    robots = '<meta name="robots" content="noindex, nofollow">\n' if noindex else ""
    doc = f'''<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc, quote=True)}">
{robots}<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:locale" content="en_US">
<meta property="og:site_name" content="Grand Hill">
<meta property="og:title" content="{html.escape(title, quote=True)}">
<meta property="og:description" content="{html.escape(desc, quote=True)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}{OG}">
<meta property="og:image:alt" content="Grand Hill, painting and finishes in Florida">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(title, quote=True)}">
<meta name="twitter:description" content="{html.escape(desc, quote=True)}">
<meta name="twitter:image" content="{SITE}{OG}">
<meta name="theme-color" content="#262B33">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<script>document.documentElement.classList.add("js")</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@300;400;500;600;700&family=Inter:wght@400;500;600&display=swap">
<link rel="stylesheet" href="/assets/css/tokens.css">
<link rel="stylesheet" href="/assets/css/components.css">
<link rel="stylesheet" href="/assets/css/site.css">
{extra_head}</head>
<body class="gh">
<a class="gh-skip" href="#main">Skip to content</a>
{body[0] if transparent else header(current, here=path) + body}
{footer()}
<script src="/assets/js/site.js" defer></script>
</body>
</html>
'''
    out = os.path.join(ROOT, path.lstrip("/"))
    if path.endswith("/"):
        out = os.path.join(out, "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write(doc)


def page_head(eyebrow, h1, lede):
    return f'''<section class="gh-page-head"><div class="gh-container">
  <p class="gh-eyebrow">{eyebrow}</p><h1 class="gh-h1">{h1}</h1><p class="gh-body-lg">{lede}</p>
</div></section>'''





# ---------------------------------------------------------------- HOME
home_hero = f'''<section class="gh-hero gh-inverse gh-on-image" data-hero-carousel aria-label="Painting and finishes inspiration">
  <div class="gh-photo" aria-hidden="true">
    {''.join(f'<img class="gh-hero-slide{" is-active" if i == 0 else ""}" {"src" if i == 0 else "data-src"}="/assets/img/hero-{name}.jpg" alt="" width="1672" height="941" {"fetchpriority=high" if i == 0 else ""}>' for i, name in enumerate(["exterior", "craft", "interior", "detail"]))}
    <div class="gh-hero-veil"></div>
  </div>
  <div class="gh-carousel-controls" hidden>
    <div class="gh-carousel-dots" role="group" aria-label="Choose background image">
      {''.join(f'<button type="button" data-hero-go="{i}" aria-label="Show {label}" aria-pressed="{"true" if i == 0 else "false"}"><span></span></button>' for i, label in enumerate(["building exterior", "painting detail", "commercial interior", "stucco detail"]))}
    </div>
    <button class="gh-carousel-pause" type="button" aria-label="Pause slideshow" aria-pressed="false">Pause</button>
  </div>
  <div class="gh-hero-inner">
    {header("", transparent=True)}
    <div class="gh-container gh-hero-wrap">
      <div class="gh-hero-main">
        <div class="gh-hero-body">
          <p class="gh-eyebrow">Precision in every finish.</p>
          <h1 class="gh-display">Commercial and residential painting in Florida.</h1>
          <p class="gh-body-lg">Interior and exterior painting and finishes for retail, offices and multifamily properties, and for homes. Planned around your schedule and inspected before handoff.</p>
          <div class="gh-hero-actions"><a class="gh-btn gh-btn-primary" href="/contact/">Request a quote {ARROW}</a></div>
        </div>
      </div>
    </div>
  </div>
</section>'''

proof_html = f'''<section class="gh-section" aria-labelledby="feat-h"><div class="gh-container">
  <div class="gh-section-head"><p class="gh-eyebrow">Featured project</p><h2 class="gh-h2" id="feat-h">Recent work.</h2></div>
  <div class="gh-featured" data-placeholder="featured-project">
    <a href="/projects/" class="gh-project" aria-label="View projects"><div class="gh-photo">{SLOT}<span class="gh-photo-caption">Photo placeholder</span></div></a>
    <div>
      <p class="gh-label">Location &middot; Scope</p>
      <h3 class="gh-h3">Featured project name</h3>
      <p>Short description of the project, the finish challenge and the result.</p>
      <ul class="gh-meta-list"><li><span>Client</span><span>To be added</span></li><li><span>Scope</span><span>To be added</span></li><li><span>Credit</span><span>To be added</span></li></ul>
      <a class="gh-link" href="/projects/">All projects {ARROW}</a>
      <p class="gh-placeholder-note">Placeholder. Replace with the first real project, with photos, scope and credit, before launch.</p>
    </div>
  </div>
</div></section>

<section class="gh-section gh-section-alt" aria-labelledby="test-h"><div class="gh-container">
  <h2 class="gh-label" id="test-h" style="margin-bottom:24px">Testimonials</h2>
  <figure class="gh-testimonial" data-placeholder="testimonial" style="margin:0">
    <div class="gh-testimonial-rule"></div>
    <blockquote>Client quote goes here.</blockquote>
    <figcaption><span class="gh-name">Client name</span><span class="gh-role">Title, company</span></figcaption>
    <p class="gh-placeholder-note">Placeholder. Use only a real quote, with the client's written permission, before launch.</p>
  </figure>
</div></section>
''' if SHOW_PROOF else ""

home_main = f'''<main id="main">
<section class="gh-section" aria-labelledby="who-h"><div class="gh-container"><div class="gh-two-col">
  <div><p class="gh-eyebrow">Who we are</p><h2 class="gh-h2" id="who-h" style="margin-top:16px">A finishing partner for commercial and residential work.</h2></div>
  <div class="gh-prose gh-who">
    <p class="gh-body-lg">Grand Hill is a Florida company focused on painting and finishes for commercial and residential projects. We deliver the work from the first walkthrough to the final handoff, on schedule and inspected, and we answer for every surface.</p>
    <p>Our team brings an architectural and engineering eye to material and color selection.</p>
    <p><a class="gh-link" href="/services/">Our services {ARROW}</a> &nbsp; <a class="gh-link" href="/about/">About Grand Hill {ARROW}</a></p>
  </div>
</div></div></section>

<section class="gh-section gh-section-alt" aria-labelledby="svc-h"><div class="gh-container">
  <div class="gh-section-head"><p class="gh-eyebrow">Services</p><h2 class="gh-h2" id="svc-h">Painting and finishes for every project.</h2></div>
  <div class="gh-cards-3">
    <article class="gh-service">{svc_photo("painting", *SVC_PHOTOS["painting"])}<h3 class="gh-h4">Painting</h3>
      <p>Commercial and residential interior and exterior painting. Our anchor service, planned around your schedule and the occupants of the building.</p>
      <a class="gh-link" href="/services/painting/">Painting {ARROW}</a></article>
    <article class="gh-service">{svc_photo("finishes", *SVC_PHOTOS["finishes"])}<h3 class="gh-h4">Finishes &amp; surface care</h3>
      <p>Stucco and EIFS, pressure washing, protective coatings and wallcoverings, specified and applied to the architect's intent.</p>
      <a class="gh-link" href="/services/finishes-and-surface-care/">Finishes {ARROW}</a></article>
    <article class="gh-service">{svc_photo("interiors", *SVC_PHOTOS["interiors"])}<h3 class="gh-h4">Interiors &amp; flooring</h3>
      <p>Commercial flooring, interior wall and fixture repairs, and fixture installs, scheduled around your operations.</p>
      <a class="gh-link" href="/services/interiors-and-flooring/">Interiors {ARROW}</a></article>
  </div>
</div></section>

<section class="gh-section" aria-labelledby="why-h"><div class="gh-container">
  <div class="gh-section-head"><p class="gh-eyebrow">Why Grand Hill</p><h2 class="gh-h2" id="why-h">Why work with Grand Hill.</h2></div>
  <ul class="gh-why">
    <li><svg class="gh-icon gh-why-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="8" r="4"/><path d="M4 21v-2a5 5 0 0 1 5-5h6a5 5 0 0 1 5 5v2"/></svg><h3>One point of contact</h3><p>One team from the first walkthrough to the final handoff, so you always know who answers for the work.</p></li>
    <li><svg class="gh-icon gh-why-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/></svg><h3>Planned around your operations</h3><p>Work is sequenced around opening hours, tenants and residents, so the space keeps working.</p></li>
    <li><svg class="gh-icon gh-why-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1L7 17M17 7l2.1-2.1"/></svg><h3>Built for Florida</h3><p>Preparation and coatings are chosen for Florida's sun, humidity and rain, so finishes last.</p></li>
    <li><svg class="gh-icon gh-why-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg><h3>Consistent across locations</h3><p>The same standard on every site, whether it is a single home or a roll-out across several stores.</p></li>
  </ul>
</div></section>

<section class="gh-section gh-section-alt" aria-labelledby="process-h"><div class="gh-container">
  <div class="gh-section-head"><p class="gh-eyebrow">Our process</p><h2 class="gh-h2" id="process-h">How we deliver every project.</h2></div>
  <ol class="gh-method gh-method-plain" aria-label="How every project runs">
    <li><h3>Prepare</h3><p>Surfaces are cleaned, repaired and primed to specification.</p></li>
    <li><h3>Document</h3><p>Conditions, products and sign-offs are recorded.</p></li>
    <li><h3>Inspect</h3><p>Each scope is checked against the specification before handoff.</p></li>
  </ol>
</div></section>

{proof_html}
</main>
{quote_band()}'''


HOME_SCHEMA = {"@context":"https://schema.org","@graph":[
  {"@type":["HousePainter","LocalBusiness"],"@id":SITE+"/#business","name":"Grand Hill","legalName":"Grand Hill, LLC","url":SITE+"/",
   "logo":SITE+"/assets/logo/grand-hill-logo-primary.svg","image":SITE+OG,
   "description":"Painting and finishes for commercial and residential projects across Florida.",
   "slogan":"Precision in every finish.","areaServed":{"@type":"State","name":"Florida"},
   "knowsAbout":["Commercial painting","Residential painting","Exterior painting","Interior painting","Stucco","EIFS","Pressure washing","Protective coatings","Wallcoverings","Commercial flooring"]},
  {"@type":"WebSite","@id":SITE+"/#website","url":SITE+"/","name":"Grand Hill","publisher":{"@id":SITE+"/#business"},"inLanguage":"en-US"}]}
HOME_HEAD = ('<link rel="preload" as="image" href="/assets/img/hero.webp" fetchpriority="high">\n'
             '<script type="application/ld+json">' + json.dumps(HOME_SCHEMA, separators=(",",":")) + '</script>\n')
page("/", "Commercial & Residential Painting in Florida | Grand Hill",
     "Commercial and residential painting and finishes across Florida, for retail, offices, multifamily and homes. Planned around your schedule, inspected before handoff.",
     (home_hero + home_main,), transparent=True,
     extra_head=HOME_HEAD)

PAINT_NAMES = {x["slug"]: x["name"] for x in SERVICES}

DETAILS = {
  "painting": [
    ("Interior painting", "Offices, retail floors, common areas and residences, finished to one consistent standard."),
    ("Exterior painting", "Exterior surfaces prepared and coated to stand up to Florida sun, humidity and rain."),
    ("Surface preparation and repair", "Cleaning, patching and priming before any coat goes on."),
    ("Occupied buildings", "Work sequenced around opening hours, tenants and residents."),
  ],
  "finishes-and-surface-care": [
    ("Stucco and EIFS", "Repair and installation, with patches and new work matched to the existing finish."),
    ("Pressure washing", "Exterior cleaning to prepare surfaces for coating or restore their appearance."),
    ("Caulking and sealing", "Joints and openings sealed to keep water out and finishes intact."),
    ("Protective and specialty coatings", "Coatings selected for moisture, wear and corrosion resistance."),
    ("Wallcoverings", "Installed to specification, with seams and edges checked before handoff."),
  ],
  "interiors-and-flooring": [
    ("Commercial flooring", "VCT, LVP, carpet tile, ceramic tile and welded-seam sheet vinyl, installed and repaired."),
    ("Interior wall and fixture repairs", "Patching, refinishing and repair of walls and fixtures, ready for reopening."),
    ("Cashwrap and fixture installation", "Counters, shelving and display fixtures installed and secured to plan."),
    ("Fixture and component roll-outs", "Repeatable installs across multiple stores, scheduled and reported by location."),
  ],
}

def svc_ld(x):
    cat = {"@type":"OfferCatalog","name":x["name"].replace("&","and")+" services","itemListElement":[
        {"@type":"Offer","itemOffered":{"@type":"Service","name":t,"description":d}} for t,d in DETAILS[x["slug"]]]}
    return '<script type="application/ld+json">' + json.dumps({"@context":"https://schema.org","@type":"Service","name":x["name"].replace("&","and"),"serviceType":x["stype"],
        "url":SITE+x["path"],"description":x["short"],"provider":{"@id":SITE+"/#business"},"areaServed":{"@type":"State","name":"Florida"},"hasOfferCatalog":cat}, separators=(",",":")) + '</script>\n'

# Landing: short, scannable, every card leads to a detail page
rows = "".join(f'''
    <article class="gh-service">{svc_photo(x["key"], *SVC_PHOTOS[x["key"]])}<h2 class="gh-h4">{x["name"].replace("&","&amp;")}</h2>
      <p>{x["short"]}</p>
      <a class="gh-link" href="{x["path"]}">{x["name"].replace("&","&amp;")} {ARROW}</a></article>''' for i, x in enumerate(SERVICES))
services_body = f'''<main id="main" class="gh-services-landing">
{page_head("Services", "Painting and finishes.", "Commercial and residential work, three services, one quality standard.")}
<section class="gh-section" style="padding-top:0"><div class="gh-container">
  <div class="gh-cards-3">{rows}
  </div>
</div></section>
</main>
{quote_band()}'''

SVC_SCHEMA = {"@context":"https://schema.org","@type":"ItemList","name":"Grand Hill services","itemListElement":[
    {"@type":"ListItem","position":i+1,"name":x["name"].replace("&","and"),"url":SITE+x["path"]} for i,x in enumerate(SERVICES)]}
SVC_HEAD = '<script type="application/ld+json">' + json.dumps(SVC_SCHEMA, separators=(",",":")) + '</script>\n'
page("/services/", "Painting, Finishes & Flooring Services | Grand Hill", "Commercial and residential painting; stucco, EIFS, pressure washing and coatings; and flooring and interior repairs across Florida.", services_body, current="/services/", extra_head=SVC_HEAD)

# Detail pages
for x in SERVICES:
    others = "".join(f'''<a class="gh-link" href="{o["path"]}">{o["name"].replace("&","&amp;")} {ARROW}</a>''' for o in SERVICES if o is not x)
    def _slug(t): return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")
    caps = "".join(f'<article class="gh-capability">{svc_photo(x["key"] + "-" + _slug(t), t, t, cls="gh-capability-photo")}<h3 class="gh-h4">{t}</h3><p>{d}</p></article>' for t, d in DETAILS[x["slug"]])
    capcls = "gh-capabilities is-" + str(len(DETAILS[x["slug"]]))
    hero_ext = "jpg" if os.path.exists(os.path.join(ROOT, "assets", "img", "services", x["key"] + ".jpg")) else "webp"
    hero = f'''<section class="gh-hero gh-hero-service gh-inverse gh-on-image">
  <div class="gh-photo" aria-hidden="true">{SLOT}<img class="gh-photo-img" src="/assets/img/services/{x["key"]}.{hero_ext}" alt="" width="1600" height="1200" fetchpriority="high" onerror="this.remove()"><div class="gh-hero-veil"></div></div>
  <div class="gh-hero-inner">
    {header("/services/", transparent=True, here=x["path"])}
    <div class="gh-container gh-hero-wrap">
      <div class="gh-hero-main">
        <div class="gh-hero-body">
          <p class="gh-eyebrow">{x["name"].replace("&","&amp;")}</p>
          <h1 class="gh-display">{x["h1"]}</h1>
          <p class="gh-body-lg">{x["short"]}</p>
          <div class="gh-hero-actions"><a class="gh-btn gh-btn-primary" href="/contact/">Request a quote {ARROW}</a></div>
        </div>
      </div>
    </div>
  </div>
</section>'''
    body = f'''{hero}<main id="main">
<section class="gh-section"><div class="gh-container">
  <div class="gh-two-col">
    <div><p class="gh-eyebrow">Overview</p><h2 class="gh-h2" style="margin-top:16px">What this includes.</h2></div>
    <div class="gh-prose"><p class="gh-body-lg">{x["lede"]}</p>
    <p><a class="gh-link" href="/contact/">Request a quote {ARROW}</a></p></div>
  </div>
</div></section>
<section class="gh-section gh-section-alt" aria-labelledby="cap-h"><div class="gh-container">
  <div class="gh-section-head"><p class="gh-eyebrow">Scope</p><h2 class="gh-h2" id="cap-h">{x["name"].replace("&","&amp;")}, in detail.</h2></div>
  <div class="{capcls}">{caps}</div>
</div></section>
<section class="gh-section"><div class="gh-container"><div class="gh-two-col">
  <div><p class="gh-eyebrow">More services</p><h2 class="gh-h2" style="margin-top:16px">Explore the rest.</h2></div>
  <div class="gh-prose gh-related">{others}<a class="gh-link" href="/services/">All services {ARROW}</a></div>
</div></div></section>
</main>
{quote_band()}'''
    page(x["path"], x["title"], x["desc"], (body,), current="/services/", transparent=True, extra_head=svc_ld(x))

# ---------------------------------------------------------------- AUDIENCE PAGES (commercial / residential)
def _ico(p):
    return f'<svg class="gh-icon gh-why-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">{p}</svg>'

AUDIENCES = [
  dict(path="/commercial-painting/", nav="Commercial", eyebrow="Commercial", img="hero-exterior.jpg",
       title="Commercial Painting Contractor in Florida | Grand Hill",
       desc="Commercial painting for retail, offices and multifamily properties across Florida. Work scheduled around your operations, documented and inspected before handoff.",
       h1="Commercial painting, planned around your operations.",
       short="Retail, offices and multifamily properties painted on schedule, with one point of contact from the first walkthrough to handoff.",
       lede="Commercial properties cannot stop for a repaint. We plan each project around opening hours, tenants and access, put the scope in writing and inspect every area before handoff.",
       cards_eyebrow="Who we work with", cards_h="Built for commercial properties.",
       cards=[
         ("Retail and store roll-outs", _ico('<path d="M3 9l1.5-5h15L21 9"/><path d="M4 9v11h16V9"/><path d="M9 20v-6h6v6"/>'), "One standard across every location, scheduled and reported store by store."),
         ("Offices and common areas", _ico('<rect x="5" y="3" width="14" height="18"/><path d="M9 7h2M13 7h2M9 11h2M13 11h2M9 15h2M13 15h2"/>'), "Work sequenced around the people using the building, including after-hours scopes."),
         ("Multifamily properties", _ico('<rect x="3" y="10" width="7" height="11"/><rect x="12" y="3" width="9" height="18"/><path d="M15 8h3M15 12h3M15 16h3M6 14h1M6 18h1"/>'), "Exteriors, common areas and unit turns planned around residents and tenants."),
         ("Property managers and facility teams", _ico('<rect x="5" y="4" width="14" height="17"/><path d="M9 4V2h6v2"/><path d="M9 11h6M9 15h4"/>'), "A written scope, clear documentation and one team that answers for the work."),
       ],
       steps_h="How a commercial project runs.",
       steps=[("Walk and scope", "We visit the site, confirm access and hours, and write the scope down."),
              ("Sequence", "Work is planned around operations, tenants and deliveries."),
              ("Prepare and coat", "Surfaces are cleaned, repaired and primed, then coated to specification."),
              ("Inspect and hand off", "Each area is checked against the scope before it is handed back.")],
       other=("/residential-painting/", "Residential painting"), stype="Commercial painting",
       audience="Owners and managers of retail, office and multifamily properties"),
  dict(path="/residential-painting/", nav="Residential", eyebrow="Residential", img="hero-detail.jpg",
       title="Residential Painting in Florida | Grand Hill",
       desc="Interior and exterior painting for homes in Florida: careful preparation, a clear written scope and a finish inspected before handoff.",
       h1="Residential painting, done carefully.",
       short="Interior and exterior painting for homes, with careful preparation, a clear written scope and a finish inspected before handoff.",
       lede="A home repaint should be straightforward. We walk the property with you, write down the scope and colors, protect your space, prepare every surface and inspect the finish before we call it done.",
       cards_eyebrow="What we paint", cards_h="Inside and out.",
       cards=[
         ("Interior painting", _ico('<rect x="4" y="3" width="14" height="6"/><path d="M18 6h2v5h-8v4"/><rect x="10" y="15" width="4" height="6"/>'), "Walls, ceilings and trim, finished to one consistent standard."),
         ("Exterior and stucco", _ico('<path d="M3 11l9-8 9 8"/><path d="M5 10v11h14V10"/><path d="M10 21v-6h4v6"/>'), "Surfaces prepared and coated to stand up to Florida sun, humidity and rain."),
         ("Cleaning and preparation", _ico('<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/>'), "Pressure washing, patching and priming before any coat goes on."),
         ("Repairs and finishing details", _ico('<rect x="4" y="4" width="16" height="16"/><path d="M8 12l3 3 5-6"/>'), "Caulking, sealing and touch-ups checked before handoff."),
       ],
       steps_h="How a home project runs.",
       steps=[("Walk and scope", "We walk the property with you and write down the scope and colors."),
              ("Protect and prepare", "Floors and furniture are protected, and surfaces are cleaned, repaired and primed."),
              ("Paint", "Coats are applied to specification, one area at a time."),
              ("Final walkthrough", "We check the finish against the scope before handoff.")],
       other=("/commercial-painting/", "Commercial painting"), stype="Residential painting",
       audience="Homeowners in Florida"),
]

for a in AUDIENCES:
    cards = "".join(f'<li>{ico}<h3>{t}</h3><p>{d}</p></li>' for t, ico, d in a["cards"])
    steps = "".join(f'<li><h3>{t}</h3><p>{d}</p></li>' for t, d in a["steps"])
    svc_links = "".join(f'<a class="gh-link" href="{o["path"]}">{o["name"].replace("&","&amp;")} {ARROW}</a>' for o in SERVICES)
    img_ok = os.path.exists(os.path.join(ROOT, "assets", "img", a["img"]))
    photo = (f'<img class="gh-photo-img" src="/assets/img/{a["img"]}" alt="" width="1672" height="941" fetchpriority="high" onerror="this.remove()">' if img_ok else "")
    hero = f'''<section class="gh-hero gh-hero-service gh-inverse gh-on-image">
  <div class="gh-photo" aria-hidden="true">{photo}<div class="gh-hero-veil"></div></div>
  <div class="gh-hero-inner">
    {header(a["path"], transparent=True, here=a["path"])}
    <div class="gh-container gh-hero-wrap">
      <div class="gh-hero-main">
        <div class="gh-hero-body">
          <p class="gh-eyebrow">{a["eyebrow"]}</p>
          <h1 class="gh-display">{a["h1"]}</h1>
          <p class="gh-body-lg">{a["short"]}</p>
          <div class="gh-hero-actions"><a class="gh-btn gh-btn-primary" href="/contact/">Request a quote {ARROW}</a></div>
        </div>
      </div>
    </div>
  </div>
</section>'''
    body = f'''{hero}<main id="main">
<section class="gh-section"><div class="gh-container">
  <div class="gh-two-col">
    <div><p class="gh-eyebrow">Overview</p><h2 class="gh-h2" style="margin-top:16px">{a["eyebrow"]} painting.</h2></div>
    <div class="gh-prose"><p class="gh-body-lg">{a["lede"]}</p>
    <p><a class="gh-link" href="/contact/">Request a quote {ARROW}</a> &nbsp; <a class="gh-link" href="{a["other"][0]}">{a["other"][1]} {ARROW}</a></p></div>
  </div>
</div></section>
<section class="gh-section gh-section-alt" aria-labelledby="aud-h"><div class="gh-container">
  <div class="gh-section-head"><p class="gh-eyebrow">{a["cards_eyebrow"]}</p><h2 class="gh-h2" id="aud-h">{a["cards_h"]}</h2></div>
  <ul class="gh-why">{cards}</ul>
</div></section>
<section class="gh-section" aria-labelledby="steps-h"><div class="gh-container">
  <div class="gh-section-head"><p class="gh-eyebrow">Our process</p><h2 class="gh-h2" id="steps-h">{a["steps_h"]}</h2></div>
  <ol class="gh-method gh-method-plain is-4" aria-label="{a["steps_h"]}">{steps}</ol>
</div></section>
<section class="gh-section gh-section-alt"><div class="gh-container"><div class="gh-two-col">
  <div><p class="gh-eyebrow">Services</p><h2 class="gh-h2" style="margin-top:16px">What we can take on.</h2></div>
  <div class="gh-prose gh-related">{svc_links}<a class="gh-link" href="/services/">All services {ARROW}</a></div>
</div></div></section>
</main>
{quote_band()}'''
    ld = '<script type="application/ld+json">' + json.dumps({"@context":"https://schema.org","@type":"Service","name":a["stype"],"serviceType":a["stype"],
        "url":SITE+a["path"],"description":a["desc"],"provider":{"@id":SITE+"/#business"},"areaServed":{"@type":"State","name":"Florida"},
        "audience":{"@type":"Audience","audienceType":a["audience"]}}, separators=(",",":")) + '</script>\n'
    page(a["path"], a["title"], a["desc"], (body,), current=a["path"], transparent=True, extra_head=ld)

# ---------------------------------------------------------------- PROJECTS
projects_body = f'''<main id="main">
{page_head("Projects", "Selected work.", "Commercial and residential projects, and the finishes that define them.")}
<section class="gh-section gh-section-alt" style="padding-top:64px"><div class="gh-container">
  <div class="gh-projects-grid">
    <a class="gh-project" href="/projects/sample-project/" data-placeholder="project-card">
      <div class="gh-photo">{SLOT}<span class="gh-photo-caption">Photo placeholder</span></div>
      <div class="gh-project-meta"><div><h2 class="gh-h4">Project name</h2><p class="gh-label">Location &middot; Scope</p></div><span class="gh-project-arrow">{ARROW_UR}</span></div>
    </a>
  </div>
  <p class="gh-placeholder-note">Placeholder. Each project needs real photos, a short scope and the right credit (team experience, or the partner company with its authorization).</p>
</div></section>
</main>
{quote_band()}'''
if SHOW_PROJECTS:
    page("/projects/", "Painting & Finishes Projects in Florida | Grand Hill", "Selected commercial and residential painting and finishes projects completed by Grand Hill across Florida.", projects_body, current="/projects/")

project_detail = f'''<main id="main">
<section class="gh-page-head"><div class="gh-container">
  <p class="gh-eyebrow">Project</p><h1 class="gh-h1">Project name</h1>
  <p class="gh-body-lg">Location &middot; Year &middot; Scope</p>
</div></section>
<div class="gh-container" style="padding-bottom:128px">
  <div class="gh-photo" style="aspect-ratio:16/9">{SLOT}<span class="gh-photo-caption">Photo placeholder</span></div>
  <div class="gh-two-col" style="margin-top:64px">
    <ul class="gh-meta-list"><li><span>Client</span><span>To be added</span></li><li><span>Scope</span><span>To be added</span></li><li><span>Credit</span><span>To be added</span></li></ul>
    <div class="gh-prose"><p class="gh-body-lg">Project description: the brief, the finish challenge and the result.</p>
    <p class="gh-placeholder-note">Template page for project details. Duplicate this folder for each project. It is hidden from search engines until it holds real content.</p>
    <p style="margin-top:32px"><a class="gh-link" href="/projects/">All projects {ARROW}</a></p></div>
  </div>
</div>
</main>
{quote_band()}'''
if SHOW_PROJECTS:
    page("/projects/sample-project/", "Project name | Grand Hill", "Project detail template.", project_detail, current="/projects/", noindex=True)

# ---------------------------------------------------------------- ABOUT
about_body = f'''<main id="main">
{page_head("About", "A finishing company built on one standard.", "Direct, accountable and careful with every surface.")}
<section class="gh-section gh-section-alt" style="padding-top:64px" aria-labelledby="how-h"><div class="gh-container">
  <div class="gh-section-head"><p class="gh-eyebrow">How we work</p><h2 class="gh-h2" id="how-h">From walkthrough to handoff.</h2>
  <p>Work is carried out by prequalified specialty crews that carry their own insurance, under Grand Hill's direction and inspection. We answer for the result.</p></div>
  <ol class="gh-steps">
    <li><h3>Scope</h3><p>We walk the site, confirm surfaces, substrates and finish specifications, and note access constraints.</p></li>
    <li><h3>Estimate</h3><p>A clear written estimate with scope, exclusions and schedule. No surprises in the numbers.</p></li>
    <li><h3>Execute</h3><p>A prequalified crew works to a schedule built around the building and its occupants.</p></li>
    <li><h3>Inspect</h3><p>We inspect against the specification, correct anything that falls short and hand off.</p></li>
  </ol>
</div></section>

<section class="gh-section" aria-labelledby="team-h"><div class="gh-container">
  <div class="gh-section-head"><p class="gh-eyebrow">Leadership</p><h2 class="gh-h2" id="team-h">The people behind Grand Hill.</h2></div>
  <div class="gh-cards-2">
    <article class="gh-person"><h3>Julio Adiel Canelo</h3><p class="gh-label">Commercial Member</p><p>Brings projects and client relationships. Leads safety and supervises work in the field.</p></article>
    <article class="gh-person"><h3>Adrian Gerig</h3><p class="gh-label">Administrative Member</p><p>Leads administration, project management and client communication.</p></article>
  </div>
</div></section>

<section class="gh-section gh-section-alt" aria-labelledby="area-h"><div class="gh-container"><div class="gh-two-col">
  <div><p class="gh-eyebrow">Service area</p><h2 class="gh-h2" id="area-h" style="margin-top:16px">Florida.</h2></div>
  <div class="gh-prose"><p class="gh-body-lg">We are based in Central Florida and take on commercial and residential projects across the state.</p>
  <p>Not sure whether your project is in range? <a href="/contact/" style="color:var(--ink);text-underline-offset:4px;text-decoration-color:var(--accent);text-decoration-thickness:2px">Ask us.</a></p></div>
</div></div></section>
</main>
{quote_band()}'''
page("/about/", "About Grand Hill | Florida Painting & Finishes Contractor", "Meet the team behind Grand Hill, a Florida painting and finishes contractor. See how we work from walkthrough to handoff and where we serve.", about_body, current="/about/")

# ---------------------------------------------------------------- CONTACT
def field(id_, label, kind="text", req=False, span2=False, autocomplete="", placeholder=""):
    r = ' <span class="req" aria-hidden="true">*</span>' if req else ""
    reqa = " required" if req else ""
    ac = f' autocomplete="{autocomplete}"' if autocomplete else ""
    ph = f' placeholder="{placeholder}"' if placeholder else ""
    return f'''<div class="gh-field{' gh-span-2' if span2 else ''}"><label class="gh-field-label" for="{id_}">{label}{r}</label>
<input class="gh-input" id="{id_}" name="{id_}" type="{kind}"{reqa}{ac}{ph}></div>'''

contact_body = f'''<main id="main">
{page_head("Contact", "Request a quote.", "Tell us about the project. We respond within one business day.")}
<section class="gh-section gh-section-alt" style="padding-top:64px"><div class="gh-container"><div class="gh-contact">
  <div>
    <form id="quote-form" class="gh-form" name="quote" method="POST" action="/thank-you/" data-netlify="true" netlify-honeypot="bot-field" novalidate>
      <input type="hidden" name="form-name" value="quote">
      <p class="gh-hp" aria-hidden="true"><label>Leave this field empty <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
      {field("name", "Name", req=True, autocomplete="name")}
      {field("company", "Company", req=True, autocomplete="organization")}
      {field("email", "Email", "email", req=True, autocomplete="email")}
      {field("phone", "Phone", "tel", autocomplete="tel")}
      <div class="gh-field"><label class="gh-field-label" for="service">Service</label>
        <select class="gh-select" id="service" name="service"><option value="">Select a service</option><option>Painting: interior</option><option>Painting: exterior</option><option>Finishes and surface care</option><option>Interiors and flooring</option><option>Not sure yet</option></select></div>
      {field("location", "Project location", autocomplete="address-level2", placeholder="City, Florida")}
      <div class="gh-field gh-span-2"><label class="gh-field-label" for="details">Project details <span class="req" aria-hidden="true">*</span></label>
        <textarea class="gh-textarea" id="details" name="details" required></textarea>
        <p class="gh-help">Scope, approximate size, timeline and any plans or specifications you can share.</p></div>
      <div class="gh-span-2"><button class="gh-btn gh-btn-primary" type="submit">Send request {ARROW}</button><div id="form-status" class="gh-form-status" aria-live="polite"></div></div>
    </form>
    <div id="form-success" class="gh-form-success" role="status" tabindex="-1" hidden>{CHECK}<div><strong>Request received.</strong><p>Thank you. We will respond within one business day.</p></div></div>
  </div>
  <aside class="gh-contact-side" aria-label="Contact details">
    <h2 class="gh-h3">Contact</h2>
    <dl>
      {('<dt class="gh-label">Phone</dt><dd>' + PHONE + "</dd>") if PHONE else ""}
      <dt class="gh-label">Email</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd>
      <dt class="gh-label">Service area</dt><dd>Florida</dd>
    </dl>
  </aside>
</div></div></section>
</main>'''
page("/contact/", "Request a Painting Quote in Florida | Grand Hill", "Request a quote for a commercial or residential painting or finishes project in Florida. Grand Hill responds within one business day.", contact_body, current="/contact/")

thanks = f'''<main id="main">
{page_head("Thank you", "Request received.", "Thank you. We will respond within one business day.")}
<div class="gh-container" style="padding-bottom:128px"><a class="gh-link" href="/">Back to home {ARROW}</a></div>
</main>'''
page("/thank-you/", "Thank you | Grand Hill", "Your request has been received.", thanks, noindex=True)

# ---------------------------------------------------------------- INSIGHTS (built, hidden at launch)
insights = f'''<main id="main">
{page_head("Insights", "Insights.", "Notes on finishes, coatings and project planning.")}
<div class="gh-container" style="padding-bottom:128px"><div class="gh-empty"><h2 class="gh-h4">No articles yet.</h2>
<p class="gh-muted">This section is built but hidden at launch: it is not linked in the navigation or the sitemap, and it is marked noindex. To publish it, add the link to the header and footer, remove the noindex tag and add the URL to sitemap.xml.</p></div></div>
</main>'''
page("/insights/", "Insights | Grand Hill", "Insights from Grand Hill on finishes and coatings.", insights, noindex=True)

# ---------------------------------------------------------------- 404
nf = f'''<main id="main">
{page_head("404", "Page not found.", "The page you are looking for does not exist or has moved.")}
<div class="gh-container" style="padding-bottom:128px"><a class="gh-link" href="/">Back to home {ARROW}</a></div>
</main>'''
page("/404.html", "Page not found | Grand Hill", "Page not found.", nf, noindex=True)

# ---------------------------------------------------------------- robots + sitemap
urls = ["/", "/services/"] + [x["path"] for x in SERVICES] + ["/commercial-painting/", "/residential-painting/"] + (["/projects/"] if SHOW_PROJECTS else []) + ["/about/", "/contact/"]
with open(os.path.join(ROOT, "sitemap.xml"), "w") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "".join(f"  <url><loc>{SITE}{u}</loc><lastmod>{datetime.date.today().isoformat()}</lastmod></url>\n" for u in urls) + "</urlset>\n")
with open(os.path.join(ROOT, "robots.txt"), "w") as f:
    f.write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
print("ok")
