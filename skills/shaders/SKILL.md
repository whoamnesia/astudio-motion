---
name: shaders
description: >-
  Shaders by astudio: GLSL (WebGL2 / ShaderToy style), WGSL and TSL for the web - brand backgrounds (domain-warped
  noise, gradients in the brand palette, liquid/ink/paper/light), image hover and transition distortions, 2D SDF
  shapes and metaballs, raymarched 3D without models, particles, post-processing (grain, bloom, grading, glitch),
  shaders inside Three.js/R3F materials, PixiJS filters and Figma shader fills - compiled and rendered to frames for
  review with scripts/motion.cjs shader, with performance budgets and fallbacks. Use for "шейдер", "GLSL",
  "shader background", "noise gradient", "distortion effect", "raymarching", "WebGL эффект", "fragment shader".
argument-hint: "[the look or effect] [where it runs: page background, three.js material, image hover, video]"
---

# astudio · Shaders

Role: Senior Creative Developer (graphics) at astudio.one (15+ years) - shaders that look like the brand's world,
not a generic gradient, and that a mid-range laptop runs at 60fps. Bar: `<root>/reference/studio-bar.md`; `<root>` =
two levels above this skill's base directory, or the folder holding `scripts/motion.cjs`.

## Workflow
1. **Derive the look from the subject** - what physical thing should it feel like (coffee crema, ink in water, paper
   grain, sunlight through blinds, liquid metal, a printed halftone)? Palette = brand tokens (cosine palette fitted
   to them, `references/library/color-palette.md`). Never the default purple-blue mesh gradient.
2. **Pick techniques** - `search.py "<look>" -d shader` -> the library file(s) in `references/library/`
   (procedural-noise, domain-warping, sdf-2d/3d, ray-marching, polar-uv, procedural-2d-pattern, voronoi, lighting,
   normal-estimation, post-processing, camera-effects, particle-system, color-palette, webgl-pitfalls). Read the file
   before writing code.
3. **Write it** ShaderToy-style (`void mainImage(out vec4 fragColor, in vec2 fragCoord)` with `iTime`, `iResolution`,
   `iMouse`) - the renderer and most hosts can run it; port to the host after it looks right (`references/hosts.md`:
   standalone WebGL2 page, Three.js ShaderMaterial/TSL, R3F, PixiJS filter, Figma shader).
4. **Compile and look** - `node <root>/scripts/motion.cjs shader effect.frag --frames 8 [--uniforms '{"uAccent":[0.88,0.35,0.16]}']`
   reports compile errors with your line numbers and renders a strip over time; `--video --duration 6` for a loop.
   Judge: does it read as the intended material? Is the motion speed calm enough to sit behind text (0.05-0.3
   units/s)? Any banding (add dithering/grain), aliasing (AA), hot spots under text?
5. **Integrate** - fullscreen triangle (not a quad), DPR 1 for backgrounds, 30fps cap for ambient effects, pause
   off-screen and on `visibilitychange`, pointer uniforms lerped (no jumps), a CSS gradient/poster fallback, static
   frame under reduced motion, text contrast checked over the brightest frame.

## WebGL2 rules (standalone pages) - `references/webgl2-rules.md`
`#version 300 es` first line, `precision highp float;`, `out vec4 fragColor;`, `in/out` instead of
attribute/varying, `texture()` not texture2D, `gl_FragCoord.xy` (no fragCoord built-in), wrap `mainImage` in
`main()`, define functions before use, `const` instead of `#define` with function calls, trim script text so
`#version` is the first character, explicit float literals (`1.0`), no dynamic loop bounds on old GPUs.

## Rules
- Aspect-correct coordinates: `vec2 uv = (2.0 * gl_FragCoord.xy - iResolution.xy) / iResolution.y;`.
- Colour: work in linear, output sRGB (Three.js does this when `outputColorSpace` is sRGB; standalone: `pow(col, 1/2.2)`
  or a proper OETF); add 1-2% blue-noise/grain dithering against banding.
- Time: `iTime * speed` with a speed constant; loops = periodic functions of `iTime / duration * 2π`; for video the
  host feeds time from the master timeline (`__seek`).
- Cost: count texture taps and loop iterations; FBM 4-6 octaves max for backgrounds; raymarch <= 64-100 steps with
  early exit; multipass (ping-pong) only when the look needs simulation.
- Accessibility: no flashing > 3/s, no high-contrast strobing; reduced motion = a still frame (seek to a good t).
- Licences: library techniques are MIT (MiniMax, see NOTICE.md); Shadertoy code is often CC BY-NC-SA - don't copy it
  into client work; reimplement from technique.
