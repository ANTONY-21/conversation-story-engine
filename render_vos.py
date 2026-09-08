#!/usr/bin/env python3
"""Render AK-voice VOs for inflation_convo via IndexTTS2 (wan2gp jkbr7vf3f3c1qz).
Proven contract (from cardboard_full/render_vos.py): key 'prompt', media.audio_guide =
raw b64 NO data: URI, spec-wrapped payload, response 'media_b64'.
Vikram lines get pitch shift -6% in post (asetrate+atempo) for character separation.
Skips existing wavs; caller scales wan2gp 0->1 before and 1->0 after."""
import json, os, base64, subprocess, sys

BEATS = '/opt/kinocut-work/inflation_convo/beats.json'
VO_DIR = '/opt/kinocut-work/inflation_convo/voice'
REF = '/root/ak-ai-company/news-engine/assets/ak_voice_ref_v6.wav'
EP = 'jkbr7vf3f3c1qz'
os.makedirs(VO_DIR, exist_ok=True)

def env_key(name):
    for line in open('/opt/hermes/.env'):
        if line.startswith(name + '='):
            return line.strip().split('=', 1)[1].strip().strip('"').strip("'")
    raise SystemExit(name + ' not in /opt/hermes/.env')

POLLER = r'''
import sys, json, base64, time, urllib.request
job, key, out = sys.argv[1], sys.argv[2], sys.argv[3]
for i in range(90):
    time.sleep(5)
    req = urllib.request.Request(
        "https://api.runpod.ai/v2/%s/status/%s" % (EP, job),
        headers={"Authorization": "Bearer " + key})
    try:
        d = json.load(urllib.request.urlopen(req, timeout=30))
    except Exception as e:
        print("poll err", e); continue
    s = d.get("status")
    if s == "COMPLETED":
        o = d.get("output") or {}
        mb = o.get("media_b64") or d.get("media_b64")
        open(out, "wb").write(base64.b64decode(mb))
        print("SAVED")
        sys.exit(0)
    if s in ("FAILED", "CANCELLED"):
        print("FAILED", json.dumps(d)[:400]); sys.exit(1)
print("TIMEOUT"); sys.exit(1)
'''
open('/tmp/vo_poller.py', 'w').write('EP = "%s"\n' % EP + POLLER)

def render_vo(text, out_path):
    audio_b64 = base64.b64encode(open(REF, 'rb').read()).decode()
    spec = {"model_type": "index_tts2", "prompt": text,
            "temperature": 0.9, "top_p": 0.95,
            "media": {"audio_guide": audio_b64}}
    payload = json.dumps({"input": {"spec": spec}})
    with open('/tmp/vo_payload.json', 'w') as f:
        f.write(payload)  # ARG_MAX trap: never inline in curl
    key = env_key('RUNPOD_API_KEY')
    r = subprocess.run(['curl', '-s', '--http1.1', '-X', 'POST',
        'https://api.runpod.ai/v2/%s/run' % EP,
        '-H', 'Authorization: Bearer ' + key,
        '-H', 'Content-Type: application/json',
        '-d', '@/tmp/vo_payload.json'], capture_output=True, text=True, timeout=120)
    job = json.loads(r.stdout).get('id')
    if not job:
        print('run failed:', r.stdout[:200]); return False
    print('job', job, flush=True)
    p = subprocess.run(['python3', '/tmp/vo_poller.py', job, key, out_path],
                       capture_output=True, text=True, timeout=560)
    if 'SAVED' not in p.stdout:
        print('poll:', p.stdout[-200:], p.stderr[-200:]); return False
    return True

def main():
    b = json.load(open(BEATS))
    ok = 0
    for bt in b['beats']:
        out = '%s/b%d.wav' % (VO_DIR, bt['id'])
        if os.path.exists(out) and os.path.getsize(out) > 10000:
            print('skip b%d (exists)' % bt['id']); ok += 1; continue
        print('b%d %s: %s' % (bt['id'], bt['speaker'], bt['vo'][:50]), flush=True)
        if render_vo(bt['vo'], out):
            ok += 1
        else:
            print('FAILED b%d' % bt['id'])
    print('%d/%d VOs ready' % (ok, len(b['beats'])))
    sys.exit(0 if ok == len(b['beats']) else 1)

if __name__ == '__main__':
    main()
