# Third-party sources and licences

astudio-motion is original work by astudio (MIT, see LICENSE) that adapts ideas, rules and data from the projects
below. Where text or data is reused, the original licence applies to that part.

## Vendored files (copied, with attribution headers)
| Path | Source | Licence |
|---|---|---|
| `skills/shaders/references/library/*.md` (15 technique files) | MiniMax-AI/skills - `skills/shader-dev/techniques` | MIT, Copyright (c) 2026 MiniMax |
| `data/shots.csv` (38 shot specs extracted from recipes) | Ryan-yang125/motion-lexicon - `skills/motionboard/recipes` | MIT, Copyright (c) 2026 Motionboard |
| `data/gsap-presets.csv` | nextlevelbuilder/ui-ux-pro-max (via astudio-aio `data/motion.csv`) | MIT |

## Adapted (rules and structure rewritten in our own words, with credit)
| Topic | Source | Licence |
|---|---|---|
| UI animation build sequence, frequency gate, recipes, review standards, performance tiers | emilkowalski/skills (animate, review-animations, animation-performance, find/remove/improve-animations, animation-vocabulary) | MIT, Copyright (c) 2026 Emil Kowalski |
| Three lenses (restraint / polish / play), AI-slop motion anti-checklist and thresholds, creation gotchas | kylezantos/design-motion-principles | MIT, Copyright (c) 2026 Kyle Zantos |
| GSAP core, timeline, ScrollTrigger, plugins, React/frameworks, performance rules | greensock/gsap-skills | MIT, Copyright (c) 2026 GreenSock |
| Film grammar (vector law, the current, carriers, causal motion, sustained motion), story, spec, review, render contract | heygen-com/hyperframes (motion-doctrine, cut-the-curve, hyperframes references) | Apache License 2.0 |
| Lottie/dotLottie workflow, accessibility tiers and WCAG mapping, SVG/page-transition/micro-interaction notes | iart-ai/web-animation-skills | MIT, Copyright (c) 2026 iart.ai |
| Animated diagrams (dash flow, travelling dots, self-check) | csthink/dashmotion | MIT, Copyright (c) 2026 Mars (csthink) |
| Launch-film rules (one shape never cut, springs, cursor-driven change, music-first timing) | AbubakrChan/product-launch-motion | MIT, Copyright (c) 2026 Abubakr Chan |
| Three.js r180-r183 API changes and common mistakes, asset pipeline | CloudAI-X/threejs-skills | MIT, Copyright (c) 2026 CloudAI-X |
| WebGPU/TSL rules | OpenAEC-Foundation/Three.js-Claude-Skill-Package | MIT, Copyright (c) 2026 OpenAEC Foundation |
| Blender 5.x bpy rules, API changes, animation data model | EL4CTEO/blender-skills | MIT, Copyright (c) 2026 EL4CTEO |
| Animation quality gate (contact sheets before accepting) | RobLe3/cc-blender-skill | MIT, Copyright (c) 2026 RobLe3 |
| Blender MCP setup notes | ahujasid/blender-mcp | MIT, Copyright (c) 2025 Siddharth Ahuja |
| React Native motion (UI thread, press, haptics) | expo/skills (expo-animation), emilkowalski/skills (animate-expo) | MIT |
| Rive data binding patterns, Spline/R3F/Barba integration notes | freshtechbro/claudedesignskills | MIT, Copyright (c) 2025 Claude Skills Project |
| 3D web stack selection notes | sickn33/antigravity-awesome-skills | MIT |

## Referenced for ideas only (no text reused; no licence file published)
figma/mcp-server-guide (Figma Motion implement/use skills), remotion-dev/skills, fal-ai-community/skills.
Google Labs stitch-skills (Apache-2.0) and garrytan/gstack (MIT) were reviewed for workflow ideas.

## Official documentation consulted
Figma blog "Introducing Figma Motion" and Figma Learn "Motion design fundamentals"; Blender 5.2 LTS release notes;
Unreal Engine "Your first graphic with Motion Design"; Rive data binding docs; the course catalogue in
`data/learning.csv` (links to the original authors' free materials).
