# The World in One Day — 26 November 2026

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/baddairdrop-svg/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/baddairdrop-svg/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

A program that draws one image summing up the world's news of
Thursday 26 November 2026, for the make.fun bounty
[news-image-20261126](https://make.fun/bounty/news-image-20261126),
entered by **@badd-airdrop2**.

## The image

"THE WORLD IN ONE DAY": a 1024x1024 newspaper front page with a
masthead, a segmented region-count strip, a five-number stat strip,
three hero cards with drawn scenes and WHY IT MATTERS lines, a
ten-card grid numbered 4-13, a dotted world map with numbered pins,
a 65-story ALSO list (stories 14-78), and a red DATE CHECK box.

Every story on the page happened or was first reported on Thursday
26 November 2026, as the named outlets reported it. Each story was
verified independently: event date and first publication date
checked separately against the original source. Big stories from
other days (the Macy's postponement decision, the Sudan Blue Nile
strikes, the Chen Jining probe, Real Madrid 5-1 PSV, the US jobless
claims release, the Hera Dimorphos images, the India-Nepal package,
the Swiss tourist elephant attack) are listed in the DATE CHECK box
with their real dates, not presented as the day's news. Two honest
framings are printed on the page: Kyiv (night of 25-26 Nov, 26 Nov
Kyiv time) and the Bogor mine (23 Nov collapse, search resumed
26 Nov).

1. **EU summit ends without a deal** — no agreement on the
   €1.582tn budget or the €45bn Ukraine loan. (Reuters/AP)
2. **Strikes kill nine in Gaza** — overnight strikes hit Deir
   Al-Balah, Gaza City and Bureij, medics said. (Reuters)
3. **Korea raises rates** — Bank of Korea lifts its base rate
   25bp to 3.25%, the third hike this year. (Reuters/BOK)

No quotes, numbers or faces are invented, and no real person is
drawn. Map and drawings are original vector art.

## How it runs

`main.py` is pure Python 3 standard library only (no network, no
fonts on disk, no randomness, no clock). Type is set from DejaVu
glyph bitmaps carried in `glyphs.py` (rasterised at build time by
`gen_glyphs.py`, which is not needed at runtime). The page is drawn
on a 2x supersampled canvas with a hand-written PNG encoder and
written to `/output/entry.png`. Running it twice writes the same
bytes.

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```
