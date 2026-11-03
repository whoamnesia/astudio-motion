#!/usr/bin/env node
/*
astudio-motion render & review - frame-accurate capture of web animation (HTML/CSS/WAAPI/GSAP/Motion/
Three.js/canvas/shaders) with Playwright, plus ffmpeg encoding. Look at motion instead of guessing.

Usage:
  node motion.cjs strip  <page|url> [--duration 3] [--frames 12 | --at 0,0.2,0.5] [--width 1440 --height 900]
                         [--selector "#hero"] [--out .astudio/motion/strip.png] [--reduced-motion] [--mode auto|hook|clock]
      Contact sheet of the animation at evenly spaced (or given) times, labelled with t and frame.
  node motion.cjs video  <page|url> --duration 8 [--fps 30] [--width 1920 --height 1080] [--selector el]
                         [--out film.mp4] [--gif] [--webm] [--scale 1] [--crf 18]
      Deterministic render: the page clock is frozen and stepped one frame at a time; every frame is captured.
  node motion.cjs check  <page|url> [--duration 3] [--fps 15] [--loop] [--width --height] [--selector el]
      Motion report: per-frame change sparkline, first-frame-empty, empty-opening, hard-stop, dead stretches (>3s), never-settles,
      loop seam (with --loop), reduced-motion end state, console errors.
  node motion.cjs coverage <page|url> [--width 1440 --height 900] [--settle 1400] [--json out.json]
      Site-wide motion coverage: scrolls the whole page like a visitor and reports every visible element that
      never moved (no transform/opacity/clip change), per section and for text separately - static islands on a
      showcase site. Also measures LCP with and without prefers-reduced-motion (does the motion delay first paint?).
  node motion.cjs still  <page|url> --at 1.25 [--out frame.png]
  node motion.cjs shader <file.frag> [--duration 4] [--width 1280 --height 720] [--frames 8 | --video --fps 30]
                         [--out shader.png] [--uniforms '{"uAccent":[0.9,0.35,0.16]}']
      Compiles a GLSL ES 3.00 / ShaderToy-style fragment shader (mainImage or main) in WebGL2, reports compile
      errors with line numbers, renders a strip (default) or a video.

Time control (--mode):
  hook  - the page defines window.__seek(t) (seconds), or window.__timelines {id: gsapTimeline} (HyperFrames style).
  clock - Playwright freezes Date/performance/timers/rAF and steps them (GSAP, Motion, three.js loops), and every
          CSS/WAAPI animation is paused and set to the same time.
  auto  - hook if present, else clock (default).
Needs Playwright (+ Chromium) and, for video/gif/webm, ffmpeg. Exit code 2 = a dependency is missing.
*/
const fs = require('fs');
const path = require('path');
const os = require('os');
const zlib = require('zlib');
const { execFileSync, spawnSync } = require('child_process');

function args(argv) {
  const o = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const k = a.slice(2);
      const n = argv[i + 1];
      if (n === undefined || n.startsWith('--')) o[k] = true; else { o[k] = n; i++; }
    } else o._.push(a);
  }
  return o;
}

function loadPlaywright() {
  const tries = ['playwright', '/opt/node-tools/node_modules/playwright', path.join(process.env.NODE_PATH || '', 'playwright')];
  try { const g = execFileSync('npm', ['root', '-g'], { encoding: 'utf8' }).trim(); tries.push(path.join(g, 'playwright')); } catch (e) {}
  for (const t of tries) { try { return require(t); } catch (e) {} }
  console.error('Playwright not found. Install: npm i -D playwright && npx playwright install chromium');
  process.exit(2);
}

function hasFfmpeg() { return spawnSync('ffmpeg', ['-version']).status === 0; }

// Local pages are served over http://127.0.0.1 (not file://) so fetch()-based loaders (three.js GLTF/SVG/HDR loaders,
// Lottie/Rive files, fonts, JSON) work exactly as on a real site.
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.mjs': 'text/javascript', '.cjs': 'text/javascript', '.css': 'text/css',
  '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp',
  '.avif': 'image/avif', '.gif': 'image/gif', '.glb': 'model/gltf-binary', '.gltf': 'model/gltf+json', '.bin': 'application/octet-stream',
  '.hdr': 'application/octet-stream', '.exr': 'application/octet-stream', '.ktx2': 'image/ktx2', '.wasm': 'application/wasm', '.woff2': 'font/woff2',
  '.woff': 'font/woff', '.ttf': 'font/ttf', '.otf': 'font/otf', '.mp4': 'video/mp4', '.webm': 'video/webm', '.mp3': 'audio/mpeg', '.wav': 'audio/wav',
  '.lottie': 'application/zip', '.riv': 'application/octet-stream', '.frag': 'text/plain', '.glsl': 'text/plain', '.txt': 'text/plain' };
