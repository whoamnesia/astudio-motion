/*
astudio site motion - total choreography for showcase sites (reference/site-motion.md as code).

Every visible element gets a reveal from one vocabulary, on one set of tokens, so the whole page speaks one motion
language. Mark elements with data-reveal="<type>":
  heading     SplitText lines+words in line masks (data-split="chars" adds chars)   h1/h2/h3, footer wordmark
  lines       body paragraphs, line by line in masks
  words       eyebrows, labels, nav links, short phrases
  button      clip wipe from the left + label rises; hover = label roll; magnetic on fine pointers
  image       container clip wipe up + inner image scale + scroll parallax (data-parallax="0" turns it off)
  hero-image  the LCP photo: visible at frame 0, partial clip + scale only
  cards       grid items, revealed in batches
  rows        a list/table/menu container: its rows one by one, [data-reveal-value] children follow from the right
  icon        stroked SVG draws (DrawSVG), filled icons scale + rotate in
  count       numbers count up (keeps prefix/suffix)
  rule        dividers scale in from the left
  badge       drops in, then turns with scroll (data-spin="90")
  header      fixed header: slides in during the intro, hides on scroll down (data-autohide)
  marquee     a container with [data-marquee-track] (content duplicated once): speed follows scroll velocity
  fade        fallback: rise + fade
Elements inside [data-hero] play on the intro timeline (order by type, override with data-at="0.4"); the rest
reveal once at "top 85%". Do not nest data-reveal elements (inner ones are left alone and stay visible).
Maps: SiteMotion.map(svgOrContainer) - see the attribute list above map() below and reference/site-motion.md §6.

Setup (static page, GSAP 3.13+ - all plugins are free):
  <script>document.documentElement.classList.add('sm-js');setTimeout(function(){var d=document.documentElement;
    if(!d.classList.contains('sm-ready'))d.classList.add('sm-off')},3000)</script>          (inline, in <head>)
  <link rel="stylesheet" href="site-motion.css">
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
  ... ScrollTrigger.min.js, SplitText.min.js, DrawSVGPlugin.min.js, MotionPathPlugin.min.js (same folder)
  <script src="https://unpkg.com/lenis@1.3.27/dist/lenis.min.js"></script>               (optional smooth scroll)
  <script src="site-motion.js"></script>
  <script>SiteMotion.init();</script>
Bundlers: import gsap and the plugins, assign them to window (window.gsap = gsap; window.ScrollTrigger = ...),
then import this file - or port init() into a useGSAP() hook (React) / onMounted (Vue) and call revert() on unmount.
*/
(function (root) {
  'use strict';
  var T = {
    reveal: 'expo.out', soft: 'power3.out', move: 'power4.inOut', draw: 'sine.inOut',
    text: 1.2, lines: 1.1, media: 1.4, mediaScale: 1.9, block: 1.1, hover: 0.55,
    sChars: 0.02, sWords: 0.05, sLines: 0.09, sRows: 0.06, sCards: 0.1,
    start: 'top 85%', batchStart: 'top 90%'
  };
  var INTRO_AT = { 'hero-image': 0, heading: 0, words: 0.2, lines: 0.35, button: 0.55, icon: 0.6, count: 0.6, rows: 0.6,
    cards: 0.65, badge: 0.75, image: 0.45, rule: 0.5, fade: 0.6, header: 0.5, marquee: 0.9 };

  function $all(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }
  function radius(el) { var r = getComputedStyle(el).borderRadius; return r && r !== '0px' ? ' round ' + r : ''; }
  function show(el) { gsap.set(el, { autoAlpha: 1 }); }

  // ---------- builders: each returns a tween/timeline (paused when placed on the intro timeline) ----------
  function split(el, type, mask) {
    if (!root.SplitText) return null;
    return SplitText.create(el, { type: type, mask: mask, linesClass: 'sm-line', wordsClass: 'sm-word', charsClass: 'sm-char' });
  }
  var B = {
    heading: function (el) {
      var chars = el.getAttribute('data-split') === 'chars', s = split(el, chars ? 'lines,words,chars' : 'lines,words', 'lines');
      show(el);
      if (!s) return gsap.from(el, { y: 40, autoAlpha: 0, duration: T.text, ease: T.reveal });
      return gsap.from(chars ? s.chars : s.words, { yPercent: 110, rotate: 5, transformOrigin: '0% 100%', duration: T.text,
        ease: T.reveal, stagger: chars ? T.sChars : T.sWords, onComplete: function () { s.revert(); } });
    },
    lines: function (el) {
      var s = split(el, 'lines', 'lines'); show(el);
      if (!s) return gsap.from(el, { y: 30, autoAlpha: 0, duration: T.lines, ease: T.reveal });
      return gsap.from(s.lines, { yPercent: 100, autoAlpha: 0, duration: T.lines, ease: T.reveal, stagger: T.sLines,
        onComplete: function () { s.revert(); } });
    },
    words: function (el) {
      var s = split(el, 'words', 'words'); show(el);
      if (!s) return gsap.from(el, { y: 20, autoAlpha: 0, duration: 0.9, ease: T.reveal });
      return gsap.from(s.words, { yPercent: 100, duration: 0.9, ease: T.reveal, stagger: 0.03, onComplete: function () { s.revert(); } });
    },
    button: function (el) {
      var r = radius(el), inner = el.querySelector('.sm-roll__in');
      var tl = gsap.timeline({ onStart: function () { show(el); } });
      tl.fromTo(el, { clipPath: 'inset(0% 100% 0% 0%' + r + ')' }, { clipPath: 'inset(0% 0% 0% 0%' + r + ')', duration: 1.0, ease: T.move, clearProps: 'clipPath' });
      // the label's hover transition would make it lag behind the reveal: switch it off until the reveal ends
      if (inner) tl.fromTo(inner, { yPercent: 105, transition: 'none' }, { yPercent: 0, duration: 0.9, ease: T.reveal, clearProps: 'transform,transition' }, 0.12);
      return tl;
    },
    image: function (el) {
      var img = el.tagName === 'IMG' ? null : el.querySelector('img,video,canvas,svg'), r = radius(el);
      var par = img && el.getAttribute('data-parallax') !== '0';
      var tl = gsap.timeline({ onStart: function () { show(el); } });
      tl.fromTo(el, { clipPath: 'inset(100% 0% 0% 0%' + r + ')' }, { clipPath: 'inset(0% 0% 0% 0%' + r + ')', duration: T.media, ease: T.move, clearProps: 'clipPath' });
      if (img) tl.fromTo(img, { scale: par ? 1.4 : 1.25 }, { scale: par ? 1.15 : 1, duration: T.mediaScale, ease: T.reveal }, 0);
      if (par) gsap.fromTo(img, { yPercent: -6 }, { yPercent: 6, ease: 'none', scrollTrigger: { trigger: el, start: 'top bottom', end: 'bottom top', scrub: 1 } });
      return tl;
    },
    'hero-image': function (el) {   // the LCP photo: never hidden, only a partial clip + scale
      var img = el.tagName === 'IMG' ? el : (el.querySelector('img,video') || el), r = radius(el);
      var tl = gsap.timeline();
      tl.fromTo(el, { clipPath: 'inset(10% 8% 10% 8%' + r + ')' }, { clipPath: 'inset(0% 0% 0% 0%' + r + ')', duration: 1.6, ease: T.reveal, clearProps: 'clipPath' });
      if (img !== el) tl.fromTo(img, { scale: 1.18 }, { scale: 1, duration: 1.8, ease: T.reveal, clearProps: 'transform' }, 0);
      return tl;
    },
    cards: function (el) {
      var img = el.querySelector('img'); var tl = gsap.timeline();
      tl.fromTo(el, { y: 60, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: T.block, ease: T.reveal, clearProps: 'transform' });
      if (img) tl.fromTo(img, { scale: 1.15 }, { scale: 1, duration: T.mediaScale, ease: T.reveal, clearProps: 'transform' }, 0);
      return tl;
    },
    rows: function (el) {
      var rows = el.tagName === 'TABLE' ? $all('tr', el) : Array.prototype.slice.call(el.children);
      var tl = gsap.timeline({ onStart: function () { show(el); } });
      rows.forEach(function (row, i) {
        tl.fromTo(row, { y: 24, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: 1.0, ease: T.reveal, clearProps: 'transform' }, i * T.sRows);
        var v = $all('[data-reveal-value]', row);
        if (v.length) tl.fromTo(v, { x: 12, autoAlpha: 0 }, { x: 0, autoAlpha: 1, duration: 0.9, ease: T.reveal, clearProps: 'transform' }, i * T.sRows + 0.1);
      });
      return tl;
    },
    icon: function (el) {
      var strokes = $all('path,line,polyline,circle,rect,ellipse,polygon', el).filter(function (p) {
        var s = getComputedStyle(p).stroke; return s && s !== 'none' && getComputedStyle(p).fill === 'none'; });
      var tl = gsap.timeline({ onStart: function () { show(el); } });
      if (strokes.length && root.DrawSVGPlugin) tl.from(strokes, { drawSVG: '0%', duration: 0.9, ease: T.draw, stagger: 0.08 });
      else tl.fromTo(el, { scale: 0.7, rotate: -10, autoAlpha: 0 }, { scale: 1, rotate: 0, autoAlpha: 1, duration: 0.9, ease: T.soft, clearProps: 'transform' });
      return tl;
    },
    count: function (el) {
      var txt = el.textContent, m = txt.match(/-?\d[\d\s.,]*\d|\d/);
      var tl = gsap.timeline({ onStart: function () { show(el); } });
      tl.fromTo(el, { y: 20, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: 0.9, ease: T.reveal, clearProps: 'transform' });
      if (!m) return tl;
      var raw = m[0], dec = (raw.match(/[.,](\d{1,2})$/) || ['', ''])[1].length;
      var num = parseFloat(raw.replace(/[\s\u00a0]/g, '').replace(dec ? /[.,](?=\d{3}\b)/g : /[.,]/g, '').replace(',', '.'));
      var sep = /[\s\u00a0]/.test(raw) ? '\u00a0' : (!dec && /[.,]\d{3}/.test(raw) ? raw.match(/[.,]/)[0] : ''), o = { v: 0 };
      var fmt = function (v) { var s = v.toFixed(dec); return sep ? s.replace(/\B(?=(\d{3})+(?!\d))/g, sep) : s; };
      el.style.fontVariantNumeric = 'tabular-nums';
      el.textContent = txt.replace(raw, fmt(0));
      tl.to(o, { v: num, duration: 1.6, ease: 'power2.out', onUpdate: function () { el.textContent = txt.replace(raw, fmt(o.v)); },
        onComplete: function () { el.textContent = txt; } }, 0);
      return tl;
    },
    rule: function (el) { return gsap.fromTo(el, { scaleX: 0, transformOrigin: '0% 50%', autoAlpha: 1 }, { scaleX: 1, duration: 1.2, ease: T.move }); },
    badge: function (el) {
      var spin = parseFloat(el.getAttribute('data-spin') || '0');
      if (spin) gsap.to(el.querySelector('[data-spin-target]') || el, { rotate: '+=' + spin, ease: 'none', scrollTrigger: { trigger: el, start: 'top bottom', end: 'bottom top', scrub: 1 } });
      return gsap.fromTo(el, { y: -30, rotate: -20, autoAlpha: 0 }, { y: 0, rotate: 0, autoAlpha: 1, duration: 1.0, ease: T.soft });
    },
    header: function (el) {
      if (el.hasAttribute('data-autohide')) {
        var hidden = false;
        ScrollTrigger.create({ start: 'top -120', end: 'max', onUpdate: function (st) {
          var h = st.direction === 1; if (h !== hidden) { hidden = h; gsap.to(el, { yPercent: h ? -110 : 0, duration: 0.6, ease: 'power3.inOut', overwrite: 'auto' }); } } });
      }
      return gsap.fromTo(el, { yPercent: -110, autoAlpha: 1 }, { yPercent: 0, duration: 0.9, ease: T.reveal, clearProps: 'transform' });
    },
    marquee: function (el) {
      var track = el.querySelector('[data-marquee-track]') || el.firstElementChild; show(el);
      var loop = gsap.to(track, { xPercent: -50, ease: 'none', duration: parseFloat(el.getAttribute('data-duration') || '30'), repeat: -1 });
      var dir = 1;
      ScrollTrigger.create({ trigger: el, start: 'top bottom', end: 'bottom top', onToggle: function (st) { st.isActive && !el.__paused ? loop.play() : loop.pause(); },
        onUpdate: function (st) { var v = st.getVelocity(); if (Math.abs(v) > 10) dir = v > 0 ? 1 : -1;
          gsap.to(loop, { timeScale: dir * Math.min(5, 1 + Math.abs(v) / 400), duration: 0.6, ease: T.soft, overwrite: true }); } });
      var btn = el.querySelector('[data-marquee-toggle]');
      if (btn) btn.addEventListener('click', function () { el.__paused = !el.__paused; el.__paused ? loop.pause() : loop.play(); btn.setAttribute('aria-pressed', String(!!el.__paused)); });
      return gsap.from(el, { autoAlpha: 0, duration: 0.8, ease: T.soft });
    },
    fade: function (el) { return gsap.fromTo(el, { y: 30, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: T.block, ease: T.reveal, clearProps: 'transform' }); }
  };

  // ---------- interactions: label roll, magnetic pull ----------
  function prepareRoll(el) {
    if (el.querySelector('.sm-roll')) return;
    var target = el; while (target.children.length === 1 && target.firstElementChild.children.length === 0 && target.firstElementChild.tagName !== 'svg') target = target.firstElementChild;
    var textNode = Array.prototype.find.call(target.childNodes, function (n) { return n.nodeType === 3 && n.textContent.trim(); });
    if (!textNode) return;
    var label = textNode.textContent.trim(), outer = document.createElement('span'), inner = document.createElement('span');
    outer.className = 'sm-roll'; inner.className = 'sm-roll__in'; inner.setAttribute('data-text', label); inner.textContent = label;
    outer.appendChild(inner); target.replaceChild(outer, textNode);
  }
  function magnetic(el) {
    var xTo = gsap.quickTo(el, 'x', { duration: 0.6, ease: 'power3.out' }), yTo = gsap.quickTo(el, 'y', { duration: 0.6, ease: 'power3.out' });
    var k = parseFloat(el.getAttribute('data-magnetic') || '0.25') || 0.25;
    el.addEventListener('pointermove', function (e) { var r = el.getBoundingClientRect(); xTo((e.clientX - r.left - r.width / 2) * k); yTo((e.clientY - r.top - r.height / 2) * k); });
    el.addEventListener('pointerleave', function () { xTo(0); yTo(0); });
  }

  // ---------- maps ----------
  /* SiteMotion.map(el, opts): el = the map <svg> or its container. Attributes (all optional except the route):
     [data-map-base] land/background · [data-map-street] street strokes (main roads first in DOM) · [data-map-area]
     parks/water fills · [data-map-block] buildings · [data-map-label] text labels · [data-map-poi] metro/landmarks
     (drawn around 0,0 or with transform-box fill-box) · [data-map-start] start point · [data-map-route] the route
     path (one continuous path built from the street coordinates) · [data-map-route-mask] the solid copy inside a
     <mask> when the visible route is dashed · [data-map-traveller] a <g> drawn centred on 0,0 that rides the tip ·
     [data-map-pin] destination pin · [data-map-pin-shadow] · [data-map-ripple] circles around the destination ·
     [data-map-time] walking time text ("7 мин") · [data-map-card] the address card (HTML or SVG). */
  function map(el, opts) {
    opts = opts || {};
    var q = function (s) { return $all(s, el); }, one = function (s) { return el.querySelector(s); };
    var route = one('[data-map-route]'), drawPath = one('[data-map-route-mask]') || route;
    if (!route) return null;
    var L = route.getTotalLength(), speed = opts.speed || 520, dur = Math.min(2.6, Math.max(1.3, L / speed));
    var tl = gsap.timeline({ paused: true, defaults: { ease: T.reveal } });
    q('[data-map-street]').concat([drawPath]).forEach(function (p) { p.setAttribute('pathLength', '1'); p.style.strokeDasharray = '1'; });
    tl.from(q('[data-map-base]'), { autoAlpha: 0, scale: 1.04, transformOrigin: '50% 50%', duration: 1.2 }, 0)
      .fromTo(q('[data-map-street]'), { strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: 1.0, ease: T.draw, stagger: 0.06 }, 0.1)
      .from(q('[data-map-area]'), { autoAlpha: 0, duration: 0.8, stagger: 0.05 }, 0.4)
      .from(q('[data-map-block]'), { autoAlpha: 0, y: 8, duration: 0.8, stagger: { each: 0.02, from: 'center' } }, 0.5)
      .from(q('[data-map-label]'), { autoAlpha: 0, y: 6, duration: 0.8, stagger: 0.05 }, 0.8)
      .from(q('[data-map-poi]'), { autoAlpha: 0, scale: 0.6, transformOrigin: '50% 50%', duration: 0.6, ease: 'back.out(1.6)', stagger: 0.08 }, 0.9)
      .from(q('[data-map-start]'), { autoAlpha: 0, scale: 0.6, transformOrigin: '50% 50%', duration: 0.6, ease: 'back.out(1.6)' }, 0.9)
      .to(q('[data-map-start]'), { scale: 1.35, transformOrigin: '50% 50%', duration: 0.3, ease: T.soft, yoyo: true, repeat: 1 }, 1.25);
    var trav = one('[data-map-traveller]'), at = 1.45;
    var draw = gsap.fromTo(drawPath, { strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: dur, ease: T.draw,
      onUpdate: function () { if (!trav) return; var pt = route.getPointAtLength(this.ratio * L); gsap.set(trav, { x: pt.x, y: pt.y }); } });
    if (trav) { var p0 = route.getPointAtLength(0); tl.fromTo(trav, { x: p0.x, y: p0.y, autoAlpha: 0 }, { autoAlpha: 1, duration: 0.25 }, at - 0.1); }
    tl.add(draw, at);
    var arrive = at + dur, pin = one('[data-map-pin]');
    if (trav) tl.to(trav, { autoAlpha: 0, duration: 0.25 }, arrive);
    if (pin) tl.fromTo(pin, { y: -40, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: 0.35, ease: 'power3.in' }, arrive - 0.3)   // motion-lint-allow ease-in-ui (gravity: the pin falls)
      .fromTo(pin, { scaleX: 1.08, scaleY: 0.92, transformOrigin: '50% 100%' }, { scaleX: 1, scaleY: 1, duration: 0.3, ease: T.soft }, arrive + 0.05);
    tl.from(q('[data-map-pin-shadow]'), { scale: 0.4, autoAlpha: 0, transformOrigin: '50% 50%', duration: 0.35, ease: T.soft }, arrive)
      .fromTo(q('[data-map-ripple]'), { scale: 1, autoAlpha: 0.5, transformOrigin: '50% 50%' }, { scale: 2.4, autoAlpha: 0, duration: 1.2, ease: 'power2.out', stagger: 0.4, immediateRender: false }, arrive + 0.05);
    gsap.set(q('[data-map-ripple]'), { autoAlpha: 0 });
    var time = one('[data-map-time]'); if (time) tl.add(B.count(time), arrive + 0.1);
    var card = one('[data-map-card]') || (opts.card && document.querySelector(opts.card));
    if (card) tl.fromTo(card, { clipPath: 'inset(0% 100% 0% 0%' + radius(card) + ')', autoAlpha: 1 }, { clipPath: 'inset(0% 0% 0% 0%' + radius(card) + ')', duration: 0.9, ease: T.move, clearProps: 'clipPath' }, arrive + 0.15);
    if (opts.scrub) ScrollTrigger.create({ trigger: el, start: 'top 75%', end: 'bottom 40%', scrub: 1, animation: tl });
    else ScrollTrigger.create({ trigger: el, start: 'top 65%', once: true, onEnter: function () { tl.play(); } });
    var replay = opts.replay && document.querySelector(opts.replay);
    if (replay) replay.addEventListener('click', function () { tl.restart(); });
    return tl;
  }

  // ---------- init ----------
  function init(opts) {
    opts = opts || {};
    for (var k in (opts.tokens || {})) T[k] = opts.tokens[k];
    var plugins = ['ScrollTrigger', 'SplitText', 'DrawSVGPlugin', 'MotionPathPlugin'].map(function (n) { return root[n]; }).filter(Boolean);
    gsap.registerPlugin.apply(gsap, plugins);
    var html = document.documentElement, api = { tokens: T, map: map, lenis: null };
    html.classList.add('sm-ready');
    var all = $all('[data-reveal]').filter(function (el) { return !(el.parentElement && el.parentElement.closest('[data-reveal]')); });
    var mm = gsap.matchMedia();
    api.revert = function () { mm.revert(); };
    (document.fonts ? document.fonts.ready : Promise.resolve()).then(function () {
      mm.add({ full: '(prefers-reduced-motion: no-preference)', calm: '(prefers-reduced-motion: reduce)', fine: '(hover: hover) and (pointer: fine)' }, function (ctx) {
        var c = ctx.conditions;
        if (c.calm) {   // total choreography, gently: every element fades, nothing travels
          var heroEls = all.filter(function (el) { return el.closest('[data-hero]'); });
          gsap.set(heroEls, { autoAlpha: 1 });
          ScrollTrigger.batch(all.filter(function (el) { return heroEls.indexOf(el) < 0; }), { start: T.batchStart, once: true,
            onEnter: function (els) { gsap.fromTo(els, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4, ease: 'power1.out', stagger: 0.03 }); } });
          $all('[data-map-route],[data-map-pin]').forEach(function (e) { gsap.set(e, { autoAlpha: 1 }); });
          return;
        }
        if (c.fine && root.Lenis && opts.smooth !== false) {
          var lenis = api.lenis = new Lenis({ lerp: 0.09, anchors: true });
          lenis.on('scroll', ScrollTrigger.update);
          var raf = function (t) { lenis.raf(t * 1000); }; gsap.ticker.add(raf); gsap.ticker.lagSmoothing(0);
        }
        $all('[data-reveal="button"],[data-roll]').forEach(prepareRoll);
        if (c.fine) $all('[data-magnetic],[data-reveal="button"]').forEach(magnetic);
        var intro = gsap.timeline({ delay: opts.introDelay || 0 }), used = {};
        all.forEach(function (el) {
          var type = el.getAttribute('data-reveal'), build = B[type] || B.fade;
          if (el.closest('[data-hero]') || type === 'header' || type === 'hero-image') {
            var base = el.hasAttribute('data-at') ? parseFloat(el.getAttribute('data-at')) : (type in INTRO_AT ? INTRO_AT[type] : 0.6);
            var n = used[type] = (used[type] || 0) + 1, step = type === 'heading' ? 0.12 : type === 'hero-image' ? 0.15 : 0.08;
            intro.add(build(el), el.hasAttribute('data-at') ? base : base + (n - 1) * step);
          } else if (type === 'cards') {
            el.__smBatch = true;
          } else if (type === 'marquee') {
            build(el);
          } else {
            var tw = build(el); tw.pause();
            ScrollTrigger.create({ trigger: el, start: T.start, once: true, onEnter: function () { tw.play(); } });
          }
        });
        var cards = all.filter(function (el) { return el.__smBatch; });
        if (cards.length) ScrollTrigger.batch(cards, { start: T.batchStart, once: true, onEnter: function (els) {
          els.forEach(function (el, i) { B.cards(el).delay(i * T.sCards); }); } });
        if (opts.maps !== false) $all('[data-map]').forEach(function (m) { map(m, { scrub: m.getAttribute('data-map') === 'scrub' }); });
        api.intro = intro;
        return function () { if (api.lenis) { api.lenis.destroy(); api.lenis = null; } };
      });
      ScrollTrigger.refresh();
    });
    return api;
  }

  root.SiteMotion = { init: init, map: map, tokens: T, builders: B };
})(window);
