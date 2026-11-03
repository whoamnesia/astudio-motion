# Motion pipeline playbook

## 1. Brief template (write it down in phase 1)
```
CLIENT / PRODUCT: name · what it is · audience · language(s)
SURFACE:          product UI | marketing site | brand film | social clip | 3D experience | mobile app (per part if mixed)
GOAL:             what motion must achieve (orientation, feedback, story, conversion, delight) - one sentence
DELIVERABLE:      code in <stack> | MP4/WebM/GIF W x H fps length | Lottie/Rive | .blend + renders | AE/C4D scripts
EXISTING:         motion tokens, libraries installed (motion, gsap, three, lottie, rive), brand assets, references given
CONSTRAINTS:      performance targets, devices, accessibility level, deadline, legal (music, logos)
ASSUMPTIONS:      what I decided without asking (user can overrule)
```

## 2. Intake questions (only what blocks; one round)
- Where will it run and in what format (site/app/video/3D)? - blocks everything.
- What exactly moves and why (the moment or the system)? - blocks scope.
- Brand assets and existing motion (tokens, references, things to keep)?
- For video: length, aspect ratio(s), real product screens available? (Sound: silent unless the brief asks.)
Offer "decide for me". Never ask for curve values or durations.

## 3. Phase outputs
| Phase | Output |
|---|---|
| Direction | `.astudio/motion/references.md`, motion contract (MOTION.md draft or notes), SPEC.md for films |
| System | `design-tokens/motion.tokens.json`, `motion.css`, `motion.tailwind.css` (or merged into existing tokens) |
| Build | code in the project stack / video project / .blend + scripts |
| Review | `.astudio/motion/*.png` strips, `check` output, lint output, notes with P0-P2 |
| Deliver | previews (GIF/MP4/strips), MOTION.md, report |

## 4. Pulling in sub-skills mid-job
| Signal | Skill |
|---|---|
| a marketing/landing/showcase site to animate ("оживи сайт", "как на Awwwards") | gsap with `reference/site-motion.md` + `templates/site-motion.js` (total choreography); ui-motion only for app components |
| the logo must move (site intro, video end card, loader) | svg-motion (2D) or threejs/blender (3D) |
| a designer already made Lottie/Rive files, or the product needs stateful illustrations | lottie-rive |
| "make a video of it" | motion-video (reuses the same DOM/brand) |
| a 3D object or scene | threejs (web) / blender (renders, video, GLB) |
| a background/effect no library has | shaders |
| the team works in AE/C4D/Cavalry/Unreal/Figma | motion-tools (scripts, setups, handoff) |
| the product is a native app | native-motion |
| existing motion feels off/janky/cheap | motion-review first, then fix in the matching skill |

## 5. Delivery report
- What was made and where; how to preview (`npx serve`, open the HTML, the MP4/GIF paths).
- The motion idea and signature moment in two sentences; the personality numbers (curves, springs, durations).
- Checks run: `check` results, lint results, `coverage` (sites: % moving, static sections, LCP delta), strips
  reviewed (paths), what could not be checked (sound heard, GPU speed, real devices, Safari).
- Accessibility: what happens under reduced motion; pause controls.
- Assets and licences: stock/3D/fonts/music with credits; placeholders to replace.
- Weakest moment and what you would change with more time.
- Next steps: e.g. a film from the same motion system, Lottie exports of the icons, a MOTION.md review with the team.
