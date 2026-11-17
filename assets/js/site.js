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
        form.hidden = true;
        document.getElementById('form-success').hidden = false;
        document.getElementById('form-success').focus();
      })
      .catch(function () {
        submit.disabled = false;
        status.innerHTML = '<p class="gh-error" role="alert">' + ICON_ALERT + '<span>We could not send your request. Please try again or email us directly.</span></p>';
      });
  });
})();

/* Home hero background video: starts only for visitors who can take it (no reduced motion, no data saver, not a small screen); sources are never fetched otherwise. */
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
