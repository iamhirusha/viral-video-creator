#!/usr/bin/env python3
"""
POV horror episode builder — free + local.
  python3 build.py episodes/ep1_test.json            -> renders the mp4 named in the spec

Set FONT_DIR, POV_ROOT, and KOKORO_DIR if fonts, assets, or models are not next to this script.
Pipeline: Kokoro-ONNX TTS -> faster-whisper word timings -> numpy SFX/ambience mix
          -> PIL frame renderer (push-in, shake, flicker, grain, phone UI, word captions)
          -> ffmpeg (libx264 + aac), 1080x1920 @ 30fps.
Everything is cached under build_cache/ so re-renders only redo what changed.
"""
import json, sys, os, hashlib, subprocess, math, functools
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.signal import butter, sosfilt, resample_poly
import sfx

ROOT = os.path.abspath(os.environ.get('POV_ROOT') or os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, 'build_cache'); os.makedirs(CACHE, exist_ok=True)
W, H, SR = 1080, 1920, sfx.SR

def _font_roots():
    roots = []
    if os.environ.get('FONT_DIR'):
        roots.append(os.environ['FONT_DIR'])
    roots += [
        os.path.join(ROOT, 'fonts'),
        os.path.join(os.path.dirname(ROOT), 'fonts'),
        os.path.join(os.path.dirname(os.path.dirname(ROOT)), 'fonts'),
        '/usr/share/fonts/truetype/sand-box/google',
        '/usr/share/fonts/truetype',
        '/usr/share/fonts',
        os.path.expanduser('~/.fonts'),
        os.path.expanduser('~/.local/share/fonts'),
    ]
    return [r for r in roots if os.path.isdir(r)]

def find_font(*names):
    """Locate a .ttf by file name or partial stem. Set FONT_DIR to override."""
    for root in _font_roots():
        for dirpath, _, files in os.walk(root):
            lower = {f.lower(): os.path.join(dirpath, f) for f in files if f.lower().endswith(('.ttf', '.otf'))}
            for name in names:
                if name.lower() in lower:
                    return lower[name.lower()]
            for name in names:
                stem = os.path.splitext(name)[0].lower()
                for fname, path in lower.items():
                    if stem in fname:
                        return path
    raise FileNotFoundError(
        'Missing font (looked for %s). Install Anton, Inter, and Bebas Neue, '
        'or set FONT_DIR to a folder that contains them.' % ', '.join(names)
    )

FONT_CAP = find_font('Anton-Regular.ttf', 'Anton.ttf')
FONT_UI = find_font('Inter-VariableFont_opsz,wght.ttf', 'Inter-VariableFont_opsz_wght.ttf', 'Inter-Regular.ttf', 'Inter.ttf')
FONT_TITLE = find_font('BebasNeue-Regular.ttf', 'BebasNeue.ttf', 'Bebas Neue Regular.ttf')

@functools.lru_cache(None)
def font(path, size, wght=None):
    f = ImageFont.truetype(path, size)
    if wght:
        try: f.set_variation_by_axes([14, wght] if 'opsz' in path else [wght])
        except Exception: pass
    return f

def h(*a): return hashlib.md5(json.dumps(a, sort_keys=True).encode()).hexdigest()[:12]

# ----------------------------------------------------------------- VOICES
_kokoro = None
def tts(text, voice, speed):
    global _kokoro
    p = os.path.join(CACHE, f'tts_{h(text, voice, speed)}.wav')
    if not os.path.exists(p):
        if _kokoro is None:
            from kokoro_onnx import Kokoro
            model_dir = os.environ.get('KOKORO_DIR') or os.path.join(ROOT, 'models')
            _kokoro = Kokoro(os.path.join(model_dir, 'kokoro-v1.0.onnx'), os.path.join(model_dir, 'voices-v1.0.bin'))
        a, sr = _kokoro.create(text, voice=voice, speed=speed, lang='en-us')
        sf.write(p, a, sr)
    a, sr = sf.read(p, dtype='float32')
    return a, sr

