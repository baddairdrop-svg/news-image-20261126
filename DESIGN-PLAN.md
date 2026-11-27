# DESIGN PLAN — news-image-20261126 (build chat, 26 Nov 2026)

Status: skeleton plan written in this session before stories are final.
Final entry files (main.py, README.md, LICENSE, .makefun/owner.json) will be
written with the write tool in this same session after the closing sweep.
Nothing here is submitted. Submit only on Bedill's final word.

## Locked constraints (Bedill + kit)
- One image, 1024x1024 PNG/JPEG, <=1 MiB, deterministic bytes on two runs, no network.
- Program: main.py (Python 3.13, pure stdlib) in repo root, writes /output/entry.png.
- English exclusively in the image. All times UTC, printed "ALL TIMES UTC".
- Every story happened or was first reported on Thursday 26 November 2026
  (any time zone, converted to UTC). Doubtful = out. DATE CHECK lists near-misses with real dates.
- Target >40 verified stories; count is whatever verifies, never padded.
- Accuracy and readability above count. Independent audit before SIAP.
- Target file size <= ~400k bytes (tie-break = smaller bytes).

## Main template (Bedill sharpening, 07:10 WIB)
Rank 1 of 25 Nov (@hwang-steven, 50 stories, screenshot
~/workspace/user/media_library/image/53/537c499ce3af68f4487ed66d1469e9b1cc99e1af484cf687990339338322593e.jpg)
is the PRIMARY design template for 26 Nov - style may be very close, code and
facts are our own, written in this session. This is ATM, not a pixel copy.
Do not copy its date errors (Java gold pit 23 Nov, Dhaka wage, Gaza chief 24 Nov).

## Layout (ATM ranks 1-5, 24-25 Nov; v4.4 premium base)
1. Masthead: THE WORLD IN ONE DAY / "Thursday 26 November 2026" serif,
   italic teaser with 3 hero headlines, story/region/field counts (must sum).
   Title pattern (Bedill 07:11 WIB, same as rank 1 of 25 Nov):
   - Entry title for submit: "Thursday 26 November 2026: <N> stories..." with our real final count.
   - Masthead subline: "<N> STORIES - <R> REGIONS - <F> FIELDS - ALL FIRST REPORTED ON
     THURSDAY 26 NOVEMBER 2026" with N/R/F counted from final verified stories, never invented.
     Audit gate: only print ALL FIRST REPORTED if every final story passes the
     first-reported-on-26-Nov test; otherwise use the kit wording
     "happened or was first reported" so the claim stays defensible.
     Bedill filler rule (09:17 WIB): if verified 26 Nov stories are still short
     after the closing sweep, TRUE verified 25 Nov stories may be added as filler.
     Then the masthead must NOT claim ALL FIRST REPORTED ON 26 NOV - use honest
     wording (e.g. 24 HOURS window / clear marking), DATE CHECK stays honest,
     26 Nov stories keep hero/grid priority, and the final composition
     (N of 26 Nov, M of 25 Nov) is reported plainly to Bedill.
2. Segmented colour region bar (counts sum to total, never faked) + fields tag line.
3. Stat strip: exactly 5 hard numbers, each traceable to a numbered story on the page.
   No orphan stats, no trivia, no misdated numbers.
4. Heroes 1-3: flat-vector scene, PLACE - CATEGORY tag, headline, 2-line summary,
   confidence badge (OFFICIAL / REPORTED / CLAIM), red WHY IT MATTERS one-liner (<=10 words).
5. Grid 4-13: uniform cards, icon/scene, place-category, headline + summary, badge, big-number chip.
6. WHERE IT HAPPENED map: dots = story numbers, colour by region, pins ~25% bolder than
   crisp-badger (thumbnail), each pin verified on correct country/city, region counts beside map.
7. ALSO list (14 to total): strict one-liners, number + PLACE bold + headline, two columns,
   zero truncation, CLAIM badges only on contested items.
8. DATE CHECK red box: rule line + "Left out as earlier news:" + 4-8 near-misses with real dates.
9. Footer: badge legend (OFFICIAL = authority's own figure/act, REPORTED = press report,
   CLAIM = one side's account), named sources line, "Every drawing original."

## Typography / rendering (from v4.4, rebuilt fresh here)
- DejaVu Serif Bold masthead + headlines, DejaVu Sans body, glyph bitmaps embedded as data.
- 2x supersampled canvas, hand-written PNG encoder, pure stdlib, no fonts on disk at runtime.
- Design top third for 256px thumbnail first; test at 256px before SIAP. Zero tofu.

## Story slots (to fill after closing sweep, 27 Nov 07:00 WIB)
- Heroes: 3 most consequential verified 26 Nov stories across regions/fields.
- Grid: next 10 by consequence + visual distinctness.
- ALSO: remainder to >40 total, one-liners only.
- Early sweep (07:07 WIB) gave only 6 verified minor Oceania stories - none are hero material.
  See ~/workspace/makefun-hunter/04-projects/news-image-20261126-early-sweep.md
- Scheduled to verify in closing sweep: Bank of Korea decision, Berlin remarks 12:00 GMT,
  Brussels summit, India Constitution Day + Mumbai 26/11, chess Game 3, India A semi,
  Delhi HC hearing, US Thanksgiving reporting, PIA 26 Nov operations.

## Blockers right now
- Fresh kit news-image-20261126: awaiting Bedill go-ahead to download/unpack (asked 07:05 WIB).
- Stories: UTC day ends 27 Nov 07:00 WIB; final story set cannot lock before closing sweep.
- Repo: new public GitHub repo under baddairdrop-svg, created after opening (26 Nov 07:00 WIB),
  MIT licence, About website + topic makefun, README badges, .makefun/owner.json wallet
  HfASmMsq4dHhrV9iFRpETCyACVcFAGZX7JFg3Fs2zQ4i - to create at build stage, pattern of 24/25 Nov.
