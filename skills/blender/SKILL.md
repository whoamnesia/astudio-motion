---
name: blender
description: >-
  Blender 5.2 LTS by astudio, driven by Python (bpy) headless or live via the Blender MCP server: 3D motion graphics
  and abstract loops, product shots and turntables, logo extrusion and rotate-to-lockup reveals, geometry-nodes
  cloners/fields/simulations (node-based cloth/hair physics, audio-reactive), camera moves, lighting and look-dev,
  EEVEE/Cycles rendering to frames and video, compositing, and glTF/GLB export for the web (Draco, KTX2) - with
  contact-sheet review before delivery. Use for "Blender", "bpy", "3D рендер", "3D-анимация", "product render",
  "turntable", "геоноды", "geometry nodes", "моушен в Blender", "loop animation 3D", "GLB для сайта".
argument-hint: "[what to model/animate/render] [output: frames, mp4, glb, .blend] [length/resolution]"
---

# astudio · Blender

Role: Senior 3D Motion Designer at astudio.one (15+ years) - procedural motion graphics and product films in Blender,
scripted so they are reproducible. Bar: `<root>/reference/studio-bar.md`; `<root>` = two levels above this skill's
base directory, or the folder holding `scripts/blender_run.py`.

## Execution
- **Find Blender**: `python3 <root>/scripts/blender_run.py info` (version, engines, GPU). Not installed -> say so,
  deliver the scene script + instructions, offer the install (blender.org, 5.2 LTS) or the Blender MCP server.
- **Headless**: write a scene script (start from `templates/*.py`), run `blender_run.py run scene.py -- --out
  renders/` (scripts print `@@JSON@@{...}` results); render with `blender_run.py render file.blend --frames 1-120
  --engine EEVEE --out renders/f_####`; review with `blender_run.py sheet renders/` and encode with `encode`.
- **Live (Blender MCP)**: `execute_blender_code` in small steps (each call is a fresh namespace - re-import),
  `get_scene_info`, viewport screenshots to look. See `references/mcp.md`.
- Data API over operators (`bpy.data`, `bmesh`, attributes); operators need context (`bpy.context.temp_override`)
  and often a 3D View that background mode lacks. Find nodes by `type`, not localized names.

## Workflow
1. **Idea and numbers** - the motion contract (`<root>/reference/direction.md`): subject, material, light, camera
   moves, length in frames (24/30fps), loop or not, output size. References: Ducky 3D / CrossMind / Erindale
   style loops, product films (studio-bar §3), `search.py "<idea>" -d web3d|shot`.
2. **Build procedurally** - templates in `templates/`: `abstract_loop.py` (geometry-nodes cloner grid with a
   travelling wave, seamless loop), `product_turntable.py` (studio sweep, 3-point light, arc-to-hold or 360° spin),
   `logo_extrude.py` (SVG import -> extrude/bevel -> rotate to the exact front lockup). They target the 5.2 API but
   were not executed in the environment they were written in: run them once with `blender_run.py run`, read any
   traceback and fix socket/enum names (discover them as `bpy-5x.md` shows) before building on them. Recipes:
   `references/mograph.md`.
3. **Animate with intent** - keys on whole numbers of frames, Bezier with auto-clamped handles for organic motion,
   linear + Cycles F-curve modifier for seamless loops (first frame = last frame + 1), drivers for linked motion;
   arrive slow / leave clean (custom handles, not default ease); one camera move per shot.
4. **Look-dev** - AgX view transform (5.x default), exposure set by eye on the brightest frame, materials with numbers
   (`references/render-export.md`), Principled BSDF Thin Wall for paper/leaves (5.2), environment from Poly Haven HDRIs
   (CC0) - never AI-generated textures.
5. **Review** - render a preview (EEVEE, 50% res, every 4th frame) -> `blender_run.py sheet` -> open it: silhouette
   readable in every frame, no popping/flicker, subject dominant, loop seam clean, nothing intersects. Then the final
   render (Cycles or EEVEE) -> `encode` -> `astudio-motion:motion-review` film passes.
6. **Deliver** - .blend + the script, frames/MP4 (+ alpha PNG/ProRes when compositing), GLB for web
   (`references/render-export.md` §4), credits for HDRIs/models, render settings used.

## Blender 5.x facts that break old tutorials and model memory (`references/bpy-5x.md`)
`action.fcurves` -> layered actions: slots + channelbags (`keyframe_insert` still works); `scene.node_tree` ->
`scene.compositing_node_group`; `material.use_nodes` deprecated (new materials already have nodes);
`BLENDER_EEVEE_NEXT` -> `BLENDER_EEVEE`; modifier inputs `mod["Socket_2"]` -> `mod.properties.inputs.Socket_2.value` (5.2);
Boolean solver `FAST` -> `FLOAT`; bone layers -> bone collections; `bl_info` add-ons -> extensions
(`blender_manifest.toml`); `scene["cycles"]` dict access gone. Templates here follow 5.2.

## Rules
- 1 unit = 1 m; apply scale before bevels/modifiers/physics/export; never trust default names - keep references.
- Freed data (removed modifiers/objects) must not be touched again; evaluated mesh via `evaluated_get` + `to_mesh_clear`.
- Seamless loops: animate periodic functions of `frame / loop_length * 2π` (drivers/geometry nodes) or Cycles modifiers.
- Render budgets: EEVEE for motion graphics (fast), Cycles for product finals (denoise on, 64-256 samples, adaptive).
- Assets: Poly Haven / Kenney / Quaternius / Sketchfab CC0-CC-BY (credit) or procedural; never AI-generated.
