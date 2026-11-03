# Web motion APIs - what to use when

## CSS transitions
Retarget from the current value when interrupted - right for anything a user can trigger repeatedly.
Name properties explicitly; `transition-behavior: allow-discrete` lets `display`/`overlay` participate (dialogs,
popovers) together with `@starting-style`.

## @starting-style (entry without JS)
```css
.popover:popover-open { opacity: 1; transform: none; transition: opacity 200ms var(--ease-out), transform 200ms var(--ease-out), display 200ms allow-discrete, overlay 200ms allow-discrete; }
@starting-style { .popover:popover-open { opacity: 0; transform: scale(0.96); } }
.popover { opacity: 0; transform: scale(0.96); }
```
Pairs with the Popover API and `<dialog>` for accessible, JS-free open/close motion.

## CSS keyframe animations
Predetermined motion; runs off the main thread for transform/opacity. Use for loaders, entrance sequences that
must stay smooth during hydration, ambient loops with meaning. Not for toasts/toggles (they restart from zero).

## Scroll-driven animations
`animation-timeline: scroll()` (scroller progress) and `view()` (element's visibility in the scrollport), with
`animation-range` (`entry`, `exit`, `cover`, `contain`). Chromium and Safari 26+; always wrap in
`@supports (animation-timeline: view())` with an IntersectionObserver or static fallback. Use linear-ish keyframes
(the scroll is the easing) and keep effects small.

## Web Animations API
```js
const a = el.animate([{ transform: 'translateY(8px)', opacity: 0 }, { transform: 'none', opacity: 1 }],
  { duration: 300, easing: 'cubic-bezier(0.23, 1, 0.32, 1)', fill: 'both' });
await a.finished;
```
Programmatic control (pause, reverse, `currentTime`, `playbackRate`) with CSS-level performance. `document.getAnimations()`
lists everything running - the motion.cjs renderer uses it to freeze time.

## View Transitions API
- Same-document: `document.startViewTransition(update)`; CSS pseudo-elements `::view-transition-old/new/group(name)`.
- Cross-document (MPA): `@view-transition { navigation: auto; }` in both pages.
- Name shared elements uniquely (`view-transition-name`), few at a time (each is a snapshot); `view-transition-class`
  to style groups. Respect reduced motion by disabling the pseudo-element animations.
- React 19 `<ViewTransition>` / `next-view-transitions` for Next.js.

## Motion (motion.dev, formerly Framer Motion)
`npm i motion` · `import { motion, AnimatePresence, useReducedMotion } from "motion/react"`.
- `animate`/`initial`/`exit` + `AnimatePresence` for exit animations (`mode="wait" | "popLayout"`).
- `layout` / `layoutId` for FLIP and shared elements (main thread).
- springs: `{ type: "spring", visualDuration: 0.4, bounce: 0.15 }` or `{ stiffness, damping, mass }`.
- gestures: `whileHover`, `whileTap`, `drag` with `dragConstraints`, `onDragEnd` velocity.
- hardware acceleration: transform/opacity/filter/clip-path go to WAAPI; `x`/`y`/`scale` shorthands are accelerated
  from motion 14.2; layout animations, `useTransform`, drag and `onUpdate` stay on the main thread.
- vanilla: `import { animate, scroll, inView } from "motion"`.

## When to reach for GSAP instead
Multi-step timelines with overlaps and labels, ScrollTrigger scenes (pinning, scrub, horizontal), SplitText, SVG
morph/draw, Flip across layout changes, video timelines - see `astudio-motion:gsap`.

## Framework notes
- React: never animate through state per frame; motion values or refs. Cleanup on unmount (useGSAP / motion handles it).
- Vue: `<Transition>`/`<TransitionGroup>` with CSS classes, or motion-v / GSAP in `onMounted` with `gsap.context` revert.
- Svelte: `transition:fly|fade|scale` with custom easing functions; `animate:flip` for lists; `prefersReducedMotion` store.
- Tailwind v4: `transition-[transform,opacity] duration-200 ease-(--ease-out)`, `motion-safe:` / `motion-reduce:`
  variants, `starting:` variant for @starting-style.
