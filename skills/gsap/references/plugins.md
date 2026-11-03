# GSAP plugins (all free, `npm i gsap`)

| Plugin | Use | Notes |
|---|---|---|
| **SplitText** | split into chars/words/lines for reveals | `SplitText.create(el, { type: "lines,words", mask: "lines", autoSplit: true, onSplit(self) { return gsap.from(self.lines, { yPercent: 110, stagger: 0.08, ease: "expo.out" }); } })` - autoSplit re-splits on resize/font load and returns the animation for cleanup; `aria` handled by default (screen readers get the original text); revert on unmount or when the reveal ends. Showcase sites: headings by words/chars, body copy by lines (`mask: "lines"`, yPercent 100, stagger 0.09, 1.1s expo.out); product UI: headlines only. |
| **ScrambleText** | text that scrambles then locks | for a logo/wordmark lock or a single word; `scrambleText: { text: "astudio", chars: "lowerCase", speed: 0.4 }` |
| **Flip** | animate between layout states | `const state = Flip.getState(".items"); changeLayout(); Flip.from(state, { duration: 0.5, ease: "power2.inOut", absolute: true, nested: true, onEnter: els => gsap.fromTo(els, {opacity:0, scale:.95}, {opacity:1, scale:1}) })` - filters, grid/list toggles, shared elements across containers |
| **DrawSVG** | draw strokes | `drawSVG: "0%" -> "100%"` or `"50% 50%" -> "0% 100%"`; needs strokes, not fills (svg-motion skill) |
| **MorphSVG** | morph path shapes | `morphSVG: { shape: "#target", type: "rotational", map: "complexity" }`; `MorphSVGPlugin.convertToPath("circle, rect")` first |
| **MotionPath** | move along a path | `motionPath: { path: "#route", align: "#route", alignOrigin: [0.5, 0.5], autoRotate: true }`; MotionPathHelper for editing |
| **Draggable + Inertia** | drag with momentum | `Draggable.create(".knob", { type: "rotation", inertia: true, snap: v => Math.round(v / 30) * 30 })`; bounds; `onDrag` -> quickSetter |
| **Observer** | unified wheel/touch/pointer intent | full-page section slideshows without native scroll (use sparingly - accessibility) |
| **ScrollToPlugin** | animated scroll to anchors | `gsap.to(window, { scrollTo: { y: "#pricing", offsetY: 80 }, duration: 1, ease: "power2.inOut" })` - respect reduced motion (instant) |
| **ScrollSmoother** | smooth scroll + data-speed parallax | needs wrapper/content markup; desktop only; or use Lenis |
| **CustomEase / CustomWiggle / CustomBounce** | shared curves, wiggles | `CustomEase.create("ui-out", "0.23,1,0.32,1")` |
| **Physics2D / PhysicsProps** | velocity/gravity particles | confetti-like bursts on rare success moments |
| **GSDevTools** | scrub timelines while developing | never in production |
| **PixiPlugin** | tween Pixi display objects | with PixiJS scenes |
| **EasePack** | rough, slow, expoScale | `expoScale(1, 3)` keeps zooms perceptually even |

## Registering
```js
import gsap from "gsap"; import { ScrollTrigger } from "gsap/ScrollTrigger"; import { SplitText } from "gsap/SplitText"; import { Flip } from "gsap/Flip";
gsap.registerPlugin(ScrollTrigger, SplitText, Flip);
```

## Page transitions
- **View Transitions** (preferred, native): `document.startViewTransition()` in SPAs; `@view-transition { navigation: auto }` in MPAs.
- **Barba.js** for classic multi-page sites with GSAP overlay wipes: `barba.init({ transitions: [{ leave: ({current}) => gsap.to(current.container, { autoAlpha: 0, y: -20, duration: 0.4 }), enter: ({next}) => gsap.from(next.container, { autoAlpha: 0, y: 20, duration: 0.5, ease: "expo.out" }) }] })`;
  kill ScrollTriggers in `beforeLeave`, re-init in `after`; update analytics and focus.
- Overlay wipe pattern: a fixed panel `scaleY 0 -> 1` from bottom (0.5s power3.inOut), swap content, `scaleY 1 -> 0`
  from top; total <= 1s; skip under reduced motion.