function serve(file) {
  const http = require('http'); const root = path.dirname(path.resolve(file));
  return new Promise(res => {
    const srv = http.createServer((req, rsp) => {
      const p = path.join(root, decodeURIComponent(req.url.split('?')[0]));
      if (!p.startsWith(root)) { rsp.writeHead(403); return rsp.end(); }
      fs.readFile(fs.existsSync(p) && fs.statSync(p).isDirectory() ? path.join(p, 'index.html') : p, (err, buf) => {
        if (err) { rsp.writeHead(404); return rsp.end(); }
        rsp.writeHead(200, { 'Content-Type': MIME[path.extname(p).toLowerCase()] || 'application/octet-stream', 'Cache-Control': 'no-store' }); rsp.end(buf);
      });
    }).listen(0, '127.0.0.1', () => { srv.unref(); res({ srv, url: `http://127.0.0.1:${srv.address().port}/${encodeURIComponent(path.basename(file))}` }); });
  });
}
async function toUrl(t) {
  if (/^https?:|^file:|^data:/.test(t)) return { url: t };
  const q = t.indexOf('?'), file = q >= 0 ? t.slice(0, q) : t, query = q >= 0 ? t.slice(q) : '';   // page.html?play keeps its query
  const s = await serve(file); return { srv: s.srv, url: s.url + query };
}

// ---------- minimal PNG decode (8-bit RGB/RGBA, non-interlaced) for frame differencing ----------
function decodePNG(buf) {
  let p = 8, w = 0, h = 0, ct = 0, idat = [];
  while (p < buf.length) {
    const len = buf.readUInt32BE(p), type = buf.toString('ascii', p + 4, p + 8), d = buf.subarray(p + 8, p + 8 + len);
    if (type === 'IHDR') { w = d.readUInt32BE(0); h = d.readUInt32BE(4); ct = d[9]; }
    else if (type === 'IDAT') idat.push(d);
    else if (type === 'IEND') break;
    p += 12 + len;
  }
  const bpp = ct === 6 ? 4 : 3, stride = w * bpp, raw = zlib.inflateSync(Buffer.concat(idat));
  const out = Buffer.alloc(h * stride);
  for (let y = 0; y < h; y++) {
    const f = raw[y * (stride + 1)], src = raw.subarray(y * (stride + 1) + 1, (y + 1) * (stride + 1));
    for (let x = 0; x < stride; x++) {
      const a = x >= bpp ? out[y * stride + x - bpp] : 0, b = y ? out[(y - 1) * stride + x] : 0,
        c = x >= bpp && y ? out[(y - 1) * stride + x - bpp] : 0;
      let v = src[x];
      if (f === 1) v += a; else if (f === 2) v += b; else if (f === 3) v += (a + b) >> 1;
      else if (f === 4) { const pp = a + b - c, pa = Math.abs(pp - a), pb = Math.abs(pp - b), pc = Math.abs(pp - c); v += pa <= pb && pa <= pc ? a : pb <= pc ? b : c; }
      out[y * stride + x] = v & 255;
    }
  }
  return { w, h, bpp, data: out };
}
function lumaGrid(png, gw = 96, gh = 54) {
  const { w, h, bpp, data } = decodePNG(png), g = new Float32Array(gw * gh);
  for (let gy = 0; gy < gh; gy++) for (let gx = 0; gx < gw; gx++) {
    const x = Math.min(w - 1, Math.floor((gx + 0.5) * w / gw)), y = Math.min(h - 1, Math.floor((gy + 0.5) * h / gh)), i = (y * w + x) * bpp;
    g[gy * gw + gx] = 0.2126 * data[i] + 0.7152 * data[i + 1] + 0.0722 * data[i + 2];
  }
  return g;
}
const diff = (a, b) => { let s = 0; for (let i = 0; i < a.length; i++) s += Math.abs(a[i] - b[i]); return s / a.length / 255; };
const stddev = g => { let m = 0; for (const v of g) m += v; m /= g.length; let s = 0; for (const v of g) s += (v - m) ** 2; return Math.sqrt(s / g.length) / 255; };
const spark = vals => { const bars = '▁▂▃▄▅▆▇█', mx = Math.max(...vals, 1e-9); return vals.map(v => v < 1e-4 ? '·' : bars[Math.min(7, Math.floor(v / mx * 7.999))]).join(''); };

