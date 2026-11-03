# Animated technical diagrams (adapted from DashMotion, MIT)

Turn plain text or Mermaid-like descriptions into a self-contained HTML/SVG diagram where data visibly flows.

## Modes
- **Flow** (pipelines, request paths, CI/CD, data flow): boxes + directed connectors with moving dashes.
- **Architecture** (services, regions, layers): grouped boxes, connectors with travelling dots for traffic.
- **Sequence** (steps over time): nodes light up in order, a dot travels between them, one step at a time.

## The two animation contracts
1. **Flowing dashed connectors** - a path with `stroke-dasharray: 6 6` and a linear animation of
   `stroke-dashoffset` from 0 to -12 (one dash period) over 0.6-1s, `infinite`. Direction = data direction. Speed can
   encode volume (slower = less traffic).
   ```css
   .flow { stroke-dasharray: 6 6; animation: flow 0.8s linear infinite; }
   @keyframes flow { to { stroke-dashoffset: -12; } }
   ```
2. **Travelling dots** - a small circle following the connector path:
   ```svg
   <circle r="3.5" class="dot"><animateMotion dur="2.4s" repeatCount="indefinite" keyPoints="0;1" keyTimes="0;1" calcMode="linear"><mpath href="#edge-a-b"/></animateMotion></circle>
   ```
   Offset multiple dots with `begin="-0.8s"`; never more than 2-3 dots per edge.

## Design tokens (shared)
Ground and ink from the brand (or neutral: ground #F6F7F9 / #0F1115, ink #1A1D24 / #E7E9EE), one accent for active
flow, a muted colour for idle edges, 1.5px strokes, 8-12px corner radius on nodes, labels in the UI font 12-14px,
monospace only for real identifiers. Layout on a grid (multiples of 8); edges orthogonal with rounded corners or
smooth curves - one style per diagram.

## Accessibility
- `@media (prefers-reduced-motion: reduce)` - stop dashes and dots, keep arrowheads so direction stays readable.
- A play/pause button when the diagram loops (WCAG 2.2.2).
- `<title>`/`<desc>` in the SVG and a text summary of the flow next to it.

## Output
One self-contained `.html` (inline CSS/SVG, no external requests) - opens from the file system. If a GIF/MP4 is
requested: `node <root>/scripts/motion.cjs video diagram.html --duration <one loop> --fps 30 --out diagram.mp4 --gif`
and check the loop seam with `motion.cjs check --loop`.

## Self-check before delivering
Every edge connects two nodes (no floating ends); arrow directions match the described flow; labels don't collide
with edges; text >= 12px at the delivered size; dash direction = data direction; the loop is seamless; reduced
motion shows a complete static diagram.
