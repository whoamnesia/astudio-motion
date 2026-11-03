# What each kind of motion job must contain

## Marketing site / landing / showcase motion (`reference/site-motion.md`)
- total choreography: every visible element performs - headings, body text, labels, buttons, links, images, icons,
  numbers, list/menu/table rows, rules, badges, maps, header, footer - from one reveal grammar by content type, on
  one set of tokens, in reading order; `motion.cjs coverage` shows no static section and >= 90% moving;
- smooth and light: reveals 0.9-1.4s on expo.out/power4.out, overlapping staggers, image wipes with inner scale and
  parallax, Lenis smooth scroll on desktop, lerped hovers/magnetic buttons, nothing stops hard;
- one signature moment on top (hero intro, a scroll scene, a map journey, a 3D object) - built from the subject;
- the hero paints on the first frame (LCP image visible with a partial clip + scale, heading rising from t=0),
  settled <= 2.0s, LCP not delayed by more than 300ms;
- maps: the route built on the street geometry, drawn with a traveller, pin drop on arrival, every map layer builds;
- one scroll-driven scene every few sections; pins <= 2-3 screens; parallax on images only;
- page transitions if multi-page (View Transitions or an overlay wipe);
- reduced motion: every element still fades in gently, no travel; pause control for anything auto-moving > 5s;
  60fps on a mid-range laptop.

## Product UI motion system
- tokens (durations, eases, springs, staggers) + reduced-motion mapping;
- recipes per component: press, hover, popover/dropdown, tooltip, modal, drawer/sheet, toast, accordion, tabs,
  list add/remove, skeleton -> content, route transition, success/error, drag;
- never-animate list (keyboard shortcuts, command palette, tables, high-frequency toggles);
- MOTION.md and code that references tokens.

## Brand / logo motion
- a logo reveal (1.5-3s) built from the mark's own construction, plus a short web intro (<1s) and a loop/idle if
  needed; end pose = the exact lockup; versions: 16:9, 1:1, 9:16, transparent (WebM/ProRes 4444 note) and Lottie
  for web/apps when it is vector;
- motion principles for the brand (personality in numbers) for other teams to follow.

## Launch / promo film (20-45s)
- story: hook -> tension -> reveal -> proof -> payoff -> claim -> end card; one viewer doing one real task;
- real product UI rebuilt in DOM, pushed 1.6-2x on the action; a cursor that causes changes;
- 3-5 transitions with causes; if the brief asks for sound: music-first timing (beat grid), sound on visible actions;
- frame 0 composed (the subject already on screen, mid-motion);
- end card: mark performed in during the last 5-10%, CTA held 1.5-3s;
- deliverables: 16:9 master + 9:16/1:1 cut-downs as needed, captions if there is speech, a poster frame.

## Explainer / data video
- one concept worked through one concrete example; numbers true and sourced;
- information cards readable within ~2.5s and then held; charts that build in reading order.

## Social clip
- 9:16 1080x1920 (and 4:5 1080x1350); text in the safe area (top 250px, bottom 340px clear); hook in the first
  second; readable without sound; loop seam clean if it loops.

## 3D web experience
- a staged subject (light, ground/contact shadow, camera with intent), not a spinning default mesh;
- loading strategy (poster first, progressive), fallbacks (no WebGL, reduced motion), DPR cap, draw-call budget;
- interaction that reveals something (rotate to inspect, scroll to explore), never a toy for its own sake.

## Mobile app motion
- navigation transitions per platform, sheets with springs, press feedback on press-in, haptics on causal moments,
  gestures interruptible with velocity, reduced-motion respected; on the UI thread.
