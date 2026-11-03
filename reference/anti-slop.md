# Motion slop registry

A tell is motion that reads as generated because it was produced by default, uniformly, without a reason. One
instance can be polish; the same pattern everywhere is the tell. `scripts/motion_lint.py` detects many in source;
the rest need eyes on `motion.cjs strip`. Each tell has a replacement - removal alone leaves dead motion.

## Interfaces and websites
| Tell | Flag when | Instead |
|---|---|---|
| Pulsing indicators: glowing dots, breathing CTAs, throbbing rings, "AI active" pulses | any instance without a stated reason | static status treatment; a live indicator changes when the state changes |
| Uniform fade-in-up on every section/card/paragraph | >= 4 components share identical enter values | a reveal grammar by content type (site-motion.md §3): headings split in masks, body by lines, images wipe + scale, rows one by one, numbers count |
| Text that fades as one block, or text left static while the rest moves | a paragraph/heading popping in whole, or `coverage` reports static text | lines/words/chars rising in masks on showcase sites; in product UI reading text appears instantly |
| Static islands - a moving hero over sections that just sit there | `motion.cjs coverage`: a section with nothing moving, or < 70% of its elements | every section and element performs in the same language (total choreography) |
| Snappy product-UI timing on a showcase site | scroll reveals under 0.6s, `power2.out` 0.4s everywhere | 0.9-1.4s on expo.out/power4.out with overlapping staggers (site-motion.md §2) |
| Motion that stops at full speed | `motion.cjs check` reports `hard-stop` | every arrival decelerates on a long-tailed ease-out |
| Hidden hero photo, curtain or preloader before the first screen | `coverage` LCP delta > 300ms, `check` reports `empty-opening` | the LCP image visible at frame 0 with a partial clip + scale; heading rising from t=0 |
| Hover scale 1.05 on every card/button/image | >= 3 components | one deliberate hover per component type, gated to fine pointers; colour/shadow/underline responses |
| Stagger on every list (product UI) | >= 2 staggered lists in an app view | one staggered moment; utility lists never stagger (showcase sites stagger by the shared rhythm instead) |
| Blur-everywhere entrances | >= 3 components share the same blur(Npx) enter | blur only on one hero element or as a crossfade mask |
| Bouncy springs on utility actions (dropdowns, toggles, menus, modals) | any bounce > 0 there | ui-out curve or a spring with bounce 0 |
| Scale(0) pop-ins, ease-in entrances, `transition: all` | any | scale 0.95 + opacity, ease-out, named properties |
| Floating blobs, drifting particles, rotating badges as decoration | always on, no meaning | stillness, or motion tied to scroll/interaction/content |
| Long preloaders, counters, gates | blocking > 1s | content on first paint; a branded preloader < 1s only while real assets load |
| Scroll hijacking, pinned sections that trap for many screens | pin > 3 screens, wheel captured | native scroll; short pins with visible progress |
| Cursor trails/blobs that hide the real cursor | system cursor hidden or affordances lost | a follower that adds information (preview, label), fine pointers only |
| Parallax on text, everything parallax | text moving while read | parallax on images/shapes only, small offsets, removed under reduced motion |
| Animated gradient/mesh/aurora backgrounds in purple-blue | default palette, no subject link | the brand's palette and a subject-derived shader (domain warp of coffee crema, ink, paper) or a still field |

## Films and rendered video
| Tell | Instead |
|---|---|
| a black or navy void with small things floating in the middle | a world with a ground, light and a subject filling >= 40% of the frame |
| an empty or near-empty opening (only background, a dot or a hairline for the first 0.3s) | frame 0 is composed: part of the subject already on screen or mid-motion - it is the thumbnail and the autoplay first impression |
| glow, bloom, lens flares, neon rings, particle bursts as decoration | light that comes from a source; particles only when the story needs them |
| everything fading and sliding up; every scene entering the same way | 3-5 transitions with causes; entrances chosen per element |
| crossfades between worlds | cut-the-curve, match cut, object-becomes-world |
| idle wobble, breathing, floating, slow creeping scale on titles | staged reveals, camera with intent, product behaving |
| titles that keep moving after they land | land, then hold dead still |
| click rings and ripples on every click | the click causes the next thing on the same frame |
| bounce/elastic eases; one `power2.out` 0.5s on everything | eases by role; back.out(1.4-1.7) or damping 0.7-0.85 for life |
| text too small or too brief to read | >= 2.6% of the short side; 0.5s + 0.3s/word hold |
| a product shown as tilted mockups and invented dashboards | the real UI rebuilt in DOM, pushed in 1.6-2x on the action |
| purple-blue gradients, mesh gradients, glass cards; cream paper + serif + mono labels | the brand's own material, written as numbers in SPEC.md |
| HUD readouts, corner brackets, frame borders as decoration | nothing, or real data |
| stock "trusted by" logo row | logos one by one on the beat, only with permission |

## 3D and shaders
| Tell | Instead |
|---|---|
| a lone object spinning forever on black | a staged object: light, ground, contact shadow, a camera move with intent, an end pose |
| torus knots, icospheres and generic blobs as "3D" | the subject's own object (product, logo extruded from its SVG, the brand's shape) |
| chrome + rainbow iridescence by default | a material from the brand's world, defined with numbers (roughness, metalness, colour) |
| unbounded bloom/chromatic aberration | post-processing that serves the light; subtle grain |
| full-screen noise gradients unrelated to the brand | shaders derived from the subject (paper, liquid, light, the logo's geometry) |

## Why removal is not enough
A page or film with every tell removed and nothing in their place is dead motion. Replace each with the decided
idea: one authored moment, transitions with causes, motion that carries information (`studio-bar.md`).
