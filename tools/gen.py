#!/usr/bin/env python3
"""Generates the static pages for the Grand Hill site. Usage: gen.py <site_dir>"""
import re, os, sys, html, json, datetime

ROOT = sys.argv[1]
SITE = "https://grandhillcorp.com"
EMAIL = "info@grandhillcorp.com"          # TODO: confirm public inbox
PHONE = None                              # TODO: set the real phone number; it then appears in footer + contact
SHOW_PROJECTS = False                     # set True once there are real projects: adds Projects to menu, footer, sitemap
INSTAGRAM = "https://www.instagram.com/grandhillcorp/"
FACEBOOK = "https://www.facebook.com/grandhillcorp/"
GOOGLE_TAG = "GTM-PP5QMSCD"                 # Google tag / Analytics ID; set to None to remove tracking from every page
BACKOFFICE = "https://app.grandhillcorp.com"   # "Team login" link in the footer
SHOW_PROOF = False                        # set True once there is a real featured project and a real, authorized testimonial on the home page
OG = "/assets/img/og-image.png"

ARROW = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12h16M14 6l6 6-6 6"/></svg>'
SOC = {
 "instagram": '<svg class="gh-soc" viewBox="0 0 24 24" aria-hidden="true"><rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.2" cy="6.8" r=".6" fill="currentColor"/></svg>',
 "facebook": '<svg class="gh-soc" viewBox="0 0 24 24" aria-hidden="true"><path d="M14 8.5h2.5V5H14c-2.2 0-3.5 1.5-3.5 3.6V11H8v3.4h2.5V21H14v-6.6h2.4l.5-3.4H14V9.1c0-.4.2-.6.6-.6z"/></svg>',
 "mail": '<svg class="gh-soc" viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5.5" width="18" height="13" rx="2"/><path d="M3.5 7l8.5 6 8.5-6"/></svg>',
}
ARROW_UR = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 17L17 7M8 7h9v9"/></svg>'
_ICONS = {
    "compass": '<circle cx="12" cy="12" r="9"/><path d="M15.5 8.5l-2 5-5 2 2-5z"/>',
    "clipboard": '<rect x="6" y="4" width="12" height="17" rx="1"/><path d="M9 4h6v3H9zM9 14l2 2 4-4"/>',
    "users": '<circle cx="9" cy="8" r="3"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/><circle cx="17" cy="9" r="2.5"/><path d="M17 14c2.5 0 4.5 2 4.5 4.5"/>',
    "pin": '<path d="M12 21s7-6.2 7-11a7 7 0 10-14 0c0 4.8 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/>',
    "building": '<path d="M4 20V9l8-5 8 5v11z"/><path d="M9 20v-6h6v6"/>',
    "gear": '<circle cx="12" cy="12" r="3"/><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M18.4 5.6l-2.1 2.1M7.7 16.3l-2.1 2.1"/>',
    "chart": '<path d="M4 20h16M7 20v-7M12 20V6M17 20v-10"/>',
    "flow": '<circle cx="6" cy="6" r="2.5"/><circle cx="18" cy="18" r="2.5"/><path d="M8.5 6H14a3 3 0 013 3v6.5"/>',
    "ruler": '<path d="M4 16L16 4l4 4L8 20z"/><path d="M7 13l2 2M10 10l2 2M13 7l2 2"/>',
    "doc": '<path d="M7 3h7l4 4v14H7z"/><path d="M14 3v4h4M9.5 12h5M9.5 16h5"/>',
    "roller": '<rect x="4" y="3" width="14" height="6" rx="1"/><path d="M18 6h2v5H11v3"/><rect x="9" y="14" width="4" height="7" rx="1"/>',
    "search": '<circle cx="11" cy="11" r="6"/><path d="M20 20l-4.5-4.5"/>',
}
def ico(name, cls="gh-ico"):
    return f'<span class="{cls}" aria-hidden="true"><svg viewBox="0 0 24 24">{_ICONS[name]}</svg></span>'
def title_block(icon, eyebrow, h2, hid, extra_cls=""):
    return f'<div class="gh-title-plain{extra_cls}"><p class="gh-eyebrow">{eyebrow}</p><h2 class="gh-h2" id="{hid}">{h2}</h2></div>'

CHECK = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M8 12.5l3 3 5-6"/></svg>'

SLOT = ('<div class="gh-photo-slot" aria-hidden="true"><svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice">'
        '<rect class="pl" width="400" height="300"/>'
        '<path class="ln" d="M40 260h320M70 260V90h120v170M190 260V60h140v200M90 120h80M90 160h80M90 200h80M210 100h100M210 140h100M210 180h100M210 220h100"/>'
        '</svg></div>')

SVC_CARD_REAL = {}   # real project photos for service cards go here once we have ones that show the work (finishes, flooring)

def svc_photo(key, label, alt, cls="gh-service-photo"):
    """Placeholder until /assets/img/services/<key>.webp (1600x1200) exists; the real photo then covers it."""
    real = SVC_CARD_REAL.get(key)
    if real and cls == "gh-service-photo":
        return (f'<div class="gh-photo {cls}"><img class="gh-photo-img" src="/assets/img/projects/{real[0]}" alt="{real[1]}" '
                f'width="800" height="600" loading="lazy" decoding="async"></div>')
    ext = "webp"
    exists = os.path.exists(os.path.join(ROOT, "assets", "img", "services", key + "." + ext))
    placeholder = "" if exists else SLOT + f'<span class="gh-photo-caption">Photo placeholder &middot; {label}</span>'
    return (f'<div class="gh-photo {cls}">{placeholder}'
            f'<img class="gh-photo-img" src="/assets/img/services/{key}.{ext}" alt="{alt}" width="1600" height="1200" loading="lazy" decoding="async" onerror="this.remove()"></div>')

SVC_PHOTOS = {
  "painting": ("Painting", "Warm-white Florida apartment exterior with crisp trim and dark windows"),
  "finishes": ("Finishes", "Textured ivory stucco facade with a recessed control joint and crisp corner"),
  "interiors": ("Interiors", "Retail interior with new flooring and installed fixtures"),
}

