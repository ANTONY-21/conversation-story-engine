# Conversation Story Engine (v1.0)

Two-character dialogue-format finance stories — speech bubbles, name tags, listener reactions, multiple distinct backgrounds. Built 2026-09-08.

**First video:** "The ₹10 Chai That Costs ₹14" — 49.5s, 8 dialogue turns, 5 backgrounds, QC 12-frame vision pass, number-lock 6/6 PASS.

## Architecture (sourced from AK's starred repos)

| Component | Source repo | Licence | Role |
|---|---|---|---|
| Dialogue scene grammar | AIComicBuilder (1.85k★) | Apache-2.0 | speech bubbles, name tags, listener reactions, beat structure |
| Character art style | ian-xiaohei-illustrations (11.2k★) | MIT | Xiaohei-style two-character poses/expressions |

Laws carried from the cardboard engine (mandatory in every story):
1. **NUMBER-LOCK** — every on-screen figure derived from beats.json data block, never re-typed. `number_lock.py` hard-gates pre-render.
2. **SCRIPT-DRIVEN VISUALS** — all text (kickers, bubbles, tags) flows from beats.json `on_screen`; zero hardcoded strings.
3. **PATTERN VARIETY** — rotate ≥2 levers per story: background set, character look, camera, beat order.
4. **QC GATE** — no render ships without frame-count QC + vision pass.
5. **RunPod discipline** — workers scaled to 0/0 immediately after every batch.

## Repo layout

```
beats.json          # story data: turns, on_screen text, numbers (single source of truth)
scene_plan.json     # frame plan: scene → background → duration
storyboard.md       # pipeline front door
number_lock.py      # pre-render number consistency gate
render_vos.py       # IndexTTS2 VO batch (wan2gp, media inside spec)
build_entry.py      # composition entry builder
assemble.py         # ffmpeg final assembly (vertical + horizontal)
poll_outstanding.py # recover unfinished RunPod jobs
scale_wangp.py      # endpoint scale up/down helper
voice/              # per-turn VO wavs
masters/            # final videos + thumbnail
```

## Reuse for the next story

1. New `beats.json` (topic from finance_topics.db; conversation-friendly topics: debt, fees, scams, habits — not just investing crashes)
2. Run `number_lock.py` → must PASS before anything renders
3. `render_vos.py` → VOs (cache-aware, reruns only missing turns)
4. `build_entry.py` → scene plan → `assemble.py` → both masters
5. QC vision pass on sampled frames → `upload.json` → scale endpoints 0/0

## Parked: photoreal MultiTalk path

`/opt/kinocut-work/convo1` holds a parallel prep: 10 IndexTTS2 VOs (two voices), 2 SDXL photoreal character refs (Priya/Vikram, credit-card-debt story), OmniVoice-designed female voice. Engine: MeiGen-AI/MultiTalk (2.99k★, Apache-2.0) via wan2gp `multitalk` — audio-driven multi-person conversational video, contract = avatar (image_start + image_refs + audio_guide).
