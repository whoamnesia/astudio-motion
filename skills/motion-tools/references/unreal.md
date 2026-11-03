# Unreal Engine 5.7 - Motion Design (real-time broadcast and event graphics)

## The toolset
- **Motion Design mode** (toolbar button or the Modes dropdown, Shift+9): a 2D-friendly viewport, the Motion Design
  Outliner, actor types for graphics.
- **Shapes and Text 3D** actors (parametric, extruded, bevelled), **Cloners** (grid/circle/line/mesh/spline layouts)
  and **Effectors** (plane/sphere/radial with falloffs) for MoGraph-style motion, **Modifiers** stack.
- **Material Designer**: layer-based materials (like a photo editor's layers): fills, gradients, textures, masks,
  UV transforms that can be animated.
- **Sequencer**: keyframe tracks with Auto-key; **marks** split in/loop/out animations so a graphic can play on,
  hold, and play off on command; curve editor for easing.
- **Remote Control**: expose properties (text, colours, switches) to a web/remote UI; **Behaviors** add logic (switch
  styles, toggle elements) - the graphic becomes a template operators drive live.
- **Rundown**: playlists of graphics pages for live shows; **Transition Logic** for in/out between pages; Media Plate
  for video.

## Typical build: lower third
1. Null actor as the root; a background shape (rounded rect) + Text 3D lines (name, title) + logo plane.
2. Material Designer: brand gradient fill on the bar, logo texture with clamp.
3. Sequencer: in animation frames 0-20 (bar scales X from the left on an expo-like curve, text masks up 4 frames
   later), mark "In"; hold; out animation reverse and faster (60-70% duration), mark "Out".
4. Remote Control: expose Text 3D text, colour, logo visibility; Behaviors for style variants.
5. Rundown: add the page, test play-in/next/out; check safe areas (title-safe 80%).

## Scripting
Python Editor Scripting (enable the Python plug-in): spawn actors, set properties, batch-generate pages from CSV;
Blueprints for runtime logic. Deliver scripts with the engine version and plug-ins listed.

## Craft notes
Broadcast safe colours and legal levels (no pure white/black fills on big areas, avoid > 100 IRE); readable type
sizes at distance (>= 3.5% of frame height for names); in/out under 0.5s; nothing flashes; motion consistent across
all pages of a show (one curve set).

## Learn
Epic's "Unreal Engine: Motion Design. Introduction" course and "Your first graphic with Motion Design" doc;
RedefineFX playlist (cloners, effectors, Niagara) - `search.py "unreal" -d learn`.
