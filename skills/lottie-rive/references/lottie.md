# Lottie / dotLottie

## Install and play
```bash
npm i @lottiefiles/dotlottie-web        # vanilla (canvas + WASM)
npm i @lottiefiles/dotlottie-react      # React
```
```js
import { DotLottie } from "@lottiefiles/dotlottie-web";
const dl = new DotLottie({ canvas: document.querySelector("#hero-lottie"), src: "/hero.lottie",
  loop: true, autoplay: true, renderConfig: { autoResize: true, devicePixelRatio: Math.min(devicePixelRatio, 2) } });
```
```jsx
import { DotLottieReact } from "@lottiefiles/dotlottie-react";
<DotLottieReact src="/success.lottie" autoplay loop={false} dotLottieRefCallback={setDl} style={{ width: 96 }} />
```
CDN web component for static pages: `<script src="https://unpkg.com/@lottiefiles/dotlottie-wc@latest/dist/dotlottie-wc.js" type="module"></script>`
then `<dotlottie-wc src="/a.lottie" autoplay loop></dotlottie-wc>` (pin a version in production).

## Control
`play() pause() stop() setSpeed(1.5) setMode("forward"|"reverse"|"bounce"|"reverse-bounce") setFrame(42)
setSegment(30, 90) setLoop(bool)`; events: `load` (totalFrames available), `complete`, `frame` ({currentFrame}),
`loop`, `play`, `pause`. Markers authored in AE (`setMarker("idle")`) are cleaner than frame numbers.

### Segment state machine (no Rive needed)
```js
dl.addEventListener("load", () => dl.setSegment(0, 30));          // idle loop
button.addEventListener("click", () => { dl.setLoop(false); dl.setSegment(30, 90); dl.play(); });
dl.addEventListener("complete", () => { dl.setLoop(true); dl.setSegment(0, 30); dl.play(); });
```
dotLottie also supports authored state machines (Lottie Creator) loaded with `stateMachineId`.

## Scroll-driven
```js
const dl = new DotLottie({ canvas, src: "/story.lottie", autoplay: false });
let total = 0; dl.addEventListener("load", () => total = dl.totalFrames);
ScrollTrigger.create({ trigger: ".story", start: "top top", end: "+=150%", pin: true, scrub: true,
  onUpdate: self => total && dl.setFrame(self.progress * (total - 1)) });
```
(Or IntersectionObserver + rAF without GSAP.) `@lottiefiles/lottie-interactivity` maps `scroll`, `hover`, `click`,
`cursor` modes to frame ranges declaratively.

## Theming
dotLottie themes (authored in Lottie Creator / via the dotlottie-js API) override colours and values by slot id:
`dl.setTheme("dark")`. For old JSON files: recolour by editing the JSON `c.k` colour arrays (0..1 RGB) in named layers
- script it, never by hand.

## Mobile runtimes
dotlottie-android, dotlottie-ios, dotlottie-react-native, dotlottie-flutter; same file, same themes. Keep parity
by testing the same segments on each.

## Optimisation checklist
- Export only used layers; delete hidden layers and unused precomps/assets.
- Shapes over images; if images are needed, compress (WebP) and embed in `.lottie`.
- Avoid: expressions-heavy rigs, layer effects (blur/glow are mostly unsupported), many masks/mattes (expensive),
  3D layers, blending modes, unconverted text (outline it or use embedded fonts carefully).
- Frame rate 30 for UI (60 only for fast motion); trim in/out points; round keyframe values.
- Target sizes: icons < 30KB, illustrations < 150KB, hero scenes < 400KB.
- Check: `npx @lottiefiles/lottie-js` or LottieFiles' optimiser; render in a page and strip it with motion.cjs.

## Accessibility
`<div role="img" aria-label="Payment complete">` around the canvas; decorative -> `aria-hidden="true"`. Under
`prefers-reduced-motion: reduce`: `autoplay: false` and `setFrame(lastMeaningfulFrame)`. Loops > 5s get a pause
control. Don't convey information only through animation.

## Building a Lottie without AE
- Lottie Creator (web), Figma plugins (LottieFiles), Cavalry export, Rive -> no (Rive has its own format).
- Programmatic: small JSON hand-authored or generated (shape layers with keyframed transforms) is feasible for
  simple icons; validate in a player and keep the source script.
