# WebGPU and TSL (Three Shading Language)

Status: WebGPURenderer and TSL are production-usable but evolving - pin the three.js version. WebGPU: Chrome/Edge
113+, Safari 18+ (macOS/iOS 26 broadly), Firefox behind a flag on some platforms. Always ship a WebGL fallback
(WebGPURenderer falls back to its WebGL2 backend automatically when `forceWebGL` or unavailable - test both).

## Setup
```js
import * as THREE from 'three/webgpu';
import { color, uv, sin, time, mix, positionLocal, normalLocal, Fn, vec3 } from 'three/tsl';
const renderer = new THREE.WebGPURenderer({ antialias: true });
await renderer.init();                       // MUST resolve before the first render
renderer.setAnimationLoop(render);           // not requestAnimationFrame
```
- No raw GLSL/ShaderMaterial with the WebGPU backend - write node materials in TSL (compiles to WGSL or GLSL).
- No EffectComposer - use `const post = new THREE.PostProcessing(renderer); post.outputNode = ...` with TSL passes
  (`pass(scene, camera)`, `bloom()`, `dof()`, `fxaa()`...).
- Built-in `time` / `deltaTime` nodes are uniforms the renderer updates - don't feed your own Timer into a uniform.
- Compute: `const update = Fn(() => { ... })().compute(count); renderer.compute(update);` for GPU particles (100k+).

## Node material example (animated surface)
```js
const mat = new THREE.MeshStandardNodeMaterial({ roughness: 0.35 });
const wave = sin(positionLocal.y.mul(6).add(time.mul(1.5))).mul(0.04);
mat.positionNode = positionLocal.add(normalLocal.mul(wave));          // vertex displacement
mat.colorNode = mix(color('#14161C'), color('#E0592A'), uv().y.add(wave.mul(4)));
```

## When to choose WebGPU
GPU compute (particles, simulations, instancing at scale), modern post chains, or a project already on it. For a
simple hero object WebGL is fine and more compatible. Counters differ: `renderer.info.render.drawCalls` per frame
(WebGPU) vs `info.render.calls` (WebGL).

## Fallback
```js
import WebGPU from 'three/addons/capabilities/WebGPU.js';
const renderer = WebGPU.isAvailable() ? new THREE.WebGPURenderer() : new THREE.WebGPURenderer({ forceWebGL: true });
```
Plus a static poster for no-GPU / reduced-motion cases. The motion.cjs renderer has WebGL2 (SwiftShader) but no
WebGPU in headless CI - review WebGPU scenes with `forceWebGL: true` there.
