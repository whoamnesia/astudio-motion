# GSAP core and timelines

## Tweens
- `gsap.to(targets, vars)` current -> vars · `gsap.from(targets, vars)` vars -> current (entrances) ·
  `gsap.fromTo(targets, from, to)` explicit · `gsap.set(targets, vars)` immediate.
- vars: `duration` (default 0.5), `delay`, `ease`, `stagger`, `repeat` (-1 infinite - never in video), `yoyo`,
  `overwrite` (false | true | "auto"), `immediateRender` (true by default for from/fromTo), `onStart/onUpdate/onComplete`.
- CSS: camelCase (`backgroundColor`), transform aliases `x y xPercent yPercent scale scaleX rotation rotationX
  rotationY skewX transformOrigin`, `autoAlpha` (opacity + visibility), CSS variables (`"--hue": 180`),
  directional rotation (`"-170_short"`, `"+=30_cw"`), `svgOrigin` for SVG (not together with transformOrigin),
  `clearProps: "transform"`.
- function-based values: `x: (i, el) => i * 40`; relative values: `"+=100"`, `"-=0.5"`.
- `gsap.defaults({ ease: "expo.out", duration: 0.8 })` for a project baseline; per-timeline `defaults` better.

## Eases (by role - reference/easing-timing.md)
`expo.out` arrivals · `power4.out`/`quint` titles · `power2.inOut` camera/colour floods · `power3.in` exits ·
`back.out(1.4-1.7)` small overshoot · `none` for scrub and constant motion · `steps(n)` for stepped looks ·
`CustomEase.create("ui-out", "0.23, 1, 0.32, 1")` to share curves with CSS tokens. Avoid `bounce`/`elastic` in UI
and films (only for deliberate play).

## Stagger
`stagger: 0.06` or `{ each: 0.06, from: "start" | "center" | "end" | "edges" | "random" | index, grid: "auto", axis: "x" , ease: "power1.in" }`
or `{ amount: 0.4 }` (total). Total stagger <= 0.5s for UI; letters 0.02-0.035, words 0.06-0.12.

## Timelines
```js
const tl = gsap.timeline({ defaults: { duration: 0.8, ease: "expo.out" } });
tl.from(".hero__title .line", { yPercent: 110, stagger: 0.08 })
  .from(".hero__media", { clipPath: "inset(12% 12% 12% 12%)", scale: 1.15, duration: 1.2, ease: "power3.out" }, "<0.1")
  .from(".hero__cta", { autoAlpha: 0, y: 12, duration: 0.5 }, "-=0.6")
  .addLabel("settled");
```
Position parameter: absolute `1.2`, relative `"+=0.3"` / `"-=0.3"`, `"<"` start of previous, `">"` end of previous,
`"<0.2"`, labels `"settled+=0.2"`. Prefer it to `delay` chains. Nest timelines (`tl.add(child, "<")`) to compose
scenes. Control: `play pause reverse restart seek(t|label) progress(0..1) timeScale(2) kill()`; `tl.tweenTo("label")`.
Timeline options: `repeat`, `yoyo`, `paused: true` (video masters), `onComplete`, `smoothChildTiming`.

## Hero entrance pattern (load)
1. Content painted complete without JS (no FOUC hiding unless under `.js`).
2. `gsap.matchMedia()`: under `(prefers-reduced-motion: no-preference)` set hidden states with `gsap.set`, then play
   the timeline; under `reduce` only short fades.
3. <= 4-5 elements in the load sequence, settled by ~1.2-1.5s; the signature element first.
4. Lines in masks: wrap each line in `overflow: clip` (SplitText `mask: "lines"`), animate `yPercent: 110 -> 0`.

## Cursor follower / magnetic button
```js
const xTo = gsap.quickTo(".cursor", "x", { duration: 0.4, ease: "power3" }), yTo = gsap.quickTo(".cursor", "y", { duration: 0.4, ease: "power3" });
window.addEventListener("pointermove", e => { xTo(e.clientX); yTo(e.clientY); }, { passive: true });
```
Magnetic: inside the button's radius, `quickTo` x/y toward `(pointer - centre) * 0.3`, clamp to ~12px; release
with `elastic.out(1, 0.6)` only on playful brands, otherwise `power3.out`. Fine pointers only.

## utils worth knowing
`gsap.utils.mapRange(inMin,inMax,outMin,outMax,v)`, `clamp`, `normalize`, `interpolate`, `snap`, `wrap`,
`random(min,max,step,true)` (returns a function), `distribute({base,amount,from,grid,ease})`, `toArray`,
`selector(scope)`, `pipe`. Use them for scroll-progress mapping and grid stagger patterns.

## Do not
Animate width/height/top/left for movement · use invalid ease names · rely on default immediateRender when stacking
from() tweens · forget that `from()` uses the current state as the end · chain with delays instead of a timeline ·
create tweens every frame (reuse, quickTo).
