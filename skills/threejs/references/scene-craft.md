# Staging a 3D scene like a photograph

## Minimal modern scene (vanilla, import map)
```html
<script type="importmap">{ "imports": { "three": "https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js",
  "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/" } }</script>
<script type="module">
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';

const canvas = document.querySelector('#scene');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(devicePixelRatio, 1.75));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.AgXToneMapping; renderer.toneMappingExposure = 1.0;
const scene = new THREE.Scene();
scene.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture;
const camera = new THREE.PerspectiveCamera(32, 1, 0.1, 100); camera.position.set(0, 0.4, 5.2);

const draco = new DRACOLoader().setDecoderPath('https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/libs/draco/');
const gltf = await new GLTFLoader().setDRACOLoader(draco).loadAsync('/models/product.glb');
const product = gltf.scene; scene.add(product);
// contact shadow: a soft radial texture on a plane under the object (cheap and convincing)
const tex = new THREE.CanvasTexture(Object.assign(document.createElement('canvas'), { width: 256, height: 256 }));
const g = tex.image.getContext('2d'), grd = g.createRadialGradient(128,128,0,128,128,128);
grd.addColorStop(0,'rgba(0,0,0,.45)'); grd.addColorStop(1,'rgba(0,0,0,0)'); g.fillStyle = grd; g.fillRect(0,0,256,256);
const shadow = new THREE.Mesh(new THREE.PlaneGeometry(3, 3), new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false }));
shadow.rotation.x = -Math.PI / 2; shadow.position.y = -1.0; scene.add(shadow);

function resize() { const { clientWidth: w, clientHeight: h } = canvas; renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); }
new ResizeObserver(resize).observe(canvas); resize();
await renderer.compileAsync(scene, camera);           // avoid a hitch on first frame
const timer = new THREE.Timer(); timer.connect(document);
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
renderer.setAnimationLoop(() => { timer.update(); const t = timer.getElapsed();
  if (!reduce) product.rotation.y = Math.sin(t * 0.35) * 0.35;  // a slow, bounded turn with an end pose, not an endless spin
  renderer.render(scene, camera); });
</script>
```

## Camera
- 35-50mm feel: fov 28-40 for products (less distortion), 45-60 for environments.
- One move per beat (dolly in, orbit 15-30°, rise), expo.out arrivals, power2.inOut travels; camera paths via
  `CatmullRomCurve3` sampled by scroll progress; always `lookAt` a stable target (no wobble).
- Depth of field only when it guides attention (post `BokehPass` / drei `<DepthOfField>`), subtle.

## Light
- Environment light for reflections (RoomEnvironment, or an HDRI from Poly Haven via `HDRLoader`, mapping
  `EquirectangularReflectionMapping`), plus a key directional light for shape and shadows.
- 3-point: key (upper left, warm), fill (opposite, 30-50%), rim (behind, cool) - products read best with a rim.
- Shadows: one shadow-casting light, tight `shadow.camera` bounds, `shadow.mapSize` 1024-2048, `bias` -0.0005,
  `normalBias` 0.02; or fake contact shadows (above) for performance.

## Materials (with numbers)
| Look | MeshPhysicalMaterial |
|---|---|
| matte plastic | roughness 0.55-0.7, metalness 0 |
| satin paint | roughness 0.35, clearcoat 0.5, clearcoatRoughness 0.2 |
| brushed aluminium | metalness 1, roughness 0.3-0.4, anisotropy 0.6 |
| chrome | metalness 1, roughness 0.05 (needs a good environment) |
| glass | transmission 1, thickness 0.5-1.5, roughness 0.05, ior 1.5 (expensive) |
| ceramic | roughness 0.25, clearcoat 1, sheen 0 |
| fabric | sheen 1, sheenRoughness 0.8, roughness 0.9 |
Colour textures `colorSpace = SRGBColorSpace`; normal/roughness/metalness maps stay linear.

## Composition
The subject fills 40-70% of the frame height; leave a calm zone for HTML text; the 3D canvas sits behind or beside
the copy, never under body text that must be read. Match the scene's palette to the brand tokens (background =
`--ground`, accent as a material or light colour - once).

## 3D logo from the brand SVG
```js
import { SVGLoader } from 'three/addons/loaders/SVGLoader.js';
const data = await new SVGLoader().loadAsync('/brand/logo-mark.svg');
const group = new THREE.Group();
for (const path of data.paths) for (const shape of SVGLoader.createShapes(path)) {
  const geo = new THREE.ExtrudeGeometry(shape, { depth: 24, bevelEnabled: true, bevelThickness: 3, bevelSize: 2, bevelSegments: 6, curveSegments: 24 });
  group.add(new THREE.Mesh(geo, new THREE.MeshPhysicalMaterial({ color: path.color, roughness: 0.3, metalness: 0.1, clearcoat: 0.6 })));
}
group.scale.set(0.01, -0.01, 0.01);                       // SVG y-down -> three y-up
new THREE.Box3().setFromObject(group).getCenter(group.position).multiplyScalar(-1);
```
End pose = the exact front view of the mark (rotate-to-lockup with a long expo.out). A coin/medal variant: extrude
a disc + the mark slightly raised on both faces, chrome rim (mirror the back face so text reads from both sides).

## Interaction
- Drag to rotate with damping (OrbitControls `enableDamping`, limited polar/azimuth angles, no zoom on landing pages).
- Pointer parallax: lerp camera position toward pointer * 0.15; fine pointers only.
- Raycast only a list of pickables on `layers`, never `scene.children` recursively each move.
