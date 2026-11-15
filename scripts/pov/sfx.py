"""Synthesized horror SFX (no downloads, no licences). All return float32 mono @ SR."""
import numpy as np
from scipy.signal import butter, sosfilt

SR = 48000
rng = np.random.default_rng(7)

def _env(n, a=0.005, r=0.3):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / r)
    return e

def _lp(x, f, o=4):  return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)
def _hp(x, f, o=4):  return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)
def _bp(x, lo, hi, o=4): return sosfilt(butter(o, [lo, hi], 'band', fs=SR, output='sos'), x)

def thud(dur=1.6):
    n = int(SR * dur); t = np.arange(n) / SR
    f = 55 * np.exp(-t * 3) + 30
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, .002, .35)
    knock = _lp(rng.standard_normal(n), 900) * _env(n, .001, .06) * 2.5
    # muffled "through the ceiling" thump + small rattle
    rattle = _bp(rng.standard_normal(n), 2000, 5000) * _env(n, .01, .12) * .15
    return _norm(body + knock + rattle, .95)

def creak(dur=1.4, base=180):
    n = int(SR * dur); t = np.arange(n) / SR
    wob = base + 60 * np.sin(2 * np.pi * 1.3 * t) + 40 * rng.standard_normal(n).cumsum() / np.sqrt(n)
    ph = 2 * np.pi * np.cumsum(wob) / SR
    saw = 2 * ((ph / (2 * np.pi)) % 1) - 1
    stick = (rng.random(n) < 0.004).astype(float)      # stick-slip grains
    x = _bp(saw * (0.4 + stick * 8), 300, 2500)
    e = np.sin(np.pi * t / dur) ** 1.5
    return _norm(x * e, .5)

def footstep():
    n = int(SR * .35)
    x = _lp(rng.standard_normal(n), 400) * _env(n, .002, .05) * 3
    x += np.sin(2 * np.pi * 70 * np.arange(n) / SR) * _env(n, .002, .08)
    return _norm(x, .5)

def ping():
    n = int(SR * .35); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 1318 * t) * _env(n, .002, .07)
    x[int(SR * .09):] += (np.sin(2 * np.pi * 1760 * t) * _env(n, .002, .08))[:n - int(SR * .09)]
    return _norm(x, .35)

def sting(dur=2.5):
    n = int(SR * dur); t = np.arange(n) / SR
    cl = sum(np.sin(2 * np.pi * f * t + rng.random() * 6) for f in [311, 329.6, 349.2, 466, 622, 659])
    hit = _lp(rng.standard_normal(n), 3000) * _env(n, .001, .15) * 2
    sub = np.sin(2 * np.pi * 40 * t) * _env(n, .001, .8) * 1.5
    return _norm((cl / 6) * _env(n, .005, .9) + hit + sub, .95)

def riser(dur=3.0):
    n = int(SR * dur); t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    x = np.zeros(n)
    for i in range(0, n, 2400):   # sweeping band
        j = min(n, i + 2400); fc = 300 + 5000 * (i / n) ** 2
        x[i:j] = _bp(noise[i:j], fc, fc * 1.6, 2)
    tone = np.sin(2 * np.pi * np.cumsum(200 + 600 * (t / dur) ** 2) / SR) * .3
    return _norm((x + tone) * (t / dur) ** 2, .6)

def heartbeat(bpm=70, dur=6):
    n = int(SR * dur); out = np.zeros(n); beat = int(SR * 60 / bpm)
    k = int(SR * .25); tk = np.arange(k) / SR
    lub = np.sin(2 * np.pi * 50 * tk) * np.exp(-tk * 25)
    for s in range(0, n - k - int(SR * .2), beat):
        out[s:s + k] += lub; out[s + int(SR * .18):s + int(SR * .18) + k] += lub * .6
    return _norm(out, .6)

def rain(dur):
    n = int(SR * dur)
    x = _bp(rng.standard_normal(n), 800, 7000) * .5
    drops = (rng.random(n) < .0015) * rng.standard_normal(n) * 4
    x += _hp(drops, 2500)
    return _norm(x, .12)

def drone(dur):
    n = int(SR * dur); t = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * f * t) for f in [43.65, 44.2, 65.4, 87.3, 92.5])
    x *= .6 + .4 * np.sin(2 * np.pi * .07 * t)
    x += _lp(rng.standard_normal(n), 120) * 3
    return _norm(x, .22)

def lullaby_hum(dur=5.0):
    """Wordless detuned music-box-ish hum, played 'through the monitor'."""
    notes = [659, 587, 523, 587, 659, 659, 659, 0, 587, 587, 587, 0, 659, 784, 784]
    n = int(SR * dur); out = np.zeros(n); step = n // len(notes)
    for i, f in enumerate(notes):
        if not f: continue
        tk = np.arange(step) / SR
        v = np.sin(2 * np.pi * f * .5 * tk * (1 + .003 * np.sin(2 * np.pi * 5 * tk)))
        out[i * step:(i + 1) * step] += v * np.sin(np.pi * tk / tk[-1])
    out = _bp(out, 300, 3000) + _hp(rng.standard_normal(n), 3000) * .03   # monitor hiss
    return _norm(out, .3)

def _norm(x, peak):
    m = np.max(np.abs(x)) or 1
    return (x / m * peak).astype(np.float32)

LIB = dict(thud=thud, creak=creak, footstep=footstep, ping=ping, sting=sting,
           riser=riser, heartbeat=heartbeat, lullaby=lullaby_hum)