def sos(kind, f): return butter(4, f, kind, fs=SR, output='sos')

def voice_fx(a, cfg):
    fx = cfg.get('fx', [])
    if 'whisper' in fx:        # breathy: thin out lows, add envelope-following air
        env = np.convolve(np.abs(a), np.ones(480) / 480, 'same')
        air = sosfilt(sos('high', 2500), np.random.default_rng(1).standard_normal(len(a))) * env * 1.2
        a = sosfilt(sos('high', 180), a) * .8 + air
    if 'far' in fx:            # through a ceiling / down a hallway
        a = sosfilt(sos('low', 1800), a)
        out = a.copy()
        for d, g in [(0.045, .5), (0.11, .35), (0.19, .25), (0.31, .15)]:
            k = int(SR * d); out[k:] += a[:-k] * g
        a = out * .6
    if 'monitor' in fx:        # baby-monitor speaker
        a = sosfilt(butter(4, [400, 3200], 'band', fs=SR, output='sos'), a)
        a = np.tanh(a * 3) * .4 + np.random.default_rng(2).standard_normal(len(a)) * .006
    return a.astype(np.float32)

def make_line(line, voices):
    cfg = voices[line['who']]
    pitch = cfg.get('pitch', 1.0)
    a, sr = tts(line['text'], cfg['voice'], round(cfg.get('speed', 1.0) / pitch, 3))
    up = int(round(SR * 100 / pitch)); a = resample_poly(a, up, sr * 100).astype(np.float32)
    # trim lead/tail silence
    nz = np.where(np.abs(a) > 0.01)[0]
    if len(nz): a = a[max(0, nz[0] - 1200): nz[-1] + 2400]
    a = voice_fx(a, cfg) * cfg.get('gain', 1.0)
    return a

_whisper = None
def word_times(a, text):
    """Word-level timings: faster-whisper alignment, mapped onto the *script* words."""
    p = os.path.join(CACHE, f'wt_{h(text, len(a))}.json')
    if os.path.exists(p): return json.load(open(p))
    global _whisper
    if _whisper is None:
        from faster_whisper import WhisperModel
        _whisper = WhisperModel('base.en', device='cpu', compute_type='int8')
    a16 = resample_poly(a, 1, 3).astype(np.float32)
    segs, _ = _whisper.transcribe(a16, word_timestamps=True, language='en', initial_prompt=text)
    ww = [(w.start, w.end) for s in segs for w in s.words]
    words = text.split()
    if len(ww) == len(words):
        res = [[w, s, e] for w, (s, e) in zip(words, ww)]
    else:   # fallback: spread script words over the speech span, weighted by length
        t0 = ww[0][0] if ww else 0; t1 = ww[-1][1] if ww else len(a) / SR
        L = np.cumsum([0] + [len(w) + 2 for w in words]); L = L / L[-1]
        res = [[w, t0 + (t1 - t0) * L[i], t0 + (t1 - t0) * L[i + 1]] for i, w in enumerate(words)]
    json.dump(res, open(p, 'w')); return res

# ----------------------------------------------------------------- AUDIO MIX
def mix_audio(spec, dur):
    n = int(SR * dur) + SR; bus = np.zeros(n, np.float32); amb = np.zeros(n, np.float32)
    def add(buf, x, t, g=1.0):
        s = int(t * SR); e = min(n, s + len(x))
        if s < n: buf[s:e] += x[:e - s] * g
    for b in spec.get('ambience', []):
        x = getattr(sfx, b['name'])(dur=b.get('end', dur) - b.get('start', 0))
        add(amb, x, b.get('start', 0), b.get('gain', 1.0))
    for s in spec.get('sfx', []):
        add(bus, sfx.LIB[s['name']](**s.get('args', {})), s['t'], s.get('gain', 1.0))
    captions = []
    voicebus = np.zeros(n, np.float32)
    for li, ln in enumerate(spec['lines']):
        a = make_line(ln, spec['voices'])
        add(voicebus, a, ln['t'])
        for wi, (w, s, e) in enumerate(word_times(a, ln['text'])):
            captions.append(dict(w=w, s=ln['t'] + s, e=ln['t'] + e, who=ln['who'], label=ln.get('label'), g=f'{li}_{wi // 3}'))
    # sidechain-duck the ambience under dialogue
    env = np.convolve(np.abs(voicebus), np.ones(4800) / 4800, 'same')
    amb *= 1 - np.clip(env * 6, 0, .55)
    out = bus + amb + voicebus
    out = np.tanh(out * 1.1) * .92
    p = os.path.join(CACHE, 'mix.wav'); sf.write(p, out[:int(SR * dur)], SR)
    return p, captions

