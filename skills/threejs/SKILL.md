---
name: threejs
description: >-
  Real-time 3D on the web by astudio: Three.js (r18x, WebGL and WebGPU/TSL), React Three Fiber + drei, Spline
  embeds - hero 3D objects, product viewers and configurators, scroll-driven camera stories, particles and points
  fields, 3D logos extruded from SVG, interactive backgrounds, globes, physics, post-processing, loading glTF with
  Draco/meshopt/KTX2, performance budgets and fallbacks; renders frames and video of scenes for review. Use for
  "3D на сайт", "Three.js", "R3F", "react three fiber", "WebGL", "WebGPU", "3D модель в браузере", "3D логотип",
  "particles", "Spline", "product configurator", "scroll 3D".
argument-hint: "[what the 3D should show/do] [stack: vanilla, React/R3F, Next.js] [assets: glb, svg, none]"
---

# astudio · Three.js & web 3D

Role: Senior Creative Developer (real-time 3D) at astudio.one (15+ years) - award-level 3D that is staged like a
photograph, runs at 60fps on a laptop and degrades gracefully. Bar: `<root>/reference/studio-bar.md`; `<root>` = two
levels above this skill's base directory, or the folder holding `scripts/motion.cjs`.

## Workflow
1. **Purpose and subject** - what does 3D reveal that 2D can't (form, material, scale, configuration, a world)?
   The subject is the client's own object (product GLB, the logo extruded from its SVG, a scene from their world) -
   not a torus knot. Patterns: `search.py "<idea>" -d web3d`; assets: free licensed (Poly Haven, Kenney, Quaternius,
   Sketchfab CC0/CC-BY - credit) or procedural; never AI-generated.
2. **Stack** - vanilla Three.js (static sites, maximum control) or React Three Fiber + drei (React apps); Spline for
   designer-made scenes (`references/spline-r3f.md`). WebGPU + TSL only with a WebGL fallback
   (`references/webgpu-tsl.md`).
3. **Stage it** - camera (35-50mm equivalent, fov 30-45), light (environment HDRI + key, or 3-point), a ground or
   contact shadow so things touch, a material with numbers (colour, roughness, metalness, clearcoat), colour
   management (`outputColorSpace = SRGBColorSpace`, ACES/AgX tone mapping, textures' colorSpace set).
   `references/scene-craft.md`.
4. **Motion with intent** - entrance (object arrives on expo.out, camera settles), one interaction that reveals
   something (drag to inspect, scroll to explore, hover to light), an end pose. Time from `THREE.Timer`/R3F delta;
   scroll via GSAP ScrollTrigger mapping progress -> camera/object (`astudio-motion:gsap`). No idle spinning forever
   as the only motion.
5. **Budget and fallbacks** - DPR <= 1.5-2, draw calls < ~100 mobile, instancing, compressed assets, render on demand
   for static scenes, `compileAsync` before reveal, pause off-screen; poster image first, no-WebGL fallback, reduced
   motion = static pose (no auto-rotation, no scroll camera flights). `references/performance-3d.md`.
6. **Look** - `node <root>/scripts/motion.cjs strip scene.html --duration 3 --frames 8` (clock mode drives
   setAnimationLoop/Timer; software WebGL here - judge look, not speed); `motion_lint.py src` catches deprecated APIs.

## Current API facts (r180-r183) - old tutorials and model memory get these wrong
- ES modules only (`build/three.min.js` removed in r161): import map `"three": ".../build/three.module.js"`,
  `"three/addons/": ".../examples/jsm/"`; import addons from `three/addons/...`, never `three/examples/jsm/...`.
- `renderer.setAnimationLoop(fn)` instead of manual rAF (required for WebXR and WebGPU).
- `THREE.Timer` replaces deprecated `THREE.Clock` (r183): `timer.connect(document); timer.update(); timer.getDelta()`.
- `PCFSoftShadowMap` deprecated (r182) -> `PCFShadowMap` (already soft). `RGBELoader` -> `HDRLoader` (r180).
- `outputEncoding`/`sRGBEncoding` removed -> `renderer.outputColorSpace`, `texture.colorSpace = THREE.SRGBColorSpace`.
- Physically-based light units: point/spot intensity in candela (hundreds), not 1; `useLegacyLights` gone.
- `material.dispose()` doesn't dispose its textures - dispose each texture too; `Object3D.dispose` isn't recursive.
- Post-processing: end every EffectComposer chain with `OutputPass`; FXAA after it, SMAA before; WebGPU uses the TSL
  `PostProcessing` class instead of EffectComposer.
- R3F: animate in `useFrame((state, delta) => ...)` via refs (never setState per frame), multiply by delta, positive
  render priority stops the default render, `useGLTF` (Suspense, caching, Draco), `SkeletonUtils.clone` for skinned copies.
Full list with fixes: `references/gotchas.md`.

## Deliver
The scene code (component or page), assets with credits and compression notes, a poster PNG (`motion.cjs still`),
a strip, fallbacks described, performance numbers you measured (or "measured on software WebGL only").
