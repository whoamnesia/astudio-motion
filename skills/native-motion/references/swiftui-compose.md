# SwiftUI, Jetpack Compose, Flutter

## SwiftUI (iOS 17-26)
- Springs are the default language: `withAnimation(.smooth) {}` (no bounce), `.snappy` (small bounce), `.bouncy`;
  custom `.spring(duration: 0.4, bounce: 0.15)` - same parameters `easing.py spring` prints.
- State-driven: `.animation(.snappy, value: isOn)` scoped to a value; `.transition(.move(edge: .bottom).combined(with: .opacity))`
  for insert/remove; `.contentTransition(.numericText())` for numbers; `.symbolEffect(.bounce, value: count)` for SF Symbols.
- Shared elements: `matchedGeometryEffect(id:in:)` within a view; `.navigationTransition(.zoom(sourceID:in:))` +
  `.matchedTransitionSource` for navigation zoom (iOS 18+).
- Multi-step: `PhaseAnimator` (cycle through phases), `KeyframeAnimator` (per-property keyframe tracks with
  `SpringKeyframe`, `CubicKeyframe`, `LinearKeyframe`).
- Gestures: `DragGesture` with `predictedEndTranslation`/velocity for flick dismissal; `.sensoryFeedback(.selection, trigger: value)`
  / `.impact(weight: .light)` / `.success` for haptics on the same state change.
- Reduce Motion: `@Environment(\.accessibilityReduceMotion) var reduce` -> use `.opacity` transitions and no springs travel.
- Press: `ButtonStyle` with `configuration.isPressed ? 0.97 : 1` + `.animation(.snappy(duration: 0.15), value: configuration.isPressed)`.
```swift
struct PressScale: ButtonStyle { func makeBody(configuration: Configuration) -> some View {
  configuration.label.scaleEffect(configuration.isPressed ? 0.97 : 1).animation(.snappy(duration: 0.15), value: configuration.isPressed) } }
```

## Jetpack Compose
- `animateFloatAsState(target, animationSpec = spring(dampingRatio = Spring.DampingRatioNoBouncy, stiffness = Spring.StiffnessMediumLow))`,
  `animateColorAsState`, `animateDpAsState`; `tween(durationMillis = 250, easing = CubicBezierEasing(0.23f, 1f, 0.32f, 1f))`.
- `AnimatedVisibility(enter = fadeIn() + slideInVertically { it / 4 }, exit = fadeOut())`; `AnimatedContent(targetState)`
  with `togetherWith`/`SizeTransform`; `updateTransition` for multi-property state machines; `Crossfade`.
- Shared elements: `SharedTransitionLayout` + `Modifier.sharedElement(rememberSharedContentState(key), animatedVisibilityScope)`
  (Compose 1.7+); predictive back animations on Android 14+ (`PredictiveBackHandler`).
- Gestures: `Modifier.draggable`/`anchoredDraggable` with velocity thresholds; `Animatable.animateTo(..., initialVelocity = v)`.
- Haptics: `LocalHapticFeedback.current.performHapticFeedback(HapticFeedbackType.TextHandleMove / LongPress)`, or
  `View.performHapticFeedback(HapticFeedbackConstants.CONFIRM)`.
- Reduced motion: read `Settings.Global.ANIMATOR_DURATION_SCALE` (0 = animations off) and swap to fades.
- Material 3 motion tokens: emphasized decelerate `(0.05, 0.7, 0.1, 1)` for entering, emphasized accelerate
  `(0.3, 0, 0.8, 0.15)` for exiting, standard `(0.2, 0, 0, 1)`; durations short 50-200, medium 250-400, long 450-600ms;
  M3 Expressive adds spring-based motion schemes (spatial vs effects springs) - effects (colour/opacity) never bounce.

## Flutter
- Implicit: `AnimatedContainer`, `AnimatedOpacity`, `AnimatedSwitcher` (with `transitionBuilder`), `TweenAnimationBuilder`;
  curves `Cubic(0.23, 1, 0.32, 1)`, `Curves.easeOutExpo`; springs via `SpringSimulation` /
  `SpringDescription.withDampingRatio(mass: 1, stiffness: 300, ratio: 0.85)`.
- Explicit: `AnimationController` + `CurvedAnimation` + `AnimatedBuilder`; dispose controllers.
- `Hero` for shared elements; page transitions via `PageRouteBuilder` / go_router `CustomTransitionPage`.
- Haptics: `HapticFeedback.selectionClick()`, `lightImpact()`, `mediumImpact()`.
- Reduced motion: `MediaQuery.of(context).disableAnimations`.
- Rive/Lottie: `rive` and `lottie` packages.

## Cross-platform consistency
Define the spring once (damping ratio + response) and generate each platform's value with `easing.py spring`; keep
the same role map (press, sheet, navigation, list, success) across platforms; let each platform keep its native
navigation transitions unless the brand requires a custom one.
