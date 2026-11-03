# Showcase-site motion: total choreography

For marketing, landing, brand, portfolio, agency, promo, e-commerce showcase and event sites ("оживи сайт",
"как на Awwwards", "сделай вау"). Product UI (apps, dashboards, settings, forms in a tool) keeps the restraint rules
of `principles.md` §1 and `astudio-motion:ui-motion`. Builders: `astudio-motion:gsap` -> `templates/site-motion.js`
+ `templates/site-motion.css` (the system below as code).

## Contents
1. The doctrine
2. Smoothness in numbers
3. Reveal grammar by content type
4. Harmony rules
5. First paint and LCP
6. Maps and routes
7. Reduced motion
8. Taste: references for sites
9. Done means

## 1. The doctrine
- **Everything performs.** Every visible element has an authored entrance: headings, body text, eyebrows, buttons,
  links, nav, images, icons, numbers, list rows, prices, table rows, rules, badges, maps, footer. A section that
  just sits there while the one above it danced is a *static island* - the page reads half-finished. Text is
  animated too: line, word and character reveals in masks are the heart of award-level sites.
- **Harmony.** One motion language for the whole site: one ease family, one duration scale, one direction, one
  trigger line, one stagger rhythm. Content types differ in *how* they reveal (§3), never in *which language*
  they speak. A visitor should feel one hand made every move.
- **Smoothness is the product.** Long-tailed eases, generous durations, overlapping sequences, smooth scroll,
  lerped interactions. Nothing snaps, nothing stops at full speed (`motion.cjs check` reports `hard-stop`),
  nothing jitters. Soft and light: small travel inside masks, opacity always paired with movement, no overshoot on
  text or images.
- **A signature on top.** One authored moment (the hero intro, a pinned scroll scene, a map journey, a 3D reveal)
  is the wow; the total choreography is the stage it stands on. Both are required.
- **Still fast.** The LCP element paints on the first frame (§5); everything runs on transform / opacity /
  clip-path at 60-120fps; content is complete without JS and under reduced motion.

## 2. Smoothness in numbers (house defaults - tune per brand, never below these floors)
| Token | Value | Use |
|---|---|---|
| `--ease-reveal` | `cubic-bezier(0.16, 1, 0.3, 1)` · GSAP `expo.out` | every entrance: text, cards, rows, icons |
| `--ease-soft` | `cubic-bezier(0.25, 1, 0.5, 1)` · `power3.out` | hovers, small moves, colour, follow-ups |
| `--ease-move` | `cubic-bezier(0.76, 0, 0.24, 1)` · `power4.inOut` | image wipes, on-screen moves, menus, page transitions |
| `--ease-draw` | `cubic-bezier(0.37, 0, 0.63, 1)` · `sine.inOut` | line drawing, routes, rules |
| `--dur-text` | 1.1-1.3s | heading lines/words/chars, body lines |
| `--dur-media` | 1.3-1.5s wipe + 1.8-2.0s inner scale | images and video |
| `--dur-block` | 1.0-1.2s | cards, rows, buttons, icons |
| `--dur-hover` | 0.5-0.6s | hover/leave on a showcase site (product UI stays 150-250ms) |
| `--dur-move` | 0.8-1.0s | menus, overlays, tabs, page transitions |
| stagger | chars 0.02 · words 0.05 · lines 0.09 · rows 0.06 · cards 0.1 | cap a visible group at ~10 steps |
| overlap | the next element starts when the previous is 20-35% done | never strictly sequential |
| travel | text: yPercent 100-110 inside a line mask · blocks: 40-70px · rows: 24px · icons: scale 0.7 -> 1 | |

Rules that make it feel smooth:
- Smooth scroll (Lenis `lerp: 0.09` or `duration: 1.2`) on desktop fine pointers, synced to ScrollTrigger; native
  on touch and under reduced motion. Scroll-linked effects use `scrub: 0.8-1.2` (smoothing), never raw `scrub: true`.
- Images move inside their frame: wipe the container, scale the image 1.25 -> 1, then parallax the image ±8-12% on
  scrub. Two layers moving at different speeds read as depth, one layer reads as a slide.
- Interactions are lerped: cursor followers and magnetic buttons via `gsap.quickTo(el, "x", { duration: 0.6,
  ease: "power3.out" })`; hovers roll labels (the label slides up, its copy slides in) instead of jumping.
- Banned on a showcase site: reveals under 0.6s (`motion_lint` `short-reveal`), `linear`/`none` outside scrub and
  marquees, back/elastic on text or images, opacity-only blinks, movement that stops at full speed, `scrub: true`
  on visible travel, toggling classes that jump states without a transition.

