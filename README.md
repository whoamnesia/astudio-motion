# astudio-motion — Motion & 3D studio for Claude Code

Author: **astudio** — [astudio.one](https://astudio.one). One plugin: a main skill and 11 sub-skills for interface animation, motion review, GSAP scroll
stories, SVG and logo animation, Lottie/Rive, video made from code, Three.js/WebGPU, shaders, Blender, After Effects /
Cavalry / Cinema 4D / Unreal / Figma Motion and native mobile motion — with a motion database, a frame-accurate
render-and-review tool and an award-level bar.

## Установка из GitHub / Install from GitHub

В Claude Code / In Claude Code:
```
/plugin marketplace add whoamnesia/astudio-motion
/plugin install astudio-motion@astudio-motion
```
Перезапустите Claude Code (restart Claude Code). Обновление / update: `/plugin marketplace update astudio-motion`.

Скиллы появятся в меню `/` как `astudio-motion:astudio-motion`, `astudio-motion:threejs` и т. д. Пара к дизайн-плагину
[astudio-aio](https://github.com/whoamnesia/astudio-aio): его можно поставить рядом, конфликтов нет.

## Установка (локально, без GitHub)

1. Скопируйте папку `astudio-motion` к себе, например в `~/claude-plugins/astudio-motion`.
2. В Claude Code выполните:
   ```
   /plugin marketplace add ~/claude-plugins/astudio-motion
   /plugin install astudio-motion@astudio-motion
   ```
3. Перезапустите Claude Code. Команды появятся как `astudio-motion:astudio-motion`, `astudio-motion:ui-motion` и т. д.
4. Для рендера и проверки анимаций нужны Playwright + Chromium (`npm i -g playwright && npx playwright install chromium`)
   и ffmpeg (для видео). Python 3.8+ — для `search.py`, `easing.py`, `motion_lint.py`, `blender_run.py`.
   Blender 5.2 LTS — только для скилла `blender`.

## Skills

| Command | What it does |
|---|---|
| `astudio-motion:astudio-motion` | **Main.** Routes any motion/3D/video request, plans the motion language (references, personality in numbers, system, signature moment), builds, renders frames and reviews. |
| `astudio-motion:ui-motion` | Interface animation: gate (should it animate?), recipes for every component, CSS/@starting-style/View Transitions/WAAPI/Motion, motion tokens, Figma Motion -> code. |
| `astudio-motion:motion-review` | Review, audit, jank diagnosis, motion opportunities, removing motion; findings table + Block/Approve; film review. |
| `astudio-motion:gsap` | **Whole-site animation (total choreography): every element and all text reveal smoothly from one system** (`templates/site-motion.js`: text in masks, image wipes, label-roll buttons, counters, maps with routes, Lenis). GSAP timelines, ScrollTrigger stories, SplitText, Flip, SVG plugins, page transitions, React/Vue/Svelte/Astro. |
| `astudio-motion:svg-motion` | Logo reveals and stings (template included), animated icons, line drawing, morphs, loaders, animated diagrams. |
| `astudio-motion:lottie-rive` | dotLottie playback/segments/scroll/theming/optimisation; Rive state machines, data binding, events, runtimes. |
| `astudio-motion:motion-video` | Launch films, explainers, social clips from HTML + GSAP rendered to MP4 (film template included); story, SPEC, seam ledger, sound. |
| `astudio-motion:threejs` | Three.js r18x / R3F / WebGPU+TSL / Spline: staged hero objects, 3D logos from SVG, scroll cameras, particles, budgets, fallbacks. |
| `astudio-motion:shaders` | GLSL/WGSL/TSL backgrounds, distortions, SDF, raymarching, post FX; compile + render check; MIT technique library. |
| `astudio-motion:blender` | bpy headless or Blender MCP: mograph loops, product turntables, logo extrude, geometry nodes, render, GLB for web. |
| `astudio-motion:motion-tools` | After Effects expressions/scripts, Cavalry, Cinema 4D, Unreal Motion Design, Figma Motion authoring, Jitter. |
| `astudio-motion:native-motion` | React Native Reanimated 4/Expo, SwiftUI, Jetpack Compose, Flutter: springs, gestures, haptics, 120fps. |

## Tools
```bash
node scripts/motion.cjs strip page.html --duration 2 --frames 12           # contact sheet of an animation
node scripts/motion.cjs video film.html --duration 12 --fps 30 --out film.mp4 --gif
node scripts/motion.cjs check page.html --duration 3                       # sparkline, empty opening, hard stops, reduced motion
node scripts/motion.cjs coverage index.html                                 # whole site: static sections/text, LCP delay
node scripts/motion.cjs shader bg.frag --frames 8                          # compile + render a fragment shader
python3 scripts/easing.py spring --bounce 0.15 --duration 0.4              # spring -> CSS linear() + platform values
python3 scripts/easing.py tokens --out design-tokens                       # motion tokens (DTCG, CSS, Tailwind v4)
python3 scripts/motion_lint.py src/ --mode ui                              # motion craft + slop lint
python3 scripts/search.py "saas launch film" --plan                        # motion plan from the database
python3 scripts/blender_run.py info                                        # find Blender, run bpy scripts headless
```

## Layout
```
astudio-motion/
  .claude-plugin/plugin.json, marketplace.json
  skills/<12 skills>/SKILL.md + references/ (+ templates/)
  reference/  studio-bar, site-motion, direction, principles, easing-timing, choreography, accessibility,
              performance, anti-slop, motion-system, review, tools
  scripts/    motion.cjs · easing.py · motion_lint.py · search.py · blender_run.py
  data/       easings, durations, ui-recipes, transitions, shots (38 launch-film shots), gsap-presets, tools,
              web3d-patterns, shader-techniques, learning (43 free courses/docs)
  NOTICE.md   third-party sources and licences
```

## Принципы студии
Роль — Senior Motion Designer & Creative Developer студии astudio.one (15+ лет): каждый запрос — дорогой заказ уровня
Awwwards/Motionographer. Перед работой — референсы и встроенная библиотека кадров; у каждой анимации есть цель
(проверка по частоте и назначению); кривые и длительности из системы токенов; 60 fps; уважение к
`prefers-reduced-motion`; картинки и видео — только свои, лицензионные стоки или сделанные кодом (без ИИ-генерации);
готово = отрендерено, просмотрено по кадрам и проверено скриптами.

## Что нового в 1.1.0 (по ревью итерации 1)
- **Сайты анимируются целиком.** Новый `reference/site-motion.md`: каждый элемент и весь текст получают своё
  появление из одной системы — плавно и согласованно. Тайминги плавнее (появления 1,1–1,3 с, плавная прокрутка
  Lenis), без «мёртвых» разделов. Отдельный рецепт для карт: маршрут строится по линиям улиц, по нему бежит
  точка, при прибытии падает метка.
- **Шаблон `skills/gsap/templates/site-motion.js` + `.css`.** Атрибут `data-reveal` на каждом элементе, вводная сцена
  первого экрана, кнопки с «перекатом» подписи, счётчики, бегущая строка от скорости прокрутки, `SiteMotion.map()`.
- **Главное фото не задерживается.** Оно видно с первого кадра; задержку первой отрисовки меряет
  `motion.cjs coverage`.
- **Ролики и заставки начинаются с собранного кадра** (проверка `empty-opening`), движение не обрывается на полной
  скорости (`hard-stop`).
- **Звук — только по запросу.**
- Новые проверки: `motion.cjs coverage`, `empty-opening`, `hard-stop`; линтер для сайтов: `short-reveal`,
  `lcp-hidden`.

## Licence
astudio-motion original content © astudio — [astudio.one](https://astudio.one) (MIT). Reused material keeps its licence; see `NOTICE.md`.
