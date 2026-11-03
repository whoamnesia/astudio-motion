# Three.js / R3F gotchas (r180-r183) - wrong -> right

Distilled from CloudAI-X/threejs-skills and OpenAEC three.js packages (MIT). `motion_lint.py` flags several.

## Renderer, loop, time
- `<script src="three.min.js">` -> ES module via import map (build/three(.min).js removed in r161).
- `three/examples/jsm/...` -> `three/addons/...` (the examples path fails under import maps).
- `requestAnimationFrame(animate)` -> `renderer.setAnimationLoop(animate)` (WebXR only runs through it; WebGPURenderer
  awaits init inside it).
- `new THREE.Clock()` / `getElapsedTime()` -> `const timer = new THREE.Timer(); timer.connect(document);` then
  `timer.update()` first in the loop and `timer.getDelta()/getElapsed()` (Clock deprecated r183; getElapsedTime calls
  getDelta internally and zeroes the next delta).
- reading `renderer.info.render.calls` before `render()` -> after it (counters reset at the start of render).
- `renderer.compile()` -> `await renderer.compileAsync(scene, camera)` (compile returns before programs finish).

## Colour, light, shadows
- `outputEncoding = sRGBEncoding` -> `outputColorSpace = THREE.SRGBColorSpace`; textures: `colorSpace`.
- `new PointLight(0xffffff, 1, 100)` -> `new PointLight(0xffffff, 100, 20)` (candela, inverse-square).
- `useLegacyLights` / `physicallyCorrectLights` do nothing - retune intensities.
- `PCFSoftShadowMap` -> `PCFShadowMap` (r182).
- `RGBELoader` -> `HDRLoader` from `three/addons/loaders/HDRLoader.js` (r180).
- `scene.background = hdr` -> also `hdr.mapping = THREE.EquirectangularReflectionMapping` (else a flat quad).
- manual PMREM for an equirect environment adds nothing - assign the texture with the mapping; keep PMREMGenerator for `fromScene`.
- `light.layers.set(1)` does not limit a light to meshes - lights are tested against the camera's layers.
- `mesh.layers.set(1)` -> `mesh.layers.enable(1)` (set removes layer 0 where camera and lights live).
- `new ContactShadows()` doesn't exist in three - it's drei; in vanilla fake it with a radial-gradient plane.

## Materials and textures
- `ShaderMaterial({ glslVersion: GLSL3 })` + `gl_FragColor` -> leave glslVersion unset (already GLSL ES 3.00 with the alias).
- `material.envMapIntensity` to dim `scene.environment` -> `scene.environmentIntensity`.
- `material.stencilMask` doesn't exist -> `stencilFuncMask` / `stencilWriteMask`; stencil needs `WebGLRenderer({ stencil: true })`.
- multiply/subtract blending need `premultipliedAlpha = true`.
- aoMap no longer needs a `uv2` attribute - it samples `aoMap.channel` (0 = uv).

## Disposal and memory
- `material.dispose()` -> also dispose every texture on the material.
- `gltf.scene.dispose()` -> traverse: geometry.dispose(), each material's textures + material.dispose().
- disabling `frustumCulled` scene-wide -> `geometry.computeBoundingSphere()` after CPU vertex edits.
- allocating `new Vector3()` every frame -> reuse module-level temporaries.

## Post-processing
- `ShaderPass(GammaCorrectionShader)` -> `OutputPass` (tone mapping + colour space) ending every chain.
- FXAA after OutputPass (needs sRGB); SMAA before it (linear).
- `new FilmPass(0.35, 0.5, 648, false)` -> `new FilmPass(0.35, false)`; `SMAAPass(w, h)` / `HalftonePass(w, h, p)` -> no size args (r175).
- half-resolution bloom via constructor size is undone by `addPass` resize - set `bloomPass.resolution` after, or use selective bloom.
- EffectComposer with WebGPURenderer -> TSL `PostProcessing` (`references/webgpu-tsl.md`).

## React Three Fiber
- rAF loop -> `useFrame`; fixed `+= 0.01` -> `+= delta * speed`.
- `useFrame(() => setRotation(...))` -> mutate `ref.current` (no React re-render per frame).
- `useFrame(fn, 1)` (positive priority) stops automatic rendering - render yourself or use 0.
- `state.clock.getElapsedTime()` -> `state.clock.elapsedTime`.
- `position={{ x: 1 }}` -> `position={[1, 0, 0]}`.
- `useEffect(() => new GLTFLoader().load(...))` -> `useGLTF(url)` (+ `useGLTF.preload(url)`).
- `useGLTF(url).scene.clone()` for skinned meshes -> `useMemo(() => SkeletonUtils.clone(scene), [scene])`.
- `<Canvas frameloop="demand">` + `invalidate()` for static scenes; `dpr={[1, 1.75]}`; `<PerformanceMonitor>` to scale quality.
- Raycasting all objects on every pointer move -> limit with `layers` / explicit pickable lists; `<Bvh>` for heavy meshes.
