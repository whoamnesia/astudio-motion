# ScrollTrigger and scroll storytelling

## 1. Basics
```js
gsap.registerPlugin(ScrollTrigger);
gsap.from(".reveal", { autoAlpha: 0, y: 40, duration: 1.1, ease: "expo.out",
  scrollTrigger: { trigger: ".reveal", start: "top 85%", toggleActions: "play none none none", once: true } });
```
- `start` / `end`: "triggerPos viewportPos" (`"top 80%"`, `"center center"`, `"bottom top"`, `"+=200%"`), or functions.
- `toggleActions`: onEnter onLeave onEnterBack onLeaveBack (`play pause resume reverse restart reset complete none`).
- `scrub: true | 0.8-1.2` - progress follows scroll (number = smoothing seconds - use it for anything visible that
  travels; it is what makes scroll motion feel silky). Never with toggleActions.
- `pin: true | ".el"`, `pinSpacing` (false for overlapping stacks), `anticipatePin: 1`.
- `snap: 1 / (n - 1)` or `{ snapTo: "labels", duration: 0.4, ease: "power1.inOut" }`.
- callbacks: `onEnter onLeave onUpdate(self => self.progress, self.direction, self.getVelocity())`, `onToggle`.
- `ScrollTrigger.batch(".card", { onEnter: els => gsap.from(els, { autoAlpha: 0, y: 20, stagger: 0.06 }) })` for
  many items.
- `ScrollTrigger.refresh()` after layout changes (images, fonts, dynamic content); resize is automatic (debounced).
- Order: create triggers top to bottom, or set `refreshPriority` (lower = earlier section).

## 2. Pinned scene (the signature scroll story)
```js
const tl = gsap.timeline({ scrollTrigger: { trigger: ".story", start: "top top", end: "+=200%", scrub: 0.8, pin: true, anticipatePin: 1 } });
tl.to(".story__img--1", { clipPath: "inset(0 0 100% 0)", ease: "none" })
  .from(".story__img--2", { scale: 1.15, ease: "none" }, "<")
  .from(".story__caption--2 .line", { yPercent: 110, stagger: 0.05, ease: "none" }, "<0.2");
```
ScrollTrigger goes on the **timeline**, never on a child tween; scrubbed tweens use `ease: "none"` (the scroll is the
easing). Each ~100px of scroll must visibly change something. Total pin <= 2-3 screens.

## 3. Horizontal gallery
```js
const track = document.querySelector(".h-track");
const tween = gsap.to(track, { x: () => -(track.scrollWidth - innerWidth), ease: "none",
  scrollTrigger: { trigger: ".h-wrap", pin: true, scrub: 1, end: () => "+=" + (track.scrollWidth - innerWidth), invalidateOnRefresh: true } });
gsap.utils.toArray(".h-card").forEach(card => gsap.from(card.querySelector("img"), { scale: 1.2, ease: "none",
  scrollTrigger: { trigger: card, containerAnimation: tween, start: "left right", end: "right left", scrub: true } }));
```
`ease: "none"` on the horizontal tween (1:1 mapping). Touch / reduced motion: native horizontal scroll with
`scroll-snap-type: x mandatory` instead.

## 4. Parallax and depth
`gsap.to(".layer", { yPercent: -15, ease: "none", scrollTrigger: { trigger: ".hero", start: "top top", end: "bottom top", scrub: true } })`
- small offsets (5-20%), images and shapes only, removed under reduced motion.
- inner-image parallax: container `overflow: hidden`, image scaled 1.15-1.2, translate yPercent ±8.

## 5. Common scroll patterns
- **Text highlight on scroll**: words from muted to ink as the paragraph crosses the viewport
  (`scrub`, `stagger` over SplitText words, colour or opacity only).
- **Image sequence (scrollytelling of a product)**: canvas drawing frame `Math.round(progress * (n - 1))` of
  preloaded WebP frames; keep sequences <= 120-150 frames, WebP, lazy-load beyond the first screens.
- **Stacking cards**: each card pinned with `pinSpacing: false`, previous scales to 0.95 and dims.
- **Progress bar**: `scaleX` of a fixed bar scrubbed by the whole document.
- **Section colour change**: `onEnter/onEnterBack` tween of a CSS variable on `body` (colour flood, 0.6s power2.inOut).
- **Scroll velocity skew**: `onUpdate(self => quickSkew(clamp(self.getVelocity() / -300)))` - subtle, off under reduced motion.

## 6. Making scroll scenes reviewable
Add a test hook so `motion.cjs` can render scroll progress deterministically:
```js
window.__seek = (t) => { const p = Math.min(1, t / 4); window.scrollTo(0, p * (document.documentElement.scrollHeight - innerHeight)); ScrollTrigger.update(); };
```
Then `node <root>/scripts/motion.cjs strip page.html --duration 4 --frames 12 --mode hook` shows the whole story
as a strip (4 seconds = top to bottom). With scrub smoothing the frame lags slightly - set `scrub: true` while
reviewing.

For whole-site coverage (does every section and text block move?) run
`node <root>/scripts/motion.cjs coverage page.html` - it scrolls the page like a visitor and lists static elements.

## 7. Do not
Nest ScrollTriggered tweens inside a parent timeline · put ScrollTrigger on a child tween · use scrub and
toggleActions together · use an ease other than "none" with containerAnimation · leave markers on · forget
refresh after dynamic layout · pin many screens or capture the wheel · parallax body text.
