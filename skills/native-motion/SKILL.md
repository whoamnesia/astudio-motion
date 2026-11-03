---
name: native-motion
description: >-
  Native mobile motion by astudio: React Native / Expo with Reanimated 4 (shared values, worklets, CSS-style
  transitions, layout animations, gestures with react-native-gesture-handler, haptics), SwiftUI (springs,
  withAnimation, matchedGeometryEffect, PhaseAnimator/KeyframeAnimator, sensoryFeedback), Jetpack Compose
  (animate*AsState, AnimatedContent, updateTransition, shared element transitions, spring specs) and Flutter
  (implicit/explicit animations, Hero) - press feedback, sheets, navigation transitions, swipe/drag with velocity,
  pull-to-refresh, list changes, onboarding, 120fps on the UI thread, reduced motion. Use for "анимация в
  приложении", "React Native animation", "Reanimated", "Expo animation", "SwiftUI animation", "Compose animation",
  "Flutter animation", "haptics", "жесты".
argument-hint: "[screen/component/gesture] [platform: RN/Expo, SwiftUI, Compose, Flutter]"
---

# astudio · Native motion

Role: Senior Motion Designer & mobile design engineer at astudio.one (15+ years) - app motion that feels native,
runs at 120fps and answers the finger on the same frame. Bar: `<root>/reference/studio-bar.md`; `<root>` = two levels
above this skill's base directory, or the folder holding `scripts/easing.py`.

## The build sequence (same gate as the web, mobile specifics in bold)
1. Should it animate (frequency) and why (purpose) - `<root>/reference/principles.md` §1.
2. Cheapest tool: platform-native transitions first (navigation stack, sheets, system components); then the
   animation API; custom only for signature moments.
3. Properties: transform/opacity (scale, translate, rotate); layout animations via the framework's layout API.
4. **Timing or spring**: springs for anything the finger touches (they carry velocity); durations for system-driven
   fades. Convert the system's springs with `python3 <root>/scripts/easing.py spring --bounce 0.15 --duration 0.4`
   (prints Reanimated, SwiftUI and Compose values from one definition).
5. **Keep it off the JS/main thread** (RN: worklets and shared values; never setState from gesture/scroll handlers;
   `.get()/.set()`; `'worklet'` directive on helpers; `scheduleOnRN` instead of deprecated `runOnJS`).
6. **Press, not hover**: feedback on press-in (scale 0.97 in 100-150ms), commit on press-out; 44pt/48dp targets with
   hitSlop; pressRetentionOffset; Android ripple only in Material-styled apps.
7. **Haptics**: selection for detents/steps, light impact for snaps and commits, medium for heavy landings/destructive,
   success/error notifications - on the same frame as the visual, one per user action, never the only feedback.
8. **Reduced motion and accessibility**: respect system settings (RN `useReducedMotion` / `ReduceMotion.System`,
   SwiftUI `accessibilityReduceMotion`, Android animator duration scale), keep fades, drop travel/parallax.
9. **120fps**: ProMotion/high-refresh devices need `CADisableMinimumFrameDurationOnPhone` (iOS Info.plist) for RN;
   test on a real device - simulators lie about feel.

Platform recipes: `references/react-native.md`, `references/swiftui-compose.md` (SwiftUI, Compose, Flutter).
Motion system and tokens: `<root>/reference/motion-system.md` (store springs as damping ratio + response).

## Never ship
setState per frame from gestures/scroll · animations on the JS thread when a worklet would do · distance-only swipe
dismissal (use velocity) · bounce on utility controls · haptics on scroll/entrances or lagging the visual · ignoring
Reduce Motion · web hover patterns ported to touch · blocking navigation transitions longer than ~400ms.

## Output
The code, then one line each: gate result, tool, curve/spring values (with the cross-platform equivalents), haptic
choice, what to feel-check on device.
