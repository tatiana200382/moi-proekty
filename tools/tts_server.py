# -*- coding: utf-8 -*-
"""Локальный сервер озвучки: Silero ru, порт 8765. POST /say?text=... -> audio/wav."""
import io, wave, numpy as np, torch, silero
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models', model='silero_tts',
                          language='ru', speaker='v4_ru', trust_repo=True, verbose=False)

def soften(x: np.ndarray, sr: int = 48000) -> np.ndarray:
    """Мягче: убрать резкие верха, чуть замедлить, выровнять громкость."""
    # 1) низкочастотный фильтр (убирает «металл» на верхних частотах)
    fc = 6500.0
    rc = 1.0 / (2 * np.pi * fc)
    dt = 1.0 / sr
    alpha = dt / (rc + dt)
    y = np.empty_like(x)
    prev = x[0]
    for i, v in enumerate(x):
        prev = prev + alpha * (v - prev)
        y[i] = prev
    # 2) чуть медленнее и спокойнее
    n = int(len(y) * 1.02)
    y = np.interp(np.linspace(0, len(y) - 1, n), np.arange(len(y)), y)
    # 3) громкость и плавные края
    peak = float(np.max(np.abs(y))) or 1.0
    y = y / peak * 0.92
    fade = int(0.012 * sr)
    if len(y) > 2 * fade:
        y[:fade] *= np.linspace(0, 1, fade)
        y[-fade:] *= np.linspace(1, 0, fade)
    return y


def synth(text: str, speaker: str = 'baya') -> bytes:
    audio = model.apply_tts(text=text, speaker=speaker, sample_rate=48000)
    a = (soften(audio.numpy()) * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(48000)
        w.writeframes(a.tobytes())
    return buf.getvalue()

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        u = urlparse(self.path)
        if u.path != '/say':
            self.send_response(404); self.end_headers(); return
        q = parse_qs(u.query)
        text = (q.get('text') or [''])[0]
        speaker = (q.get('speaker') or ['baya'])[0]
        if not text:
            self.send_response(400); self.end_headers(); return
        data = synth(text, speaker)
        self.send_response(200)
        self.send_header('Content-Type', 'audio/wav')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)
    def log_message(self, *a):
        pass

if __name__ == '__main__':
    HTTPServer(('127.0.0.1', 8765), H).serve_forever()
