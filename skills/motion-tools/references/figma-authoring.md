# Authoring motion in Figma (Figma MCP `use_figma` + motion APIs)

Applies when the Figma MCP server is connected and the user wants animation built INSIDE the Figma file. To turn
Figma motion into code, use `astudio-motion:ui-motion` -> `references/figma-motion.md`.

## Gating
Motion APIs may not be enabled for the user: any motion property/helper then throws `"<name>" is not a supported
API`. Bail out on the first such error - do not retry; tell the user motion isn't enabled for them. Custom animation
styles and `TextStagger` may be unavailable even when other motion APIs work - discover before use
(`figma.motion.figmaAnimationStyles()`, `figma.getLocalCustomAnimationStylesAsync()`); never silently substitute.

## API surface (Plugin API via use_figma)
- `node.manualKeyframeTracks` - read/write keyframe tracks (position, scale, rotation, opacity, fills, strokes,
  effects); `node.applyManualKeyframeTrack(field, track)` / `node.removeManualKeyframeTrack(field)`.
- Animation styles (presets: fade, move, scale...): `applyAnimationStyle`, `removeAnimationStyle`, `node.animationStyles`;
  stack them to play together or sequence them.
- Custom animation styles (reusable named motion saved in the file): `figma.createCustomAnimationStyle`, local style
  discovery/editing.
- Text animation: per character/word/line/paragraph with stagger (TextStagger), typewriter reveals.
- Timeline: `node.timelines`, `node.setTimelineDuration(id, seconds)`.
- Easing objects: cubic-bezier, spring, hold - use the project's motion tokens (convert springs with `easing.py`).

## Workflow
1. Inspect the frame (structure, existing tracks/styles, timeline duration) before writing.
2. Plan in numbers (durations, eases, staggers) from the motion system; one change at a time.
3. Prefer animation styles and components with motion (animated components travel with the component across files)
   and **motion variables** with modes (switch an easing set per page) over one-off keyframes - that builds a system.
4. Write keyframes; set the timeline duration; verify by reading the tracks back and exporting a preview (MP4/GIF
   from the file) if available.
5. Defaults when the user gave none: 0.25-0.7s, stagger related elements, sequence by hierarchy (header -> subheader
   -> primary -> secondary), ease-out / ease-in-out families; avoid flashy loops, large rotations, excessive bounce.

## Handoff
Dev Mode's Motion tab exposes timing, easing and keyframes and copies CSS / JSON / React (motion.dev). Time-based
comments let reviewers point at a moment. Note for developers: Smart Animate prototype transitions are not exported
through MCP; GIF/animated SVG exports carry no motion data for code.
