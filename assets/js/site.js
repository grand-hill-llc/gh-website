/* Grand Hill: mobile menu and quote form handling. No dependencies. */
(function () {
  var btn = document.querySelector('.gh-menu-btn');
  var nav = document.getElementById('site-nav');
  var header = document.querySelector('.gh-header');
  if (btn && nav) {
    var setOpen = function (open) {
      nav.classList.toggle('is-open', open);
      header.classList.toggle('is-open', open);
      btn.setAttribute('aria-expanded', String(open));
      btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
      btn.querySelector('.i-menu').toggleAttribute('hidden', open);
      btn.querySelector('.i-close').toggleAttribute('hidden', !open);
    };
    btn.addEventListener('click', function () { setOpen(btn.getAttribute('aria-expanded') !== 'true'); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { setOpen(false); btn.focus(); } });
    window.addEventListener('resize', function () { if (window.innerWidth > 960) setOpen(false); });
  }


  /* Services dropdown: toggle for touch and keyboard (hover and focus also open it on desktop) */
  var subItem = document.querySelector('.gh-nav-item.has-sub');
  var subBtn = subItem && subItem.querySelector('.gh-sub-toggle');
  if (subItem && subBtn) {
    var setSub = function (open) { subItem.classList.toggle('is-open', open); subBtn.setAttribute('aria-expanded', String(open)); };
    subBtn.addEventListener('click', function (e) { e.stopPropagation(); setSub(!subItem.classList.contains('is-open')); });
    document.addEventListener('click', function (e) { if (!subItem.contains(e.target)) setSub(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setSub(false); });
  }

  /* Header turns solid once the page has scrolled */
  if (header) {
    var onScroll = function () { header.classList.toggle('is-stuck', window.scrollY > 8); };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* Scroll reveal for blocks below the fold (skipped for reduced motion) */
  if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    var targets = document.querySelectorAll('.gh-section-head, .gh-prose, .gh-method li, .gh-cards-3, .gh-featured, .gh-testimonial, .gh-cta-band-inner, .gh-steps li, .gh-person, .gh-service-row, .gh-project, .gh-contact > div');
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    targets.forEach(function (el, i) {
      if (el.getBoundingClientRect().top < window.innerHeight) return;
      el.style.setProperty('--d', ((i % 3) * 0.08) + 's');
      el.classList.add('gh-reveal'); io.observe(el);
    });
  }

  var form = document.getElementById('quote-form');
  if (!form) return;
  var status = document.getElementById('form-status');
  var ICON_ALERT = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v6M12 16v1"/></svg>';

  function setError(field, msg) {
    var wrap = field.closest('.gh-field');
    var old = wrap.querySelector('.gh-error');
    if (old) old.remove();
    wrap.classList.toggle('is-error', !!msg);
    field.setAttribute('aria-invalid', msg ? 'true' : 'false');
    if (msg) {
      var p = document.createElement('p');
      p.className = 'gh-error'; p.id = field.id + '-error'; p.innerHTML = ICON_ALERT + '<span></span>';
      p.lastChild.textContent = msg;
      wrap.appendChild(p);
      field.setAttribute('aria-describedby', p.id);
    } else { field.removeAttribute('aria-describedby'); }
  }
  function validate(field) {
    var v = field.value.trim();
    if (field.required && !v) { setError(field, 'This field is required.'); return false; }
    if (field.type === 'email' && v && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) { setError(field, 'Enter a valid email address.'); return false; }
    setError(field, ''); return true;
  }
  var fields = Array.prototype.slice.call(form.querySelectorAll('input:not([type=hidden]):not(.gh-hp input), select, textarea')).filter(function (f) { return !f.closest('.gh-hp'); });
  fields.forEach(function (f) { f.addEventListener('input', function () { if (f.closest('.gh-field').classList.contains('is-error') && f.value.trim()) setError(f, ''); }); });
  fields.forEach(function (f) { f.addEventListener('blur', function () { if (f.value || f.closest('.gh-field').classList.contains('is-error')) validate(f); }); });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var bad = fields.filter(function (f) { return !validate(f); });
    if (bad.length) { bad[0].focus(); return; }
    var submit = form.querySelector('button[type=submit]');
    submit.disabled = true;
    fetch('/', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: new URLSearchParams(new FormData(form)).toString() })
      .then(function (r) { if (!r.ok) throw new Error('bad status'); })
      .then(function () {
        /* Go to the thank-you page so analytics can count the lead; keep the in-page message if the redirect is blocked. */
        window.location.assign('/thank-you/');
        setTimeout(function () {
          form.hidden = true;
          document.getElementById('form-success').hidden = false;
          document.getElementById('form-success').focus();
        }, 1500);
      })
      .catch(function () {
        submit.disabled = false;
        status.innerHTML = '<p class="gh-error" role="alert">' + ICON_ALERT + '<span>We could not send your request. Please try again or email us directly.</span></p>';
      });
  });
})();

