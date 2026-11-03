# Implementing Figma Motion in code

Figma Motion (open beta since June 2026) puts a timeline on the canvas: keyframes for position, scale, rotation,
opacity, fills/strokes/effects and shader properties; preset animation styles (fade, move, scale) that stack or
sequence; animated components; motion variables with modes (switch easing sets per page); text animations
(characters/words/lines with stagger); export MP4/GIF/SVG/WebM; Dev Mode Motion tab with CSS, JSON and React /
motion.dev code.

## With the Figma MCP server
1. Parse `fileKey` and `node-id` from the URL (`/design/:fileKey/...?node-id=1-2` -> nodeId `1:2`).
2. `get_design_context(fileKey, nodeId)` - structure of record: layout, sizing, assets, styles, Code Connect hints,
   motion placement markers (`data-node-id`, `data-motion-keys`, `data-motion-wrapper-for`).
3. `get_motion_context(fileKey, nodeId, recursive: true)` - the source of truth for motion (capped at 500 nodes):
   - `codeSnippets` (CSS @keyframes and motion.dev): use them directly, don't regenerate from tracks;
   - `textAnimations`: always implement; each group starts at `startMs + orderPosition * staggerStepMs` and plays
     `groupDurationMs` (startMs already includes delay); compute orderPosition from `grouping` and `order`
     (CENTER_OUT pairs start together);
   - `keyframeBindings`: fallback only when both snippet formats are missing; `motionSummary` appears only then;
   - top-level `timelineCohorts` (`rootNodeId, durationMs, loopMode once|loop|boomerang, memberNodeIds`): drive
     members from one timeline;
   - duplicate snippets are deduped to a comment pointing at the first node - reuse that component/class.
4. Merge by node id: place each animated node using design context, attach its motion from motion context. Respect
   split markers (a wrapper may carry translate while the child carries opacity).
5. Adapt to the stack: CSS snippet -> CSS module/Tailwind arbitrary values; motion.dev snippet -> `motion/react`.
   Add reduced-motion and frequency judgement the file cannot carry (a looping hero in the file may need a pause
   control on the site).
6. Render and compare: `motion.cjs strip` your build against an MP4 exported from Figma (`ffmpeg -ss T -i
   ref.mp4 -frames:v 1 ref-T.png` at the same times).

## Known gaps to surface verbatim-style to the user
- Prototype interactions (Smart Animate between frames, transition settings) are not exposed through MCP - only
  canvas keyframes are.
- Animated GIF/SVG export is not available through MCP - vectors come out static; use video export or code.
- Groups render with `display: contents` in the sites runtime; animations targeting group boxes may need a wrapper.
When `get_motion_context` does return valid code for a listed gap, the gap has been fixed - use the output.

## Authoring motion inside Figma (use_figma + figma-use-motion)
See `astudio-motion:motion-tools` (Figma section): manual keyframe tracks, animation styles, custom animation
styles, text stagger, timeline duration, easing objects (cubic-bezier, spring, hold). Bail out on
"not a supported API" errors (motion not enabled for the user) instead of retrying.

## Without MCP
Ask for: an MP4/WebM export of the frame, Dev Mode's copied CSS/React snippet, or the timing/easing values. From
video, recover timing by stepping frames and measuring positions (`motion-system.md` §4).
