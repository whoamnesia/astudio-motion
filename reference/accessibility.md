# Motion accessibility

Not optional and not a follow-up: the reduced-motion path ships in the same change as the animation.

## 1. Tier motion, don't nuke it
Removing all motion over-corrects: elements teleport, focus rings and progress lose their cues.
- **Tier 1 - remove under reduced motion** (vestibular triggers): parallax; large slides across the viewport;
  scale/zoom of large elements; 3D rotation and spin; auto-playing carousels and marquees; smooth-scroll hijacking;
  scroll-jacked pinned scenes; motion paths; camera flythroughs; anything implying self-motion.
- **Tier 2 - soften**: replace travel with a short opacity fade (<= 200ms), shrink distance and duration, keep the
  fact of the transition so nothing teleports.
- **Tier 3 - keep**: opacity fades, colour/background transitions, focus rings, loading indicators, motion essential
  to meaning (a progress bar, a drag following the finger).
Reduced motion means fewer and gentler, not zero. On a showcase site with total choreography every element still
arrives - as a soft 0.4s fade with no travel, no splits, no parallax, no smooth scroll (site-motion.md §7).

## 2. Implementation
```css
@media (prefers-reduced-motion: reduce) {
  .hero-title { animation: fade 200ms ease both; }   /* keep a fade, drop the rise */
  .parallax { transform: none !important; }
}
@media (hover: hover) and (pointer: fine) { .card:hover { transform: translateY(-2px); } }
```
```js
const reduce = matchMedia('(prefers-reduced-motion: reduce)');
gsap.matchMedia().add({ full: '(prefers-reduced-motion: no-preference)', calm: '(prefers-reduced-motion: reduce)' }, (ctx) => {
  const { full } = ctx.conditions;
  gsap.from('.hero h1', { y: full ? 40 : 0, opacity: 0, duration: full ? 0.9 : 0.2, ease: 'expo.out' });
});
```
React: `useReducedMotion()` (motion/react, react-native-reanimated); SwiftUI: `@Environment(\.accessibilityReduceMotion)`;
Compose: check `Settings.Global.ANIMATOR_DURATION_SCALE`; Lenis/smooth scroll: do not initialise when reduced.
Motion tokens can encode it: under reduced motion, long durations map to short ones and `--motion-travel: 0px`
(`easing.py tokens`).

## 3. WCAG mapping
- **2.2.2 Pause, Stop, Hide (A)** - anything auto-moving for more than 5s in parallel with content (carousels,
  marquees, background video, looping 3D) needs a pause control, regardless of the media query.
- **2.3.1 Three Flashes (A)** - nothing flashes more than 3 times per second; avoid saturated red flashes and
  full-frame strobes in films and transitions.
- **2.3.3 Animation from Interactions (AAA)** - interaction-triggered motion (scroll, hover) can be disabled;
  honouring prefers-reduced-motion is the technique (C39).
- Content never hides behind animation: render complete without JS and under reduced motion; hidden start states
  only under a `.js` class and `(prefers-reduced-motion: no-preference)`.

## 4. Other
- Keyboard: focus never lands inside an element that is still animating in; animate focus rings quickly (<= 150ms).
- Screen readers: duplicated marquee content `aria-hidden="true"`; decorative canvases `aria-hidden` with a text
  alternative nearby; `role="img"` + label on meaningful animations (Lottie/Rive) and a static fallback.
- Video: captions for speech, no information carried only by motion or sound, a poster frame that reads alone.
- Native: respect system settings (iOS Reduce Motion, Android "Remove animations"); haptics are never the only
  feedback.
- Check with `node <root>/scripts/motion.cjs check <page>` (renders with and without reduced motion and compares the
  end states) and by emulating `prefers-reduced-motion: reduce` in DevTools.