/* Decorative hero backgrounds; text stays steady while photographs dissolve. */
(function () {
  var hero = document.querySelector('[data-hero-carousel]');
  if (!hero) return;
  var slides = Array.from(hero.querySelectorAll('.gh-hero-slide'));
  var controls = hero.querySelector('.gh-carousel-controls');
  var dots = Array.from(hero.querySelectorAll('[data-hero-go]'));
  var pause = hero.querySelector('.gh-carousel-pause');
  var motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  var connection = navigator.connection || {};
  var paused = motion.matches || connection.saveData || /(^|-)2g$/.test(connection.effectiveType || '');
  var current = 0, timer, request = 0;
  function schedule() {
    clearTimeout(timer);
    if (!paused && !document.hidden) timer = setTimeout(function () { show((current + 1) % slides.length); }, 7000);
  }
  async function show(index) {
    var ticket = ++request;
    var image = slides[index];
    if (!image.src) image.src = image.dataset.src;
    try { await image.decode(); } catch (_) { schedule(); return; }
    if (ticket !== request) return;
    slides[current].classList.remove('is-active');
    image.classList.add('is-active');
    current = index;
    dots.forEach(function (dot, i) { dot.setAttribute('aria-pressed', String(i === index)); });
    schedule();
  }
  function updatePause() {
    pause.textContent = paused ? 'Play' : 'Pause';
    pause.setAttribute('aria-label', paused ? 'Play slideshow' : 'Pause slideshow');
    pause.setAttribute('aria-pressed', String(paused));
    schedule();
  }
  dots.forEach(function (dot, i) { dot.addEventListener('click', function () { paused = true; updatePause(); show(i); }); });
  pause.addEventListener('click', function () { paused = !paused; updatePause(); });
  hero.addEventListener('focusin', function (event) { if (event.target !== pause) { paused = true; updatePause(); } });
  document.addEventListener('visibilitychange', schedule);
  motion.addEventListener('change', function () { if (motion.matches) { paused = true; updatePause(); } });
  controls.hidden = false;
  updatePause();
})();

/* Optional legacy video support on other hero layouts. */
(function () {
  var video = document.querySelector('[data-hero-video]');
  var btn = document.querySelector('[data-hero-pause]');
  if (!video) return;
  var conn = navigator.connection || {};
  var skip = window.matchMedia('(prefers-reduced-motion: reduce)').matches ||
    conn.saveData || /(^|-)2g$/.test(conn.effectiveType || '') ||
    window.matchMedia('(max-width: 768px)').matches;
  if (skip) { video.remove(); if (btn) btn.remove(); return; }
  var drop = function () { video.remove(); if (btn) btn.remove(); };
  var srcs = video.querySelectorAll('source');
  if (srcs.length) srcs[srcs.length - 1].addEventListener('error', drop);
  video.addEventListener('error', drop);
  video.preload = 'auto';
  video.load();
  var p = video.play();
  var started = function () {
    video.classList.add('is-playing');
    if (btn) btn.hidden = false;
  };
  if (p && p.then) p.then(started).catch(drop);
  else started();
  if (btn) btn.addEventListener('click', function () {
    var paused = btn.getAttribute('aria-pressed') === 'true';
    if (paused) { video.play(); btn.setAttribute('aria-pressed', 'false'); btn.setAttribute('aria-label', 'Pause background video'); }
    else { video.pause(); btn.setAttribute('aria-pressed', 'true'); btn.setAttribute('aria-label', 'Play background video'); }
  });
})();

/* Recent work lightbox: native <dialog>, arrow keys, backdrop click, focus returns to the thumbnail. */
(function () {
  var openers = Array.prototype.slice.call(document.querySelectorAll('.gh-work-open'));
  if (!openers.length || typeof HTMLDialogElement === 'undefined') return;
  var dlg = document.createElement('dialog');
  dlg.className = 'gh-lightbox';
  dlg.setAttribute('aria-label', 'Image viewer');
  dlg.innerHTML = '<button type="button" class="gh-lightbox-btn gh-lightbox-close" aria-label="Close">&times;</button>' +
    '<button type="button" class="gh-lightbox-btn gh-lightbox-prev" aria-label="Previous image">&#8249;</button>' +
    '<figure class="gh-lightbox-fig"><img alt=""><figcaption></figcaption></figure>' +
    '<button type="button" class="gh-lightbox-btn gh-lightbox-next" aria-label="Next image">&#8250;</button>';
  document.body.appendChild(dlg);
  var img = dlg.querySelector('img'), cap = dlg.querySelector('figcaption');
  var prev = dlg.querySelector('.gh-lightbox-prev'), next = dlg.querySelector('.gh-lightbox-next');
  var cur = 0, opener = null;
  var show = function (i) {
    cur = (i + openers.length) % openers.length;
    var o = openers[cur], t = o.querySelector('img');
    img.src = o.getAttribute('data-full');
    img.alt = t ? t.alt : '';
    cap.textContent = o.getAttribute('data-caption') || '';
  };
  openers.forEach(function (o, i) {
    o.addEventListener('click', function () {
      opener = o; show(i);
      prev.hidden = next.hidden = openers.length < 2;
      dlg.showModal();
      document.documentElement.style.overflow = 'hidden';
    });
  });
  prev.addEventListener('click', function () { show(cur - 1); });
  next.addEventListener('click', function () { show(cur + 1); });
  dlg.querySelector('.gh-lightbox-close').addEventListener('click', function () { dlg.close(); });
  dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
  dlg.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowLeft') { show(cur - 1); e.preventDefault(); }
    else if (e.key === 'ArrowRight') { show(cur + 1); e.preventDefault(); }
  });
  dlg.addEventListener('close', function () {
    document.documentElement.style.overflow = '';
    if (opener) opener.focus();
  });
})();