// ---------- session with frozen time ----------
async function open(pw, target, o, extra = {}) {
  const width = +(o.width || 1440), height = +(o.height || 900);
  const browser = await pw.chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  const ctx = await browser.newContext({ viewport: { width, height }, deviceScaleFactor: +(o.scale || 1),
    reducedMotion: (o['reduced-motion'] || extra.reduced) ? 'reduce' : 'no-preference' });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(String(e.message || e)));
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  const mode = o.mode || 'auto';
  if (mode !== 'hook') await page.clock.install({ time: new Date('2026-01-01T00:00:00Z') });
  const served = await toUrl(target);
  if (served.srv) browser.on('disconnected', () => served.srv.close());
  await page.goto(served.url, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts && document.fonts.ready);
  // freeze time at once (before waiting for hooks) so CSS/JS animations can't play out while we wait
  await page.evaluate(() => {
    window.__am = { t: 0, seen: new Map() };
    window.__amSeekCSS = (t) => {
      for (const a of document.getAnimations()) {
        // scroll/view timelines follow scroll position, not time: leave them alone
        if (a.timeline && !(a.timeline instanceof DocumentTimeline)) continue;
        if (!window.__am.seen.has(a)) window.__am.seen.set(a, { c0: a.currentTime || 0, t0: window.__am.t });
        const s = window.__am.seen.get(a); const ct = s.c0 + (t - s.t0) * 1000; if (!Number.isFinite(ct)) continue; a.pause(); a.currentTime = ct;
      }
      window.__am.t = t;
    };
    window.__amSeekCSS(0);
  });
  if (mode !== 'hook') {
    // the page clock keeps running between evaluate() and pauseAt(): aim slightly ahead and retry if overtaken
    for (let i = 0, ok = false; !ok; i++) {
      try { await page.clock.pauseAt(new Date(await page.evaluate(() => Date.now()) + 20)); ok = true; }
      catch (e) { if (i >= 4 || !/past/.test(String(e))) throw e; }
    }
  }
  // hooks may be defined asynchronously (module scripts with top-level await, assets loading): wait for them
  const hasHook = () => page.evaluate(() => typeof window.__seek === 'function' || !!(window.__timelines && Object.keys(window.__timelines).length));
  const waitMs = mode === 'hook' ? 20000 : (mode === 'auto' ? 1500 : 0);
  let hook = await hasHook();
  for (let waited = 0; !hook && waited < waitMs; waited += 100) { await new Promise(r => setTimeout(r, 100)); hook = await hasHook(); }
  if (mode === 'hook' && !hook) throw new Error('--mode hook: the page never defined window.__seek(t) or window.__timelines within 20s');
  const useHook = mode === 'hook' || (mode === 'auto' && hook);
  let now = 0;
  async function seek(t) {
    if (useHook) {
      await page.evaluate(async (t) => {
        if (typeof window.__seek === 'function') await window.__seek(t);
        else for (const tl of Object.values(window.__timelines)) { tl.pause(); tl.seek(t, false); }
        window.__amSeekCSS(t);
      }, t);
    } else {
      if (t < now) throw new Error('clock mode renders forward only');
      const ms = Math.round((t - now) * 1000);
      if (ms > 0) await page.clock.runFor(ms);
      await page.evaluate(t => window.__amSeekCSS(t), t);
    }
    now = t;
    // no rAF wait here: under a frozen clock rAF only fires through runFor; the screenshot itself forces a paint
  }
  async function shot(file) {
    const opts = { path: file, animations: 'allow' };
    if (o.selector) { const el = await page.$(o.selector); if (!el) throw new Error('selector not found: ' + o.selector); return el.screenshot(opts); }
    return page.screenshot(opts);
  }
  return { browser, page, seek, shot, errors, useHook, width, height };
}

function times(o, def = 3) {
  if (o.at) return String(o.at).split(',').map(Number).sort((a, b) => a - b);
  const d = +(o.duration || def), n = +(o.frames || 12);
  return Array.from({ length: n }, (_, i) => +(d * i / (n - 1)).toFixed(4));
}

async function sheet(pw, files, labels, out, cols) {
  const b = await pw.chromium.launch(); const p = await b.newPage({ viewport: { width: 1600, height: 100 } });
  cols = cols || (files.length > 9 ? 4 : 3);
  const cells = files.map((f, i) => `<figure><img src="data:image/png;base64,${fs.readFileSync(f).toString('base64')}"><figcaption>${labels[i]}</figcaption></figure>`).join('');
  await p.setContent(`<style>body{margin:0;background:#16181d;font:13px ui-monospace,monospace;color:#c9ccd3}
    .g{display:grid;grid-template-columns:repeat(${cols},1fr);gap:10px;padding:10px}figure{margin:0}img{width:100%;display:block;border:1px solid #2c3038}
    figcaption{padding:4px 2px}</style><div class="g">${cells}</div>`);
  await p.waitForTimeout(100);
  await p.screenshot({ path: out, fullPage: true }); await b.close();
}

async function cmdStrip(pw, o) {
  const target = o._[1]; const T = times(o);
  const out = o.out || '.astudio/motion/strip.png'; fs.mkdirSync(path.dirname(out), { recursive: true });
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'am-')); const s = await open(pw, target, o);
  const files = [];
  for (const [i, t] of T.entries()) { await s.seek(t); const f = path.join(tmp, `f${i}.png`); await s.shot(f); files.push(f); }
  await s.browser.close();
  const fps = +(o.fps || 30);
  await sheet(pw, files, T.map(t => `t=${t.toFixed(2)}s  f${Math.round(t * fps)}`), out, o.cols && +o.cols);
  console.log(`strip: ${out}  (${T.length} frames, mode ${s.useHook ? 'hook' : 'clock'})`);
  if (s.errors.length) console.log('console errors:', s.errors.slice(0, 5).join(' | '));
  console.log('Now OPEN the strip and judge: hierarchy of motion, easing feel, overlaps, landing, legibility at each moment.');
}

