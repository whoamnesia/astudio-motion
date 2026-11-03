# SVG motion techniques

## 1. Preparing an SVG for animation
- Keep `viewBox`; remove fixed `width/height` or set them by CSS. Group parts that move together (`<g id="mark">`,
  `<g id="wordmark">`, one `<path>` per letter if letters animate).
- Inline the SVG in HTML (CSS/JS can't reach into `<img src>`). Strip editor junk (SVGO with `removeViewBox: false`,
  keep ids you animate: `cleanupIds: false` or prefix).
- Counters as `fill-rule="evenodd"` so masks and one-colour versions behave.
- `pathLength="1"` on stroked paths to normalise dash math.

## 2. Stroke draw-on
```css
.draw { stroke-dasharray: 1; stroke-dashoffset: 1; animation: draw 1.1s cubic-bezier(0.65, 0, 0.35, 1) forwards; }
@keyframes draw { to { stroke-dashoffset: 0; } }
```
GSAP: `gsap.from(".draw", { drawSVG: 0, duration: 1.1, ease: "power2.inOut", stagger: 0.1 })`.
Draw direction follows the path direction - reverse the path if it draws backwards.

## 3. Morphing
- GSAP MorphSVG: `gsap.to("#a", { morphSVG: { shape: "#b", type: "rotational" }, duration: 0.7, ease: "power2.inOut" })`.
- CSS `d: path(...)` transition works only with identical command lists (same number/types of commands).
- Flubber (`flubber.interpolate(a, b)`) as an MIT alternative for arbitrary shapes, driven by a tween's progress.

## 4. Animated icon recipes
| Icon | Motion |
|---|---|
| menu <-> close | top and bottom bars rotate ±45° around their own centres and translate to the middle; middle bar scales X to 0; 200ms ui-out |
| play <-> pause | morph (MorphSVG) or crossfade + scale 0.8 -> 1 with 2px blur; 180ms |
| copy -> check | copy icon blurs out at scale 0.25, check draws on (stroke-dashoffset) 250ms |
| chevron expand | rotate 180° on the icon's centre, 200ms ui-in-out |
| heart / like | scale 0.85 on press, 1.15 overshoot on commit (back.out 2), fill floods from centre via clip circle; rare tier |
| bell notification | a single 2-3 swing rotation on the hinge (top centre), 500ms; never looping |
| search -> close | circle shrinks into the handle as the handle rotates into an X |
| spinner | an arc (dasharray 0.25 1) rotating linear 0.9s + dash length breathing 1.4s ease-in-out (Material style) |

## 5. Motion along a path
`<animateMotion dur="3s" repeatCount="indefinite" rotate="auto"><mpath href="#route"/></animateMotion>` for simple
loops; GSAP MotionPath for timelines (`align`, `autoRotate`, `start/end` fractions); CSS `offset-path: path('...')`
+ `offset-distance: 0% -> 100%` for HTML elements on a path.

## 6. Masks and clip reveals
`clip-path: inset(0 100% 0 0)` -> `inset(0)` wipes; `circle(0% at 50% 50%)` -> `circle(150%)` iris; SVG `<mask>` with an
animated shape for organic reveals; text knockout via `<clipPath><text/></clipPath>` with an image/video under it.

## 7. Filters and gradients
`feTurbulence` + `feDisplacementMap` for liquid/heat wobble (animate `baseFrequency` slowly; expensive at large
sizes - prefer a shader); `feGaussianBlur` on small groups only; animated gradients via `stop-color`/`offset` or a
moving `gradientTransform`.

## 8. SMIL vs CSS vs JS
SMIL (`<animate>`, `<animateMotion>`) works in all modern browsers and inside `<img>`-embedded SVGs (self-contained
animated SVG files, e.g. for READMEs) but is hard to sequence and can't respect reduced motion unless scripted. CSS for
simple loops and state transitions; GSAP for choreography, morphs and drawing in sync with other things.

## 9. Reduced motion
Static final state (the logo, the check, the diagram without flowing dashes); loaders keep a minimal, slower
indication; looping diagrams pause by default with a play control if the motion carries meaning.
