# Other video-from-code frameworks

## HyperFrames (HeyGen, Apache-2.0)
HTML rendered to video by seeking a paused timeline frame by frame (the same idea as our pipeline), with a Studio
preview app, a registry of blocks/transitions and checks.
- `npx hyperframes init <dir>` · `npx hyperframes check --json` · `npx hyperframes snapshot --review` ·
  `npx hyperframes render` · `npx hyperframes capture <url> --json` (site as subject) · `catalog --tag transition`.
- Contract: every timed element has `class="clip"`, `data-start`, `data-duration`; each composition builds one paused
  timeline and registers `window.__timelines["<composition-id>"] = tl`; no Date.now/unseeded random/timers/repeat -1;
  never tween display/visibility/autoAlpha on a `.clip` (animate a child); no CSS transform on elements GSAP
  transforms; media never play()/pause()/seek; fonts via @font-face from `assets/fonts/`; 90% action-safe / 80%
  title-safe.
- motion.cjs drives HyperFrames pages too (it seeks `window.__timelines`), useful for quick strips without the CLI.
- Some HyperFrames features (avatars, TTS voices) are paid HeyGen services - offer the free option beside them.

## Remotion (React)
- `npx create-video@latest`; compositions in `src/Root.tsx`; animate ONLY from `useCurrentFrame()` +
  `interpolate()` / `spring({ frame, fps, config: { damping } })`; `<Sequence from durationInFrames>` for timing,
  `<Series>`, `<TransitionSeries>` (@remotion/transitions) for scene transitions; `<OffthreadVideo>`, `<Audio>`;
  `staticFile()` for assets; `delayRender/continueRender` for async data.
- Three.js: `@remotion/three` `<ThreeCanvas>`, animate from `useCurrentFrame()` (never useFrame clocks).
- Render: `npx remotion render <id> out.mp4`; Lambda/Cloud Run for scale; parameterised renders via `inputProps`.
- Licence: free for individuals and small companies; companies above the threshold need a company licence - tell the
  user before choosing it for a commercial team.
- Converting: GSAP timelines map to `interpolate` per property; CSS animations must become frame-driven.

## Plain browser capture (fallback)
When a page can't be made seekable: Playwright `recordVideo` (real-time, frame drops possible) or screen capture -
fine for quick previews, never for deliverables.

## After the render
ffmpeg recipes: `scale`/`crop` for cut-downs (`crop=ih*9/16:ih` then recompose rather than crop when possible),
`-ss -t` trims, `fps=25,palettegen/paletteuse` for GIFs, `-c:v libvpx-vp9 -pix_fmt yuva420p` for alpha WebM,
`-c:v prores_ks -profile:v 4444` for alpha MOV, `-movflags +faststart` for web playback.