## 3. Reveal grammar by content type
Mark every element with `data-reveal="<type>"` (the template wires each type). Defaults:
| Content | `data-reveal` | Motion | Numbers |
|---|---|---|---|
| Hero / display heading | `heading` | SplitText lines + words (+ chars for one hero line) in line masks: yPercent 110 -> 0, rotate 4-6° -> 0 (origin 0 100%) | 1.2s expo.out, words 0.05, chars 0.02 |
| Section heading h2/h3 | `heading` | same split, words | 1.1s expo.out, words 0.05 |
| Eyebrow, label, kicker, tag | `words` | words rise 100% in masks, or ScrambleText for tech brands | 0.9s, 0.03 |
| Body paragraph | `lines` | SplitText lines in masks: yPercent 100 -> 0 + opacity 0 -> 1 | 1.1s expo.out, lines 0.09, starts 0.15s after its heading |
| Buttons, CTAs | `button` | background wipes from the left (scaleX 0 -> 1, origin left) then the label rises from its mask; hover = label roll + magnetic pull (fine pointers) | 1.0s move ease + 0.9s reveal, +0.12s |
| Links, nav items | `words` / `rows` | items fall in from masks; underline draws scaleX 0 -> 1 from the left on hover, leaves to the right | 0.9s, 0.05 |
| Photos, video | `image` | container clip-path `inset(100% 0 0 0)` -> `inset(0)` (power4.inOut) + inner scale 1.25 -> 1 (expo.out) + scrub parallax ±10% | 1.4s + 1.9s |
| Hero / LCP photo | `hero-image` | visible at frame 0: clip `inset(10% 8% round R)` -> `inset(0 round R)` + scale 1.18 -> 1 - never hidden | 1.6s expo.out from t=0 |
| Cards, tiles, grid items | `cards` | ScrollTrigger.batch: y 60 -> 0 + opacity, inner image scale 1.15 -> 1 | 1.1s, 0.1 |
| List rows, menu items, prices, table rows | `rows` | row by row y 24 -> 0 + opacity; the price/value follows 0.1s later from x 12 | 1.0s, 0.06 |
| Icons, pictograms | `icon` | DrawSVG strokes 0 -> 100% (sine.inOut) or scale 0.7 -> 1 + rotate -10° -> 0 (power3.out) | 0.9s |
| Numbers, stats | `count` | count up from 0 with tabular figures, unit fades after | 1.6s power2.out |
| Dividers, rules, borders | `rule` | scaleX 0 -> 1 from the left | 1.2s power4.inOut |
| Badges, stickers, seals | `badge` | drop in (y -30, rotate -20° -> 0, power3.out) then rotate with scroll (scrub) | 1.0s |
| Marquee | `marquee` | continuous, speed and direction follow scroll velocity, pauses off-screen, pause control | |
| Maps | `map` | §6 | |
| Footer wordmark | `heading` (chars) | giant letters rise from the baseline, links in columns as `rows` | 1.2s, 0.03 |
| Anything else visible | `fade` | y 30 -> 0 + opacity - the fallback, never the plan | 1.0s |
Fixed header: slides down from -100% at t≈0.5s on load, hides on scroll down and returns on scroll up (0.6s
power3.inOut). Tabs and panels on a showcase page: the outgoing content leaves (0.35s), the incoming content reveals
with its own grammar (rows, image) - the switch is a small scene, not a swap.

## 4. Harmony rules
1. **One module, one vocabulary.** All entrances come from the same `data-reveal` types and tokens; no section
   invents its own animation. `node <root>/scripts/motion.cjs coverage <page>` must show every section moving and
   >= 90% of visible elements (text included) moving.
2. **One current.** Things rise from below, masks open upward, images wipe up; horizontal motion is reserved for
   marquees, galleries and rules (left -> right). A direction change needs a cause.
3. **One trigger line.** `start: "top 85%"`, `once: true` for reveals (batches "top 90%"). Inside a section the
   order is reading order: heading -> body lines -> media -> secondary -> CTA, overlapping 0.15-0.25s.
4. **One rhythm.** Staggers come from the table; a section never mixes 0.02 and 0.2 steps.
5. **One lead at a time.** At every moment one thing leads (the heading), the rest supports with less travel and
   later starts. Rich, never chaotic: squint at the strip - the eye should know where to go.
6. **Intro hands over.** The hero sequence settles (<= 2.0s), then scroll reveals take over from the first scroll;
   the header and the first scroll cue arrive last in the intro.
7. **Interactions match.** Hovers use `--ease-soft` 0.5s, menus/tabs `--ease-move` 0.8s, everywhere.

## 5. First paint and LCP
- The LCP element (usually the hero photo or the h1) paints on the first frame: the hero photo starts visible with
  a partial clip and a scale (`hero-image`); the heading's first line starts rising at t=0 and is fully visible by
  ~0.8s. Never opacity 0, `inset(100%)`, `scale(0)`, a curtain or a preloader over the hero.
- Intro timeline: t=0 hero image (visible, scaling) + heading line 1 · 0.1-0.7 heading lines/words · 0.35-1.1 body
  lines, CTA · 0.5-1.3 header/nav, facts, secondary media · settled <= 2.0s. `motion.cjs check` must not report
  `empty-opening`.
