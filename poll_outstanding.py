#!/usr/bin/env python3
"""Poll outstanding VO jobs until done, saving wavs. Then report which beats remain."""
import json, os, subprocess, sys, time

EP = 'jkbr7vf3f3c1qz'
VO_DIR = '/opt/kinocut-work/inflation_convo/voice'
key = None
for line in open('/opt/hermes/.env'):
    if line.startswith('RUNPOD_API_KEY='):
        key = line.strip().split('=',1)[1].strip().strip('"').strip("'")

PENDING = json.load(open('/tmp/pending_jobs.json'))  # {job_id: wav_out_path}

deadline = time.time() + int(sys.argv[1] if len(sys.argv) > 1 else 1800)
remaining = dict(PENDING)
while remaining and time.time() < deadline:
    for job, out in list(remaining.items()):
        try:
            r = subprocess.run(['curl','-s','--http1.1',
                'https://api.runpod.ai/v2/%s/status/%s' % (EP, job),
                '-H','Authorization: Bearer '+key],
                capture_output=True, text=True, timeout=60)
            d = json.loads(r.stdout)
        except Exception as e:
            print('poll err', job, e, flush=True); continue
        s = d.get('status')
        if s == 'COMPLETED':
            o = d.get('output') or {}
            mb = o.get('media_b64') or d.get('media_b64')
            if mb:
                open(out,'wb').write(__import__('base64').b64decode(mb))
                print('SAVED', out, os.path.getsize(out), flush=True)
            else:
                print('COMPLETED but no media:', json.dumps(d)[:300], flush=True)
            del remaining[job]
        elif s in ('FAILED','CANCELLED'):
            print('FAILED', job, json.dumps(d)[:300], flush=True)
            del remaining[job]
    if remaining:
        time.sleep(10)

print('remaining after poll:', list(remaining.keys()), flush=True)
