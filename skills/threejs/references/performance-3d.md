# 3D performance and fallbacks

## Budgets (mid-range laptop / phone)
| Item | Target |
|---|---|
| pixel ratio | `min(devicePixelRatio, 1.5-2)`; full-screen shaders 1 |
| draw calls | < 50-100 (phone), < 300 (desktop) |
| triangles | hero object 50-150k; whole scene < 500k (desktop) |
| textures | <= 2048 px, KTX2/Basis; total VRAM < ~200MB |
| model download | < 2-5MB (Draco/meshopt); stream secondary assets later |
| shadows | one caster light, 1024-2048 map; or baked/fake contact shadows |
| post-processing | 1-3 passes; bloom selective; no full-res DoF on phones |

## Techniques
- Instancing (`InstancedMesh`, `BatchedMesh`) for repeats; merge static geometry; LOD for big scenes.
- Render on demand for static views (`frameloop="demand"` / render only on input); pause when the canvas is off-screen
  (IntersectionObserver) or the tab is hidden.
- `compileAsync` and preloading before reveal; show a poster/skeleton while loading, fade the canvas in when the first
  frame is ready.
- Avoid per-frame allocations; reuse vectors; update uniforms not materials.
- `renderer.info` after render for calls/triangles/textures; Spector.js for frame captures; Chrome Performance for
  CPU; `PerformanceMonitor` (drei) to lower DPR/effects adaptively.

## Fallbacks and accessibility
- No WebGL/WebGPU: a static image (poster rendered from the scene: `motion.cjs still scene.html --at 2`), same layout.
- Reduced motion: no auto-rotation, no scroll-driven camera flights, no parallax; the scene shows its hero pose;
  interactions that the user starts (drag) remain.
- Canvas is decorative unless it carries information: `aria-hidden="true"` + text nearby, or `role="img"` with a label.
- Never block scrolling or text with the canvas; pointer events only where interaction exists (`pointer-events: none`
  on decorative canvases).
- Battery: cap fps at 30 for ambient backgrounds; stop when hidden.