- Measure: `motion.cjs coverage` prints LCP with motion vs reduced motion; the difference stays under 300ms.
- Hidden start states only under `html.js` + `(prefers-reduced-motion: no-preference)` (an inline `<head>` script
  sets the class); a failsafe reveals everything after 3s if the script fails; SplitText waits for
  `document.fonts.ready` (or `autoSplit`) so lines do not re-flow mid-animation.

## 6. Maps and routes
A map is a small film: the world builds, the journey is drawn, the arrival is celebrated. Animate all of it.
**Geometry first (the "crooked route" fix):**
- Build the route from the same coordinates as the streets it follows (copy the street path's segments), as one
  continuous `<path>` with filleted corners (radius 8-14px: arcs or `Q` curves at every turn), `stroke-linecap:
  round; stroke-linejoin: round`, no self-overlaps, no wobble from hand-placed points.
- Check alignment on a 2x still (`motion.cjs still map.html --at <end> --scale 2`): the route sits on the street's
  centre line everywhere.
**Drawing:**
- Solid route: `pathLength="1"`, `stroke-dasharray: 1`, `stroke-dashoffset: 1 -> 0`.
- Dashed or dotted route: never animate the dashed path itself (dashes crawl). Put it under a `<mask>` whose solid
  copy (stroke-width = route width + 4) draws with `dashoffset`; the dashes stay still and get uncovered.
- Constant perceived speed: duration = length / 450-600 px/s (typically 1.4-2.4s), `sine.inOut`. A traveller (dot,
  walking figure, cup) rides the drawing tip on the same progress: `MotionPathPlugin` on the same timeline position
  and ease, or `path.getPointAtLength(progress * L)` in `onUpdate` - tip and traveller never drift apart.
**Sequence (causal):**
1. base land and blocks: opacity + scale 1.04 -> 1 (1.2s expo.out);
2. streets draw, main roads first (stagger 0.06, 1.0s `--ease-draw`); parks and water fill in (opacity 0.8s);
3. buildings rise from the route outward (y 8 + opacity, stagger 0.02);
4. street labels and district names reveal by words (0.8s), POIs (metro, landmarks) pop: scale 0.6 -> 1,
   back.out(1.6), 0.6s, stagger 0.08;
5. the start point pulses once; the route draws with its traveller;
6. on arrival (same frame): the pin drops (y -40 -> 0 power3.in 0.35s, squash 1.08/0.92 -> 1 0.3s power3.out, its
   shadow scales in), two ripples (scale 1 -> 2.4, opacity 0.5 -> 0, 1.2s), the walking time counts up
   ("7 мин"), the address card wipes in.
Plays once when the map is 65% in view, or scrubbed (`scrub: 1`) when the map is a scroll story. Hover on a POI
lifts its label; a "build route" button replays the journey. Reduced motion: the complete map with the route and
pin already in place.

## 7. Reduced motion (total choreography, gently)
Every element still appears - with a soft fade (opacity 0 -> 1, 0.4s, stagger 0.03) and no travel: no splits, no
masks moving, no parallax, no smooth scroll, no marquee travel, no scrub-driven movement. Hero photo and heading
visible immediately. The template does this through `gsap.matchMedia()`.

## 8. Taste: references for sites
Before building, study 5-8 current sites (studio-bar.md §3) and *measure* them:
- Awwwards: Sites of the Day and collections "Animation", "Scrolling", "Typography", "Transitions", "Interaction";
  `site:awwwards.com/sites <subject> animation`. Behance: `site:behance.net/gallery web animation <subject>`,
  "website motion design", "UI animation landing".
- Studios whose sites set the bar for smoothness and text motion: Locomotive, Cuberto, Obys, Immersive Garden,
  darkroom.engineering (the Lenis authors), 14islands, Resn, Active Theory, Lusion, Dogstudio - look at their
  recent award-winning work.
- Record a live reference to measure it: `node <root>/scripts/motion.cjs strip https://example.com --duration 2.5
  --frames 12` (clock mode works on URLs) - read off the order, durations, stagger and how far things travel.
- Write into `.astudio/motion/references.md` what you take as numbers ("hero h1: chars, 0.02 stagger, 1.2s
  expo.out, rotate 6°"), never a copy of a site.

## 9. Done means (showcase site)
- `motion.cjs coverage`: no FAIL; every section moves; >= 90% of visible elements and >= 90% of text move; LCP
  delta < 300ms.
- `motion.cjs check` on the hero: no `empty-opening`, no `hard-stop`; reduced-motion end state complete.
- `motion_lint.py --mode marketing`: no FAIL; `short-reveal` and `uniform-fade-up` addressed.
- Strips: hero 0-2s, three scrolled sections (scroll hook), the map journey, a hover; looked at for harmony (one
  language), smoothness (every arrival decelerates) and density (one lead at a time).
