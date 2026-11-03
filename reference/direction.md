# Motion direction: from brand to numbers

Adjectives are where the default motion lives. Given "smooth, modern, premium" the model fills every gap with the
same defaults: everything fades up on power2.out in 0.5s. Every adjective turned into a number is a decision taken
back from those defaults.

## 1. Read what exists
- Existing motion tokens/curves in the codebase (CSS vars, Tailwind theme, `motion.ts`, GSAP defaults, Figma motion
  variables). Extend them; a parallel system is a defect.
- The brand: logo geometry, type, colour, voice (astudio-aio's DESIGN.md / tokens if present).
- The stack and runtime: React/Vue/Svelte/static, Motion/GSAP already installed?, React Native/SwiftUI/Compose,
  video pipeline (Remotion/HyperFrames), 3D (three/R3F/Spline).
- References (studio-bar.md §3) and the built-in plan: `search.py "<brief>" --plan`.

## 2. Motion personality -> numbers
Pick 2-3 brand words and translate each:
| Word | Becomes |
|---|---|
| precise / technical | ui-out curves, 150-250ms, no overshoot, straight paths, hard cuts allowed, mono-rhythmic staggers |
| premium / calm | expo-out arrivals 600-900ms, springs damping 0.8+, long holds, little simultaneous motion, slow camera (3-5°/s) |
| friendly / human | ui-out + springs damping 0.7, 3-5% overshoot on arrivals, arcs, soft follow-through |
| playful / young | springs damping 0.45-0.6 on position/scale, squash on impact, staggered characters, colour floods |
| bold / energetic | fast moves 0.3-0.4s with motion blur, cuts on the beat, whips, scale bursts, high contrast in timing |
| cinematic | a lens and a light: 35mm framing, key light upper left, rim behind, 6% vignette, camera with intent, rack focus |
| editorial | type-led: mask reveals of lines, hold to read, minimal motion outside type |
| smooth / silky / "как на Awwwards" | total choreography (site-motion.md): expo.out 1.1-1.3s reveals, image wipes 1.4s with inner scale, Lenis lerp 0.09, scrub 1, staggers chars 0.02 / words 0.05 / lines 0.09, hovers 0.55s soft, nothing under 0.6s |

## 3. The motion contract (write it before code, ~150 words)
```
ROLE:        Senior Motion Designer, astudio.one - a commission at award level
PURPOSE:     what motion does here (feedback / orientation / story / delight), in one sentence
REFERENCES:  3-8 links or built-in shots/patterns, and what is taken from each
PERSONALITY: 2-3 words -> their numbers (curves, springs, durations, overshoot, blur)
SYSTEM:      tokens: durations, eases, springs, stagger; reduced-motion mapping
SIGNATURE:   the one authored moment (hero/scroll scene/transition/logo sting/3D reveal)
CHOREOGRAPHY: order of things, the current/direction, transitions with causes
COVERAGE:    sites - the reveal grammar per content type; every section and element performs (site-motion.md §3)
BUDGET:      frequency tiers; what never animates; perf budget (fps, DPR, draw calls, file sizes)
DONE:        strips + check + lint pass, reduced-motion tiered, spec/tokens delivered
```
If a line reads like a mood ("smooth and modern"), it is not decided yet.

## 4. The film SPEC (video work)
```
GOAL:    what the viewer feels/does at the end
OUTPUT:  W x H, fps, length (seconds x fps = frames); BPM + frames per beat if music
LOOK:    ground hex + texture %, ink, one accent and where it may appear; display face/weight/px/tracking;
         the medium (paper, product UI, glass, clay, 3D studio) with numbers; light, shadow, grain, vignette
OBJECTS: every thing the story needs recognised, with the material/details that make it read without a label
MOTION:  eases by role as named curves; springs as damping ratio; durations and staggers in frames
SHOTS:   one line per shot: frame range, the hero move, what the viewer reads (and for how long), sound, hand-off
BANNED:  the defaults this film must not become (anti-slop.md) + brand-specific
QA:      frames to check and what each must show
```

## 5. Present directions
For new brand motion, offer 2-3 directions compactly: name, personality words with their numbers, the signature
moment in one line, a 6-frame strip or a 3-second loop, honest risk. Unattended / "just do it": commit to the
strongest and name the others in one line each.
