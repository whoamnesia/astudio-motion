# GSAP in frameworks - setup and cleanup

Principle everywhere: create animations after the DOM exists, scope selectors to the component root, revert
everything (tweens, ScrollTriggers, SplitText, matchMedia) when the component unmounts or the route changes.

## React / Next.js
```tsx
"use client";
import { useRef } from "react";
import gsap from "gsap"; import { useGSAP } from "@gsap/react"; import { ScrollTrigger } from "gsap/ScrollTrigger";
gsap.registerPlugin(useGSAP, ScrollTrigger);           // module top level, once

export function Hero() {
  const root = useRef<HTMLElement>(null);
  const { contextSafe } = useGSAP(() => {
    const mm = gsap.matchMedia();
    mm.add({ full: "(prefers-reduced-motion: no-preference)", calm: "(prefers-reduced-motion: reduce)" }, (ctx) => {
      const { full } = ctx.conditions!;
      gsap.from(".title .line", { yPercent: full ? 110 : 0, autoAlpha: full ? 1 : 0, duration: full ? 0.9 : 0.2, stagger: 0.08, ease: "expo.out" });
    });
  }, { scope: root });                                  // selectors scoped to root, auto-revert on unmount
  const onEnter = contextSafe(() => gsap.to(".cta", { scale: 1.02, duration: 0.2 })); // handlers created later stay in context
  return <section ref={root}>...</section>;
}
```
- `useGSAP(fn, { scope, dependencies, revertOnUpdate })` - default empty deps; pass deps to re-run; `revertOnUpdate`
  to revert before re-running.
- Without @gsap/react: `useLayoutEffect(() => { const ctx = gsap.context(() => {...}, root); return () => ctx.revert(); }, [])`.
- Never set React state from GSAP onUpdate per frame; read values via refs.
- Next.js: GSAP only in client components; SSR-safe (no window access at module level beyond registerPlugin);
  `ScrollTrigger.refresh()` after route content loads; with App Router transitions kill triggers in the leaving tree.
- StrictMode double-invokes effects in dev - useGSAP/context revert handles it.

## Vue 3 / Nuxt
```js
import { onMounted, onUnmounted, ref } from "vue"; import gsap from "gsap";
const root = ref(); let ctx;
onMounted(() => { ctx = gsap.context(() => { gsap.from(".item", { autoAlpha: 0, y: 16, stagger: 0.05 }); }, root.value); });
onUnmounted(() => ctx && ctx.revert());
```
Nuxt: register plugins in a client-only plugin (`plugins/gsap.client.ts`); `<ClientOnly>` for pinned sections if
hydration mismatches; refresh ScrollTrigger on `page:finish`.

## Svelte / SvelteKit
`onMount(() => { const ctx = gsap.context(() => {...}, node); return () => ctx.revert(); })`; or a Svelte action
`use:reveal` that returns `{ destroy() { ctx.revert(); } }`. In SvelteKit, refresh triggers in `afterNavigate`.

## Astro
`<script>` blocks run once per page - wrap in `document.addEventListener("astro:page-load", init)` with View
Transitions, and kill triggers on `astro:before-swap`.

## Static HTML
```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.13.0/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.13.0/dist/ScrollTrigger.min.js"></script>
<script>document.documentElement.classList.add("js"); gsap.registerPlugin(ScrollTrigger); /* ... */</script>
```
Hidden start states in CSS only under `.js` and `(prefers-reduced-motion: no-preference)`.

## When to create vs kill
Create on mount (or when a section enters, for heavy scenes); kill on unmount, route change, or when switching
breakpoints (matchMedia handles that). `ScrollTrigger.getAll().forEach(t => t.kill())` only as a last resort - prefer
contexts. Debug leaks: count `ScrollTrigger.getAll().length` after navigating back and forth.
