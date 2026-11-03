# Easing, springs and timing

Never invent a curve because it looks familiar. Take values from here, from `data/easings.csv` /
`data/durations.csv` (`search.py -d easing|duration`), or compute them (`scripts/easing.py`).
Extend the project's existing motion tokens before adding new ones.

## 1. Ease by role
| Role | Curve | CSS | GSAP |
|---|---|---|---|
| UI enter/exit, popovers, toasts | strong ease-out | `cubic-bezier(0.23, 1, 0.32, 1)` | `power4.out` |
| On-screen move / morph / tab indicator | strong ease-in-out | `cubic-bezier(0.77, 0, 0.175, 1)` | `power4.inOut` |
| Drawers, sheets | drawer | `cubic-bezier(0.32, 0.72, 0, 1)` | custom |
| Hero arrival, camera push/pull, title landing | expo-out (long tail) | `cubic-bezier(0.16, 1, 0.3, 1)` | `expo.out` |
| Camera pan, colour flood, page wipe | cubic/quart in-out | `cubic-bezier(0.65, 0, 0.35, 1)` | `power2.inOut` / `power3.inOut` |
| Exit that accelerates away, zoom-through | ease-in | `cubic-bezier(0.32, 0, 0.67, 0)` | `power2.in` / `power3.in` |
| Hover / colour | ease | `ease` | `power1.out` |
| Constant (marquee, progress, rotation, scrubbed scroll) | linear | `linear` | `none` |
| Gesture, drag release, "alive" | spring | `linear()` from `easing.py spring` | spring via Motion/Reanimated |
Built-in CSS `ease-out`/`ease-in-out` are too weak for deliberate motion. One ease for everything (the same
`power2.out` 0.5s) is the flat default that makes work look generated - vary by role.

## 2. Springs
Name springs by **damping ratio** (ζ) and **response** (duration):
| ζ | Feel | Use |
|---|---|---|
| 1.0 | no bounce | default for UI springs, opacity-adjacent motion |
| 0.75-0.85 | premium settle, a hint of life | sheets, morphs, launch-film containers |
| 0.6-0.7 | snappy | toggles, chips, drag release |
| 0.4-0.6 | playful | celebrations, kids, games |
| < 0.3 | cartoon | never in product UI |
Apple/Motion parameterisation: `bounce = 1 - ζ` (0 = critically damped, 0.15 snappy, 0.3 bouncy), `duration` =
perceptual duration. Position and scale may bounce; **opacity and colour never bounce**.
`python3 <root>/scripts/easing.py spring --bounce 0.15 --duration 0.4` prints the CSS `linear()` easing, the real
settle time, and Motion / SwiftUI / Compose / Reanimated equivalents.
Use springs when: the user can interrupt or reverse (drag, swipe), an element should feel alive, mouse-tracking,
layout morphs. Use durations when: the motion is predetermined, must sync to other things (film, scroll), or must be
exactly reproducible.

## 3. Durations
| Element | ms |
|---|---|
| press feedback | 100-160 |
| tooltip | 125-200 (first one delayed; neighbours instant) |
| dropdown / select | 150-250 |
| modal | 200-300 |
| drawer / sheet | 300-500 |
| toast | 300-400 |
| accordion | 150-250 (layout cost) |
| page / route | 300-600 |
| showcase-site reveal (text, cards, rows) | 900-1400 (site-motion.md §2) |
| showcase image wipe + inner scale | 1300-1500 + 1800-2000 |
| showcase hover / menu / page transition | 500-600 / 800-1000 / 900-1200 |
| hero load sequence | first frame composed (LCP visible), readable by ~0.8s, settled <= 2.0s |
| film: fast move | 300-600 |
| film: single entry | <= 800 |
UI stays under 300ms unless there is a reason; showcase sites live on the long, smooth end of the scale. Exits are 40-50% shorter than entrances (or ~75%), and subtler
(smaller travel). Distance and size scale duration: 100px move ~200ms, full-screen ~400-500ms.

## 4. Staggers and overlap
- list items 30-80ms apart, words 60-120ms, letters ~1 frame (33ms at 30fps); total stagger <= 500ms - with 8+
  items stagger only the first few or tighten.
- next element starts when the previous is 30-50% done.
- product UI: one staggered moment per view; utility lists (search results, settings, tables) never stagger.
- showcase sites: every group staggers on one shared rhythm (chars 0.02 · words 0.05 · lines 0.09 · rows 0.06 ·
  cards 0.1) - consistency, not scarcity, is the rule.
- GSAP: `stagger: { each: 0.06, from: "start" }`; Motion: `staggerChildren: 0.05`; CSS: `animation-delay: calc(var(--i) * 50ms)`.

## 5. Film timing
- frames per beat = fps × 60 / BPM; compute each beat from its index, never add a rounded beat repeatedly.
- text hold: 0.5s + 0.3s per word; final line >= 2s; text >= 2.6% of the frame's short side.
- stillness before climax: 0.3-0.75s.
- something new every 2-4s; shots average 1.8-3s; a demo may hold one framing 7-10s while the UI acts.
- arrive slow, leave clean: long-tailed arrivals, single-motion exits (never slide-stop-leave).
- motion blur at the fastest frame: 6-12px on text-sized elements, 15-20px full-frame, along the direction of travel.

## 6. Checking a curve
`easing.py bezier 0.16 1 0.3 1` plots it and reports when 90%/99% of travel is reached: an arrival should hit 90% in
the first ~35% of its duration. `easing.py compare ui-out expo-out cubic-in-out` shows them side by side.
If a motion "feels slow", check this first: the curve, not the duration, is usually the problem.