async function captureSeq(pw, o, target, extra = {}) {
  const dur = +(o.duration || 3), fps = +(o.fps || 30), n = Math.round(dur * fps) + 1;
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'am-')); const s = await open(pw, target, o, extra);
  const files = [];
  for (let i = 0; i < n; i++) { await s.seek(i / fps); const f = path.join(tmp, `f${String(i).padStart(5, '0')}.png`); await s.shot(f); files.push(f); }
  await s.browser.close();
  return { tmp, files, fps, s };
}

function encode(tmp, fps, out, o) {
  const ext = path.extname(out).toLowerCase(); fs.mkdirSync(path.dirname(path.resolve(out)), { recursive: true });
  const inp = ['-y', '-framerate', String(fps), '-i', path.join(tmp, 'f%05d.png')];
  const even = 'pad=ceil(iw/2)*2:ceil(ih/2)*2';
  let a;
  if (ext === '.gif') a = [...inp, '-vf', `fps=${Math.min(fps, 25)},scale=${o['gif-width'] || 720}:-1:flags=lanczos,split[s0][s1];[s0]palettegen=stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=4`, out];
  else if (ext === '.webm') a = [...inp, '-vf', even, '-c:v', 'libvpx-vp9', '-b:v', '0', '-crf', String(o.crf || 32), '-pix_fmt', 'yuv420p', out];
  else a = [...inp, '-vf', even, '-c:v', 'libx264', '-preset', 'slow', '-crf', String(o.crf || 18), '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out];
  const r = spawnSync('ffmpeg', a, { encoding: 'utf8' });
  if (r.status !== 0) throw new Error('ffmpeg failed: ' + (r.stderr || '').split('\n').slice(-4).join(' '));
}

async function cmdVideo(pw, o) {
  if (!hasFfmpeg()) { console.error('ffmpeg not found. Install it (apt install ffmpeg / brew install ffmpeg).'); process.exit(2); }
  const target = o._[1]; if (!o.duration) throw new Error('--duration is required for video');
  const out = o.out || '.astudio/motion/film.mp4';
  const { tmp, files, fps, s } = await captureSeq(pw, o, target);
  encode(tmp, fps, out, o);
  const outs = [out];
  if (o.gif) { const g = out.replace(/\.\w+$/, '.gif'); encode(tmp, fps, g, o); outs.push(g); }
  if (o.webm) { const w = out.replace(/\.\w+$/, '.webm'); encode(tmp, fps, w, o); outs.push(w); }
  const sheetOut = out.replace(/\.\w+$/, '-sheet.png'); const pick = [0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1].map(k => files[Math.round(k * (files.length - 1))]);
  await sheet(pw, pick, pick.map(f => { const i = +path.basename(f).slice(1, 6); return `t=${(i / fps).toFixed(2)}s f${i}`; }), sheetOut, 4);
  console.log(`video: ${outs.join(', ')}  (${files.length} frames @ ${fps}fps, ${s.width}x${s.height}, mode ${s.useHook ? 'hook' : 'clock'})`);
  console.log(`contact sheet: ${sheetOut} - open it and review before delivering.`);
  if (s.errors.length) console.log('console errors:', s.errors.slice(0, 5).join(' | '));
  fs.rmSync(tmp, { recursive: true, force: true });
}

async function cmdStill(pw, o) {
  const s = await open(pw, o._[1], o); await s.seek(+(o.at || 0)); const out = o.out || '.astudio/motion/still.png';
  fs.mkdirSync(path.dirname(out), { recursive: true }); await s.shot(out); await s.browser.close();
  console.log('still:', out); if (s.errors.length) console.log('console errors:', s.errors.slice(0, 5).join(' | '));
}

async function cmdCheck(pw, o) {
  const target = o._[1]; const fps = +(o.fps || 15); o.fps = fps; o.duration = o.duration || 3;
  const { files, s } = await captureSeq(pw, o, target);
  const grids = files.map(f => lumaGrid(fs.readFileSync(f)));
  const d = grids.slice(1).map((g, i) => diff(grids[i], g));
  const issues = [];
  if (stddev(grids[0]) < 0.01) issues.push(['WARN', 'first-frame-empty', 'frame 0 is a flat field - the thumbnail/first paint shows nothing']);
  // empty opening: the first 0.3s show (almost) nothing but the background - thumbnails, autoplay previews and the
  // first impression of a page/film all land on these frames
  const cover = g => { const srt = Float32Array.from(g).sort(), med = srt[srt.length >> 1]; let c = 0; for (const v of g) if (Math.abs(v - med) > 20) c++; return c / g.length; };
  const openN = Math.max(1, Math.round(fps * 0.3)), openCov = Math.max(...grids.slice(0, openN + 1).map(cover));
  const endCov = cover(grids[grids.length - 1]);
  if (process.env.AM_DEBUG) console.log('cover open/end', openCov, endCov);
  if (endCov > 0.01 && openCov < endCov * 0.3) issues.push(['WARN', 'empty-opening', `the first 0.3s show ${(openCov * 100).toFixed(1)}% content vs ${(endCov * 100).toFixed(1)}% at the end - open on a composed frame (part of the subject already on screen / mid-motion)`]);
  // hard stops: a burst of motion whose last moving frame is still near full speed = no deceleration into place
  { let st = -1; const runs = [];
    d.forEach((v, i) => { if (v > 0.0008) { if (st < 0) st = i; } else if (st >= 0) { runs.push([st, i - 1]); st = -1; } });
    for (const [a0, a1] of runs) { if (a1 - a0 < 3) continue; const seg = d.slice(a0, a1 + 1), pk = Math.max(...seg);
      if (pk > 0.003 && seg[seg.length - 1] >= 0.45 * pk) issues.push(['WARN', 'hard-stop', `motion stops abruptly at t=${((a1 + 1) / fps).toFixed(2)}s (last moving frame at ${Math.round(seg[seg.length - 1] / pk * 100)}% of peak speed) - land on a long-tailed ease-out`]); } }
  let run = 0, worst = 0, at = 0;
  d.forEach((v, i) => { if (v < 0.0008) { run++; if (run > worst) { worst = run; at = i - run + 1; } } else run = 0; });
  if (worst / fps > 3 && +o.duration > 4) issues.push(['WARN', 'dead-stretch', `${(worst / fps).toFixed(1)}s with no visible change from t=${(at / fps).toFixed(1)}s`]);
  const tail = d.slice(-Math.max(2, Math.round(fps * 0.4)));
  if (!o.loop && tail.every(v => v > 0.002)) issues.push(['INFO', 'still-moving-at-end', 'the last ~0.4s is still moving - fine for loops/ambient, otherwise extend --duration or let it land']);
  if (o.loop) { const seam = diff(grids[0], grids[grids.length - 1]); issues.push([seam > 0.004 ? 'FAIL' : 'OK', 'loop-seam', `first vs last frame difference ${seam.toFixed(4)} (should be ~0)`]); }
  const busy = d.filter(v => v > 0.05).length;
  if (busy > d.length * 0.5) issues.push(['WARN', 'constant-churn', `${busy}/${d.length} frame steps change >5% of the frame - too much moving at once?`]);
  // reduced-motion end state
  const r = await open(pw, target, o, { reduced: true }); await r.seek(+o.duration); const rf = path.join(os.tmpdir(), `am-r-${Date.now()}.png`); await r.shot(rf); await r.browser.close();
  const rg = lumaGrid(fs.readFileSync(rf)), endDiff = diff(rg, grids[grids.length - 1]);
  if (stddev(rg) < 0.01) issues.push(['FAIL', 'reduced-motion-blank', 'with prefers-reduced-motion the page ends blank - content hidden behind animation']);
  else if (endDiff > 0.03) issues.push(['WARN', 'reduced-motion-differs', `reduced-motion end state differs ${(endDiff * 100).toFixed(1)}% from the normal end state - check nothing is missing`]);
  else issues.push(['OK', 'reduced-motion', 'end state matches with prefers-reduced-motion']);
  if (s.errors.length) issues.push(['WARN', 'console-errors', s.errors.slice(0, 3).join(' | ')]);
  const peak = d.indexOf(Math.max(...d));
  console.log(`motion check: ${target}  ${o.duration}s @ ${fps}fps, mode ${s.useHook ? 'hook' : 'clock'}`);
  console.log(`change per frame: ${spark(d)}`);
  console.log(`peak change at t=${((peak + 1) / fps).toFixed(2)}s; frames with visible change: ${d.filter(v => v > 0.0008).length}/${d.length}`);
  for (const [sev, rule, msg] of issues) console.log(`${sev.padEnd(4)} [${rule}] ${msg}`);
  const fails = issues.filter(i => i[0] === 'FAIL').length;
  console.log(fails ? `\nFAIL=${fails}` : '\nno FAIL - now run `strip` and LOOK at the motion.');
  process.exitCode = fails ? 1 : 0;
}

// ---------- coverage: does every visible element of a site perform? ----------
const SAMPLER = () => {
  const SEL = 'h1,h2,h3,h4,h5,h6,p,li,blockquote,figcaption,dt,dd,img,picture,video,canvas,svg,button,a,input,select,textarea,label,td,th,[data-reveal]';
  const TEXT = /^(H[1-6]|P|LI|BLOCKQUOTE|FIGCAPTION|DT|DD|LABEL|TD|TH|A|BUTTON)$/;
  const items = new Map();
  const sectionOf = el => el.closest('section,header,footer,nav,aside,article,main > *,body > *') || document.body;
  function collect() {
    const all = [...document.querySelectorAll(SEL)].filter(e => !e.closest('[aria-hidden="true"]') || e.tagName === 'IMG');
    const set = new Set(all);
    for (const el of all) {
      if (items.has(el)) continue;
      let p = el.parentElement, nested = false; while (p) { if (set.has(p)) { nested = true; break; } p = p.parentElement; }
      if (nested) continue;
      const hasText = (el.textContent || '').trim().length > 0, media = /^(IMG|PICTURE|VIDEO|CANVAS|SVG)$/i.test(el.tagName) || el.querySelector('img,svg,video,canvas,picture');
      if (!hasText && !media) continue;
      const sec = sectionOf(el);
      const ancestors = []; for (let a = el.parentElement; a && a !== document.documentElement; a = a.parentElement) ancestors.push(a);
      const upToSec = []; for (let a = el.parentElement; a && a !== sec.parentElement; a = a.parentElement) upToSec.push(a);
      const desc = [...el.querySelectorAll('*')]; const pick = desc.length <= 4 ? desc : [desc[0], desc[1], desc[desc.length - 2], desc[desc.length - 1]];
      items.set(el, { sec, ancestors, upToSec, pick, prev: null, moved: false, seen: false, text: TEXT.test(el.tagName) && hasText });
    }
  }
  const r1 = v => Math.round(v);
  function sig(it, el) {
    const r = el.getBoundingClientRect(), sr = it.sec.getBoundingClientRect();
    let op = 1; const cs = getComputedStyle(el); op *= +cs.opacity; for (const a of it.ancestors) op *= +getComputedStyle(a).opacity;
    let clip = cs.clipPath + cs.filter + cs.transform; for (const a of it.upToSec) { const c = getComputedStyle(a); clip += '|' + c.clipPath + c.transform; }
    let inner = ''; for (const d of it.pick) { const q = d.getBoundingClientRect(); inner += `${r1(q.left - r.left)},${r1(q.top - r.top)},${r1(q.width)},${r1(q.height)};`; }
    return { r, op, s: `${r1(r.left - sr.left)},${r1(r.top - sr.top)},${r1(r.width)},${r1(r.height)}|${Math.round(op * 50)}|${clip}|${inner}` };
  }
  function tick() {
    const vh = innerHeight;
    for (const [el, it] of items) {
      if (!el.isConnected) continue;
      const { r, op, s } = sig(it, el);
      const vis = r.width >= 4 && r.height >= 4 && r.bottom > 0 && r.top < vh && Math.min(r.bottom, vh) - Math.max(r.top, 0) > Math.min(r.height * 0.5, vh * 0.4);
      if (it.prev !== null && s !== it.prev) it.moved = true;
      it.prev = s;
      if (vis && op > 0.05 && getComputedStyle(el).visibility !== 'hidden') it.seen = true;
    }
  }
  window.__cov = { start() { collect(); tick(); this.t = setInterval(() => { tick(); }, 50); this.c = setInterval(collect, 700); },
    report() {
      clearInterval(this.t); clearInterval(this.c); tick();
      const label = sec => { if (sec === document.body) return 'body'; const h = sec.querySelector('h1,h2,h3'); return `${sec.tagName.toLowerCase()}${sec.id ? '#' + sec.id : sec.classList[0] ? '.' + sec.classList[0] : ''}${h ? ' "' + h.textContent.trim().replace(/\s+/g, ' ').slice(0, 32) + '"' : ''}`; };
      const out = [];
      for (const [el, it] of items) if (it.seen) out.push({ sec: label(it.sec), moved: it.moved, text: it.text, tag: el.tagName.toLowerCase(),
        what: ((el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 40)) || (el.getAttribute('alt') || el.getAttribute('src') || el.querySelector('img')?.getAttribute('src') || '').split('/').pop() });
      return out;
    } };
};

async function cmdCoverage(pw, o) {
  const target = o._[1], width = +(o.width || 1440), height = +(o.height || 900), settle = +(o.settle || 1400);
  const served = await toUrl(target), browser = await pw.chromium.launch();
  const lcpOf = async reduced => {
    const ctx = await browser.newContext({ viewport: { width, height }, reducedMotion: reduced ? 'reduce' : 'no-preference' });
    const page = await ctx.newPage();
    await page.addInitScript(() => { window.__lcp = { t: 0, el: '' }; try { new PerformanceObserver(l => { for (const e of l.getEntries()) window.__lcp = { t: e.startTime, el: e.element ? (e.element.tagName.toLowerCase() + (e.element.currentSrc ? ' ' + e.element.currentSrc.split('/').pop() : ' "' + (e.element.textContent || '').trim().slice(0, 30) + '"')) : '' }; }).observe({ type: 'largest-contentful-paint', buffered: true }); } catch (e) {} });
    await page.goto(served.url, { waitUntil: 'load' }); await page.waitForTimeout(3000);
    const v = await page.evaluate(() => window.__lcp); await ctx.close(); return v;
  };
  const ctx = await browser.newContext({ viewport: { width, height } });
  const page = await ctx.newPage(); const errors = []; page.on('pageerror', e => errors.push(String(e.message || e)));
  await page.addInitScript(SAMPLER);
  await page.goto(served.url, { waitUntil: 'load' });
  await page.evaluate(async () => { await document.fonts.ready; window.__cov.start(); });
  await page.waitForTimeout(settle + 600);
  await page.mouse.move(width / 2, height / 2);
  let last = -1, stuck = 0;
  for (let i = 0; i < 400 && stuck < 3; i++) {
    await page.mouse.wheel(0, Math.round(height * 0.45)); await page.waitForTimeout(settle);
    const y = await page.evaluate(() => Math.round(scrollY)); if (y <= last + 2) stuck++; else stuck = 0; last = y;
  }
  await page.waitForTimeout(settle);
  const rows = await page.evaluate(() => window.__cov.report());
  await ctx.close();
  const full = await lcpOf(false), calm = await lcpOf(true);
  await browser.close(); if (served.srv) served.srv.close();

  const bySec = new Map(); for (const r of rows) { if (!bySec.has(r.sec)) bySec.set(r.sec, []); bySec.get(r.sec).push(r); }
  const moved = rows.filter(r => r.moved).length, txt = rows.filter(r => r.text), txtMoved = txt.filter(r => r.moved).length;
  const issues = [];
  console.log(`motion coverage: ${target}  ${width}x${height}, scrolled to ${last}px`);
  console.log(`elements that move: ${moved}/${rows.length} (${Math.round(moved / Math.max(1, rows.length) * 100)}%) · text that moves: ${txtMoved}/${txt.length}`);
  for (const [sec, rs] of bySec) {
    const m = rs.filter(r => r.moved).length, pct = Math.round(m / rs.length * 100), still = rs.filter(r => !r.moved);
    console.log(`  ${pct === 100 ? 'OK  ' : pct >= 70 ? 'part' : 'STILL'} ${sec}  ${m}/${rs.length}` + (still.length ? `  static: ${still.slice(0, 6).map(r => `${r.tag} "${r.what}"`).join(', ')}${still.length > 6 ? ` +${still.length - 6}` : ''}` : ''));
    if (rs.length >= 3 && m === 0) issues.push(['FAIL', 'static-section', `${sec}: nothing in this section moves - a static island on an animated page`]);
    else if (rs.length >= 3 && pct < 70) issues.push(['WARN', 'static-islands', `${sec}: only ${pct}% of its elements move`]);
  }
  if (txt.length && txtMoved / txt.length < 0.7) issues.push(['WARN', 'static-text', `only ${txtMoved}/${txt.length} text elements have an entrance - on a showcase site text reveals too (lines/words in masks)`]);
  const delta = full.t - calm.t;
  console.log(`LCP: ${Math.round(full.t)}ms with motion (${full.el}) · ${Math.round(calm.t)}ms reduced motion (${calm.el})`);
  if (delta > 800) issues.push(['FAIL', 'lcp-delayed', `motion delays LCP by ${Math.round(delta)}ms - the LCP element must paint on the first frame`]);
  else if (delta > 300) issues.push(['WARN', 'lcp-delayed', `motion delays LCP by ${Math.round(delta)}ms - start the hero image/headline visible (partial clip, scale) instead of hidden`]);
  if (errors.length) issues.push(['WARN', 'console-errors', errors.slice(0, 3).join(' | ')]);
  for (const [sev, rule, msg] of issues) console.log(`${sev.padEnd(4)} [${rule}] ${msg}`);
  if (o.json) fs.writeFileSync(o.json, JSON.stringify({ rows, lcp: { full, reduced: calm }, issues }, null, 2));
  const fails = issues.filter(i => i[0] === 'FAIL').length;
  console.log(fails ? `\nFAIL=${fails}` : '\nno FAIL - coverage says what moved, not whether it is good: run `strip` and look.');
  console.log('note: interaction-only motion (hover, tabs) is not exercised; elements moved only by parallax/scroll count as moving.');
  process.exitCode = fails ? 1 : 0;
}

function shaderPage(src, o) {
  const body = src.includes('#version') ? src.trim() : `#version 300 es
precision highp float;
uniform vec3 iResolution; uniform float iTime; uniform float iTimeDelta; uniform int iFrame; uniform vec4 iMouse;
out vec4 fragColor;
${/mainImage\s*\(/.test(src) ? src + '\nvoid main(){ mainImage(fragColor, gl_FragCoord.xy); }' : src}`;
  const uni = o.uniforms ? JSON.parse(o.uniforms) : {};
  return `<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;background:#000}canvas{display:block;width:100vw;height:100vh}</style></head><body><canvas id=c></canvas>
<script>
const FS=${JSON.stringify(body)}, U=${JSON.stringify(uni)};
const c=document.getElementById('c'); c.width=innerWidth; c.height=innerHeight;
const gl=c.getContext('webgl2',{preserveDrawingBuffer:true}); window.__shaderErrors=[];
function sh(t,s){const x=gl.createShader(t);gl.shaderSource(x,s);gl.compileShader(x);if(!gl.getShaderParameter(x,gl.COMPILE_STATUS))window.__shaderErrors.push(gl.getShaderInfoLog(x));return x;}
const p=gl.createProgram();gl.attachShader(p,sh(gl.VERTEX_SHADER,'#version 300 es\\nin vec2 a;void main(){gl_Position=vec4(a,0.,1.);}'));gl.attachShader(p,sh(gl.FRAGMENT_SHADER,FS));gl.linkProgram(p);
if(!gl.getProgramParameter(p,gl.LINK_STATUS))window.__shaderErrors.push(gl.getProgramInfoLog(p));
gl.useProgram(p);const b=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,3,-1,-1,3]),gl.STATIC_DRAW);
const loc=gl.getAttribLocation(p,'a');gl.enableVertexAttribArray(loc);gl.vertexAttribPointer(loc,2,gl.FLOAT,false,0,0);
const L=n=>gl.getUniformLocation(p,n); let frame=0, last=0;
for(const [k,v] of Object.entries(U)){const l=L(k);if(!l)continue;const a=[].concat(v);[gl.uniform1f,gl.uniform2f,gl.uniform3f,gl.uniform4f][a.length-1].call(gl,l,...a);}
window.__seek=t=>{gl.viewport(0,0,c.width,c.height);gl.uniform3f(L('iResolution'),c.width,c.height,1);gl.uniform1f(L('iTime'),t);gl.uniform1f(L('iTimeDelta'),Math.max(0,t-last));gl.uniform1i(L('iFrame'),frame++);gl.uniform4f(L('iMouse'),c.width*.5,c.height*.5,0,0);gl.drawArrays(gl.TRIANGLES,0,3);last=t;};
window.__seek(0);
</script></body></html>`;
}

async function cmdShader(pw, o) {
  const file = o._[1]; const src = fs.readFileSync(file, 'utf8');
  const html = path.join(os.tmpdir(), `am-shader-${Date.now()}.html`); fs.writeFileSync(html, shaderPage(src, o));
  o.mode = 'hook'; o.width = o.width || 1280; o.height = o.height || 720;
  const s = await open(pw, html, o); const errs = await s.page.evaluate(() => window.__shaderErrors);
  if (errs.length) {
    await s.browser.close();
    const off = src.includes('#version') ? 0 : 4;
    console.log('SHADER COMPILE FAILED:');
    for (const e of errs) console.log(String(e).replace(/ERROR: 0:(\d+)/g, (m, n) => `ERROR: line ${Math.max(1, n - off)} of ${path.basename(file)}`));
    process.exit(1);
  }
  await s.browser.close();
  console.log('shader compiled OK (WebGL2' + (await isSoftware(pw) ? ', software renderer - timing is not representative of a GPU' : '') + ')');
  o.duration = o.duration || 4;
  if (o.video) { o.out = o.out || file.replace(/\.\w+$/, '.mp4'); return cmdVideo(pw, { ...o, _: ['video', html] }); }
  o.out = o.out || file.replace(/\.\w+$/, '-strip.png'); o.frames = o.frames || 8;
  return cmdStrip(pw, { ...o, _: ['strip', html] });
}
async function isSoftware(pw) {
  const b = await pw.chromium.launch(); const p = await b.newPage();
  const r = await p.evaluate(() => { const g = document.createElement('canvas').getContext('webgl2'); const d = g && g.getExtension('WEBGL_debug_renderer_info'); return d ? g.getParameter(d.UNMASKED_RENDERER_WEBGL) : ''; });
  await b.close(); return /swiftshader|llvmpipe|software/i.test(r);
}

(async () => {
  const o = args(process.argv.slice(2)); const cmd = o._[0];
  const cmds = { strip: cmdStrip, video: cmdVideo, check: cmdCheck, still: cmdStill, shader: cmdShader, coverage: cmdCoverage };
  if (!cmds[cmd] || !o._[1]) { console.log(fs.readFileSync(__filename, 'utf8').split('*/')[0].replace('/*', '').trim()); process.exit(cmd ? 1 : 0); }
  const pw = loadPlaywright();
  try { await cmds[cmd](pw, o); } catch (e) { console.error('error:', e.message); process.exit(1); }
})();
