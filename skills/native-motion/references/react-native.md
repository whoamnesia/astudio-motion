# React Native / Expo motion (Reanimated 4, Gesture Handler, Expo Haptics)

Ideas from expo/skills `expo-animation` and Emil Kowalski's `animate-expo` (MIT), adapted.

## Setup that silently breaks motion
- Reanimated 4 needs the New Architecture and `react-native-worklets` (babel plugin `react-native-worklets/plugin`
  last in the list; Expo SDK handles it). Missing plugin = worklets crash on device only.
- Wrap the app in `GestureHandlerRootView`; enable 120Hz on iOS (`CADisableMinimumFrameDurationOnPhone = true`).
- Test release builds on a device; dev mode and the JS debugger slow everything.

## Press feedback
```tsx
import Animated, { useSharedValue, useAnimatedStyle, withTiming, Easing } from 'react-native-reanimated';
const scale = useSharedValue(1);
const style = useAnimatedStyle(() => ({ transform: [{ scale: scale.get() }] }));
<Pressable onPressIn={() => scale.set(withTiming(0.97, { duration: 110, easing: Easing.bezier(0.23, 1, 0.32, 1) }))}
           onPressOut={() => scale.set(withTiming(1, { duration: 160, easing: Easing.bezier(0.23, 1, 0.32, 1) }))}
           hitSlop={8} pressRetentionOffset={16}>
  <Animated.View style={[styles.button, style]}>{children}</Animated.View>
</Pressable>
```
Reanimated 4 also supports CSS-like transitions on Animated components:
`<Animated.View style={{ transform: [{ scale: pressed ? 0.97 : 1 }], transitionProperty: 'transform', transitionDuration: 120 }} />`.

## Bottom sheet with velocity-based dismissal
```tsx
const y = useSharedValue(0); const H = 520;
const pan = Gesture.Pan()
  .onChange(e => { y.set(Math.max(0, y.get() + e.changeY)); })
  .onEnd(e => {
    const dismiss = e.velocityY > 800 || y.get() > H * 0.4;
    y.set(withSpring(dismiss ? H : 0, { velocity: e.velocityY, dampingRatio: dismiss ? 1 : 0.85, duration: 400 }));
    if (dismiss) scheduleOnRN(onClose); else scheduleOnRN(Haptics.impactAsync, Haptics.ImpactFeedbackStyle.Light);
  });
const style = useAnimatedStyle(() => ({ transform: [{ translateY: y.get() }] }));
```
Rubber-band beyond the top: `y = -Math.pow(-dy, 0.7)` when dragging up past 0. Use `@gorhom/bottom-sheet` for full
sheets (snap points, keyboard handling) and animate its content.

## Layout animations and lists
`<Animated.View entering={FadeInDown.duration(220).easing(Easing.bezier(0.23,1,0.32,1))} exiting={FadeOut.duration(150)} layout={LinearTransition.springify().dampingRatio(1)} />`
- One staggered moment per screen (`.delay(index * 40)` capped at ~6 items); lists that update often animate only the
  changed row.
- Shared element transitions (`sharedTransitionTag`) are experimental - keep a fallback crossfade.

## Scroll-linked
`useAnimatedScrollHandler` + `interpolate(scrollY, [0, 120], [1, 0], Extrapolation.CLAMP)` for collapsing headers;
never setState in onScroll.

## Haptics (expo-haptics)
| Moment | Call |
|---|---|
| value ticks past a step (picker, slider detent, segmented) | `Haptics.selectionAsync()` |
| snap home, sheet detent, drag commit | `Haptics.impactAsync(ImpactFeedbackStyle.Light)` |
| heavy landing, destructive action | `Haptics.impactAsync(ImpactFeedbackStyle.Medium)` |
| success / failure | `Haptics.notificationAsync(NotificationFeedbackType.Success / Error)` |
From a worklet: `scheduleOnRN(Haptics.selectionAsync)`.

## Reduced motion
```tsx
const reduced = useReducedMotion();
y.set(withSpring(0, { duration: 300, dampingRatio: 0.8, reduceMotion: ReduceMotion.System }));
```
Layout animations accept `.reduceMotion(ReduceMotion.System)`.

## Lottie / Rive on mobile
`lottie-react-native` or `dotlottie-react-native`; `rive-react-native` - see `astudio-motion:lottie-rive`.

## Recipes to know
toggle (knob translate + track colour, spring bounce 0, selection haptic), segmented control (indicator with layout
transition), swipe-to-delete row (pan with velocity, red background revealed by translate, haptic at threshold),
pull-to-refresh (custom indicator driven by scrollY), skeleton -> content crossfade, success check (Lottie or SVG
stroke), onboarding (pager with parallax only on illustrations, removed under reduced motion).
