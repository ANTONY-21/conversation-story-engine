#!/usr/bin/env python3
"""Build the XiaoheiConvo Remotion entry: scene plan from REAL VO durations (ffprobe),
beats.json as single source of truth, then render via npx remotion."""
import json, subprocess, os, sys

PROJ = '/opt/kinocut-work/inflation_convo'
REM = '/opt/remotion-app'
FPS = 30

BUBBLES = {
  1: ["Ten rupees in 2020.", "Now? ₹14."],
  2: ["That's inflation.", "Your rupee got weaker."],
  3: ["CPI: 4.45%", "Food: even more — 5.52%"],
  4: ["72 ÷ 4.45", "Prices double in ~16 years"],
  5: ["My savings pay 3%?", "That's LESS than inflation!"],
  6: ["Nifty wobbles — but", "over years, equity wins"],
  7: ["Money in the bank", "is slowly melting..."],
  8: ["Put it to work,", "or inflation eats it."],
}
VISUALS = {
  1: {"kind": "price_tag"},
  2: {"kind": "weak_coin"},
  3: {"kind": "stat_cards"},
  4: {"kind": "rule72"},
  5: {"kind": "real_rate"},
  6: {"kind": "ticker"},
  7: {"kind": "melting"},
  8: {"kind": "cta"},
}

def vo_durations():
    durs = {}
    for f in sorted(os.listdir(f'{PROJ}/voice')):
        if f.endswith('.wav'):
            r = subprocess.run(['ffprobe','-v','error','-show_entries','format=duration',
                '-of','csv=p=0', f'{PROJ}/voice/{f}'], capture_output=True, text=True)
            try: durs[f.replace('.wav','')] = float(r.stdout.strip())
            except ValueError: pass
    return durs

def main():
    b = json.load(open(f'{PROJ}/beats.json'))
    durs = vo_durations()
    missing = [bt['id'] for bt in b['beats'] if f"b{bt['id']}" not in durs]
    if missing:
        print('MISSING VO for beats:', missing); sys.exit(1)
    beats = []
    acc = 0
    for bt in b['beats']:
        bid = f"b{bt['id']}"
        secs = round(durs[bid] + 0.4, 2)
        frames = int(secs * FPS)
        beats.append({
            'id': bt['id'], 'start': acc, 'frames': frames, 'scene': bt['scene'],
            'speaker': bt['speaker'], 'bubble': BUBBLES[bt['id']], 'visual': VISUALS[bt['id']],
        })
        acc += frames
    size = {'w': 704, 'h': 1280, 'fps': FPS}
    entry = f"""import {{ registerRoot, Composition }} from 'remotion';
import React from 'react';
import {{ XiaoheiConvo }} from './XiaoheiConvo';

const CONVO = {json.dumps({'beats': beats, 'size': size}, indent=1)};

const Wrapper: React.FC = () => {{
  (globalThis as any).__CONVO__ = CONVO;
  return <XiaoheiConvo />;
}};

export const ConvoRoot = () => (
  <Composition id="XiaoheiConvo" component={{Wrapper}}
    durationInFrames={{CONVO.beats.reduce((a, b) => a + b.frames, 0)}}
    fps={{30}} width={{704}} height={{1280}} />
);

registerRoot(ConvoRoot);
"""
    with open(f'{REM}/src/convo_entry.tsx', 'w') as f:
        f.write(entry)
    total = acc
    json.dump(beats, open(f'{PROJ}/scene_plan.json', 'w'), indent=1)
    print(f'scenes: {len(beats)}, total frames: {total} ({total/FPS:.1f}s)')
    for bt in beats:
        print(f"  b{bt['id']} {bt['scene']} {bt['speaker']}: {bt['frames']}f")

if __name__ == '__main__':
    main()
