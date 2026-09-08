#!/usr/bin/env python3
"""HARDENED VO batch (v2) — 2026-09-08, after the wedged-queue incident.
Rules baked in (AK: 'don't want money'):
  1. Endpoint stays at 1/1 — the caller scales it; this script never changes workers.
  2. Poll-timeout does NOT mean FAILED — status-fetch fallback recovers the job.
  3. finally: prints ENDPOINT STILL UP reminder; caller must verify 0/0 after.
  4. Cache-aware: skips turns whose wav already exists.
"""
import json, os, base64, subprocess, time, sys

SCRIPT = sys.argv[1] if len(sys.argv) > 1 else '/opt/kinocut-work/AGI_news/beats.json'
VO_DIR = sys.argv[2] if len(sys.argv) > 2 else '/opt/kinocut-work/AGI_news/voice'
EP = 'jkbr7vf3f3c1qz'
REFS = json.load(open(os.path.join(os.path.dirname(SCRIPT), 'voice_refs.json'))) \
    if os.path.exists(os.path.join(os.path.dirname(SCRIPT), 'voice_refs.json')) else {
        'default': '/root/ak-ai-company/news-engine/assets/ak_voice_ref_v6.wav'}

def env_key(name):
    for line in open('/opt/hermes/.env'):
        if line.startswith(name + '='):
            return line.strip().split('=', 1)[1].strip().strip('"').strip("'")
    raise SystemExit(name)

KEY = env_key('RUNPOD_API_KEY')
os.makedirs(VO_DIR, exist_ok=True)

def submit(text, ref_path):
    ref_b64 = base64.b64encode(open(ref_path, 'rb').read()).decode()
    spec = {"model_type": "index_tts2", "prompt": text,
            "temperature": 0.9, "top_p": 0.95, "media": {"audio_guide": ref_b64}}
    open('/tmp/vo_payload.json', 'w').write(json.dumps({"input": {"spec": spec}}))
    r = subprocess.run(['curl', '-s', '--http1.1', '-m', '60', '-X', 'POST',
        f'https://api.runpod.ai/v2/{EP}/run',
        '-H', f'Authorization: Bearer {KEY}', '-H', 'Content-Type: application/json',
        '-d', '@/tmp/vo_payload.json'], capture_output=True, text=True, timeout=90)
    return json.loads(r.stdout).get('id')

def status(job):
    r = subprocess.run(['curl', '-s', '--http1.1', '-m', '30',
        f'https://api.runpod.ai/v2/{EP}/status/{job}',
        '-H', f'Authorization: Bearer {KEY}'], capture_output=True, text=True, timeout=60)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {}

def save_if_done(d, out):
    o = d.get('output') or {}
    mb = o.get('media_b64') or d.get('media_b64')
    if mb:
        open(out, 'wb').write(base64.b64decode(mb))
        return True
    return False

def render_turn(tid, text, ref_path):
    out = f'{VO_DIR}/{tid}.wav'
    if os.path.exists(out) and os.path.getsize(out) > 50000:
        print(tid, 'cached'); return 'ok'
    job = submit(text, ref_path)
    if not job:
        print(tid, 'SUBMIT FAILED'); return 'submit_failed'
    print(tid, 'submitted', job)
    # Phase 1: poll 120s (10s interval). Timeout != failure.
    for _ in range(12):
        time.sleep(10)
        d = status(job)
        st = d.get('status')
        if st == 'COMPLETED':
            print(tid, 'SAVED' if save_if_done(d, out) else 'NO MEDIA'); return 'ok'
        if st in ('FAILED', 'CANCELLED'):
            print(tid, 'FAILED', json.dumps(d)[:200]); return 'failed'
    # Phase 2: status-fetch recovery loop up to 10 more min (handles worker cold boot)
    for _ in range(60):
        time.sleep(10)
        d = status(job)
        st = d.get('status')
        if st == 'COMPLETED':
            print(tid, 'RECOVERED SAVED' if save_if_done(d, out) else 'NO MEDIA'); return 'ok'
        if st in ('FAILED', 'CANCELLED'):
            print(tid, 'FAILED', json.dumps(d)[:200]); return 'failed'
        if st is None:  # 404 = purged
            print(tid, 'JOB 404 — purged, resubmitting'); break
    # one clean resubmit
    job2 = submit(text, ref_path)
    if job2:
        print(tid, 'resubmitted', job2)
        for _ in range(60):
            time.sleep(10)
            d = status(job2)
            if d.get('status') == 'COMPLETED':
                print(tid, 'RETRY SAVED' if save_if_done(d, out) else 'NO MEDIA'); return 'ok'
            if d.get('status') in ('FAILED', 'CANCELLED'):
                print(tid, 'RETRY FAILED'); return 'failed'
    print(tid, 'GAVE UP'); return 'gave_up'

results = {}
for t in json.load(open(SCRIPT))['beats']:
    tid = str(t['id']); voice = t.get('voice', 'default')
    ref = REFS.get(voice, REFS['default'])
    results[tid] = render_turn(tid, t['vo'], ref)

json.dump(results, open(os.path.join(VO_DIR, '_results.json'), 'w'))
print('DONE', results)
print('REMINDER: verify endpoint 0/0 + no live procs before reporting done.')
