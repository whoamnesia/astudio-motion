---
name: lottie-rive
description: >-
  Lottie and Rive by astudio: integrating, controlling and optimising designer-made animation in products -
  dotLottie/Lottie playback, segments, scroll-driven and interactive Lottie, runtime theming, size optimisation;
  Rive state machines (inputs, transitions, listeners), data binding with view models, events, runtimes for web,
  React, React Native, iOS, Android, Flutter; choosing Lottie vs Rive vs code; preparing files for handoff (After
  Effects + Bodymovin, Figma Motion, Lottie Creator, Cavalry exports). Use for "Lottie", ".lottie", "Bodymovin",
  "Rive", ".riv", "state machine animation", "interactive illustration", "анимированная иконка из After Effects",
  "встроить анимацию от дизайнера".
argument-hint: "[file .json/.lottie/.riv or what should animate] [platform]"
---

# astudio · Lottie & Rive

Role: Senior Motion Designer & Creative Developer at astudio.one (15+ years) - designer-made animation that ships
crisp, small and interactive. Bar: `<root>/reference/studio-bar.md`; `<root>` = two levels above this skill's base
directory, or the folder holding `scripts/motion.cjs`.

## Choose the format
| Need | Pick |
|---|---|
| a designer-made linear animation (icon, illustration, onboarding scene, empty state) played/paused/segmented | **Lottie** (`.lottie` via dotLottie runtime) |
| interactive, stateful animation that reacts to input or app data (buttons with states, characters, progress, game UI, data-driven illustrations) | **Rive** (state machines + data binding) |
| simple UI state changes, hover/press, transitions | CSS/Motion (`astudio-motion:ui-motion`) - no file needed |
| logo/icon you can draw in SVG and animate in code | SVG + GSAP (`astudio-motion:svg-motion`) - export Lottie only if an app runtime needs it |
| video-like content (people, footage) | video (`<video>`), not Lottie |

## Lottie workflow (`references/lottie.md`)
1. Prefer `.lottie` (zip, 60-80% smaller, bundles images/themes/state machines) + `@lottiefiles/dotlottie-web`
   (canvas + WASM) or `@lottiefiles/dotlottie-react`; `lottie-web` only for legacy SVG-renderer needs.
2. Control: `play/pause/stop/setSpeed/setMode/setFrame/setSegment`, events `load/complete/frame`; segment-based
   "state machines" (play the `checked` segment, then loop `idle`).
3. Scroll: map scroll progress to `setFrame`; interactivity without wiring via `@lottiefiles/lottie-interactivity`.
4. Theme at runtime (brand colours, dark mode) via dotLottie themes/slots - don't ship two files.
5. Optimise: remove hidden layers/unused assets, no raster images unless necessary, fewer masks/mattes/effects
   (unsupported or slow), trim to the visible frame range, check the file size (< 50-100KB for icons).
6. Accessibility: `role="img"` + `aria-label`; pause under reduced motion (show a meaningful static frame via
   `setFrame`); no autoplay loops > 5s without a pause control.

## Rive workflow (`references/rive.md`)
1. In the editor: artboards, timelines, a **state machine** (states, transitions with conditions, inputs:
   boolean/number/trigger, listeners for pointer events), **view models** for data binding (string/number/color/
   enum/trigger/list properties bound to scene properties), events for app callbacks.
2. Runtime: `@rive-app/react-canvas` (`useRive`, `useStateMachineInput`, `useViewModel`, `useViewModelInstance*`),
   `@rive-app/canvas` for vanilla, native runtimes for iOS/Android/Flutter/RN; WebGL2 renderer for heavy scenes.
3. Drive it from app data (data binding) instead of a pile of inputs; listen to Rive events for app reactions.
4. Preload critical files; size the canvas with `useRive`'s layout (`Fit`, `Alignment`); pause off-screen.

## Look
`node <root>/scripts/motion.cjs strip page.html --duration <s>` renders a page hosting the Lottie/Rive file (clock
mode drives their rAF loops). Check the first and last frames, segment boundaries, and colours after theming.

## Handoff notes for designers
- AE -> Lottie: Bodymovin/LottieFiles plugin; supported: shape layers, transforms, trim paths, masks (limited),
  text (prefer outlined), precomps; avoid expressions-heavy rigs, effects, 3D layers, blending modes.
- Figma Motion exports MP4/GIF/SVG/WebM and code (CSS/React/motion.dev) - for Lottie use Lottie Creator or the
  LottieFiles plugin. Cavalry exports Lottie natively.
- Name layers meaningfully (they become selectors for theming and debugging); deliver `.lottie` with themes.
