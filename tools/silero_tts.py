import sys, wave, numpy as np, torch, silero

text = sys.argv[1]
out = sys.argv[2]
speaker = sys.argv[3] if len(sys.argv) > 3 else "baya"

model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models', model='silero_tts', language='ru', speaker='v4_ru', trust_repo=True, verbose=False)
audio = model.apply_tts(text=text, speaker=speaker, sample_rate=48000)
a = (audio.numpy() * 32767).astype(np.int16)
with wave.open(out, 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(48000)
    w.writeframes(a.tobytes())
print('ok', out)
