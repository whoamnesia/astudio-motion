# After Effects 26

## Expression library (JavaScript engine)
```js
// Inertial bounce (overshoot that decays after the last keyframe) - for playful brands only
var amp = 0.06, freq = 2.0, decay = 6.0, n = 0;
if (numKeys > 0) { n = nearestKey(time).index; if (key(n).time > time) n--; }
if (n > 0) { var t = time - key(n).time, v = velocityAtTime(key(n).time - thisComp.frameDuration / 10);
  value + v * amp * Math.sin(freq * t * 2 * Math.PI) / Math.exp(decay * t); } else { value; }
```
```js
loopOut("cycle");          // seamless loops (first key = last key); "pingpong", "offset", "continue"
```
```js
// Controlled wiggle on a slider panel (null "CONTROLS" with sliders Freq/Amp)
var c = thisComp.layer("CONTROLS"); wiggle(c.effect("Freq")("Slider"), c.effect("Amp")("Slider"));
```
```js
// Responsive text box: shape rectangle size follows a text layer (Essential Graphics friendly)
var r = thisComp.layer("Title").sourceRectAtTime(time, false), pad = [48, 28];
[r.width + pad[0] * 2, r.height + pad[1] * 2];
```
```js
// Delay a child after its parent by N frames (overlap / follow-through)
var d = framesToTime(3); thisComp.layer("Card").transform.position.valueAtTime(time - d);
```
```js
// Stagger by layer index for duplicated layers
var d = (index - 1) * framesToTime(2); thisComp.layer(1).transform.opacity.valueAtTime(time - d);
```
Text animators (Range Selector by words/characters, Ease High/Low) for per-word reveals: offset 0 -> 100% over the
hold, shape "Ramp Up", Based On Words, with Position Y 40 + Opacity 0 + Blur 8 in the animator.

## Easing in AE
With zero speed at both keys (Easy Ease style), outgoing influence `a` on key A and incoming influence `b` on key B
give `cubic-bezier(a/100, 0, 1 - b/100, 1)` - e.g. 33/33 = `cubic-bezier(0.33, 0, 0.67, 1)`, 80/80 =
`(0.8, 0, 0.2, 1)`. Curves with a fast start (ui-out `(0.23, 1, 0.32, 1)`, expo-out `(0.16, 1, 0.3, 1)`) need a non-zero
outgoing speed on key A: open the Value Graph, give key A a steep outgoing handle (high speed, influence ~16-25%) and
key B a long incoming handle (zero speed, influence ~70-90%). Easiest route: a curve plug-in that takes cubic-bezier
values directly (Flow, or similar); without one, match the graph by eye. Verify by rendering a frame strip and
comparing it with the web version at the same times (`motion.cjs strip --at`).

## ExtendScript automation (.jsx)
```js
// File > Scripts > Run Script File... or ScriptUI panel in Scripts/ScriptUI Panels
app.beginUndoGroup("astudio: build comps");
var proj = app.project, items = ["Hero", "Feature A", "Feature B"];
for (var i = 0; i < items.length; i++) {
  var c = proj.items.addComp(items[i], 1920, 1080, 1, 6, 30);
  var t = c.layers.addText(items[i]); t.property("Position").setValue([160, 540]);
  var op = t.property("Opacity"); op.setValueAtTime(0, 0); op.setValueAtTime(0.5, 100);
  var e = new KeyframeEase(0, 80); op.setTemporalEaseAtKey(2, [e], [e]);
}
app.endUndoGroup();
```
Common jobs: batch-create comps from a CSV, replace footage, apply a preset to selected layers, add to Render Queue
with an Output Module template (`rq.items.add(comp)` + `.outputModule(1).applyTemplate("H.264")`), export frames,
relink fonts report. UXP scripting is the modern API where available - check the user's AE version.

## AE 26 features worth using
Parametric 3D meshes (primitives) and Substance 3D materials (1300+) in the Advanced 3D renderer, depth of field in
Advanced 3D (26.3), Object Matte; native 3D model import (glTF/OBJ). For heavy 3D prefer C4D/Blender and composite.

## MOGRT / Essential Graphics
Expose only what editors should change (text, colour, a duration slider); responsive design - time (protected
regions for in/out animations) and position (sourceRectAtTime); test long and short strings; fonts embedded or
listed.

## Lottie (Bodymovin / LottieFiles plug-in)
Safe: shape layers, solids, transforms, trim paths, masks (Add only, simple), precomps, text (prefer outlined),
parenting, simple expressions baked to keyframes (Bake Expressions). Avoid: effects (blur/glow), 3D layers, blending
modes, track mattes on many layers, mesh warps, particles. Export `.lottie` and test in a player.

## Render
H.264 via Media Encoder (or AE's H.264 output module) at 1080p CRF-like quality 16-20 Mbps; ProRes 422 HQ masters;
ProRes 4444 with alpha for overlays; PNG sequences for compositing. Always check one frame per scene before the
full render.
