# Render, look-dev and export

## 1. Render settings (script)
```python
s = bpy.context.scene
s.render.engine = 'BLENDER_EEVEE'          # or 'CYCLES'
s.render.resolution_x, s.render.resolution_y, s.render.resolution_percentage = 1920, 1080, 100
s.render.fps = 30; s.frame_start, s.frame_end = 1, 150
s.view_settings.view_transform = 'AgX'; s.view_settings.look = 'AgX - Base Contrast'   # 'Standard' to match brand hex exactly
s.render.film_transparent = False          # True for alpha PNG/ProRes deliverables
s.render.image_settings.file_format = 'PNG'; s.render.image_settings.color_mode = 'RGBA'
s.render.filepath = '//renders/f_####'
# Cycles finals
s.cycles.samples = 128; s.cycles.use_denoising = True; s.cycles.use_adaptive_sampling = True
# EEVEE (5.x): s.eevee.taa_render_samples = 64; raytracing toggles under s.eevee.use_raytracing
# motion blur for fast motion graphics: s.render.use_motion_blur = True; s.render.motion_blur_shutter = 0.5
```
Device: `bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'OPTIX'|'CUDA'|'HIP'|'METAL'`,
`get_devices()`, enable devices, `s.cycles.device = 'GPU'`.
Video: render PNG frames, then `blender_run.py encode` (ffmpeg) - more robust than rendering straight to MP4.

## 2. Materials with numbers (Principled BSDF)
| Look | Settings |
|---|---|
| matte plastic | Roughness 0.6, Specular IOR Level 0.5 |
| glossy plastic | Roughness 0.2, Coat Weight 0.3 |
| brushed metal | Metallic 1, Roughness 0.35, Anisotropic 0.6 |
| chrome | Metallic 1, Roughness 0.04 |
| glass | Transmission Weight 1, Roughness 0.02, IOR 1.45-1.5 |
| ceramic | Roughness 0.25, Coat Weight 1, Coat Roughness 0.05 |
| paper / leaves (5.2) | Thin Wall on, Transmission 0.3-0.6, Roughness 0.8 |
| soft rubber | Roughness 0.85, Subsurface Weight 0.1 |
Colours from brand tokens converted to linear (Blender colour pickers are scene-linear): `lin = (c/255)**2.2` approx.

## 3. Light and world
HDRI (Poly Haven, CC0) at strength 0.3-1 for reflections + area lights for shape; world colour = brand ground for
graphic looks. Compositor (5.x: `scene.compositing_node_group`): Glare (bloom) subtle, Lens Distortion 0.01-0.02,
film grain via a noise texture mixed at 2-4%, vignette via an ellipse mask.

## 4. Export for the web (glTF/GLB)
```python
bpy.ops.export_scene.gltf(filepath='//web/product.glb', export_format='GLB', use_selection=True,
    export_apply=True, export_yup=True, export_draco_mesh_compression_enable=True,
    export_draco_mesh_compression_level=6, export_image_format='WEBP', export_animations=True,
    export_force_sampling=True)
```
Then compress textures to KTX2 and/or meshopt: `npx @gltf-transform/cli optimize product.glb product.min.glb
--compress meshopt --texture-compress ktx2`. Budgets: hero model < 2-5MB, textures <= 2048, < 100-150k tris.
Bake procedural materials to textures before export (glTF can't carry node graphs); one action per clip, sampled.

## 5. Delivery checklist
Frames/MP4 (+ alpha variants if compositing), the .blend saved with relative paths and packed or listed textures,
the generating script, render settings summary, credits (HDRIs, models), contact sheet of the final, notes on what
could not be checked (e.g. rendered only previews, GPU not available).
