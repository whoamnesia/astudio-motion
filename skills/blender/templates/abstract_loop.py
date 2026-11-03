"""astudio-motion Blender template - seamless abstract motion-graphics loop (Geometry Nodes cloner + travelling wave).

Run:  python3 <root>/scripts/blender_run.py run abstract_loop.py -- --out renders/loop_#### --frames 120 --res 1080x1080
      [--ground "#14161C" --a "#ECEDEF" --b "#E0592A"] [--grid 14] [--render] [--preview] [--save loop.blend]
Every instance rotates by sin(2π·frame/frames + distance·k): frame N+1 equals frame 1, so frames 1..N loop seamlessly.
Blender 5.2 LTS API (layered actions not needed - motion comes from Scene Time inside the node tree).
"""
import bpy, json, math, sys


def args():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    o = {"out": "//renders/loop_####", "frames": 120, "res": "1080x1080", "ground": "#14161C", "a": "#ECEDEF", "b": "#E0592A",
         "grid": 14, "render": False, "preview": False, "save": ""}
    i = 0
    while i < len(a):
        k = a[i].lstrip("-")
        if i + 1 < len(a) and not a[i + 1].startswith("--"):
            o[k] = a[i + 1]; i += 2
        else:
            o[k] = True; i += 1
    o["frames"], o["grid"] = int(o["frames"]), int(o["grid"])
    return o


def lin(hexstr):
    h = hexstr.lstrip("#"); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c] + [1.0]


def sock(node, name, out=False):
    coll = node.outputs if out else node.inputs
    for s in coll:
        if s.name == name or s.identifier == name:
            return s
    raise KeyError(f"{node.bl_idname} has no {'output' if out else 'input'} '{name}': {[s.name for s in coll]}")


def material(name, rgba, rough):
    m = bpy.data.materials.new(name)
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Roughness"].default_value = rough
    return m


