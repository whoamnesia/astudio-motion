"""astudio-motion Blender template - 3D logo from the brand SVG with a rotate-to-lockup reveal.

Run:  python3 <root>/scripts/blender_run.py run logo_extrude.py -- --svg brand/logo-mark.svg [--depth 0.12 --bevel 0.012]
      [--color "#E0592A" --ground "#14161C"] [--frames 96] [--res 1920x1080] [--out renders/logo_####] [--render] [--save logo.blend]
The mark starts 1.5 turns away about a tilted axis and settles on an expo ease-out to EXACTLY its front view
(rotation 0), then holds ~1s - the last frames must match the flat logo.
"""
import bpy, json, math, sys


def args():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    o = {"svg": "", "depth": 0.12, "bevel": 0.012, "color": "#E0592A", "ground": "#14161C", "frames": 96, "res": "1920x1080",
         "out": "//renders/logo_####", "render": False, "save": ""}
    i = 0
    while i < len(a):
        k = a[i].lstrip("-")
        if i + 1 < len(a) and not a[i + 1].startswith("--"):
            o[k] = a[i + 1]; i += 2
        else:
            o[k] = True; i += 1
    for k in ("depth", "bevel"):
        o[k] = float(o[k])
    o["frames"] = int(o["frames"])
    if not o["svg"]:
        sys.exit("--svg path/to/logo.svg is required")
    return o


def lin(hexstr):
    h = hexstr.lstrip("#"); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c] + [1.0]


def main():
    o = args(); scn = bpy.context.scene
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    w, h = (int(x) for x in o["res"].lower().split("x"))
    scn.render.resolution_x, scn.render.resolution_y, scn.render.fps = w, h, 30
    scn.frame_start, scn.frame_end = 1, o["frames"]; scn.render.engine = "BLENDER_EEVEE"
    try:
        scn.view_settings.view_transform = "Standard"   # brand colours must match their hex values
    except TypeError:
        pass
    scn.world = scn.world or bpy.data.worlds.new("World")
    bg = next(n for n in scn.world.node_tree.nodes if n.type == "BACKGROUND"); bg.inputs["Color"].default_value = lin(o["ground"])

    before = set(bpy.data.objects)
    bpy.ops.import_curve.svg(filepath=bpy.path.abspath(o["svg"]))
    curves = [ob for ob in bpy.data.objects if ob not in before and ob.type == "CURVE"]
    if not curves:
        sys.exit("no curves imported from the SVG")
    mat = bpy.data.materials.new("Logo"); bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = lin(o["color"]); bsdf.inputs["Roughness"].default_value = 0.35
    for c in curves:
        c.data.extrude = o["depth"] / 2 / max(c.scale)   # SVG import scales tiny; compensated below by the root scale
        c.data.bevel_depth = o["bevel"] / max(c.scale); c.data.bevel_resolution = 4
        c.data.materials.clear(); c.data.materials.append(mat)
    root = bpy.data.objects.new("Logo", None); scn.collection.objects.link(root)
    for c in curves:
        c.parent = root
    # fit: centre the logo and scale it to ~3 m wide, standing up (SVG lies in XY)
    xs = [v[0] for c in curves for v in (c.matrix_world @ __import__("mathutils").Vector(b) for b in c.bound_box)]
    ys = [v[1] for c in curves for v in (c.matrix_world @ __import__("mathutils").Vector(b) for b in c.bound_box)]
    cx, cy, width = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, max(xs) - min(xs)
    for c in curves:
        c.location.x -= cx; c.location.y -= cy
    s = 3.0 / max(width, 1e-6); root.scale = (s, s, s); root.rotation_euler = (math.radians(90), 0, 0)

    cam_d = bpy.data.cameras.new("Cam"); cam_d.lens = 85
    cam = bpy.data.objects.new("Cam", cam_d); scn.collection.objects.link(cam); scn.camera = cam
    cam.location = (0, -12.0, 0); cam.rotation_euler = (math.radians(90), 0, 0)
    for name, loc, energy in (("Key", (-4, -6, 4), 1200), ("Rim", (3, 4, 3), 900)):
        d = bpy.data.lights.new(name, "AREA"); d.size = 5; d.energy = energy
        L = bpy.data.objects.new(name, d); scn.collection.objects.link(L); L.location = loc
        L.rotation_euler = (math.radians(60 if name == "Key" else -60), 0, math.radians(-35 if name == "Key" else 160))

    # rotate-to-lockup: a spinner parent turns 1.5 turns about a tilted axis and settles at exactly 0
    spin = bpy.data.objects.new("Spin", None); scn.collection.objects.link(spin); root.parent = spin
    settle = max(2, int(o["frames"] * 0.7))
    spin.rotation_mode = "XYZ"
    spin.rotation_euler = (math.radians(25), 0, math.radians(-540)); spin.keyframe_insert("rotation_euler", frame=1)
    spin.rotation_euler = (0, 0, 0); spin.keyframe_insert("rotation_euler", frame=settle)
    act = spin.animation_data.action
    try:
        from bpy_extras import anim_utils
        fcs = anim_utils.action_ensure_channelbag_for_slot(act, spin.animation_data.action_slot).fcurves
    except Exception:
        fcs = getattr(act, "fcurves", [])
    for fc in fcs:
        for kp in fc.keyframe_points:
            kp.interpolation = "EXPO"; kp.easing = "EASE_OUT"

    scn.render.filepath = o["out"]
    if o["save"]:
        bpy.ops.wm.save_as_mainfile(filepath=bpy.path.abspath(o["save"]))
    if o["render"]:
        bpy.ops.render.render(animation=True)
    print("@@JSON@@" + json.dumps({"scene": "logo_extrude", "curves": len(curves), "frames": [1, o["frames"]], "settle_frame": settle,
          "rendered": bool(o["render"]), "note": "verify the last frame against the flat SVG"}))


main()
