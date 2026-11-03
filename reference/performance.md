# Motion performance

Frame budget: 16.7ms at 60Hz, **8.3ms at 120Hz** (most phones and many laptops) - design against the smaller one.

## 1. What you animate
| Tier | Properties | Cost |
|---|---|---|
| composite only | `transform`, `opacity` (+ in current Chrome/Firefox `filter`, `clip-path`, `background-color`) | cheapest, can run off the main thread |
| paint + composite | `box-shadow`, `border-radius`, `color`, gradients | repaint every frame |
| layout + paint + composite | `width`, `height`, `top`, `left`, `margin`, `padding`, `border-width`, font-size | most expensive; moves neighbours |
Swap down a tier: size -> `scale()`; position -> `translate()` (percentages are relative to the element); display/
visibility -> `opacity`; `box-shadow` -> `filter: drop-shadow()` or a pseudo-element's opacity; height: auto ->
`grid-template-rows: 0fr -> 1fr` (or measured height for short accordions); layout change -> FLIP.

## 2. Where it runs
| Driver | Thread |
|---|---|
| CSS transitions/animations, WAAPI, Motion's `animate()` for transform/opacity/filter/clip-path | can be hardware-accelerated (off main thread) |
| GSAP, rAF loops, Motion layout animations, `useTransform`, drag | main thread - smooth only while the page is idle |
Predetermined motion that plays while the page is busy (route changes, hydration, data loading) belongs in CSS/WAAPI.
Motion 14.2+ hardware-accelerates `x`/`y`/`scale` shorthands; older versions need the full `transform` string.

## 3. Traps that look correct
- **React state per frame** - `setState` inside rAF/pointermove/scroll re-renders every frame. Write to
  `ref.current.style.transform` or a motion value.
- **Inherited CSS variables** - updating a custom property on a parent recalculates styles for every descendant;
  set `transform` on the moving element.
- **Blur** - keep animated `blur()` <= 12-20px; 2-5px is enough for crossfades; Safari is the slowest.
- **will-change** - only on elements about to animate, removed afterwards; never on anything a camera scales (text
  goes blurry).
- **Layout thrash** - batch reads then writes; GSAP batches its own writes; use `gsap.quickTo()` for mouse followers.
- **Too many tweens/triggers** - stagger instead of N tweens; animate only visible items in long lists; kill
  off-screen loops; pause canvases outside the viewport (IntersectionObserver) and on `visibilitychange`.

## 4. WebGL / WebGPU budgets
- pixel ratio `Math.min(devicePixelRatio, 1.5-2)`; full-screen shaders at DPR 1 and often 30fps are fine.
- draw calls < ~100 on mobile; instancing/batching for repeats; merged geometry for static scenery.
- textures: KTX2/Basis (stays compressed in VRAM), sized to their screen size; glTF with Draco or meshopt.
- `renderer.setAnimationLoop`; render on demand (`frameloop="demand"` in R3F) for static scenes; dispose geometry,
  materials AND their textures on unmount.
- shader compile stalls: `await renderer.compileAsync(scene, camera)` before revealing.
- measure: `renderer.info` after render (draw calls, triangles), Chrome Performance panel, Spector.js.

## 5. Video rendering
- deterministic: every visible value is a function of timeline time (no `Date.now()`, unseeded `Math.random()`,
  network calls, infinite repeats) so every frame renders identically.
- render at the delivery size; 1080p30 default; 60fps only for fast UI demos and sports-like motion.
- H.264 `-crf 18 -pix_fmt yuv420p -movflags +faststart` for delivery; WebM VP9 for the web; GIF only for small loops
  (palettegen, <= 720px, <= 25fps).

## 6. LCP-safe entrances
- The LCP element (hero photo or h1) is never hidden at load: no `opacity: 0`, `clip-path: inset(100%)`,
  `scale(0)`, curtains or preloaders over it. Start it visible with a partial clip (`inset(10% 8%)`) and a scale
  (1.18 -> 1); the heading's first line rises from t=0.
- Hidden start states for below-the-fold content are fine (they are not LCP candidates).
- Measure: `motion.cjs coverage` prints LCP with motion vs reduced motion - keep the difference under 300ms.
- SplitText after `document.fonts.ready` (or `autoSplit`) so lines do not reflow mid-reveal; revert splits when the
  reveal ends so text reflows naturally on resize.

## 7. Measure, don't guess
`motion.cjs check` (frame-change sparkline, dead stretches), Chrome DevTools Performance + Animations panel (slow
down to 10%), Rendering > Frame Rendering Stats / Paint flashing / Layer borders, `performance.now()` marks. Test on
a mid-range phone with 4x CPU throttling. Software WebGL in CI (SwiftShader) is not representative of GPU speed.
