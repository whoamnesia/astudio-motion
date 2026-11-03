# bpy for Blender 5.x (5.2 LTS) - rules and API changes

Distilled from EL4CTEO/blender-skills (MIT) and the Blender 5.2 release notes.

## API changes (old code breaks)
| Old | 5.x |
|---|---|
| `action.fcurves` | layered actions: `action.layers[0].strips[0].channelbag(slot).fcurves`; helper `bpy_extras.anim_utils.action_ensure_channelbag_for_slot(action, slot)`; `obj.keyframe_insert(...)` still creates everything |
| `scene.node_tree` (compositor) | `scene.compositing_node_group` (a node group asset) |
| `material.use_nodes = True` | deprecated - new materials already have a node tree |
| `"BLENDER_EEVEE_NEXT"` | `"BLENDER_EEVEE"` |
| `mod["Socket_2"] = v` (GN modifier input) | `mod.properties.inputs.Socket_2.value = v` (5.2); read the identifier from the node group interface |
| Boolean `solver="FAST"` | `"FLOAT"` (and `"EXACT"`, `"MANIFOLD"`) |
| armature bone layers | bone collections |
| `bl_info` add-ons | extensions with `blender_manifest.toml` |
| `scene["cycles"]["samples"]` | `scene.cycles.samples` (props no longer dict-accessible) |
| default view transform Filmic | AgX (since 4.0); "Standard" for graphics that must match hex colours exactly |

## Layered action example
```python
import bpy
from bpy_extras import anim_utils
ob = bpy.data.objects["Cube"]
ob.animation_data_create()
act = bpy.data.actions.new("CubeSpin"); ob.animation_data.action = act
slot = act.slots.new(id_type='OBJECT', name=ob.name); ob.animation_data.action_slot = slot
cb = anim_utils.action_ensure_channelbag_for_slot(act, slot)
fc = cb.fcurves.ensure("rotation_euler", index=2)
fc.keyframe_points.insert(1, 0.0); fc.keyframe_points.insert(121, 6.283185)
for k in fc.keyframe_points: k.interpolation = 'LINEAR'
fc.modifiers.new('CYCLES')     # seamless loop
```
Simplest path that also works: `ob.rotation_euler.z = 0; ob.keyframe_insert("rotation_euler", index=2, frame=1)`.

## Rules for scripts
- **Data API over operators**: `bpy.data.meshes.new` + `bmesh`/`from_pydata`, `bpy.data.objects.new`, link to a
  collection. Operators need context: `with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):`
  and check `{'FINISHED'}`.
- **Nodes by type**: `next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')`; sockets by identifier or
  English name.
- **Enums**: discover valid values `[i.identifier for i in T.bl_rna.properties[p].enum_items]`; dynamic enums
  (render.engine, view_transform) - assign in try/except.
- **Evaluated data**: `ob.evaluated_get(depsgraph).to_mesh()` then `to_mesh_clear()`; `view_layer.update()` before
  reading `matrix_world`.
- **Freed data**: collect names first; never touch a Python reference to a removed modifier/object.
- **Names**: never rely on "Cube.001"; keep references, rename explicitly.
- **Scale/units**: 1 unit = 1 m; `transform_apply(scale=True)` before bevels/physics/export.
- **Paths**: `bpy.path.abspath("//tex/a.png")` is relative to the .blend; save with `bpy.ops.wm.save_as_mainfile(filepath=...)`.
- **Reproducibility**: seed every random (`random.seed(7)`; GN Random Value seed); scripts take args after `--`
  (`sys.argv[sys.argv.index('--') + 1:]`).
- **Report**: print `@@JSON@@` + `json.dumps({...})` with what was created (objects, frame range, output paths).

## Geometry Nodes from Python (5.x)
```python
ng = bpy.data.node_groups.new("Cloner", 'GeometryNodeTree')
ng.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
ng.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
n = ng.nodes; l = ng.links
gin, gout = n.new('NodeGroupInput'), n.new('NodeGroupOutput')
grid = n.new('GeometryNodeMeshGrid'); inst = n.new('GeometryNodeInstanceOnPoints'); cube = n.new('GeometryNodeMeshCube')
l.new(grid.outputs['Mesh'], inst.inputs['Points']); l.new(cube.outputs['Mesh'], inst.inputs['Instance'])
l.new(inst.outputs['Instances'], gout.inputs[0])
mod = ob.modifiers.new("Cloner", 'NODES'); mod.node_group = ng
```
Node type ids: `GeometryNodeMeshGrid`, `GeometryNodeInstanceOnPoints`, `GeometryNodeRotateInstances`,
`GeometryNodeScaleInstances`, `GeometryNodeSetPosition`, `GeometryNodeInputPosition`, `ShaderNodeMath`,
`ShaderNodeVectorMath`, `ShaderNodeCombineXYZ`, `ShaderNodeSeparateXYZ`, `GeometryNodeInputSceneTime`,
`GeometryNodeRealizeInstances`, `GeometryNodeSetMaterial`, `ShaderNodeTexNoise`, `FunctionNodeRandomValue`,
`GeometryNodeDistributePointsOnFaces`. 5.2 adds node-based physics (XPBD solver, Cloth/Hair Dynamics, effectors),
lists, string fields, Mesh Bevel, Sample Sound Frequencies (audio-reactive).

## Verify before saying done
Scene report (objects, materials, frame range, fps, resolution, engine), a rendered preview sheet you opened, the
script exit code 0, file paths of outputs.