# ----------------------------------------------------------------- VISUAL HELPERS
@functools.lru_cache(None)
def load_img(name, scale=1.5):
    path = os.path.join(ROOT, 'assets/img', name)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f'Missing still {path}. Generate first-person stills and place them in assets/img/ '
            f'(see skills/pov-interactive-horror and episodes/ep1_test.json).'
        )
    im = Image.open(path).convert('RGB')
    tw = int(W * scale); th = int(tw * im.height / im.width)
    im = im.resize((tw, th), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
    return im

def smooth_noise(t, seed, freq):
    return sum(math.sin(t * freq * k + seed * (k + 1.7)) / k for k in (1, 2.3, 4.1)) / 1.6

@functools.lru_cache(None)
def vignette():
    y, x = np.mgrid[0:H, 0:W]
    d = np.sqrt(((x - W / 2) / (W * .62)) ** 2 + ((y - H / 2) / (H * .62)) ** 2)
    return np.clip(1.15 - d ** 2 * .75, .25, 1)[..., None].astype(np.float32)

GRAIN = [np.random.default_rng(i).normal(0, 9, (H // 2, W // 2, 1)).astype(np.float32).repeat(2, 0).repeat(2, 1) for i in range(6)]

def rrect(d, box, r, fill, outline=None, width=0): d.rounded_rectangle(box, r, fill=fill, outline=outline, width=width)

def wrap(text, f, maxw, d):
    lines, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines

PW, PH = 820, 1340          # phone size on screen
@functools.lru_cache(None)
def phone_frame(clock):
    im = Image.new('RGBA', (PW + 40, PH + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    rrect(d, (0, 0, PW + 39, PH + 39), 90, (12, 12, 14, 255), (60, 60, 66, 255), 4)
    rrect(d, (20, 20, PW + 19, PH + 19), 72, (0, 0, 0, 255))
    rrect(d, (PW // 2 - 90, 38, PW // 2 + 130, 92), 27, (12, 12, 14, 255))    # dynamic island
    d.text((80, 44), clock, font=font(FONT_UI, 34, 650), fill='white')
    d.text((PW - 150, 44), '▂▄▆ ▮', font=font(FONT_UI, 28, 600), fill='white')
    return im

@functools.lru_cache(None)
def phone_chat(contact, clock, msgs, typing):
    im = phone_frame(clock).copy(); d = ImageDraw.Draw(im)
    d.line((20, 220, PW + 20, 220), fill=(40, 40, 44), width=2)
    d.ellipse((PW // 2 - 18 - 30, 110, PW // 2 + 50 - 30, 170), fill=(90, 90, 98))
    d.text((PW // 2 - 13, 125), contact[0], font=font(FONT_UI, 32, 700), fill='white')
    d.text((PW // 2 + 20, 175), contact, font=font(FONT_UI, 28, 500), fill=(200, 200, 205), anchor='mt')
    f = font(FONT_UI, 46, 450); y = PH - 40
    items = list(msgs) + ([('them', '…typing')] if typing else [])
    blocks = []
    for who, text in items:
        ls = wrap(text, f, 600, d); bh = 58 * len(ls) + 36
        bw = max(d.textlength(l, font=f) for l in ls) + 52
        blocks.append((who, ls, bw, bh))
    for who, ls, bw, bh in reversed(blocks):
        y -= bh
        x0 = PW - bw - 20 if who == 'me' else 60
        col = (10, 132, 255) if who == 'me' else (44, 44, 48)
        if who == 'them' and ls == ['…typing']: col = (34, 34, 38)
        rrect(d, (x0, y, x0 + bw, y + bh), 34, col)
        for i, l in enumerate(ls): d.text((x0 + 26, y + 16 + 58 * i), l, font=f, fill='white')
        y -= 18
        if y < 240: break
    return im

@functools.lru_cache(None)
def phone_monitor(img, label, clock, stamp):
    im = phone_frame(clock).copy(); d = ImageDraw.Draw(im)
    d.text((70, 140), 'LullaCam', font=font(FONT_UI, 40, 750), fill='white')
    d.text((70, 196), label, font=font(FONT_UI, 30, 450), fill=(170, 170, 178))
    cam = Image.open(os.path.join(ROOT, 'assets/img', img)).convert('RGB')
    cw = PW - 40; cam = cam.resize((cw, cw), Image.LANCZOS)
    im.paste(cam, (40, 290))
    d.ellipse((70, 320, 96, 346), fill=(255, 40, 40))
    d.text((108, 314), 'LIVE', font=font(FONT_UI, 32, 750), fill='white')
    d.text((PW - 40, 314), stamp, font=font(FONT_UI, 30, 500), fill='white', anchor='ra')
    d.text((70, 290 + cw + 50), '🔊  Audio: ON      Temp 21°C', font=font(FONT_UI, 32, 500), fill=(200, 200, 205))
    return im

def draw_phone(frame, ph, t):
    k = min(1, (t - ph['start']) / .35); k = 1 - (1 - k) ** 3        # slide-up ease
    if t > ph['end'] - .3: k = min(k, (ph['end'] - t) / .3)
    if ph['type'] == 'chat':
        shown = tuple((m['from'], m['text']) for m in ph['messages'] if m['t'] <= t)
        typing = any(m['t'] - 1.2 <= t < m['t'] and m['from'] == 'them' for m in ph['messages'])
        im = phone_chat(ph['contact'], ph.get('clock', '11:58'), shown, typing)
    else:
        sec = int(t - ph['start'] + ph.get('stamp0', 7212))
        im = phone_monitor(ph['image'], ph['label'], ph.get('clock', '11:58'), f'{sec//3600:02d}:{sec//60%60:02d}:{sec%60:02d}')
    x = (W - im.width) // 2; y = int(250 + (1 - k) * 1700)
    frame.alpha_composite(im, (x, y))

def draw_caption(frame, caps, t, ybase):
    cur = [c for c in caps if c['s'] <= t]
    if not cur or t > cur[-1]['e'] + .5: return
    c = cur[-1]
    grp = [x for x in caps if x['g'] == c['g']]
    d = ImageDraw.Draw(frame)
    pop = 1 + .18 * max(0, 1 - (t - c['s']) / .12)
    f = font(FONT_CAP, int(112 * pop)); fs = font(FONT_CAP, 112)
    words = [g['w'].upper() for g in grp]
    widths = [d.textlength(w + ' ', font=(f if g is c else fs)) for w, g in zip(words, grp)]
    x = (W - sum(widths)) / 2
    for w, g, wd in zip(words, grp, widths):
        col = (255, 45, 45) if g is c else 'white'
        if g['s'] > t: col = (255, 255, 255, 0)
        if g['s'] <= t:
            d.text((x, ybase), w, font=(f if g is c else fs), fill=col, stroke_width=11, stroke_fill='black', anchor='ls')
        x += wd
    if c.get('label'):
        d.text((W / 2, ybase - 140), c['label'], font=font(FONT_UI, 40, 700), fill=(190, 230, 255), stroke_width=6, stroke_fill='black', anchor='ms')

@functools.lru_cache(None)
def choice_card(a, b, sub):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 255)); d = ImageDraw.Draw(im)
    d.text((W / 2, 560), 'WHAT DO YOU DO?', font=font(FONT_TITLE, 120), fill='white', anchor='mm')
    for k, (txt, y) in enumerate([(a, 860), (b, 1120)]):
        rrect(d, (110, y - 100, W - 110, y + 100), 30, None, (255, 45, 45) if k == 0 else 'white', 8)
        d.text((W / 2, y), txt, font=font(FONT_TITLE, 110), fill='white', anchor='mm')
    d.text((W / 2, 1300), 'OR', font=font(FONT_TITLE, 60), fill=(150, 150, 150), anchor='mm') if False else None
    d.text((W / 2, 1420), sub, font=font(FONT_UI, 46, 650), fill=(255, 45, 45), anchor='mm')
    return im

# ----------------------------------------------------------------- RENDER
def render(spec_path):
    spec = json.load(open(spec_path)); dur = spec['duration']; fps = spec.get('fps', 30)
    out = os.path.join(ROOT, spec['output'])
    wav, caps = mix_audio(spec, dur)
    caps.sort(key=lambda c: c['s'])
    json.dump(caps, open(os.path.join(CACHE, 'captions.json'), 'w'), indent=1)
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                           '-s', f'{W}x{H}', '-r', str(fps), '-i', '-', '-i', wav,
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-maxrate', '12M', '-bufsize', '24M', '-pix_fmt', 'yuv420p',
                           '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out],
                          stdin=subprocess.PIPE)
    shake_ev = [s for s in spec.get('sfx', []) if s.get('shake')]
    for fi in range(int(dur * fps)):
        t = fi / fps
        shot = next(s for s in spec['shots'] if s['start'] <= t < s['end'])
        if shot.get('choice'):
            frame = choice_card(*shot['choice'], shot.get('sub', 'COMMENT FOR PART 2')).copy()
        else:
            src = load_img(shot['image'])
            p = (t - shot['start']) / (shot['end'] - shot['start'])
            z0, z1 = shot.get('zoom', [1.0, 1.08]); z = z0 + (z1 - z0) * (p * p * (3 - 2 * p))
            amp = shot.get('shake', 4)
            for s in shake_ev:
                dt = t - s['t']
                if 0 <= dt < 1.0: amp += s['shake'] * math.exp(-dt * 5)
            ox = smooth_noise(t, 1, 9) * amp; oy = smooth_noise(t, 2, 8) * amp
            cw = src.width / z; ch = cw * H / W
            fx, fy = shot.get('focus', [.5, .5])
            x0 = (src.width - cw) * fx + ox; y0 = (src.height - ch) * fy + oy
            x0 = min(max(0, x0), src.width - cw); y0 = min(max(0, y0), src.height - ch)
            frame = src.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch)).convert('RGBA')
            ph = next((p_ for p_ in spec.get('phone', []) if p_['start'] <= t < p_['end']), None)
            if ph:
                dim = Image.new('RGBA', (W, H), (0, 0, 0, 120)); frame.alpha_composite(dim)
                draw_phone(frame, ph, t)
            draw_caption(frame, caps, t, 1760 if ph else shot.get('cap_y', 1600))
        a = np.asarray(frame.convert('RGB'), np.float32)
        bright = 1.0
        for e in spec.get('flicker', []):
            if e['t'] <= t < e['t'] + e.get('dur', .6):
                bright *= .25 if int((t - e['t']) * 23) % 3 == 0 else 1.0
        for e in spec.get('flash', []):
            dt = t - e['t']
            if 0 <= dt < .4: a = a * (1 - .5 * (1 - dt / .4)) + np.array([180, 0, 0]) * .5 * (1 - dt / .4)
        fade = min(1, t / .25, (dur - t) / .4)
        a = a * vignette() * bright * fade + GRAIN[fi % 6]
        ff.stdin.write(np.clip(a, 0, 255).astype(np.uint8).tobytes())
        if fi % 90 == 0: print(f'  frame {fi}/{int(dur*fps)}', flush=True)
    ff.stdin.close(); ff.wait()
    print('wrote', out)

if __name__ == '__main__':
    render(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'episodes/ep1_test.json'))
