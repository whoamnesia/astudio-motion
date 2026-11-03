# Running shaders in hosts

## Three.js ShaderMaterial (WebGL)
```js
const mat = new THREE.ShaderMaterial({
  uniforms: { uTime: { value: 0 }, uRes: { value: new THREE.Vector2() }, uAccent: { value: new THREE.Color('#E0592A') }, uPointer: { value: new THREE.Vector2() } },
  vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
  fragmentShader: `uniform float uTime; uniform vec3 uAccent; varying vec2 vUv; void main(){ gl_FragColor = vec4(uAccent * (0.6 + 0.4 * sin(vUv.x * 6.0 + uTime)), 1.0); }`,
});
// in the loop: timer.update(); mat.uniforms.uTime.value = timer.getElapsed();
```
ShaderMaterial is GLSL ES 3.00 with `gl_FragColor` still aliased - leave `glslVersion` unset. Three provides
`projectionMatrix`, `modelViewMatrix`, `position`, `uv`, `normal`; `RawShaderMaterial` provides nothing.
Colour: Three converts linear -> sRGB on output; include `#include <colorspace_fragment>` / `<tonemapping_fragment>`
when your shader should match the renderer's pipeline.
Patching built-in materials: `material.onBeforeCompile = shader => { shader.uniforms.uTime = ...; shader.vertexShader = shader.vertexShader.replace('#include <begin_vertex>', ...) }`
keeps lighting/shadows while adding displacement.

## Three.js WebGPU (TSL)
No GLSL - node materials (see `astudio-motion:threejs` -> `references/webgpu-tsl.md`): `mat.colorNode = mix(color(a), color(b), mx_noise_float(uv().mul(3).add(time.mul(.1))))`.
TSL has `mx_noise_*`, `mx_fractal_noise_*`, `mx_worley_noise_*` built in.

## React Three Fiber
`shaderMaterial` from drei: `const WaveMaterial = shaderMaterial({ uTime: 0, uAccent: new THREE.Color() }, vert, frag); extend({ WaveMaterial });`
then `<waveMaterial ref={m} />` and `useFrame((_, d) => (m.current.uTime += d))`.

## Image hover / transition distortion (common web effect)
Plane per image (or one fullscreen plane sampling two textures); uniforms `uTex0`, `uTex1`, `uProgress`, `uPointer`;
displacement `uv += normalize(uv - uPointer) * strength * smoothstep(r, 0., length(uv - uPointer))` or a noise-driven
mix `mix(texture(t0, uv + d * uProgress), texture(t1, uv - d * (1. - uProgress)), uProgress)`. Animate `uProgress`
with GSAP (power2.inOut, 0.8-1.2s). Keep images' aspect with a `cover` UV transform.

## PixiJS
`new PIXI.Filter({ glProgram: PIXI.GlProgram.from({ vertex, fragment }), resources: { uniforms: { uTime: { value: 0, type: 'f32' } } } })`
(Pixi v8) - 2D sprites with GPU effects, many objects, games.

## In a motion.cjs film
Host the shader in a `<canvas>` inside the film page and render from the master timeline:
`window.__seek = t => { master.seek(t); drawShader(t); }` - time is the timeline's, never `performance.now()`.

## Figma
Figma's shader fills/effects (2026) are keyframeable on the Motion timeline; to implement them in code, reproduce the
look as a fragment shader (gradient/noise/blur families) and match parameters by eye against an exported frame.

## Fallbacks
`if (!canvas.getContext('webgl2'))` -> CSS gradient in the same palette; reduced motion -> render one frame at a chosen
t and stop; low-power -> lower resolution (`canvas.width = clientWidth * 0.5` + CSS upscale for soft backgrounds).
