# UI motion recipes

Tokens assumed (from `easing.py tokens` or the project's own):
```css
:root {
  --ease-out: cubic-bezier(0.23, 1, 0.32, 1);
  --ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);
  --ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);
}
```

## Button press
```css
.btn { transition: transform 160ms var(--ease-out), background-color 150ms ease; }
.btn:active { transform: scale(0.97); }
@media (hover: hover) and (pointer: fine) { .btn:hover { background-color: var(--btn-hover); } }
```
No lift-on-hover for every button; no ripple in a custom-designed product.

## Dropdown / popover / menu (from the trigger)
```css
.menu { transform-origin: var(--radix-dropdown-menu-content-transform-origin, var(--transform-origin, top left));
  transition: opacity 200ms var(--ease-out), transform 200ms var(--ease-out); }
.menu[data-state="closed"], .menu[data-starting-style], .menu[data-ending-style] { opacity: 0; transform: scale(0.96); }
@starting-style { .menu[data-state="open"] { opacity: 0; transform: scale(0.96); } }
@media (prefers-reduced-motion: reduce) { .menu { transition: opacity 150ms ease; transform: none !important; } }
```
Exit faster than enter (150 vs 200ms) when the library allows separate timing.

## Tooltip group (first delayed, neighbours instant)
```css
.tip { transition: opacity 125ms var(--ease-out), transform 125ms var(--ease-out); }
.tip[data-instant] { transition-duration: 0ms; }   /* set while another tooltip in the group was open < 300ms ago */
```
Hover delay ~400-600ms for the first tooltip; keyboard focus shows it without delay.

## Modal (centred, never from the trigger)
```css
.overlay { transition: opacity 250ms var(--ease-out); }
.dialog { transition: opacity 250ms var(--ease-out), transform 250ms var(--ease-out); }
.dialog[data-state="closed"] { opacity: 0; transform: scale(0.96); }
@starting-style { .dialog[open] { opacity: 0; transform: scale(0.96); } }
```
Use `<dialog>`/Radix Dialog for focus trapping and return focus. Exit ~180ms.

## Drawer / bottom sheet
```css
.sheet { transform: translateY(100%); transition: transform 500ms var(--ease-drawer); }
.sheet[data-open] { transform: translateY(0); }
```
Drag: follow the finger 1:1, dismiss on velocity (> ~0.11 px/ms) or distance > 40%, otherwise spring back
(`{ type: "spring", duration: 0.5, bounce: 0.2 }` or Vaul). Damp resistance past the top.

## Toast stack (transitions, not keyframes)
```css
.toast { transition: transform 400ms ease, opacity 400ms ease; }
.toast[data-mounted="false"] { transform: translateY(100%); opacity: 0; }
.toast[data-removed="true"] { transform: translateY(100%); opacity: 0; }
```
Stack with scale and translate per index; pause timers on hover/focus; exit the edge it came from (Sonner does this).

## Accordion (no height measuring)
```css
.panel { display: grid; grid-template-rows: 0fr; transition: grid-template-rows 200ms var(--ease-out); }
.panel[data-open] { grid-template-rows: 1fr; }
.panel > .inner { overflow: hidden; }
.panel .content { opacity: 0; transition: opacity 150ms ease; } .panel[data-open] .content { opacity: 1; transition-delay: 50ms; }
```
Native `<details>` + `::details-content` with `interpolate-size: allow-keywords` where supported.

## Staggered group entrance (one moment per view)
```css
.item { animation: rise 300ms var(--ease-out) both; animation-delay: calc(var(--i) * 50ms); }
@keyframes rise { from { opacity: 0; transform: translateY(8px); } }
@media (prefers-reduced-motion: reduce) { .item { animation: fade 150ms ease both; } @keyframes fade { from { opacity: 0; } } }
```
`style="--i: 0..n"`; cap the stagger at ~6 items, the rest arrive with the last.

## Hold to confirm (asymmetric)
```css
.hold::after { content: ""; position: absolute; inset: 0; background: var(--danger); clip-path: inset(0 100% 0 0);
  transition: clip-path 200ms var(--ease-out); }
.hold:active::after { clip-path: inset(0 0 0 0); transition: clip-path 2s linear; }
```
Fire the action on `transitionend` of the long transition; offer a normal confirm for keyboard users.

## Tab indicator
Motion: `<motion.span layoutId="tab-indicator" transition={{ type: "spring", bounce: 0, duration: 0.3 }} />`.
CSS alternative when the page is busy during navigation (smoother off-main-thread): one highlighted copy of the tab
list clipped with `clip-path: inset(...)` animated over 250ms `--ease-in-out`.

## Icon swap (copy -> check, play -> pause)
```jsx
<AnimatePresence mode="popLayout" initial={false}>
  <motion.span key={copied ? "check" : "copy"} initial={{ opacity: 0, scale: 0.25, filter: "blur(4px)" }}
    animate={{ opacity: 1, scale: 1, filter: "blur(0px)" }} exit={{ opacity: 0, scale: 0.25, filter: "blur(4px)" }}
    transition={{ type: "spring", duration: 0.3, bounce: 0 }}>{copied ? <Check/> : <Copy/>}</motion.span>
</AnimatePresence>
```

## Number ticker
Per-digit columns translating by `-digit * 1em` with `--ease-out` 400ms; `font-variant-numeric: tabular-nums`; each
column sized to its final glyph; clip vertically only. Library: NumberFlow.

## Skeleton -> content
Reserve exact dimensions; crossfade 150-250ms; shimmer slow (1.5-2s) and off under reduced motion; show skeletons
only after ~300ms of waiting.

## Scroll reveal (no JS needed where supported)
```css
@supports (animation-timeline: view()) {
  .reveal { animation: reveal linear both; animation-timeline: view(); animation-range: entry 10% cover 30%; }
}
@keyframes reveal { from { opacity: 0; clip-path: inset(12% 0 0 0); } }
```
Fallback: IntersectionObserver adding `.is-in` once; hidden start state only under `html.js` +
`(prefers-reduced-motion: no-preference)`. Product UI: never on body copy. Showcase sites: every element reveals
with its own grammar (body copy by lines in masks) - use `skills/gsap/templates/site-motion.js` instead of this
generic reveal.

## Shared element / card -> detail
Motion: matching `layoutId` on card and detail; animate inner content separately (fade in after ~60% of the morph);
counter-scale text if it distorts. Plain HTML: View Transitions with `view-transition-name: card-<id>` on both states.
```js
document.startViewTransition(() => updateDOM());
```
```css
::view-transition-group(*) { animation-duration: 350ms; animation-timing-function: var(--ease-in-out); }
@media (prefers-reduced-motion: reduce) { ::view-transition-group(*), ::view-transition-old(*), ::view-transition-new(*) { animation: none !important; } }
```

## Route transitions in Next.js App Router
Exit animations need the old tree kept alive: `app/template.tsx` with a keyed `AnimatePresence mode="wait"` and a
FrozenRouter (freeze the LayoutRouterContext) - or use View Transitions (`next-view-transitions` / React
`<ViewTransition>` where available). Debug: missing key, AnimatePresence not wrapping the keyed child, or the
layout re-mounting.

## List add / remove
`<AnimatePresence initial={false}>{items.map(i => <motion.li key={i.id} layout initial={{opacity:0,y:8}}
animate={{opacity:1,y:0}} exit={{opacity:0,scale:0.96}} transition={{type:"spring",duration:0.3,bounce:0}}/>)}`;
layout animations run on the main thread - avoid during heavy work; for long lists animate only the changed item.

## Success check
SVG path with `stroke-dasharray`/`stroke-dashoffset` drawn over 400ms `--ease-out` after a 100ms scale-in of the
circle; once, never looped; a static check under reduced motion. See `astudio-motion:svg-motion`.

## Loading button
Keep the width; crossfade label -> spinner in 150ms; spinner rotates linear 0.8-1s; disable re-submit; announce with
`aria-busy` / live region.

## Masking a crossfade that won't settle
Add `filter: blur(2-4px)` to both states during the swap (200ms ease) - the eye reads one object changing.
