"""astudio-motion Blender template - product hero shot / turntable in a studio sweep with 3-point light.

Run:  python3 <root>/scripts/blender_run.py run product_turntable.py -- [--model product.glb] --frames 150 --degrees 40
      [--res 1920x1080] [--engine CYCLES|EEVEE] [--samples 128] [--ground "#EDEBE6"] [--out renders/shot_####] [--render] [--save shot.blend]
--degrees 360 = seamless e-commerce spin (linear); otherwise an arc that arrives on an expo-like ease and holds 1s.
Without --model a bevelled placeholder box stands in (replace it with the client's GLB).
"""
import bpy, json, math, sys


def args():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    o = {"model": "", "frames": 150, "degrees": 40.0, "res": "1920x1080", "engine": "EEVEE", "samples": 128,
         "ground": "#EDEBE6", "out": "//renders/shot_####", "render": False, "save": ""}
    i = 0
    while i < len(a):
        k = a[i].lstrip("-")
        if i + 1 < len(a) and not a[i + 1].startswith("--"):
            o[k] = a[i + 1]; i += 2
        else:
            o[k] = True; i += 1
    o["frames"], o["degrees"], o["samples"] = int(o["frames"]), float(o["degrees"]), int(o["samples"])
    return o


def lin(hexstr):
    h = hexstr.lstrip("#"); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c] + [1.0]


def area(name, loc, rot, size, energy, color=(1, 1, 1)):
    d = bpy.data.lights.new(name, "AREA"); d.energy = energy; d.size = size; d.color = color; d.shape = "DISK"
    ob = bpy.data.objects.new(name, d); bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; ob.rotation_euler = [math.radians(v) for v in rot]
    return ob


def build(o):
    scn = bpy.context.scene
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    w, h = (int(x) for x in o["res"].lower().split("x"))
    scn.render.resolution_x, scn.render.resolution_y, scn.render.fps = w, h, 30
    scn.frame_start, scn.frame_end = 1, o["frames"]
    scn.render.engine = "CYCLES" if o["engine"].upper() == "CYCLES" else "BLENDER_EEVEE"
    if scn.render.engine == "CYCLES":
        scn.cycles.samples = o["samples"]; scn.cycles.use_denoising = True
    try:
        scn.view_settings.view_transform = "AgX"
    except TypeError:
        pass

    # studio sweep: a plane bent up at the back (bevelled edge) in the ground colour
    bpy.ops.mesh.primitive_plane_add(size=1)
    floor = bpy.context.active_object; floor.name = "Sweep"
    floor.scale = (14, 14, 1)
    with bpy.context.temp_override(object=floor, active_object=floor, selected_objects=[floor], selected_editable_objects=[floor]):
        bpy.ops.object.transform_apply(scale=True)
    back = floor.data
    import bmesh
    bm = bmesh.new(); bm.from_mesh(back)
    bm.edges.ensure_lookup_table()
    far = max(bm.edges, key=lambda e: sum(v.co.y for v in e.verts))
    ext = bmesh.ops.extrude_edge_only(bm, edges=[far])
    for v in [g for g in ext["geom"] if isinstance(g, bmesh.types.BMVert)]:
        v.co.z += 8.0
    bm.to_mesh(back); bm.free()
    bev = floor.modifiers.new("Curve", "BEVEL"); bev.affect = "EDGES"; bev.width = 2.5; bev.segments = 24
    bev.limit_method = "ANGLE"
    floor.location = (0, 0, -1.0)
    fm = bpy.data.materials.new("Sweep"); fb = next(n for n in fm.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    fb.inputs["Base Color"].default_value = lin(o["ground"]); fb.inputs["Roughness"].default_value = 0.9
    floor.data.materials.append(fm)

    # product: the client's GLB or a placeholder
    pivot = bpy.data.objects.new("Pivot", None); scn.collection.objects.link(pivot)
    if o["model"]:
        bpy.ops.import_scene.gltf(filepath=bpy.path.abspath(o["model"]))
        for ob in bpy.context.selected_objects:
            if ob.parent is None:
                ob.parent = pivot
    else:
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        box = bpy.context.active_object; box.name = "Product"; box.scale = (1.0, 0.6, 1.6)
        with bpy.context.temp_override(object=box, active_object=box, selected_objects=[box], selected_editable_objects=[box]):
            bpy.ops.object.transform_apply(scale=True)
        b = box.modifiers.new("Bevel", "BEVEL"); b.width = 0.06; b.segments = 6
        pm = bpy.data.materials.new("Product"); pb = next(n for n in pm.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        pb.inputs["Base Color"].default_value = lin("#E0592A"); pb.inputs["Roughness"].default_value = 0.28
        try:
            pb.inputs["Coat Weight"].default_value = 0.4
        except KeyError:
            pass
        box.data.materials.append(pm); box.parent = pivot; box.location.z = -0.2

    # 3-point light: key upper-left warm, fill opposite, rim behind cool
    area("Key", (-4.5, -4.0, 5.0), (55, 0, -45), 4.0, 900, (1.0, 0.95, 0.88))
    area("Fill", (5.0, -3.5, 2.5), (70, 0, 50), 6.0, 300)
    area("Rim", (0.5, 5.0, 4.0), (-60, 0, 180), 3.0, 700, (0.88, 0.94, 1.0))

    cam_d = bpy.data.cameras.new("Cam"); cam_d.lens = 70
    cam = bpy.data.objects.new("Cam", cam_d); scn.collection.objects.link(cam); scn.camera = cam
    cam.location = (0, -8.5, 1.6); cam.rotation_euler = (math.radians(84), 0, 0)
    cam_d.dof.use_dof = True; cam_d.dof.focus_object = pivot; cam_d.dof.aperture_fstop = 4.0

    # motion: the pivot turns; arc = ease into a hold, 360 = linear loop
    pivot.rotation_euler.z = math.radians(-o["degrees"] / 2 if o["degrees"] < 360 else 0)
    pivot.keyframe_insert("rotation_euler", index=2, frame=1)
    end = o["frames"] + 1 if o["degrees"] >= 360 else max(2, o["frames"] - 30)
    pivot.rotation_euler.z = math.radians(o["degrees"] / 2 if o["degrees"] < 360 else 360)
    pivot.keyframe_insert("rotation_euler", index=2, frame=end)
    ad = pivot.animation_data
    for fc in _fcurves(ad):
        for kp in fc.keyframe_points:
            if o["degrees"] >= 360:
                kp.interpolation = "LINEAR"
            else:
                kp.interpolation = "EXPO"; kp.easing = "EASE_OUT"
    return scn


def _fcurves(ad):
    """F-curves of an object's action in Blender 5.x (layered actions) with a fallback for older versions."""
    act = ad.action
    try:
        from bpy_extras import anim_utils
        cb = anim_utils.action_ensure_channelbag_for_slot(act, ad.action_slot)
        return list(cb.fcurves)
    except Exception:
        return list(getattr(act, "fcurves", []))


def main():
    o = args(); scn = build(o)
    scn.render.filepath = o["out"]
    if o["save"]:
        bpy.ops.wm.save_as_mainfile(filepath=bpy.path.abspath(o["save"]))
    if o["render"]:
        bpy.ops.render.render(animation=True)
    print("@@JSON@@" + json.dumps({"scene": "product_turntable", "engine": scn.render.engine, "frames": [scn.frame_start, scn.frame_end],
          "degrees": o["degrees"], "model": o["model"] or "placeholder", "rendered": bool(o["render"])}))


main()
