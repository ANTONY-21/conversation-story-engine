#!/usr/bin/env python3
"""Scale wan2gp endpoint jkbr7vf3f3c1qz (name wan2gp-video-fixed). Usage: scale_wangp.py <min> <max>
GraphQL via curl --http1.1. saveEndpoint requires name field (learned 2026-09-08)."""
import json, subprocess, sys

min_w, max_w = sys.argv[1], sys.argv[2]
EP_ID = 'jkbr7vf3f3c1qz'
EP_NAME = 'wan2gp-video-fixed'
key = None
for line in open('/opt/hermes/.env'):
    if line.startswith('RUNPOD_API_KEY='):
        key = line.strip().split('=', 1)[1].strip().strip('"').strip("'")
if not key:
    raise SystemExit('RUNPOD_API_KEY not found')

mutation = {
    "query": 'mutation { saveEndpoint(input: {id: "%s", name: "%s", workersMin: %s, workersMax: %s}) '
             '{ id name workersMin workersMax } }' % (EP_ID, EP_NAME, min_w, max_w)
}
open('/tmp/wp_mutation.json', 'w').write(json.dumps(mutation))
r = subprocess.run(['curl', '-s', '--http1.1', '-X', 'POST',
                    'https://api.runpod.io/graphql',
                    '-H', 'Authorization: Bearer ' + key,
                    '-H', 'Content-Type: application/json',
                    '-d', '@/tmp/wp_mutation.json'],
                   capture_output=True, text=True, timeout=60)
print('scale ->', min_w, max_w, ':', r.stdout[:300])
