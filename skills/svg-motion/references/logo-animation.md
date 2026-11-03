# Logo animation concepts

Choose from the mark's idea. Each concept lists its build, timing and when it fits. Durations are for a 1.5-3s sting;
a web intro uses the same idea compressed to 0.6-0.9s.

| Concept | Build | Timing | Fits |
|---|---|---|---|
| **Build from construction** | the mark assembles from the shapes it is made of (the two bars of a corner meet, the circle drops into place, the grid lines that constructed it draw and then fade) | parts arrive on expo.out staggered 80-150ms; final settle 300ms; hold 0.8s | geometric marks, marks with a clear construction |
| **Draw-on then fill** | a stroke duplicate of the outline draws (`stroke-dashoffset` / DrawSVG), the fill fades in under it, the stroke fades out | draw 0.8-1.2s power2.inOut; fill 0.3s; stroke out 0.2s | line marks, monograms, signatures; avoid for heavy solid marks |
| **Mask reveal** | the mark is uncovered by a shape from its own geometry (a wedge, the counter, a circle iris) via `clip-path` / `<mask>` | 0.6-0.9s expo.out | bold solid marks, brands with a strong graphic device |
| **Converge to mark** | elements of the brand's world (dots, cards, letters, product items) fly together and compress into the mark | gather 1-1.5s power3.inOut, final snap 0.3s | ecosystems, marketplaces, platforms; end cards of films |
| **Mark-to-wordmark unfold** | the mark lands centred, then shifts and the wordmark unfolds from behind it (clip edge following the mark's right edge, letters blur 12px -> 0) | mark 0.6s; unfold 0.6-0.8s expo.out; letters 0.05s after the mark moves | horizontal lockups; the default end card |
| **Rotate to lockup (3D)** | an object spins on a long ease-out and stops at the exact angle that forms the mark's silhouette | 2-2.5s expo.out, 1.5 turns in the first second; hold | marks that are projections of 3D forms (cubes, isometrics) - build in threejs or blender |
| **Morph from the subject** | a symbol of the subject (a coffee bean, a speech bubble, a folder) morphs into the mark | morph 0.6-0.9s power2.inOut with MorphSVG, matched point counts | when the mark abstracts a real object |
| **Letter-by-letter lock (scramble)** | the wordmark scrambles through characters and locks letter by letter | 0.6-1s; 30-50ms per letter | tech/dev brands; wordmark-only logos |
| **Stroke weight swell** | variable-weight or stroke-width grows from hairline to the final weight | 0.8s expo.out | typographic marks, editorial brands |
| **Light sweep** | a single soft highlight passes across a solid mark once | 0.8s power2.inOut | premium/metal brands; never as the only idea |

## Principles
- The end frame is the logo, pixel for pixel - verify by comparing the last rendered frame with a render of the
  static SVG.
- The first frame is composed, never empty: it is the thumbnail, the autoplay preview and the first impression.
  Start with part of the mark already on screen and in motion (the first stroke 25-40% drawn, the first part already
  arriving, the brand ground with its texture) - never 0.3s of background with a hairline growing. Shift the
  timeline (`master.seek(0.25)` as frame 0) or start the first move from a visible pose; `motion.cjs check` reports
  `empty-opening`.
- One idea, one camera: no stacked effects (draw + particles + glow + shake).
- Arrive slow, leave clean: long-tailed eases into the lockup; the lockup holds dead still 0.8-1.5s.
- Secondary motion (tagline, URL) starts 150-250ms after the mark settles, quieter (fade or small rise).
- Sound only when the brief asks for it (deliver silent by default and offer sound as a next step in one line). When
  requested: one designed hit on the settle frame, a soft whoosh on the move - synthesized or licensed.
- Versions: sting (2-3s), short (1s), web intro (<1s, plays once per session, skippable, none under reduced motion),
  idle/loop (only if the brand needs it: subtle, meaningful, pausable), loader (a part of the mark that loops
  seamlessly, e.g. a drawn arc of the mark's circle).

## Implementation notes
- Count path points for morphs (`MorphSVGPlugin.convertToPath`, `type: "rotational"`); without MorphSVG, morph only
  between paths with identical command structures.
- For draw-on of a filled shape: create a centre-line stroke path (or the outline stroke) with `vector-effect:
  non-scaling-stroke` and `pathLength="1"` so `stroke-dasharray: 1; stroke-dashoffset: 1 -> 0` works without
  measuring.
- Rotate/scale parts around their own centres: `transform-box: fill-box; transform-origin: 50% 50%`.
- Gradients/filters: animate `stop-color` / `offset` sparingly; filter blur on SVG groups is expensive on large sizes.
- Export: `motion.cjs video` renders the HTML deterministically; for alpha deliverables render on a transparent
  page (`html,body{background:transparent}`) and encode `-c:v libvpx-vp9 -pix_fmt yuva420p` (WebM) or
  `-c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le` (MOV) - motion.cjs encodes opaque H.264 by default.
