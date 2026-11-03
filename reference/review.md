# Look, critique, fix

You wrote the timeline, so you know what happens; the viewer sees it once, at full speed, often on a phone. Judge
the rendered frames, never the code. Passing the linter means nothing banned was measured; it does not mean the
motion is good.

## 1. The loop
1. `node <root>/scripts/motion.cjs check <page> --duration <s>` - change sparkline, dead stretches, loop seam,
   reduced-motion end state, console errors. Fix every FAIL.
2. `python3 <root>/scripts/motion_lint.py <src> --mode ui|marketing|video` - fix every FAIL, weigh every WARN.
   Sites: `node <root>/scripts/motion.cjs coverage <page>` - static sections/elements/text and LCP delay; fix every FAIL.
3. `node <root>/scripts/motion.cjs strip <page> --duration <s> --frames 12` (and `--at` around the hero move and
   every seam: t-0.2, t, t+0.2). Open the PNG and run the passes below.
4. Write the notes (§3), fix P0s and the P1s worth it, re-render only what changed. Max three rounds.
5. For films: `motion.cjs video` -> open the contact sheet it writes; watch the mp4 at 0.5x mentally by stepping
   frames with `--at`.
If Playwright is missing say so and critique from code - never claim a render you did not run.

## 2. Passes (each on its own)
1. **One second.** What moved first? Was it the most important thing?
2. **Hierarchy in time.** At each sampled moment, is there one thing to follow? Count simultaneous movers.
3. **Curve feel.** Does every arrival decelerate into place (no snap at the end, no slow start)? Do exits get out of
   the way? Is anything on ease-in that should not be?
4. **Timing.** UI under 300ms unless justified (180ms beats 400ms in an app); showcase-site reveals 0.9-1.4s and
   never snappy; reads held long enough (0.5s + 0.3s/word); stillness before the payoff.
5. **Continuity.** Does each element come from somewhere and go somewhere? Do seams match axis, direction and speed?
   Any teleports, pops, flashes of unstyled or blank frames?
6. **Cause.** Is every big move caused by the previous one, on the same frame?
7. **Overlap and landing.** Children lag parents by a frame or two; nothing collides; text never moves while read;
   landed titles hold still.
8. **Sameness and harmony.** Is every block entering the same generic way (slop) - or, the opposite failure, does
   each section speak a different motion language? Content types differ, the language (eases, rhythm, direction)
   is one.
8b. **Coverage (sites).** Does anything sit still while the rest performs? Text included? (`coverage`)
8c. **Smoothness.** Does every arrival decelerate softly (no `hard-stop`), do sequences overlap, does scroll feel
   lerped, do hovers glide? Would a visitor describe it as smooth and light?
9. **Slop.** Name every tell from `anti-slop.md` visible in the strip.
10. **Frequency.** Would this still feel right on the 50th use? If not, shorten or delete.
11. **Reduced motion and phone.** Does the reduced-motion end state show everything? Does it read at 390px wide?
12. **Paused frame.** Pick a random frame: does it read as a finished image?

## 3. Notes
One line per problem: `t=1.40s · where · problem -> exact change · what stays`. Rank:
- **P0** breaks the read or the contract: content hidden or unreadable, a broken seam, a slop tell in the hero,
  motion on a keyboard/100+-per-day action, a FAIL.
- **P1** weakens it: sluggish curve, dead stretch, soft payoff, uniform entrances, missing stillness.
- **P2** polish: a frame of overlap, a 20ms stagger tweak.
Fix order: delete -> reduce -> fix the curve -> fix origin/physicality -> make interruptible -> move to the GPU ->
asymmetric timing -> polish (blur masks, stagger) -> accessibility/cohesion. A busy product UI or film: remove a
third of the motion and keep the moves that lead the eye. A showcase site that feels busy needs better hierarchy
(one lead at a time, quieter supporting moves), not static islands.

## 4. Feel you cannot judge from frames
Say so instead of guessing, and point at the check: play at 0.25-0.5x in the DevTools Animations panel, step
frame by frame, test gestures on a real device (springs, drag), look again with fresh eyes. For durations under
~150ms frames can't show the feel - rely on the tables in `easing-timing.md`.

## 5. Review output (for audits of existing motion)
Part 1 - findings table (Before | After | Why), one row per issue, with `file:line`.
Part 2 - verdict by impact tier: feel-breaking regressions; missed simplifications (delete/reduce); performance;
interruptibility and timing; origin, physicality and cohesion; accessibility.
Close with **Block** (any feel-breaking regression, motion on keyboard/high-frequency actions, scale(0)/ease-in on
UI, a non-GPU animation with an easy fix, missing reduced motion) or **Approve**.
A fresh-eyes reviewer (subagent, if available) gets only the brief, the motion contract and the strips - not the
build history - and returns P0/P1 lines.

## 6. Delivery note
What was decided (and the directions not taken); what was measured vs only looked at; what nobody checked (sound
was not heard, GPU speed not measured on SwiftShader); the weakest moment and what you would change with more time;
warnings kept on purpose and why.
