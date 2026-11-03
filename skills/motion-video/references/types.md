# What each kind of film needs

## Launch / promo / feature (20-45s)
- Shape: hook -> tension -> reveal -> proof -> payoff -> claim -> end card.
- Real UI, never a mockup: from the person's recordings/screenshots, Figma frames rebuilt as states of one app (the
  change between two frames is a real click), the product's code/docs for today's labels. Missing screen -> a
  labelled placeholder. Logos/icons/fonts are the brand's files.
- Establish the workspace (enough navigation to locate the task) -> isolate the action (the relevant panel rebuilt
  and shown at 1.6-2x, text >= 26px at 1080p after the push; let a result populate) -> return the result into its
  place (or pull back to show where it is used). Never a small window in an empty canvas, never UI tilted in 3D.
- Camera cycles window -> pane -> punch-in on one control; moves 0.4-0.6s with motion blur, arriving where the cursor
  needs to be, then holding while the UI acts. Containers morph (the button becomes the menu).
- Cursor 4-7% of the frame, enters from off-screen; its click causes the next thing on the same frame.
- Shots to borrow: `search.py "<idea>" -d shot` - Auto Zoom, Morph Relay, Control-Driven Change, Pile-up and Clear,
  Prompt Carousel, Device Push-in, Rotate to Lockup, Mark-to-Wordmark Unfold...
- Real people and real output get shared; effects-heavy pieces don't.

## Explainer / tutorial
- One concept, one worked example, built in reading order; information cards on screen within ~2.5s, then held so any
  paused frame reads as a finished poster.
- Diagrams build step by step (svg-motion diagrams); highlight the active element; recap at the end.

## Data / chart video
- Real numbers, sourced on screen; charts draw in reading order (axes -> baseline -> series -> annotation);
  odometer counters with tabular figures, each digit slot sized to its final glyph.
- One insight per beat; the annotation states the finding in words.

## Social / vertical (9:16 1080x1920, 4:5 1080x1350, 1:1)
- Hook in the first second; readable without sound (captions/large type); safe areas: keep text and key action out
  of the top ~250px and bottom ~340px (platform UI); 6-15s for ads, 15-60s for content.
- Recompose for the format (don't letterbox the 16:9): stack, crop to the action, bigger type.
- Loop seamlessly when it loops: last frame = first frame (`motion.cjs check --loop`).

## Logo sting / end card
`astudio-motion:svg-motion` (2D) or threejs/blender (3D); 1.5-3s + hold; frame 0 already composed (part of the mark
on screen, mid-motion); end frame = the lockup; a designed sound hit on the settle only when sound was requested.

## Changelog / release notes video
Each item = one 3-5s beat: the UI before -> the change happening -> the label; same transition throughout (morph or
cut-the-curve in the current); a title card per section; 30-60s total.

## Character / mascot short
Acting, not idle wobble: anticipation, follow-through, overlapping action on the character are acting; the camera
and titles still obey the film rules.

## 3D / generative pieces
Build the 3D in three.js inside the film page (driven by `__seek` - set object transforms from time, render once per
frame) or render in Blender and composite the frames as `<video>`/image sequence. A 3D object needs a world (light,
ground, camera with intent), not a void.

## Music video / beat-driven
BPM -> frames per beat; layout changes on the bar, cuts on beats, accents on off-beats; the drop lands on the
biggest visual moment; analyse the track (`references/sound.md`).
