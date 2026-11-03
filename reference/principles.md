# Motion principles

## Contents
1. Why it moves (the gate)
2. The fundamentals (timing, sequencing, easing, transformation, exaggeration)
3. The 12 animation principles, translated for screens
4. Three lenses: restraint, polish, play
5. Physicality

## 1. Why it moves - the gate (run it before any curve)
**Frequency** decides the budget:
| How often the user sees it | Motion |
|---|---|
| 100+ times a day, or keyboard-initiated (shortcuts, command palette) | none - instant |
| tens of times a day (hover, list navigation, tabs) | near-imperceptible: fast and small, or nothing |
| occasional (modals, drawers, toasts, route changes) | standard |
| rare / first time (onboarding, success, celebration, brand intro) | the delight budget lives here |

**Purpose** - name it in one word or delete the animation:
feedback (the interface heard you) · spatial consistency (where it came from / went) · state indication (what
changed) · continuity (prevent a jarring teleport) · explanation (show how it works; marketing/onboarding) ·
narrative (films, scroll stories) · delight (rare tier only).

**Function** - data a person is reading or acting on does not move for style. A decorative cursor effect belongs on
a marketing page, never on a chart in a banking app.

**Context changes the budget.** The gate above is for *interactions in products*. On a showcase site (marketing,
landing, brand, portfolio, promo) every section is seen for the first time, so its entrances sit in the "rare /
first time" tier: everything visible performs - text, images, buttons, numbers, maps - in one harmonious, smooth
language (`site-motion.md`). Restraint there applies to the high-frequency controls only (form fields, nav hovers,
tabs reused often).

## 2. Fundamentals (the Figma Motion fundamentals, extended)
- **Timing** - how long. Small and near things move fast, large and far things slower; UI under 300ms, explanation
  and film longer. Duration scales with distance and size, never one number for everything.
- **Sequencing** - the order. Lead with the most important element; secondary elements follow 30-120ms later or
  start when the leader is 30-50% done. Fully sequential reads robotic, all-at-once reads cheap.
- **Easing** - how speed changes. Arrivals decelerate (ease-out, long tail), departures accelerate (ease-in),
  on-screen moves ease both ways, constant motion is linear, gestures use springs. Never ease-in on UI.
- **Transformation** - what changes: position, scale, rotation, opacity, shape (clip-path, path morph), colour,
  blur. Prefer the cheapest property that tells the story (transform/opacity first).
- **Exaggeration** - pushing beyond reality adds personality: a 3-8% overshoot, a squash on impact, a camera that
  accelerates harder than physics. Calibrate to the brand: banking 0%, consumer 3-5%, kids/gaming 10-30%.

## 3. The 12 principles (Thomas & Johnston), for screens
| Principle | On screens |
|---|---|
| Squash and stretch | press scale 0.97, a pill stretching between tabs (leading edge on a faster spring than the trailing edge), cards compressing on impact. Preserve volume. |
| Anticipation | a 60-120ms wind-up before a big move (a slight pull back before a fly-out, a hover lift before a drag). Never on frequent UI. |
| Staging | one focal point at a time; dim, blur or still everything else; the camera frames the action. |
| Straight ahead vs pose to pose | UI and film = pose to pose (keyframes); generative/physics = straight ahead (simulation, springs). |
| Follow-through and overlapping action | children lag their parent by 1-3 frames; a card's content lands 40ms after the card; hair, cloth, tails settle after the body. |
| Slow in, slow out | easing; the long-tailed ease-out is the house arrival. |
| Arcs | organic things travel on curves (motion paths, rotation + translation), mechanical things on straight lines. |
| Secondary action | small supporting motion that reinforces the main one (a shadow tightening as an object lands) - never competing. |
| Timing | frames define weight and mood: heavier = slower acceleration and longer settle. |
| Exaggeration | see above. |
| Solid drawing | in 3D and illustration: volume, perspective, consistent light; in UI: consistent depth model. |
| Appeal | clarity of shape and silhouette in every frame - check any paused frame reads as a finished image. |

## 4. Three lenses (weight them by context)
- **Restraint** (Emil Kowalski - productivity tools): "should this animate at all?" Fast (180ms ideal), purposeful,
  interruptible, deleted when in doubt.
- **Polish** (Jakub Krehel - shipped consumer apps): "is it subtle enough for production?" Enter = opacity +
  translateY 8-16px + blur 4px; exits subtler than entrances; shadows instead of borders; optical alignment;
  contextual icon swaps.
- **Play** (Jhey Tompkins - creative sites, kids, portfolios): "what could this become?" CSS @property, 3D CSS,
  scroll-driven animation, linear() springs, experimentation - in the right context.
| Project | Primary | Secondary | Selective |
|---|---|---|---|
| productivity tool | restraint | polish | play (onboarding only) |
| SaaS dashboard | restraint | polish | play (empty states) |
| marketing / landing / showcase site | polish + play (total choreography, site-motion.md) | - | restraint (forms, high-frequency controls) |
| e-commerce | polish | restraint | play (product showcase) |
| mobile app | polish | restraint | play (delighters) |
| portfolio / agency / kids | polish + play | - | restraint (high-frequency bits) |
| brand film / launch video | film grammar (choreography.md §5) | polish | - |

## 5. Physicality
- Things enter from somewhere and leave to somewhere; exit the way you entered (a toast from the bottom leaves
  through the bottom).
- Popovers scale from their trigger (transform-origin), modals from centre. Nothing appears from scale(0); start at
  0.9-0.97 with opacity 0.
- Momentum carries through interruptions: springs and transitions retarget from the current value; keyframes restart.
- Asymmetric timing where the user decides: slow on the deliberate phase (hold to confirm 2s linear), snappy on the
  system response (200ms ease-out).
- Gestures dismiss on velocity, not only distance; boundaries are damped, not hard stops.
- Big objects carry more inertia (slower start, longer settle), small ones snap. Reactions scale with implied mass.
