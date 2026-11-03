---
name: motion-video
description: >-
  Motion video made from code by astudio: product launch films, promos, feature announcements, explainers,
  tutorials-as-motion, kinetic typography, data/chart videos, social clips (9:16, 1:1, 4:5), logo stings and end
  cards, changelog videos, UI walkthroughs - written as HTML + CSS + GSAP on one paused master timeline and rendered
  deterministically to MP4/WebM/GIF with Playwright + ffmpeg (scripts/motion.cjs), or with HyperFrames / Remotion
  when the project uses them. Story first (three storylines, one spine), a SPEC with numbers, a seam ledger, film
  grammar (vector law, carriers, causes), sound on a beat grid, contact-sheet review. Use for "сделай промо-ролик",
  "видео запуска", "анимированное видео", "моушн-ролик", "explainer video", "launch video", "video ad", "reels".
argument-hint: "[what the film is about, length, aspect ratio(s), music/voice or silent]"
---

# astudio · Motion video

Role: Senior Motion Designer & Director at astudio.one (15+ years) - launch films for products like Apple, Linear,
Stripe ship, built in code. Bar: `<root>/reference/studio-bar.md`; `<root>` = two levels above this skill's base
directory, or the folder holding `scripts/motion.cjs`.

## The render contract (our pipeline)
A film is one HTML page (`templates/film.html` is the starting point):
1. One **paused master GSAP timeline**; scenes are nested timelines placed on it; `window.__seek = t => master.seek(t)`
   and `window.__duration`. Everything visible is a function of timeline time: no `Date.now()`, timers, unseeded
   `Math.random()`, network calls at render time, `repeat: -1`, or CSS animations that run on their own clock.
2. Fixed canvas: a `#stage` of exactly W x H CSS px (1920x1080 default; 1080x1920 vertical; 1080x1080 square);
   fonts loaded locally or from Google Fonts before t=0 (`document.fonts.ready`).
3. Media: footage as `<video muted>` scrubbed by the timeline (`video.currentTime = localTime`) - never `play()`;
   audio is mixed in ffmpeg afterwards, and only when the brief asks for sound (`references/sound.md`).
4. Render: `node <root>/scripts/motion.cjs video film.html --duration <s> --fps 30 --width 1920 --height 1080
   --out renders/film.mp4` (+ `--webm --gif`), then open the contact sheet it writes.
Existing HyperFrames or Remotion project -> follow that framework (`references/frameworks.md`); the craft below is
the same.

## Workflow
1. **The one thing** - what it is ("You can now ..."), the one thing to remember, one viewer doing one real task
   with one real piece of data travelling from hook to payoff (`references/story.md`).
2. **Three storylines** that are three different films, in words. The person picks; unattended -> take the
   recommendation and name the other two in one line each.
3. **SPEC.md** (`<root>/reference/direction.md` §4): every adjective as a number - look, objects, motion (eases by
   role, springs as damping), shots by frame, BANNED defaults, QA frames. References: `search.py "<idea>" -d shot`
   (38 shots measured from Apple/Linear launch films with timings and eases) and studio-bar §3.
4. **Storyboard + seam ledger** - one line per shot (frame range, hero move, what is read and for how long, sound,
   hand-off) and one row per cut (time, exit vector, entry vector, carrier, technique)
   (`<root>/reference/choreography.md` §5). Fix mismatched rows in the plan, not with easing.
5. **Build** in `templates/film.html`: brand layer (tokens), real product UI rebuilt in DOM (never invented, never a
   tilted mockup), scenes as nested timelines, transitions from `search.py -d transition`, music-first timing on a
   beat grid if there is music.
6. **Check and look** - `motion_lint.py film/ --mode video` (no FAIL); `motion.cjs check film.html --duration <s>`
   (no `empty-opening`: frame 0 is composed; no `hard-stop`; dead stretches > 3s); `motion.cjs strip film.html --at <beats and every cut ±0.2s>`.
   Review with `<root>/reference/review.md` + `astudio-motion:motion-review` film passes. Fix P0/P1, re-render only
   what changed.
7. **Render and deliver** - master + cut-downs (16:9, 9:16 with safe areas, 1:1), poster frame, captions (SRT) if
   speech, sound mixed only if requested (`references/sound.md`; otherwise silent, sound offered as a next step),
   REVIEW.md: creative calls, storylines not built, what was measured vs
   only looked at (you cannot hear the mix - say so), the weakest shot, kept warnings.

## Craft rules (the defaults that look generated are banned - `<root>/reference/anti-slop.md` films)
- Open on a composed frame: frame 0 already shows the world and part of the subject, ideally mid-motion - never
  0.3s of empty background (thumbnail, autoplay preview and first impression all land there).
- Arrive slow, leave clean: expo/quart-out arrivals, exits 40-50% shorter, one smooth motion; nothing stops at full
  speed (`hard-stop`).
- Ease by role; springs damping 0.7-0.85 for containers; no bounce/elastic; one move per shot, secondary moves
  50-70% as far and 100-200ms later.
- The hero of a shot fills >= 40% of the frame; text >= 2.6% of the short side; holds 0.5s + 0.3s/word; landed
  titles still.
- Something new every 2-4s; 3-5 transition kinds with causes; at most a third of seams are hard cuts; worlds never
  crossfade; stillness 0.3-0.75s before the payoff.
- A cursor (4-7% of the frame) causes changes on the same frame; containers morph instead of cutting.
- End card in the last 5-10%: the mark performed in, CTA held 1.5-3s.
- Assets: real product, licensed stock footage/photos (credited) or code-made visuals - no AI-generated video/images.
Type-specific guidance (launch, explainer, data, social/vertical, logo sting, changelog, 3D): `references/types.md`.