def build(o):
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    scn = bpy.context.scene
    w, h = (int(x) for x in o["res"].lower().split("x"))
    scn.render.resolution_x, scn.render.resolution_y = w, h
    scn.render.fps = 30; scn.frame_start, scn.frame_end = 1, o["frames"]
    scn.render.engine = "BLENDER_EEVEE"
    try:
        scn.view_settings.view_transform = "AgX"
    except TypeError:
        pass
    scn.world = scn.world or bpy.data.worlds.new("World")
    bg = scn.world.node_tree.nodes.get("Background") or next(n for n in scn.world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = lin(o["ground"]); bg.inputs["Strength"].default_value = 1.0

    mat_a, mat_b = material("A", lin(o["a"]), 0.45), material("B", lin(o["b"]), 0.35)

    # carrier object for the node tree
    mesh = bpy.data.meshes.new("Field"); field = bpy.data.objects.new("Field", mesh)
    scn.collection.objects.link(field)
    ng = bpy.data.node_groups.new("WaveCloner", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N, L = ng.nodes, ng.links
    out = N.new("NodeGroupOutput"); N.new("NodeGroupInput")
    grid = N.new("GeometryNodeMeshGrid")
    sock(grid, "Size X").default_value = 6.0; sock(grid, "Size Y").default_value = 6.0
    sock(grid, "Vertices X").default_value = o["grid"]; sock(grid, "Vertices Y").default_value = o["grid"]
    bar = N.new("GeometryNodeMeshCube"); sock(bar, "Size").default_value = (0.32, 0.32, 0.9)
    inst = N.new("GeometryNodeInstanceOnPoints")
    L.new(sock(grid, "Mesh", True), sock(inst, "Points")); L.new(sock(bar, "Mesh", True), sock(inst, "Instance"))

    # angle = sin(2π * frame / frames + |position| * 0.9) * 0.9
    t = N.new("GeometryNodeInputSceneTime")
    div = N.new("ShaderNodeMath"); div.operation = "DIVIDE"; div.inputs[1].default_value = float(o["frames"])
    L.new(sock(t, "Frame", True), div.inputs[0])
    tau = N.new("ShaderNodeMath"); tau.operation = "MULTIPLY"; tau.inputs[1].default_value = 2 * math.pi
    L.new(div.outputs[0], tau.inputs[0])
    pos = N.new("GeometryNodeInputPosition"); ln = N.new("ShaderNodeVectorMath"); ln.operation = "LENGTH"
    L.new(sock(pos, "Position", True), ln.inputs[0])
    k = N.new("ShaderNodeMath"); k.operation = "MULTIPLY"; k.inputs[1].default_value = 0.9
    L.new(sock(ln, "Value", True), k.inputs[0])
    add = N.new("ShaderNodeMath"); add.operation = "ADD"; L.new(tau.outputs[0], add.inputs[0]); L.new(k.outputs[0], add.inputs[1])
    sin = N.new("ShaderNodeMath"); sin.operation = "SINE"; L.new(add.outputs[0], sin.inputs[0])
    amp = N.new("ShaderNodeMath"); amp.operation = "MULTIPLY"; amp.inputs[1].default_value = 0.9; L.new(sin.outputs[0], amp.inputs[0])
    xyz = N.new("ShaderNodeCombineXYZ"); L.new(amp.outputs[0], xyz.inputs["X"])
    e2r = N.new("FunctionNodeEulerToRotation"); L.new(xyz.outputs[0], e2r.inputs[0])
    rot = N.new("GeometryNodeRotateInstances")
    L.new(sock(inst, "Instances", True), sock(rot, "Instances")); L.new(e2r.outputs[0], sock(rot, "Rotation"))
    # accent: every 7th instance gets material B (by index)
    idx = N.new("GeometryNodeInputIndex"); mod = N.new("ShaderNodeMath"); mod.operation = "MODULO"; mod.inputs[1].default_value = 7.0
    L.new(idx.outputs[0], mod.inputs[0])
    is0 = N.new("FunctionNodeCompare"); is0.data_type = "FLOAT"; is0.operation = "EQUAL"
    L.new(mod.outputs[0], is0.inputs[0]); is0.inputs[1].default_value = 0.0
    real = N.new("GeometryNodeRealizeInstances")
    sm_a = N.new("GeometryNodeSetMaterial"); sm_a.inputs["Material"].default_value = mat_a
    L.new(real.outputs[0], sm_a.inputs["Geometry"])
    sm_b = N.new("GeometryNodeSetMaterial"); sm_b.inputs["Material"].default_value = mat_b
    L.new(sm_a.outputs[0], sm_b.inputs["Geometry"])
    # selection must be evaluated on instances before realize -> store as attribute on instances
    store = N.new("GeometryNodeStoreNamedAttribute"); store.data_type = "BOOLEAN"; store.domain = "INSTANCE"
    sock(store, "Name").default_value = "accent"
    L.new(sock(rot, "Instances", True), sock(store, "Geometry")); L.new(is0.outputs[0], sock(store, "Value"))
    L.new(sock(store, "Geometry", True), real.inputs[0])
    nattr = N.new("GeometryNodeInputNamedAttribute"); nattr.data_type = "BOOLEAN"; sock(nattr, "Name").default_value = "accent"
    L.new(sock(nattr, "Attribute", True), sm_b.inputs["Selection"])
    L.new(sm_b.outputs[0], out.inputs[0])
    m = field.modifiers.new("WaveCloner", "NODES"); m.node_group = ng

    # camera: orthographic three-quarter view (graphic look); a light for shape
    cam_data = bpy.data.cameras.new("Cam"); cam_data.type = "ORTHO"; cam_data.ortho_scale = 9.5
    cam = bpy.data.objects.new("Cam", cam_data); scn.collection.objects.link(cam); scn.camera = cam
    cam.location = (9.0, -9.0, 8.0); cam.rotation_euler = (math.radians(54.7), 0, math.radians(45))
    sun_d = bpy.data.lights.new("Key", "SUN"); sun_d.energy = 3.0; sun_d.angle = math.radians(8)
    sun = bpy.data.objects.new("Key", sun_d); scn.collection.objects.link(sun); sun.rotation_euler = (math.radians(50), math.radians(-20), math.radians(30))
    return scn


def main():
    o = args(); scn = build(o)
    scn.render.filepath = o["out"]
    if o["preview"]:
        scn.render.resolution_percentage = 50; scn.frame_step = 4
    if o["save"]:
        bpy.ops.wm.save_as_mainfile(filepath=bpy.path.abspath(o["save"]))
    if o["render"]:
        bpy.ops.render.render(animation=True)
    print("@@JSON@@" + json.dumps({"scene": "abstract_loop", "frames": [scn.frame_start, scn.frame_end], "fps": scn.render.fps,
          "resolution": [scn.render.resolution_x, scn.render.resolution_y], "rendered": bool(o["render"]), "out": scn.render.filepath}))


main()
