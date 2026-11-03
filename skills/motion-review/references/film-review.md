# Reviewing a rendered film or motion piece

You may be given an MP4/WebM/GIF (yours or someone else's). Review it as a harsh motion director, not a proud author.

## 1. Sample it
```bash
ffprobe -v error -show_entries format=duration:stream=width,height,r_frame_rate -of compact ref.mp4
mkdir -p .astudio/review && ffmpeg -i ref.mp4 -vf "fps=2,scale=480:-1,tile=4x6" .astudio/review/sheet-%02d.png   # 2 fps contact sheets
ffmpeg -ss 4.2 -i ref.mp4 -frames:v 1 .astudio/review/t4.2.png                                                  # exact instants
ffmpeg -ss 4.0 -t 0.5 -i ref.mp4 -vf "fps=30,scale=360:-1,tile=5x3" .astudio/review/cut-4s.png                   # a seam, frame by frame
ffmpeg -i ref.mp4 -af ebur128 -f null - 2>&1 | tail -12                                                          # loudness (you cannot hear it - say so)
ffmpeg -i ref.mp4 -vf "select='gt(scene,0.3)',showinfo" -f null - 2>&1 | grep pts_time                           # where the cuts are
```
For your own HTML films render with `node <root>/scripts/motion.cjs video` (it writes a contact sheet) and use
`strip --at` for seams.

## 2. Describe, then judge
First describe each beat frame in one sentence as a stranger would, naming every object. An object you would
have to explain ("those bars are mirrors") is a P0. Then read the beats in order: does the sequence tell a story a
stranger follows, each beat causing the next? Then go through:
| Question | Catches |
|---|---|
| does it read as what it is? | shapes that read as other objects, plastic materials, UI that reads as a mockup |
| does the subject separate? | value too close to the ground, two focal points, nowhere for the eye |
| framing and contact | crops, text at the edge or under platform UI, floating things that should touch |
| timing as a first-time viewer | reads shorter than their words, pops with no move, jumps at cuts, everything on one curve |
| seams | axis/direction/speed mismatched, crossfades between worlds, settle-before-cut dead beats |
| tells | `<root>/reference/anti-slop.md` films section |
| pictures alone | with words covered, do the beat frames still tell the story? |
| phone | every line readable at 360px wide? |

## 3. Notes
`t=4.2s · where · problem -> exact change · what stays`; P0 (breaks the read or the contract), P1 (weakens: dead
stretch, soft payoff, jumpy seam), P2 (polish). Never score the film out of 10 - a score finds nothing to fix.
A busy film: remove a third of the motion and keep the moves that lead the eye.
"Too fast" -> slow zooms/pans to 0.7x of their speed, nothing else. "Feels like slides" -> enter the next scene
through an object on screen; cut a move mid-flight. "The titles move" -> land them and hold dead still.
