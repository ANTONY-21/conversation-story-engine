# The ₹10 Chai That Costs ₹14 — inflation conversation story

FORMAT: conversation/dialogue between two Xiaohei characters (speech bubbles, name tags,
speaker-focused camera). NOT the cardboard desk template. 5 distinct hand-drawn backgrounds.

Derived from: ian-xiaohei-illustrations (helloianneo, 11.2k★, MIT — Xiaohei character IP:
solid black body, white dot eyes, thin limbs, deadpan) + dialogue architecture from
AIComicBuilder (LingyiChen-AI, 1.85k★, Apache-2.0: script → characters → shots → Dialogue).

## Characters
- RAVI — Xiaohei, red scarf accent. Voice: AK native (IndexTTS2 ref ak_voice_ref_v6).
- VIKRAM — Xiaohei, flat cap accent, slightly wider stance. Voice: AK pitch-shifted −6% (post ffmpeg).

## Sources (number-lock, verified 2026-09-08)
- India CPI July 2026: 4.45% (from 4.38% June) — tradingeconomics.com/india/inflation-cpi
- Food inflation July 2026: 5.52% provisional — MoSPI (mospi.gov.in CFPI)
- RBI: CPI stayed below 4% target 16 consecutive months before June 2026 — RBI press release prid 63403
- USD/INR 94.82, Nifty high 24,774 → 23,653 now (−4.5%) — yfinance INR=X / ^NSEI 6mo, 2026-09-08

## Math lock (script verifies every derived number)
- Chai ₹10 (2020) → ₹14 (2026): food inflation 5.52%/yr → 10 × 1.0552^6 = ₹13.82 ≈ ₹14 (+40% displayed, actual +38.2% ≈ +40%)
- Rule of 72 at 4.45%: 72 / 4.45 = 16.2 → "about 16 years"
- Savings 3.00% vs CPI 4.45% → real rate −1.45%/yr
- Nifty: 23,653 / 24,774 − 1 = −4.52% → "down 4.5% from the high"

## Beats (8 dialogue turns, 5 backgrounds)
| id | bg | speaker | line (VO) | bubble visual |
|----|----|---------|-----------|---------------|
| b1 | tea stall street | RAVI | "Ten rupees. That's what my chai cost in twenty-twenty. Look at it now." | ₹10 → ₹14 price tag card |
| b2 | tea stall street | VIKRAM | "That's inflation, Ravi. Prices didn't just rise — your rupee got weaker." | ₹1 shrinking-coin icon |
| b3 | city park | VIKRAM | "Official inflation: four point four five percent. Food? Even more — five point five." | 2 stat cards CPI 4.45% / FOOD 5.52% |
| b4 | city park | VIKRAM | "Rule of seventy-two: seventy-two divided by four point four five — prices double in about sixteen years." | 72 ÷ 4.45 ≈ 16 YEARS |
| b5 | home desk room | RAVI | "Wait. My savings account pays three percent. That's LESS than inflation?!" | 3.00% vs 4.45% → −1.45% |
| b6 | trading floor | VIKRAM | "That's why we invest. The Nifty wobbles — down four and a half from its high — but over years, equity outruns inflation." | NIFTY 24,774 → 23,653 (−4.5%) ticker |
| b7 | evening road | RAVI | "So money just sitting in the bank is slowly... melting." | ice-cube ₹ melting icon |
| b8 | evening road | VIKRAM | "Put it to work — or inflation eats it. Follow for the next story." | CTA card |

Camera: speaker centered + slight push-in while talking; listener in soft focus at frame
edge reacting (nod = agreeing, tilt = confused). Hard cut between beats. Text pop-in
line-by-line per AK's kinetic-typography standard.
