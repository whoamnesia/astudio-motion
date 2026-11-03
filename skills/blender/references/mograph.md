# Motion-graphics recipes in Blender

## Abstract seamless loops (the Ducky 3D genre)
- Instanced primitives (cubes, rounded bars, rings) on a grid/circle; each instance's rotation/scale/offset is a
  periodic function of `time = frame / loop_len * 2π` plus a phase from its position (distance from centre, index) ->
  a wave travels through the field. Seamless by construction.
- In Geometry Nodes: Scene Time (Frame) -> Math (divide by loop_len, multiply 2π) -> add phase (Position length *
  k) -> Sine -> Rotate Instances / Set Position / Scale Instances.
- Materials: two-tone Principled (base colour from brand tokens, roughness 0.3-0.5), a gradient by object position
  (Attribute/Position -> ColorRamp), subtle subsurface for "soft" plastics; dark ground with a single soft area light
  or an HDRI; bloom via the compositor Glare node only if the brand asks for glow.
- Camera: orthographic (graphic look) or a 50-85mm perspective with a slow 5-10° orbit that also loops.
- Length: 4-8s at 30fps (120-240 frames); render frames 1..N where N = loop_len (frame N+1 equals frame 1).

## Product turntable / hero shot
- Studio: infinite curved floor (a plane with a bevelled back edge) or a shadow catcher; 3-point lighting with large
  area lights (key 45° upper left, fill opposite at 40%, rim behind); HDRI for reflections at low strength.
- Camera 50-85mm, slight high angle (10-15°), depth of field focused on the logo/hero detail at f/2.8-5.6 equivalent.
- Motion: 30-60° arc with an expo-out settle and a hold, or a full 360° loop (linear) for e-commerce spins; a
  "reveal" variant: light sweeps across (animated area light), then the camera settles.
- Materials with numbers (render-export.md §2); bevel all hard edges (Bevel modifier 1-2mm, 3 segments, harden normals).

## Logo extrude and rotate-to-lockup
- Import SVG (`bpy.ops.import_curve.svg` / File > Import > SVG), join curves, set `extrude` (depth) and `bevel_depth`,
  convert to mesh if modifiers follow; centre origin; scale to ~2m width.
- Animation: start rotated 1.5 turns about a tilted axis, settle to exactly 0 rotation on a long ease-out (Bezier with
  handles giving ~90% travel in the first third), hold 1-1.5s; light sweep on the settle.
- Materials: the brand colours in Principled; metal only if the brand is metal; no rainbow iridescence by default.

## Geometry-nodes cloner patterns
| Pattern | Nodes |
|---|---|
| grid wave | Mesh Grid -> Instance on Points -> Rotate Instances (angle = sin(time + dist*k)) |
| radial burst | Mesh Circle/Points -> Instance -> Scale Instances by noise(time) |
| text on curve / kinetic type | String to Curves -> Fill Curve -> Extrude Mesh; animate per-character offset with the index |
| growth | Curve Line -> Trim Curve (end factor animated) -> Curve to Mesh (profile circle) |
| scatter | Distribute Points on Faces (seed) -> Instance -> Realize (only if needed) |
| audio-reactive (5.2) | Sample Sound Frequencies (+ the Sound socket) -> drive scale/emission; add the sound to the VSE and set Playback Sync to "Sync to Audio" |
| node physics (5.2) | Cloth Dynamics / Hair Dynamics nodes (XPBD solver) with Collider + Gravity effectors, Tag & Filter |

## Simulations
Rigid body (cells, dominoes, drops), cloth (5.2 node-based cloth is fast for fabric reveals), fluids (Mantaflow;
heavy), particles via GN simulation zones (Simulation Input/Output) for procedural sims; bake before rendering; cache
to disk for long shots.

## Grease Pencil (2D in 3D)
Line Art modifier for outlines of 3D objects (technical/illustrative look), GP strokes for hand-drawn accents; 5.2
Delaunay fill for exact fills; "line boil" by swapping stroke variations every 2-3 frames.

## Timing in Blender
- 24 or 30 fps; keys on whole frames; Graph Editor handles: auto-clamped for no overshoot, custom handles for expo-like
  arrivals (drag the outgoing handle long, incoming short).
- Ease presets from `<root>/reference/easing-timing.md` translate roughly to Blender's "Easing" interpolation types
  (Expo Out ≈ expo-out; Back with amount 1.0-1.7 for small overshoot).
- Hold the final pose >= 1s; never let a "loop" drift (check frame 1 vs N+1 in the sheet).
