# Cavalry and Cinema 4D

## Cavalry (free since 2026; Pro features paid)
Procedural 2D: everything is a node (shapes, duplicators, behaviours, deformers, utilities) - strong for loops,
data visualisation, generative layouts and Lottie export.
- **Duplicator** (grid/circle/path/points distribution) + **Behaviours**: Stagger (offset animation by index),
  Oscillator (sine-based loops - set frequency to 1/loop length for seamless loops), Noise, Falloff, Value Array,
  Spreadsheet (CSV/Google Sheets data -> shapes for data viz).
- **JavaScript Utility / Javascript layer**: `ctx.index`, `ctx.frame`; return values to drive attributes; use for
  formulas the behaviours can't express.
- **Scripting API** (UI scripts in JS) to batch-create scenes from data.
- **Easing**: Graph Editor with bezier handles; Cavalry's ease presets ~ CSS curves (expo-out etc.) - state the
  cubic-bezier equivalent in the spec.
- **Export**: MP4/ProRes/PNG sequence, Lottie (check the supported feature list per version), SVG.
- Learn: Cavalry official "Getting Started" playlist (`search.py "cavalry" -d learn`).

## Cinema 4D 2026 + Redshift
- **MoGraph**: Cloner (Linear/Radial/Grid/Object/Honeycomb; 2026.1 Advanced Distribution), MoText, Fracture,
  Effectors (Plain, Random, Shader, Delay, Step, Formula, Python), **Fields** (Linear/Spherical/Random/Shader/Sound)
  to drive effector strength - the core of 3D motion graphics.
- Liquid Flow and simulation updates (2026); Pyro for smoke/fire; Rigid/Soft bodies via the unified simulation.
- **Python**: Script Manager scripts (`c4d.documents.GetActiveDocument()`), Python Generator objects and Python tags
  for procedural rigs; Python Effector/Field for formula-driven motion.
```python
import c4d
def main():
    doc = c4d.documents.GetActiveDocument()
    cl = c4d.BaseObject(c4d.Omgcloner); cl[c4d.ID_MG_MOTIONGENERATOR_MODE] = c4d.ID_MG_MOTIONGENERATOR_MODE_GRID
    cube = c4d.BaseObject(c4d.Ocube); cube[c4d.PRIM_CUBE_LEN] = c4d.Vector(20, 20, 60); cube.InsertUnder(cl)
    doc.InsertObject(cl); c4d.EventAdd()
if __name__ == "__main__": main()
```
- **Redshift look-dev**: Standard Material (roughness/metalness like Principled), Dome Light HDRI + area lights,
  ACES/OCIO colour management, denoise (OIDN/OptiX), motion blur on for fast mograph; render AOVs for compositing.
- **Loops**: time-based fields/effectors with periodic functions; check frame 0 vs N.
- Deliver: `.c4d` with Save Project with Assets, render settings preset, takes for variants.
- Learn: Maxon Training Team "Cinema 4D Fundamentals" and "What's New 2026.1" (`search.py "cinema 4d" -d learn`).

## Choosing between them
| Job | Pick |
|---|---|
| 2D procedural loops, data viz, Lottie | Cavalry |
| 3D mograph, product films with a TD-friendly pipeline | Cinema 4D + Redshift (or Blender - free, scriptable here) |
| character/compositing/brand films with designers in Adobe | After Effects |
| real-time broadcast graphics | Unreal Motion Design |
