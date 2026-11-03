# WebGL2 adaptation rules (adapted from MiniMax shader-dev, MIT) and portability pitfalls

## ShaderToy -> standalone WebGL2
- `canvas.getContext("webgl2")`; shader source starts with `#version 300 es` (first character - `.trim()` script text).
- Fragment: `precision highp float;` and `out vec4 fragColor;`; `varying` -> `in`; `gl_FragColor` -> `fragColor`;
  `texture2D()` -> `texture()`.
- Vertex: `attribute` -> `in`, `varying` -> `out`.
- No `fragCoord` built-in: use `gl_FragCoord.xy`, or wrap: `void main() { mainImage(fragColor, gl_FragCoord.xy); }`.
- Functions must be declared before use (reorder or forward-declare).
- `#define X normalize(vec3(...))` fails - macros can't call functions; use `const vec3 X = vec3(0.756, 0.378, -0.567);`.
- Uniforms the template provides: `iResolution (vec3)`, `iTime`, `iTimeDelta`, `iFrame`, `iMouse (vec4)`; add your own
  (`uniform vec3 uAccent;`) and pass via `--uniforms` in motion.cjs.

## Minimal host page
```html
<canvas id="c"></canvas>
<script id="fs" type="x-shader/x-fragment">#version 300 es
precision highp float; uniform vec3 iResolution; uniform float iTime; out vec4 fragColor;
void main(){ vec2 uv = gl_FragCoord.xy / iResolution.xy; fragColor = vec4(uv, 0.5 + 0.5 * sin(iTime), 1.0); }
</script>
<script>
const c = document.getElementById('c'), gl = c.getContext('webgl2');
const sh = (t, s) => { const x = gl.createShader(t); gl.shaderSource(x, s); gl.compileShader(x); if (!gl.getShaderParameter(x, gl.COMPILE_STATUS)) console.error(gl.getShaderInfoLog(x)); return x; };
const p = gl.createProgram();
gl.attachShader(p, sh(gl.VERTEX_SHADER, '#version 300 es\nin vec2 a; void main(){ gl_Position = vec4(a, 0., 1.); }'));
gl.attachShader(p, sh(gl.FRAGMENT_SHADER, document.getElementById('fs').text.trim())); gl.linkProgram(p); gl.useProgram(p);
gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer()); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 3,-1, -1,3]), gl.STATIC_DRAW);
const loc = gl.getAttribLocation(p, 'a'); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
const uR = gl.getUniformLocation(p, 'iResolution'), uT = gl.getUniformLocation(p, 'iTime');
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches; let visible = true, last = 0;
new IntersectionObserver(([e]) => visible = e.isIntersecting).observe(c);
function frame(ms) { requestAnimationFrame(frame); if (!visible || ms - last < 33) return; last = ms;  // ~30fps cap
  const dpr = 1, w = c.clientWidth * dpr, h = c.clientHeight * dpr; if (c.width !== w || c.height !== h) { c.width = w; c.height = h; }
  gl.viewport(0, 0, w, h); gl.uniform3f(uR, w, h, 1); gl.uniform1f(uT, reduce ? 2.0 : ms / 1000); gl.drawArrays(gl.TRIANGLES, 0, 3); }
requestAnimationFrame(frame);
</script>
```

## Portability pitfalls (fail silently on some GPUs)
- Integer/float mixing (`1` vs `1.0`), implicit conversions; `mod` of negative numbers; `pow(x, y)` with x < 0 = NaN.
- Precision: `mediump` on mobile breaks large coordinates/time - use `highp` and keep `iTime` wrapped
  (`mod(iTime, 1000.)`) for long sessions.
- Loops: constant bounds (old GLSL ES); `break` early instead of variable bounds.
- Division by zero and `normalize(vec3(0))` -> NaN black pixels; guard with `max(len, 1e-5)`.
- Derivatives (`dFdx`, `fwidth`) are fine in WebGL2; avoid them inside non-uniform control flow.
- Texture: UV origin bottom-left; Three sets `flipY` for images, not render targets; sample colour textures as sRGB,
  data textures linear.
- Alpha: premultiplied vs straight edges; set `transparent: true` and the right blending in Three.

## Debugging
Output intermediate values as colour (`fragColor = vec4(vec3(d), 1.)`); check compile logs (motion.cjs maps lines to
your file); binary-search the shader by commenting blocks; Spector.js for draw-call state.
