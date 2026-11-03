# Blender MCP (live control)

`ahujasid/blender-mcp` (MIT) connects Claude to a running Blender through an add-on + MCP server
(`uvx blender-mcp`). Tools typically include `get_scene_info`, `get_object_info`, `execute_blender_code`,
`get_viewport_screenshot`, Poly Haven asset search/download, and (premium/optional) model generators.

## Setup (on the user's machine)
1. Install Blender 5.2 LTS, Python 3.10+, `uv`.
2. Install the add-on (`addon.py` from the repo) in Blender: Edit > Preferences > Add-ons > Install; enable
   "Interface: Blender MCP"; in the 3D View sidebar (N) > BlenderMCP > Connect.
3. Add the MCP server to Claude Code: `claude mcp add blender uvx blender-mcp` (or the client's JSON config with the
   full path to `uvx`). Restart the client.

## Working live
- Small steps; each `execute_blender_code` call is a fresh namespace - re-import modules every call; print only
  what you need (JSON).
- Look after each meaningful step: `get_viewport_screenshot` (or render a small preview) and judge it.
- Poly Haven integration downloads CC0 HDRIs/textures/models - fine to use, credit optional (CC0) but list them.
- Do NOT use AI model-generation integrations (Hyper3D/Rodin, text-to-3D) for client work: astudio policy is real,
  licensed or procedural assets only - tell the user if they ask.
- Save often (`bpy.ops.wm.save_as_mainfile`), keep the script of everything you did so the scene is reproducible
  headless.

## Headless instead
When there is no live session, the same scripts run with `python3 <root>/scripts/blender_run.py run scene.py`.
