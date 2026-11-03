# Choreography: sequencing, transitions, scenes

## Contents
1. Hierarchy in time
2. Entrances and exits
3. Transitions in interfaces
4. Scroll choreography
5. Film grammar: the seam law, the current, carriers, causes
6. Sustained motion (a scene keeps performing)
7. Transition vocabulary

## 1. Hierarchy in time
Motion order is reading order. The most important element moves first and furthest; supporting elements move
less (50-70% of the hero's travel), later (100-200ms) and on the same curve family. Everything else holds still.
One hero move per screen or shot. Squint at a contact sheet: at every sampled moment there should be one thing the
eye follows.

## 2. Entrances and exits
- Entrance = opacity 0 -> 1 plus a small directional cue (translateY 8-24px, scale 0.96, or a mask/clip-path
  reveal), on an ease-out. Blur 4-8px -> 0 is a polish detail for a hero, not for every block.
- Exit = shorter, subtler, accelerating; the user's attention is already moving on.
- Product UI: text people read appears instantly or with a quick fade. Showcase sites: text performs too -
  headings split by words/chars in masks, body copy by lines, labels by words (site-motion.md §3), then holds still.
- Landed titles are dead still. No creeping scale, no float.
- Vary entrances by content type: a list arrives row by row, a picture opens from a mask, a figure counts up once,
  a card rises; the same fade-up on every block is the slop tell.

## 3. Transitions in interfaces
- Spatial: a detail view grows from the card that opened it (shared element / FLIP / View Transitions), a sheet
  slides from the edge it lives on, navigation forward moves left and back moves right.
- State: content swaps in place with a short crossfade (a 2-4px blur masks a seam that will not settle).
- Containers morph rather than cut: the button becomes the menu, the pill becomes the input.
- Layout changes animate transforms (FLIP), never width/height/top/left.

## 4. Scroll choreography
- Reveal once, at ~85% of the viewport, in reading order inside each section (heading -> body -> media -> CTA,
  overlapping 0.15-0.25s); content is visible without JS and under reduced motion.
- Scrubbed scenes (pinned sections): ease "none" on the scrubbed timeline, total pin <= 2-3 screens, every pinned
  screen shows progress (something visibly changes per ~100px of scroll).
- Parallax: small offsets (5-15%), only on images/shapes, never on text people read, removed under reduced motion.
- Horizontal galleries via `containerAnimation` with ease "none"; native horizontal scroll with snap on touch.
- Smooth scroll (Lenis `lerp` ~0.09) on showcase sites for desktop fine pointers, synced to ScrollTrigger, never
  trapping or overriding keyboard/anchor navigation; native on touch and under reduced motion.
- Scroll-linked motion is smoothed (`scrub: 0.8-1.2`), images parallax inside their frames, never the text being read.

## 5. Film grammar (adapted from the HyperFrames motion doctrine, Apache-2.0)
**The vector law** - how scene A exits decides how scene B enters: same axis, same direction, matched speed, and
the cut lands mid-motion on both sides. On Z, direction is the sign of scale change: growing = push, shrinking =
pull; a pull-back exit answered by a grow-from-small entry is the most common violation.
**The current** - pick one dominant direction for the film (e.g. left). Ordinary seams use it; other vectors are
reserved and mean something: upward = conclusion/elevation, Z forward = deeper into the thought, Z backward =
arrival of something bigger, scale burst = leaving a world. Never ping-pong directions without a visible cause.
**Carriers** - the eye follows objects. The strongest seams hand a concrete object across the cut at matched
position and velocity: a cursor mid-path, a container that docks into the next layout, a mark flying into its slot.
A crossfade has no carrier - avoid it between worlds.
**Causal motion** - each move is visibly launched by the last: click -> squash -> release -> flight -> impact ->
recoil -> reveal. Effects start on the causing frame, never "shortly after". A direction change needs a force.
**Stillness before climax** - 0.3-0.75s pause between the action and its payoff.
**Write the plan first** - a seam ledger: one row per cut with time, exit vector, entry vector, carrier, technique.
If a row mismatches, fix the plan, not the easing.

## 6. Sustained motion - the scene keeps performing
Idle loops (breathe, float, drift, glow pulse) are not motion; they read as "the video is waiting". Every stretch
between entry and exit is owned by one of:
- staged reveals - content held back and paid off on beats;
- camera with intent - establish wide -> travel -> arrive on the subject;
- sequenced UI life - the product behaves: progress advances, rows populate, counts tick;
- animated sequences - elements act out the beat (a card files into a stack, an item is dragged);
- cursor-led action - an oversized cursor walks the eye to a trigger; its click ignites the next beat.
Test: pause at any second - something meaningful is mid-flight.

## 7. Transition vocabulary
3-5 kinds of transition per film, each caused by something on screen, repeated rather than all different. Default
seam: cut-the-curve in the current's direction. At most a third of seams are hard cuts; worlds never crossfade.
Catalogue with build notes: `search.py -d transition` (zoom-through, inverse zoom, object becomes the world, morph,
carry across, colour flood, whip, iris from the click, dip cut, blur swap, match cut, foreground wipe, rack focus,
View Transitions, page wipe, shared element, pinned scene).
Launch-film shot language measured from Apple/Linear films (38 shots with timings and eases): `search.py -d shot`.
