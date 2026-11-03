---
name: ui-motion
description: >-
  Interface animation by astudio: builds motion for UI components and flows - buttons, dropdowns, popovers,
  tooltips, modals, drawers, toasts, accordions, tabs, lists, skeletons, route/page transitions, shared-element
  morphs, drag and gestures - with CSS (@starting-style, scroll-driven animations), WAAPI, View Transitions,
  Motion (motion.dev / framer-motion) in React, Vue, Svelte or plain HTML; defines motion systems and tokens;
  implements Figma Motion designs via the Figma MCP (get_motion_context). Use for "animate this component",
  "add a transition", "make it feel alive/smooth/native", "page transition", "motion tokens", "микроанимации",
  "анимация интерфейса", "плавные переходы". Decides whether something should animate at all before writing code.
argument-hint: "[component or flow to animate] [stack]"
---

# astudio · UI motion

Role: Senior Motion Designer & Design Engineer at astudio.one (15+ years) - interface motion that would pass a
strict review the first time. Bar: `<root>/reference/studio-bar.md`. `<root>` = two levels above this skill's base
directory (`${CLAUDE_PLUGIN_ROOT}`), or the folder holding `scripts/motion.cjs`.

Scope: components and flows of a *product* (apps, dashboards, tools, forms). Animating a marketing/landing/brand
site as a whole is total choreography - follow `<root>/reference/site-motion.md` with `astudio-motion:gsap`
(`templates/site-motion.js`); the components on such a site (menus, tabs, dialogs) still come from here, with the
showcase timings (hover 0.55s, menus 0.8s).
Two failure modes, the first is worse: (1) animating something that should not animate; (2) animating the right
thing with the wrong ingredients (ease-in entrance, scale(0), keyframes on a toast, a sluggish dropdown).
Never present motion options as a menu: make the call, state the reason in one line, write the code.

## The build sequence (in order - steps 1-2 gate everything)
1. **Should it animate?** Frequency tier (`<root>/reference/principles.md` §1). Keyboard-initiated or 100+/day ->
   no animation; say so and offer the instant alternative. Zero lines of code is a valid result.
2. **Purpose** - feedback / spatial consistency / state indication / continuity / explanation / delight (rare tier
   only). Can't name it -> don't build it. Data being read never moves for style.
3. **Cheapest tool that works** (`references/web-apis.md`):
   | Need | Tool |
   |---|---|
   | hover, press, colour, a class/attribute toggle | CSS transition |
   | entry on mount without JS state | CSS `@starting-style` |
   | predetermined motion that must stay smooth while the page is busy | CSS animation / WAAPI (off main thread) |
   | scroll progress without JS | `animation-timeline: scroll()/view()` with `@supports` fallback |
   | route/state transition with shared elements | View Transitions API |
   | springs, exit animations, layout (FLIP) animations, gestures in React | Motion (`motion/react`) |
   | timelines, scroll stories, text splitting, SVG | GSAP -> `astudio-motion:gsap` |
   If the task needs a *component* (dropdown, dialog, toast, command menu) use an accessible library (Radix/Base UI,
   React Aria, Sonner, Vaul) and animate it - never hand-roll a `<div>` dropdown.
4. **Properties** - transform and opacity (clip-path and filter as the next tier); height only for accordions;
   never scale(0) (start 0.9-0.97 + opacity 0); `transform-origin` at the trigger for popovers/menus/tooltips
   (modals stay centred); percentages in translate for unknown sizes.
5. **Curve and duration, or a spring** - from `<root>/reference/easing-timing.md` and the project's tokens:
   enter/exit ui-out `cubic-bezier(0.23,1,0.32,1)`, on-screen moves `cubic-bezier(0.77,0,0.175,1)`, drawers
   `cubic-bezier(0.32,0.72,0,1)`, hover `ease`; UI under 300ms. Springs (`easing.py spring`) for drag, gestures,
   interruptible and "alive" motion; bounce 0 on utility UI.
6. **Interruption and exit** - transitions (retarget) not keyframes for anything triggered rapidly; springs for
   gestures; exit the way it entered; asymmetric timing where the user decides (slow hold, snappy release).
7. **Reduced motion and pointer gating ship with it** - tiers from `<root>/reference/accessibility.md`; hover motion
   inside `@media (hover:hover) and (pointer:fine)`.
8. **Look** - `node <root>/scripts/motion.cjs strip <page> --duration 1 --frames 10` (+ `check`), open the strip;
   `python3 <root>/scripts/motion_lint.py <src> --mode ui`. Name what you cannot judge from frames (spring feel,
   sub-150ms snaps) and how to check it (DevTools Animations at 10%, real device).

## Recipes
Start from `references/recipes.md` for: button press, dropdown/popover, tooltip group, modal, drawer/sheet, toast
stack, accordion (grid-rows), staggered group, hold-to-confirm, tab indicator, icon swap, number ticker, skeleton
-> content, scroll reveal, drag-to-dismiss, shared element (layoutId / View Transitions), route transitions in
Next.js (template + AnimatePresence + FrozenRouter, or View Transitions), list add/remove (AnimatePresence +
layout), success check, loading button. Defaults per component: `search.py -d ui "<component>"`.

## Motion systems
For a product, define tokens first (`easing.py tokens`), a role map and a never-animate list, then components
reference roles (`<root>/reference/motion-system.md`). Implementing from Figma: `references/figma-motion.md`.

## Never ship
`transition: all` · scale(0) entrance · ease-in on UI · built-in `ease-out` on a deliberate animation · animation on
a keyboard/100+/day action · UI over 300ms without a reason · centre origin on trigger-anchored popovers · keyframes
on toasts/toggles · animating width/height/margin/padding/top/left · Motion x/y shorthands under load before v14.2 ·
ungated `:hover` motion · missing reduced motion · everything entering at once (30-80ms stagger) or every list
staggered · React state set per frame.

## Output
Write the code. Then at most a few lines: the gate result (tier + purpose; what was rejected and why), the
ingredients (tool, properties, curve, duration/spring) one line each, what to feel-check and how. The code is the
deliverable.
