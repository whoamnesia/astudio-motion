# React Three Fiber, drei and Spline

## R3F skeleton
```tsx
import { Canvas, useFrame } from "@react-three/fiber";
import { Environment, ContactShadows, useGLTF, PerformanceMonitor, AdaptiveDpr } from "@react-three/drei";
import { useRef } from "react"; import * as THREE from "three";

function Product() {
  const ref = useRef<THREE.Group>(null!); const { scene } = useGLTF("/models/product.glb");
  useFrame((state, delta) => { ref.current.rotation.y = THREE.MathUtils.damp(ref.current.rotation.y, state.pointer.x * 0.4, 4, delta); });
  return <primitive ref={ref} object={scene} />;
}
export default function Hero() {
  return (
    <Canvas dpr={[1, 1.75]} camera={{ fov: 32, position: [0, 0.4, 5.2] }} gl={{ antialias: true }} frameloop="always">
      <PerformanceMonitor />
      <AdaptiveDpr pixelated />
      <Environment preset="studio" />
      <Product />
      <ContactShadows position={[0, -1, 0]} opacity={0.45} blur={2.4} scale={6} far={2} />
    </Canvas>
  );
}
useGLTF.preload("/models/product.glb");
```
- Scroll: drei `<ScrollControls pages={3}>` + `useScroll()` offsets, or GSAP ScrollTrigger writing to a ref that
  `useFrame` reads (keep scroll logic outside React state).
- `frameloop="demand"` + `invalidate()` for static scenes; `<Bvh>` for raycast-heavy meshes; `<Instances>` for repeats;
  `<Text>` (troika, MSDF) for 3D text; `<Html>` for DOM labels; `<Float>` only for meaningful hover/idle, not filler.
- Physics: `@react-three/rapier` (`<Physics><RigidBody>`), sleep bodies, cap counts.
- Post: `@react-three/postprocessing` (`<EffectComposer><Bloom luminanceThreshold={0.9} mipmapBlur/><Vignette/></EffectComposer>`) - subtle.
- `gltfjsx` turns a GLB into a typed component (`npx gltfjsx model.glb --transform` also compresses).

## Asset pipeline
`npx @gltf-transform/cli optimize in.glb out.glb --compress draco|meshopt --texture-compress ktx2 --texture-size 2048`
(inspect first: `gltf-transform inspect in.glb`). Keep < 2-5MB for hero models; KTX2 textures stay compressed in VRAM;
wire `KTX2Loader` (`setTranscoderPath` + `detectSupport(renderer)`), `DRACOLoader`, `MeshoptDecoder` on the loader.

## Spline
- Designer-made scenes with states/events; export as a public URL or self-hosted `.splinecode`.
- React: `import Spline from '@splinetool/react-spline'` -> `<Spline scene="https://prod.spline.design/.../scene.splinecode" onLoad={app => ...} />`;
  vanilla: `@splinetool/runtime` (`new Application(canvas).load(url)`).
- Control: `app.findObjectByName("Cube")`, `app.emitEvent("mouseHover", "Cube")`, variables `app.setVariable("count", 3)`;
  listen with `onSplineMouseDown` etc.
- Next.js: dynamic import with `ssr: false`; show a poster until `onLoad`.
- Check scene weight (Spline scenes can be several MB) and test on mobile; provide the poster fallback.