CRUMB = {"/services/":"Services","/services/finishes-and-surface-care/":"Finishes and surface care","/services/interiors-and-flooring/":"Interiors and flooring","/services/commercial-painting/":"Commercial painting","/services/residential-painting/":"Residential painting","/projects/":"Projects","/about/":"About","/contact/":"Contact"}
NAV = [("Services", "/services/")] + ([("Projects", "/projects/")] if SHOW_PROJECTS else []) + [("About", "/about/"), ("Contact", "/contact/")]


# ---------------------------------------------------------------- SERVICES
SERVICES = [
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


# ---------------------------------------------------------------- AUDIENCE DATA (commercial / residential painting services)
def _ico(p):
    return f'<svg class="gh-icon gh-why-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">{p}</svg>'

AUDIENCES = [
  dict(slug="commercial-painting", path="/services/commercial-painting/", name="Commercial painting", short_name="Commercial", eyebrow="Painting · Commercial", img="hero-exterior.webp",
       card_blurb="Retail, offices and multifamily, planned around your operations.",
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
       related=["/services/finishes-and-surface-care/", "/services/interiors-and-flooring/"], sibling="/services/residential-painting/",
       caps=[("Interior painting", "Offices, retail floors and common areas, finished to one consistent standard.", "painting-interior-painting"),
             ("Exterior painting", "Building exteriors prepared and coated to stand up to Florida sun, humidity and rain.", "painting-exterior-painting"),
             ("Surface preparation and repair", "Cleaning, patching and priming before any coat goes on.", "painting-surface-preparation-and-repair"),
             ("Occupied buildings", "Work sequenced around opening hours, tenants and residents.", "painting-occupied-buildings")],
       work_h="Commercial work in Florida.",
       work=[("commercial-01.webp", "Commercial building with a tile roof, arched entrance and pale green and cream stucco", "Commercial exterior."),
             ("commercial-02.webp", "Side of a one-story commercial building with palms and large windows", "Commercial exterior, side elevation.")],
       stype="Commercial painting", audience="Owners and managers of retail, office and multifamily properties"),
  dict(slug="residential-painting", path="/services/residential-painting/", name="Residential painting", short_name="Residential", eyebrow="Painting · Residential", img="hero-detail.webp",
       card_blurb="Interior and exterior painting for homes, inspected before handoff.",
       title="Residential Painting in Florida | Grand Hill",
       desc="Interior and exterior painting for homes in Florida: careful preparation, a clear written scope and a finish inspected before handoff.",
       h1="Residential painting, done carefully.",
       short="Interior and exterior painting for homes, with careful preparation, a clear written scope and a finish inspected before handoff.",
       lede="A home repaint should be straightforward. We walk the property with you, write down the scope and colors, protect your space, prepare every surface and inspect the finish before we call it done.",
       cards_eyebrow="Who we work with", cards_h="Built for homes and communities.",
       cards=[
         ("Homeowners", _ico('<path d="M3 11l9-8 9 8"/><path d="M5 10v11h14V10"/><path d="M10 21v-6h4v6"/>'), "Interior and exterior repaints with a written scope and agreed colors."),
         ("Townhomes and condos", _ico('<rect x="3" y="10" width="7" height="11"/><rect x="12" y="3" width="9" height="18"/><path d="M15 8h3M15 12h3M15 16h3M6 14h1M6 18h1"/>'), "Units and shared exteriors painted with clear scheduling for neighbors."),
         ("HOAs and community associations", _ico('<rect x="4" y="4" width="16" height="16"/><path d="M4 10h16M10 4v16"/>'), "Exteriors and common areas planned and documented for the board."),
         ("Landlords and rental properties", _ico('<rect x="5" y="4" width="14" height="17"/><path d="M9 4V2h6v2"/><path d="M9 11h6M9 15h4"/>'), "Repaints planned around tenant turnovers."),
       ],
       steps_h="How a home project runs.",
       steps=[("Walk and scope", "We walk the property with you and write down the scope and colors."),
              ("Protect and prepare", "Floors and furniture are protected, and surfaces are cleaned, repaired and primed."),
              ("Paint", "Coats are applied to specification, one area at a time."),
              ("Final walkthrough", "We check the finish against the scope before handoff.")],
       related=["/services/finishes-and-surface-care/"], sibling="/services/commercial-painting/",
       caps=[("Interior painting", "Walls, ceilings and trim in the rooms you live in, finished to one consistent standard.", "residential-04.webp", "Open living room with vaulted ceiling, skylights and freshly painted walls"),
             ("Exterior painting", "Home exteriors prepared and coated to stand up to Florida sun, humidity and rain.", "residential-03.webp", "Pink stucco home with arched entry and white trim"),
             ("Surface preparation and repair", "Cleaning, patching and priming before any coat goes on.", "residential-05.webp", "Covered stucco entry with double front door and brick paver walkway")],
       work=[("residential-01.webp", "Two-story gray stucco home with dark shutters and landscaped grounds", "Residential exterior."),
             ("residential-02.webp", "Two-story white stucco home with red shutters and a brick paver driveway", "Residential exterior.")],
       work_h="Residential work in Florida.",
       stype="Residential painting", audience="Homeowners in Florida"),
]


_AUD_BY_PATH_ = {a["path"]: a for a in AUDIENCES}
_SVC_BY_PATH = {x["path"]: x for x in SERVICES}
_CARD = {"finishes-and-surface-care": "Stucco, EIFS, pressure washing, coatings and wallcoverings.",
         "interiors-and-flooring": "Flooring, wall and fixture repairs, and fixture installs."}
for _x in SERVICES: _x["card_blurb"] = _CARD[_x["slug"]]
ALL = AUDIENCES + SERVICES   # order shown in menus, footer and cards: commercial first

AUD_CARD_REAL = {
  "commercial-painting": ("commercial-01.webp", "Commercial building with a tile roof, arched entrance and pale green and cream stucco", 680, 510),
  "residential-painting": ("residential-02.webp", "Two-story white stucco home with red shutters and a brick paver driveway", 600, 800),
}

def card_photo(x, heading_cls="gh-service-photo"):
    real = AUD_CARD_REAL.get(x.get("slug"))
    if real and heading_cls == "gh-service-photo":
        return (f'<div class="gh-photo {heading_cls}"><img class="gh-photo-img" src="/assets/img/projects/{real[0]}" alt="{real[1]}" '
                f'width="{real[2]}" height="{real[3]}" loading="lazy" decoding="async"></div>')
    if "img" in x:
        return f'<div class="gh-photo {heading_cls}"><img class="gh-photo-img" src="/assets/img/{x["img"]}" alt="" width="1672" height="941" loading="lazy" decoding="async" onerror="this.remove()"></div>'
    return svc_photo(x["key"], *SVC_PHOTOS[x["key"]])

def more_services(current_path, cls="gh-section"):
    """Photo cards for the other services, shown at the bottom of every service page."""
    cards = ""
    for o in ALL:
        if o["path"] == current_path:
            continue
        nm = o["name"].replace("&", "&amp;")
        cards += f'''
    <article class="gh-service">{card_photo(o)}<h3 class="gh-h4">{nm}</h3>
      <p>{o["card_blurb"]}</p>
      <a class="gh-link" href="{o["path"]}">{nm} {ARROW}</a></article>'''
    return f'''<section class="{cls}" aria-labelledby="more-h"><div class="gh-container">
  <div class="gh-more-head"><div><p class="gh-eyebrow">More services</p><h2 class="gh-h2" id="more-h">Explore the rest.</h2></div>
  <a class="gh-link" href="/services/">All services {ARROW}</a></div>
  <div class="gh-cards-3">{cards}
  </div>
</div></section>'''

def header(current, transparent=False, here=""):
    logo = "reversed-transparent" if transparent else "primary"
    cls = "gh-header gh-header-transparent" if transparent else "gh-header"
    chev = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>'
    def sub():
        items = '<a href="/services/"%s>All services</a>' % (' aria-current="page"' if here == "/services/" else "")
        for x in ALL:
            items += '<a href="%s"%s>%s</a>' % (x["path"], ' aria-current="page"' if x["path"] == here else "", x["name"].replace("&", "&amp;"))
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
        <p class="gh-footer-tag">Painting, finishes and flooring for commercial and residential projects across Florida. Direct, accountable and careful with every surface.</p></div>
      <div><h4>Contact</h4><ul>{("<li>" + PHONE + "</li>") if PHONE else ""}<li><a class="gh-soc-link" href="mailto:{EMAIL}">{SOC["mail"]}{EMAIL}</a></li>{('<li><a class="gh-soc-link" href="' + INSTAGRAM + '" target="_blank" rel="noopener">' + SOC["instagram"] + 'Instagram</a></li>') if INSTAGRAM else ""}{('<li><a class="gh-soc-link" href="' + FACEBOOK + '" target="_blank" rel="noopener">' + SOC["facebook"] + 'Facebook</a></li>') if FACEBOOK else ""}</ul></div>
      <div><h4>Services</h4><ul><li><a href="/services/commercial-painting/">Commercial painting</a></li><li><a href="/services/residential-painting/">Residential painting</a></li><li><a href="/services/finishes-and-surface-care/">Finishes &amp; surface care</a></li><li><a href="/services/interiors-and-flooring/">Interiors &amp; flooring</a></li></ul></div>
      <div><h4>Company</h4><ul><li><a href="/services/">Services</a></li>{'<li><a href="/projects/">Projects</a></li>' if SHOW_PROJECTS else ""}<li><a href="/about/">About</a></li><li><a href="/contact/">Contact</a></li><li><a href="{BACKOFFICE}" rel="nofollow noopener">Team login</a></li></ul></div>
    </div>
    <div class="gh-footer-bottom"><span>&copy; 2026 Grand Hill, LLC. All rights reserved.</span><span class="gh-footer-legal"><a href="/privacy/">Privacy policy</a></span></div>
  </div>
</footer>'''


def gtag_snippet(path):
    if not GOOGLE_TAG:
        return ""
    s = (f'<script async src="https://www.googletagmanager.com/gtm.js?id={GOOGLE_TAG}"></script>\n'
         '<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag("js",new Date());'
         + ('gtag("event","generate_lead");' if path == "/thank-you/" else "") + '</script>\n')
    return s

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
{gtag_snippet(path)}<meta charset="utf-8">
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
    {''.join(f'<img class="gh-hero-slide{" is-active" if i == 0 else ""}" {"src" if i == 0 else "data-src"}="/assets/img/hero-{name}.webp" alt="" width="1672" height="941" {"fetchpriority=high" if i == 0 else ""}>' for i, name in enumerate(["exterior", "craft", "interior", "detail"]))}
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
    <div class="gh-actions"><a class="gh-link" href="/services/">Our services {ARROW}</a><a class="gh-link gh-link-quiet" href="/about/">About Grand Hill</a></div>
  </div>
</div></div></section>

<section class="gh-section gh-section-alt" aria-labelledby="svc-h"><div class="gh-container">
  <div class="gh-section-head"><p class="gh-eyebrow">Services</p><h2 class="gh-h2" id="svc-h">Painting and finishes for every project.</h2></div>
  <div class="gh-cards-4">
    <article class="gh-service">{card_photo(_AUD_BY_PATH_["/services/commercial-painting/"])}<h3 class="gh-h4">Commercial painting</h3>
      <p>{_AUD_BY_PATH_["/services/commercial-painting/"]["card_blurb"]}</p>
      <a class="gh-link" href="/services/commercial-painting/">Commercial painting {ARROW}</a></article>
    <article class="gh-service">{card_photo(_AUD_BY_PATH_["/services/residential-painting/"])}<h3 class="gh-h4">Residential painting</h3>
      <p>{_AUD_BY_PATH_["/services/residential-painting/"]["card_blurb"]}</p>
      <a class="gh-link" href="/services/residential-painting/">Residential painting {ARROW}</a></article>
    <article class="gh-service">{svc_photo("finishes", *SVC_PHOTOS["finishes"])}<h3 class="gh-h4">Finishes &amp; surface care</h3>
      <p>{_SVC_BY_PATH["/services/finishes-and-surface-care/"]["card_blurb"]}</p>
      <a class="gh-link" href="/services/finishes-and-surface-care/">Finishes {ARROW}</a></article>
    <article class="gh-service">{svc_photo("interiors", *SVC_PHOTOS["interiors"])}<h3 class="gh-h4">Interiors &amp; flooring</h3>
      <p>{_SVC_BY_PATH["/services/interiors-and-flooring/"]["card_blurb"]}</p>
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

<section class="gh-section gh-section-alt" aria-labelledby="feat-h"><div class="gh-container">
  <div class="gh-section-head"><p class="gh-eyebrow">Recent work</p><h2 class="gh-h2" id="feat-h">Finished to one standard.</h2></div>
  <div class="gh-featured">
    <a href="/services/commercial-painting/" class="gh-project" aria-label="Commercial painting"><div class="gh-photo"><img class="gh-photo-img" src="/assets/img/projects/commercial-01.webp" alt="Commercial building with a tile roof, arched entrance and pale green and cream stucco" width="680" height="510" loading="lazy" decoding="async"></div></a>
    <div>
      <p class="gh-label">Florida &middot; Commercial</p>
      <h3 class="gh-h3">Commercial exteriors that hold up.</h3>
      <p>Retail, offices and multifamily properties need a consistent finish that stands up to Florida sun and rain. We plan the work around your operations and inspect every area before handoff.</p>
      <div class="gh-actions"><a class="gh-btn gh-btn-primary" href="/services/commercial-painting/">Commercial painting {ARROW}</a><a class="gh-btn gh-btn-secondary" href="/services/residential-painting/">Residential painting</a></div>
    </div>
  </div>
</div></section>

{proof_html}
</main>
{quote_band()}'''


HOME_SCHEMA = {"@context":"https://schema.org","@graph":[
  {"@type":["HousePainter","LocalBusiness"],"@id":SITE+"/#business","name":"Grand Hill","legalName":"Grand Hill, LLC","url":SITE+"/",
   "logo":SITE+"/assets/logo/grand-hill-logo-primary.svg","image":SITE+OG,
   "description":"Painting and finishes for commercial and residential projects across Florida.",
   "slogan":"Precision in every finish.","sameAs":[u for u in (INSTAGRAM, FACEBOOK) if u],"areaServed":{"@type":"State","name":"Florida"},
   "knowsAbout":["Commercial painting","Residential painting","Exterior painting","Interior painting","Stucco","EIFS","Pressure washing","Protective coatings","Wallcoverings","Commercial flooring"]},
  {"@type":"WebSite","@id":SITE+"/#website","url":SITE+"/","name":"Grand Hill","publisher":{"@id":SITE+"/#business"},"inLanguage":"en-US"}]}
HOME_HEAD = ('<link rel="preload" as="image" href="/assets/img/hero-exterior.webp" fetchpriority="high">\n'
             '<script type="application/ld+json">' + json.dumps(HOME_SCHEMA, separators=(",",":")) + '</script>\n')
page("/", "Commercial & Residential Painting in Florida | Grand Hill",
     "Commercial and residential painting and finishes across Florida, for retail, offices, multifamily and homes. Planned around your schedule, inspected before handoff.",
     (home_hero + home_main,), transparent=True,
     extra_head=HOME_HEAD)


DETAILS = {
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
    <article class="gh-service">{card_photo(x)}<h2 class="gh-h4">{x["name"].replace("&","&amp;")}</h2>
      <p>{x["card_blurb"]}</p>
      <a class="gh-link" href="{x["path"]}">View service {ARROW}</a></article>''' for i, x in enumerate(ALL))
services_body = f'''<main id="main" class="gh-services-landing">
<section class="gh-band gh-inverse gh-on-image" style="--band-img:url(/assets/img/services-bg.svg)"><div class="gh-container"><p class="gh-eyebrow">Services</p><h1 class="gh-h1">Painting and finishes.</h1><p class="gh-body-lg">Commercial and residential painting, finishes and flooring. One quality standard.</p></div></section>
<section class="gh-section gh-section-alt"><div class="gh-container">
  <div class="gh-cards-4">{rows}
  </div>
</div></section>
<section class="gh-section" aria-labelledby="proc-h"><div class="gh-container">
  <div class="gh-section-head"><p class="gh-eyebrow">How we work</p><h2 class="gh-h2" id="proc-h">The same process on every project.</h2></div>
  <ol class="gh-steps">
    <li><h3>{ico('clipboard','gh-ico gh-ico-inline')}Scope</h3><p>We walk the site, confirm surfaces, substrates and finish specifications, and note access constraints.</p></li>
    <li><h3>{ico('doc','gh-ico gh-ico-inline')}Estimate</h3><p>A clear written estimate with scope, exclusions and schedule. No surprises in the numbers.</p></li>
    <li><h3>{ico('roller','gh-ico gh-ico-inline')}Execute</h3><p>The work follows a schedule built around the building and its occupants.</p></li>
    <li><h3>{ico('search','gh-ico gh-ico-inline')}Inspect</h3><p>We inspect against the specification, correct anything that falls short and hand off.</p></li>
  </ol>
</div></section>
</main>
{quote_band()}'''

SVC_SCHEMA = {"@context":"https://schema.org","@type":"ItemList","name":"Grand Hill services","itemListElement":[
    {"@type":"ListItem","position":i+1,"name":x["name"].replace("&","and"),"url":SITE+x["path"]} for i,x in enumerate(ALL)]}
SVC_HEAD = '<script type="application/ld+json">' + json.dumps(SVC_SCHEMA, separators=(",",":")) + '</script>\n'
page("/services/", "Painting, Finishes & Flooring Services | Grand Hill", "Commercial and residential painting; stucco, EIFS, pressure washing and coatings; and flooring and interior repairs across Florida.", services_body, current="/services/", extra_head=SVC_HEAD)

# Detail pages
for x in SERVICES:
    others = "".join(f'''<a class="gh-link" href="{o["path"]}">{o["name"].replace("&","&amp;")} {ARROW}</a>''' for o in ALL if o is not x)
    def _slug(t): return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")
    caps = "".join(f'<article class="gh-capability">{svc_photo(x["key"] + "-" + _slug(t), t, t, cls="gh-capability-photo")}<h3 class="gh-h4">{t}</h3><p>{d}</p></article>' for t, d in DETAILS[x["slug"]])
    capcls = "gh-capabilities is-" + str(len(DETAILS[x["slug"]]))
    hero_ext = "webp"
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
{more_services(x["path"])}
</main>
{quote_band()}'''
    page(x["path"], x["title"], x["desc"], (body,), current="/services/", transparent=True, extra_head=svc_ld(x))

# ---------------------------------------------------------------- AUDIENCE PAGES (commercial / residential painting)
_AUD_BY_PATH = {a["path"]: a for a in AUDIENCES}

for a in AUDIENCES:
    who = "".join(f'<li>{ico}<h3>{t}</h3><p>{d}</p></li>' for t, ico, d in a["cards"])
    def _cap_photo(k, t, alt):
        if k.endswith(".webp") and os.path.exists(os.path.join(ROOT, "assets", "img", "projects", k)):
            return f'<div class="gh-photo gh-capability-photo"><img class="gh-photo-img" src="/assets/img/projects/{k}" alt="{alt}" width="800" height="600" loading="lazy" decoding="async" onerror="this.remove()"></div>'
        return svc_photo(k, t, t, cls="gh-capability-photo")
    caps = "".join(f'<article class="gh-capability">{_cap_photo(c[2], c[0], c[3] if len(c) > 3 else c[0])}<h3 class="gh-h4">{c[0]}</h3><p>{c[1]}</p></article>' for c in a["caps"])
    steps = "".join(f'<li><h3>{t}</h3><p>{d}</p></li>' for t, d in a["steps"])
    work = a.get("work")
    work_html = ""
    if work:
        figs = "".join(f'<figure><button type="button" class="gh-work-open" data-full="/assets/img/projects/{f}" data-caption="{cap}" aria-label="View larger: {alt}"><img src="/assets/img/projects/{f}" alt="{alt}" width="680" height="510" loading="lazy" decoding="async"></button><figcaption>{cap}</figcaption></figure>' for f, alt, cap in work)
        work_html = f'''<section class="gh-section gh-section-alt" aria-labelledby="work-h"><div class="gh-container">
  <div class="gh-section-head"><p class="gh-eyebrow">Recent work</p><h2 class="gh-h2" id="work-h">{a["work_h"]}</h2></div>
  <div class="gh-work">{figs}<div class="gh-work-cta"><h3 class="gh-h4">Planning a project?</h3><p>Share the scope, location and timeline. We respond within one business day.</p><a class="gh-link" href="/contact/">Request a quote {ARROW}</a></div></div>
</div></section>
'''
    steps_cls = "gh-section" if work else "gh-section gh-section-alt"
    rel_cls = "gh-section gh-section-alt" if work else "gh-section"
    rel = f'<a class="gh-link" href="{a["sibling"]}">{_AUD_BY_PATH[a["sibling"]]["name"]} {ARROW}</a>'
    rel += "".join(f'<a class="gh-link" href="{p}">{_SVC_BY_PATH[p]["name"].replace("&","&amp;")} {ARROW}</a>' for p in a["related"])
    rel += f'<a class="gh-link" href="/services/">All services {ARROW}</a>'
    img_ok = os.path.exists(os.path.join(ROOT, "assets", "img", a["img"]))
    photo = (f'<img class="gh-photo-img" src="/assets/img/{a["img"]}" alt="" width="1672" height="941" fetchpriority="high" onerror="this.remove()">' if img_ok else "")
    hero = f'''<section class="gh-hero gh-hero-service gh-inverse gh-on-image">
  <div class="gh-photo" aria-hidden="true">{photo}<div class="gh-hero-veil"></div></div>
  <div class="gh-hero-inner">
    {header("/services/", transparent=True, here=a["path"])}
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
    <div><p class="gh-eyebrow">Overview</p><h2 class="gh-h2" style="margin-top:16px">{a["name"]}.</h2></div>
    <div class="gh-prose"><p class="gh-body-lg">{a["lede"]}</p>
    <p><a class="gh-link" href="/contact/">Request a quote {ARROW}</a></p></div>
  </div>
</div></section>
<section class="gh-section gh-section-alt" aria-labelledby="aud-h"><div class="gh-container">
  <div class="gh-section-head"><p class="gh-eyebrow">{a["cards_eyebrow"]}</p><h2 class="gh-h2" id="aud-h">{a["cards_h"]}</h2></div>
  <ul class="gh-why">{who}</ul>
</div></section>
<section class="gh-section" aria-labelledby="cap-h"><div class="gh-container">
  <div class="gh-section-head"><p class="gh-eyebrow">Scope</p><h2 class="gh-h2" id="cap-h">{a["name"]}, in detail.</h2></div>
  <div class="gh-capabilities is-{len(a["caps"])}">{caps}</div>
</div></section>
{work_html}<section class="{steps_cls}" aria-labelledby="steps-h"><div class="gh-container">
  <div class="gh-section-head"><p class="gh-eyebrow">Our process</p><h2 class="gh-h2" id="steps-h">{a["steps_h"]}</h2></div>
  <ol class="gh-method gh-method-plain is-4" aria-label="{a["steps_h"]}">{steps}</ol>
</div></section>
{more_services(a["path"], rel_cls)}
</main>
{quote_band()}'''
    cat = {"@type":"OfferCatalog","name":a["name"]+" services","itemListElement":[
        {"@type":"Offer","itemOffered":{"@type":"Service","name":t,"description":d}} for t,d,*_ in a["caps"]]}
    ld = '<script type="application/ld+json">' + json.dumps({"@context":"https://schema.org","@type":"Service","name":a["stype"],"serviceType":a["stype"],
        "url":SITE+a["path"],"description":a["desc"],"provider":{"@id":SITE+"/#business"},"areaServed":{"@type":"State","name":"Florida"},
        "audience":{"@type":"Audience","audienceType":a["audience"]},"hasOfferCatalog":cat}, separators=(",",":")) + '</script>\n'
    page(a["path"], a["title"], a["desc"], (body,), current="/services/", transparent=True, extra_head=ld)

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
about_body = f'''<main id="main" class="gh-about">
<section class="gh-band gh-inverse gh-on-image" style="--band-img:url(/assets/img/about-bg.svg)"><div class="gh-container"><p class="gh-eyebrow">About</p><h1 class="gh-h1">A finishing company built on one standard.</h1><p class="gh-body-lg">Direct, accountable and careful with every surface.</p></div></section>
<section class="gh-section gh-story" aria-labelledby="story-h"><div class="gh-container">
  <div class="gh-two-col">
    <div>{title_block('compass','Our story','Four disciplines. One team.','story-h')}</div>
    <div class="gh-prose">
      <p class="gh-body-lg">Grand Hill brings architecture, engineering, finance and operations into one team, so every project is planned, priced and delivered with the same care.</p>
      <p>We came together in Orlando around one commitment: executing high-quality projects. Each of us owns a part of the work, and together we answer for the result.</p>
    </div>
  </div>
  <ul class="gh-disc" aria-label="What each discipline brings">
    <li>{ico('building','gh-ico gh-ico-line')}<h3>Architecture</h3><p>Experience leading large-scale projects, from design intent to completion.</p></li>
    <li>{ico('gear','gh-ico gh-ico-line')}<h3>Engineering</h3><p>An eye for how a building is built and how finishes perform on it.</p></li>
    <li>{ico('chart','gh-ico gh-ico-line')}<h3>Finance</h3><p>Clear estimates and honest numbers, with no surprises.</p></li>
    <li>{ico('flow','gh-ico gh-ico-line')}<h3>Operations</h3><p>Systems and communication that keep you informed from walkthrough to handoff.</p></li>
  </ul>
</div></section>

<section class="gh-section gh-section-alt" aria-labelledby="how-h"><div class="gh-container">
  <div class="gh-two-col gh-how">
    <figure class="gh-how-photo"><img src="/assets/img/projects/residential-04.webp" alt="Open living room with vaulted ceiling, skylights and freshly painted walls" width="800" height="600" loading="lazy" decoding="async"></figure>
    <div class="gh-prose">{title_block('clipboard','How we work','From walkthrough to handoff.','how-h')}
    <p class="gh-body-lg">Every project is planned, directed and inspected by Grand Hill, from the first walkthrough to the final handoff. We answer for the result.</p>
    <p>You have one point of contact throughout. Scope, finishes and schedule are confirmed in writing before work begins.</p>
    <p><a class="gh-link" href="/contact/">Request a quote {ARROW}</a></p></div>
  </div>
  <ol class="gh-steps">
    <li><h3>{ico('ruler','gh-ico gh-ico-inline')}Scope</h3><p>We walk the site, confirm surfaces, substrates and finish specifications, and note access constraints.</p></li>
    <li><h3>{ico('doc','gh-ico gh-ico-inline')}Estimate</h3><p>A clear written estimate with scope, exclusions and schedule. No surprises in the numbers.</p></li>
    <li><h3>{ico('roller','gh-ico gh-ico-inline')}Execute</h3><p>The work follows a schedule built around the building and its occupants.</p></li>
    <li><h3>{ico('search','gh-ico gh-ico-inline')}Inspect</h3><p>We inspect against the specification, correct anything that falls short and hand off.</p></li>
  </ol>
</div></section>

<section class="gh-section" aria-labelledby="team-h"><div class="gh-container">
  <div class="gh-section-head">{title_block('users','Leadership','The people behind Grand Hill.','team-h')}</div>
  <div class="gh-cards-2">
    <article class="gh-person"><span class="gh-mono" aria-hidden="true">JC</span><h3>Julio Adiel Canelo</h3><p class="gh-label">Co-Founder · Commercial Director</p><p>Brings projects and client relationships. Leads safety and supervises work in the field.</p></article>
    <article class="gh-person"><span class="gh-mono" aria-hidden="true">AG</span><h3>Adrian Gerig</h3><p class="gh-label">Co-Founder · Operations Director</p><p>Leads administration, project management and client communication.</p></article>
    <article class="gh-person"><span class="gh-mono" aria-hidden="true">SD</span><h3>Servia Dietsch</h3><p class="gh-label">Director of Project Delivery</p><p>Architectural background and hands-on experience running large construction projects. Oversees plans, specifications and quality.</p></article>
    <article class="gh-person"><span class="gh-mono" aria-hidden="true">ST</span><h3>Susana Tomasicchio</h3><p class="gh-label">Director of Finance</p><p>Leads finance, budgeting and cost control across every project.</p></article>
  </div>
</div></section>

<section class="gh-section gh-section-alt" aria-labelledby="area-h"><div class="gh-container"><div class="gh-two-col gh-area">
  <div class="gh-prose">
    {title_block('pin','Service area','All of Florida.','area-h')}
    <p class="gh-body-lg">We are based in Central Florida and take on commercial and residential projects across the state.</p>
    <ul class="gh-regions" aria-label="Regions we serve"><li class="is-base">Central Florida <span>our base</span></li><li>North Florida</li><li>Panhandle</li><li>Tampa Bay</li><li>Southwest Florida</li><li>South Florida</li></ul>
    <p>Not sure whether your project is in range? <a href="/contact/" style="color:var(--ink);text-underline-offset:4px;text-decoration-color:var(--accent);text-decoration-thickness:2px">Ask us.</a></p>
  </div>
  <figure class="gh-map"><svg viewBox="0 0 720 696" role="img" aria-labelledby="map-t"><title id="map-t">Map of Florida. Grand Hill serves the whole state and is based in Central Florida.</title>
    <path class="gh-map-land" d="M252 10 L254 17 L258 22 L261 36 L265 40 L509 55 L507 56 L508 61 L510 64 L509 70 L513 77 L525 76 L528 54 L524 46 L525 36 L528 35 L527 33 L531 33 L534 28 L538 29 L541 32 L546 32 L555 37 L571 40 L576 39 L581 42 L580 52 L581 60 L580 62 L583 64 L585 83 L592 118 L597 129 L597 134 L606 161 L626 207 L648 244 L660 262 L665 275 L659 280 L657 285 L657 293 L661 313 L678 350 L690 388 L704 425 L710 448 L710 469 L702 533 L701 555 L699 566 L697 564 L698 560 L696 558 L691 560 L688 569 L686 571 L682 587 L684 590 L683 594 L685 596 L682 600 L680 602 L679 606 L686 603 L694 585 L697 581 L697 585 L680 620 L660 641 L652 647 L652 645 L667 631 L672 616 L670 614 L667 615 L665 613 L663 614 L652 616 L644 620 L638 616 L632 618 L630 621 L621 623 L613 623 L608 619 L605 613 L608 600 L610 600 L609 596 L605 587 L602 583 L602 580 L600 575 L596 572 L594 564 L592 562 L589 564 L586 555 L578 552 L564 542 L560 543 L557 547 L547 522 L545 507 L541 492 L532 482 L528 481 L528 476 L524 474 L524 480 L519 481 L516 465 L512 460 L513 458 L517 459 L520 462 L524 448 L523 440 L521 439 L521 435 L523 434 L522 432 L518 432 L516 435 L513 436 L515 449 L506 452 L504 456 L504 450 L502 445 L488 421 L479 400 L465 382 L460 371 L464 373 L464 375 L469 373 L472 366 L476 364 L481 355 L485 352 L484 350 L489 347 L493 340 L491 333 L484 331 L485 341 L478 339 L480 336 L478 326 L465 320 L466 326 L462 328 L466 332 L471 332 L475 342 L471 346 L470 354 L463 354 L462 357 L464 361 L461 363 L460 360 L461 352 L451 337 L453 321 L450 300 L453 300 L454 316 L457 317 L456 303 L458 300 L464 285 L464 281 L467 277 L469 261 L467 255 L467 250 L463 248 L464 244 L461 234 L465 229 L458 219 L459 216 L457 211 L454 211 L455 208 L455 203 L437 200 L434 205 L432 205 L429 196 L430 192 L421 188 L420 183 L415 173 L410 173 L408 169 L400 165 L399 149 L395 148 L391 145 L387 143 L383 138 L383 134 L378 126 L374 122 L351 110 L342 104 L330 107 L320 104 L320 107 L311 113 L314 122 L313 125 L305 124 L303 122 L295 124 L263 142 L262 142 L264 138 L261 137 L253 144 L241 144 L246 148 L246 152 L252 154 L271 145 L280 138 L281 139 L273 146 L248 157 L232 148 L226 147 L220 150 L216 141 L214 131 L217 127 L217 136 L219 145 L221 147 L224 143 L225 134 L219 125 L213 120 L208 118 L197 108 L188 104 L168 90 L133 76 L102 73 L91 74 L54 80 L41 81 L21 85 L26 83 L23 81 L26 79 L29 72 L35 69 L28 64 L27 59 L32 50 L31 44 L19 37 L18 33 L11 26 L10 24 L14 14 L13 10 Z M546 681 L552 671 L559 667 L567 663 L568 661 L580 655 L593 661 L594 666 L599 670 L597 671 L584 675 L583 673 L574 673 L573 675 L558 682 L546 683 Z M504 459 L506 460 L512 479 L515 482 L521 484 L523 482 L528 484 L523 487 L520 487 L513 483 L511 480 L506 470 L504 463 Z M610 666 L627 658 L629 661 L614 668 Z M528 683 L540 681 L537 685 L532 686 L527 686 Z"/>
    <g class="gh-map-dots" aria-hidden="true"><circle cx="48" cy="71" r="5"/><circle cx="319" cy="68" r="5"/><circle cx="560" cy="80" r="5"/><circle cx="499" cy="151" r="5"/><circle cx="486" cy="328" r="5"/><circle cx="541" cy="465" r="5"/><circle cx="696" cy="556" r="5"/><circle cx="192" cy="98" r="5"/></g>
    <g aria-hidden="true"><circle class="gh-map-halo" cx="586" cy="267" r="26"/><circle class="gh-map-base" cx="586" cy="267" r="9"/></g>
  </svg><figcaption><span class="gh-map-key"><i class="is-base"></i>Our base, Central Florida</span><span class="gh-map-key"><i></i>Projects across the state</span></figcaption></figure>
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
<section class="gh-band gh-band-sm gh-inverse gh-on-image" style="--band-img:url(/assets/img/contact-bg.svg)"><div class="gh-container"><p class="gh-eyebrow">Contact</p><h1 class="gh-h1">Request a quote.</h1><p class="gh-body-lg">Tell us about the project. We respond within one business day.</p></div></section>
<section class="gh-section gh-section-alt gh-contact-section"><div class="gh-container"><div class="gh-contact">
  <div class="gh-form-card">
    <h2 class="gh-h3">Tell us about the project</h2>
    <p class="gh-form-intro">Six quick fields. We reply within one business day.</p>
    <form id="quote-form" class="gh-form" name="quote" method="POST" action="/thank-you/" data-netlify="true" netlify-honeypot="bot-field" novalidate>
      <input type="hidden" name="form-name" value="quote">
      <p class="gh-hp" aria-hidden="true"><label>Leave this field empty <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
      {field("name", "Name", req=True, autocomplete="name")}
      {field("email", "Email", "email", req=True, autocomplete="email")}
      {field("phone", "Phone (optional)", "tel", autocomplete="tel")}
      <div class="gh-field"><label class="gh-field-label" for="service">Service <span class="req" aria-hidden="true">*</span></label>
        <select class="gh-select" id="service" name="service" required><option value="">Select a service</option><option>Commercial painting</option><option>Residential painting</option><option>Finishes and surface care</option><option>Interiors and flooring</option><option>Other</option><option>Not sure yet</option></select></div>
      {field("location", "Project city", req=True, span2=True, autocomplete="address-level2", placeholder="City, Florida")}
      <div class="gh-field gh-span-2"><label class="gh-field-label" for="details">Project details <span class="req" aria-hidden="true">*</span></label>
        <textarea class="gh-textarea" id="details" name="details" required placeholder="Company (if any), what needs to be done, approximate size and timeline."></textarea>
        <p class="gh-help">Plans or specifications help, but are not needed to start.</p></div>
      <div class="gh-span-2"><button class="gh-btn gh-btn-primary" type="submit">Send request {ARROW}</button><div id="form-status" class="gh-form-status" aria-live="polite"></div></div>
    </form>
    <div id="form-success" class="gh-form-success" role="status" tabindex="-1" hidden>{CHECK}<div><strong>Request received.</strong><p>Thank you. We will respond within one business day.</p></div></div>
  </div>
  <aside class="gh-contact-side" aria-label="Contact details">
    <div class="gh-side-photo"><img src="/assets/img/projects/residential-01.webp" alt="Two-story gray stucco home with dark shutters and landscaped grounds" width="800" height="450" loading="lazy" decoding="async"></div>
    <h2 class="gh-h4">What happens next</h2>
    <ol class="gh-next">
      <li><strong>We review your request.</strong> You hear from us within one business day.</li>
      <li><strong>We walk the site.</strong> We confirm surfaces, access and finish specifications.</li>
      <li><strong>You receive a written estimate.</strong> Scope, exclusions and schedule, in writing.</li>
    </ol>
    <h2 class="gh-h4">Direct contact</h2>
    <dl>
      {('<dt class="gh-label">Phone</dt><dd>' + PHONE + "</dd>") if PHONE else ""}
      <dt class="gh-label">Email</dt><dd><a class="gh-soc-link" href="mailto:{EMAIL}">{SOC["mail"]}{EMAIL}</a></dd>
      <dt class="gh-label">Follow</dt><dd class="gh-side-social">{('<a class="gh-soc-link" href="' + INSTAGRAM + '" target="_blank" rel="noopener">' + SOC["instagram"] + 'Instagram</a>') if INSTAGRAM else ""}{('<a class="gh-soc-link" href="' + FACEBOOK + '" target="_blank" rel="noopener">' + SOC["facebook"] + 'Facebook</a>') if FACEBOOK else ""}</dd>
      <dt class="gh-label">Service area</dt><dd>Florida, commercial and residential</dd>
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


# ---------------------------------------------------------------- PRIVACY
privacy = f'''<main id="main">
{page_head("Legal", "Privacy policy.", "How Grand Hill, LLC handles the information you share with us. Effective November 18, 2026.")}
<section class="gh-section"><div class="gh-container"><div class="gh-prose gh-legal-doc">
<h2 class="gh-h3">Who we are</h2>
<p>This website is operated by Grand Hill, LLC ("Grand Hill", "we", "us"), a Florida company. You can reach us at <a class="gh-link" href="mailto:{EMAIL}">{EMAIL}</a>.</p>

<h2 class="gh-h3">What we collect</h2>
<p><strong>Information you send us.</strong> When you request a quote, we receive your name, email address, project city, the service you are asking about, your project details, and your phone number if you choose to give it. We use it to respond to your request, prepare an estimate and manage the project if you hire us.</p>
<p><strong>Information collected automatically.</strong> We use Google Analytics to understand how the site is used. It records things like the pages you visit, approximate location (city level), device and browser type, and how you arrived at the site. It uses cookies or similar technologies to do this. We do not use it to identify you personally.</p>
<p><strong>Technical logs.</strong> Our hosting provider keeps standard server logs, such as IP address and request time, for security and reliability.</p>

<h2 class="gh-h3">How we use it</h2>
<p>We use the information to answer your inquiry, provide estimates and services, operate and improve the website, keep it secure, and meet legal and accounting obligations. We do not sell your personal information, and we do not use it for advertising profiles.</p>

<h2 class="gh-h3">Who we share it with</h2>
<p>We share information only with service providers that help us run the site and handle your request, such as website hosting and form processing (Netlify), analytics (Google), and email. We may also share what is needed to carry out your project, and where required by law. These providers may only use the information for the services they perform for us.</p>

<h2 class="gh-h3">Cookies and analytics choices</h2>
<p>You can block or delete cookies in your browser settings, and you can opt out of Google Analytics with the <a class="gh-link" href="https://tools.google.com/dlpage/gaoptout" target="_blank" rel="noopener">Google Analytics opt-out browser add-on</a>. The site works the same way if you do.</p>

<h2 class="gh-h3">How long we keep it</h2>
<p>We keep quote requests and project records for as long as needed to respond to you, complete any work and meet business and legal requirements, and then delete or anonymize them. Analytics data is kept for the period set in our Google Analytics account.</p>

<h2 class="gh-h3">Your choices</h2>
<p>You can ask us to tell you what personal information we hold about you, correct it, or delete it, by emailing <a class="gh-link" href="mailto:{EMAIL}">{EMAIL}</a>. We will respond within a reasonable time.</p>

<h2 class="gh-h3">Security</h2>
<p>The site is served over HTTPS and we limit access to the information you send us. No method of transmission or storage is completely secure, so we cannot guarantee absolute security.</p>

<h2 class="gh-h3">Children</h2>
<p>This site is intended for adults and businesses. We do not knowingly collect information from children under 13.</p>

<h2 class="gh-h3">Other websites</h2>
<p>Our pages link to other sites, such as Instagram and Facebook. Their privacy practices are their own, and this policy does not cover them.</p>

<h2 class="gh-h3">Changes to this policy</h2>
<p>If we change this policy, we will post the new version on this page and update the effective date above.</p>

<h2 class="gh-h3">Contact</h2>
<p>Questions about this policy? Email <a class="gh-link" href="mailto:{EMAIL}">{EMAIL}</a>.</p>
</div></div></section>
</main>'''
page("/privacy/", "Privacy Policy | Grand Hill", "How Grand Hill, LLC collects, uses and protects the information you share through this website.", privacy)

# ---------------------------------------------------------------- robots + sitemap
urls = ["/", "/services/"] + [x["path"] for x in ALL] + (["/projects/"] if SHOW_PROJECTS else []) + ["/about/", "/contact/", "/privacy/"]
with open(os.path.join(ROOT, "sitemap.xml"), "w") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "".join(f"  <url><loc>{SITE}{u}</loc><lastmod>{datetime.date.today().isoformat()}</lastmod></url>\n" for u in urls) + "</urlset>\n")
with open(os.path.join(ROOT, "robots.txt"), "w") as f:
    f.write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
print("ok")
