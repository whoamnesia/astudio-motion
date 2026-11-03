# Rive

## Concepts
- **Artboards** hold the scene; **timelines** are keyframed animations (can be layered).
- **State machine**: layers of states (each plays a timeline or a blend), transitions with conditions and durations,
  **inputs** (boolean, number, trigger) and **listeners** (pointer down/up/enter/exit/move on shapes -> set inputs or
  fire events). Interactivity lives in the file, not in app code.
- **Data binding**: **view models** define data (string, number, boolean, color, enum, trigger, list, image, nested
  view models); **view model instances** hold values; **bindings** connect properties to scene properties (text,
  position, colour, visibility, state machine conditions). Data can be updated from the editor, runtime code, state
  machines or scripting, and listeners/code can react to changes. Hierarchy no longer matters once bound.
- **Events**: named events (with properties) the file reports to the app (e.g. "confettiDone", "buttonPressed").
- **Scripting** (Luau-based) for logic inside the file when the state machine isn't enough.
- **Bones, constraints, meshes** for characters; **joysticks** to drive blends.

## Web / React runtime
```bash
npm i @rive-app/react-canvas      # or @rive-app/react-webgl2 for heavy scenes
```
```jsx
import { useRive, useStateMachineInput, useViewModel, useViewModelInstance, useViewModelInstanceNumber, Layout, Fit, Alignment } from "@rive-app/react-canvas";
export function Progress({ value }) {
  const { rive, RiveComponent } = useRive({ src: "/progress.riv", stateMachines: "Main", autoplay: true, autoBind: false,
    layout: new Layout({ fit: Fit.Contain, alignment: Alignment.Center }) });
  const vm = useViewModel(rive, { name: "Progress" });
  const inst = useViewModelInstance(vm, { rive });
  const { setValue } = useViewModelInstanceNumber("value", inst);
  useEffect(() => { setValue?.(value); }, [setValue, value]);
  return <RiveComponent role="img" aria-label={`Progress ${Math.round(value)}%`} />;
}
```
Inputs (older files without view models): `const hover = useStateMachineInput(rive, "Main", "isHover"); hover.value = true;`
triggers: `input.fire()`. Events: `rive.on(EventType.RiveEvent, e => ...)`.
Vanilla: `new rive.Rive({ src, canvas, stateMachines: "Main", autoplay: true, onLoad: () => r.resizeDrawingSurfaceToCanvas() })`.

## Patterns
- Stateful button: states idle/hover/pressed/loading/success; inputs from pointer listeners in-file; app fires
  `loading` and `success` triggers.
- Data-driven illustration: a dashboard mascot whose expression follows a number (view model property bound to a
  blend state).
- Toggle/checkbox with personality, avatars, onboarding characters, game UI, interactive hero illustrations.
- Combine with GSAP ScrollTrigger: drive a number property from scroll progress.

## Performance
- Preload critical files (`RuntimeLoader` / fetch + `buffer` option); one Rive instance per visible canvas; pause
  (`rive.pause()`) when off-screen; WebGL2 renderer for many objects/meshes; size the drawing surface to the canvas
  (`resizeDrawingSurfaceToCanvas`), cap DPR.
- Keep files lean: reuse components, avoid huge raster images.

## Native
`rive-ios` (SwiftUI `RiveViewModel(fileName:stateMachineName:)`), `rive-android` (`RiveAnimationView`),
`rive-react-native`, `rive-flutter` - same `.riv`, same state machine and view model names.

## Accessibility
Label the canvas (`role="img"`, `aria-label` that reflects state), keep a non-animated path under reduced motion
(set the state machine to a static state or pause on a meaningful frame), keyboard: real buttons drive inputs - the
canvas itself is not focusable UI.

## Learn
Rive's official playlists (State Machine Basics, Data Binding) and Rive Academy (School of Motion, free) - see
`search.py "rive" -d learn`.
