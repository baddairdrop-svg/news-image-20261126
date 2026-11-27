# Story data for news-image-20261126, rebuild v3 (pictorial).
#
# Selection: the 33 strongest stories from the 78-story verified
# pool for Thursday 26 November 2026 (every story happened or was
# first reported that day, verified against its named source in
# the research database). No story outside that pool is used.
# Kyiv: night of 25-26 Nov, 26 Nov Kyiv local time. Bogor mine:
# 23 Nov collapse, search resumed and toll reported 26 Nov.
# All times UTC.
#
# Regions are split finely (11): 0 North America, 1 South
# America, 2 West Europe, 3 East Europe, 4 Middle East,
# 5 Africa, 6 South Asia, 7 Southeast Asia, 8 East Asia,
# 9 Oceania, 10 Global.
#
# Story tuple: (kind, art, place, category, headline, summary,
#               source, region, field, confidence, chip, pin)
# kind: "hero" | "grid" | "also"; pin: (lon, lat) or None.

STORIES = [
    ("hero", "summit", "BRUSSELS", "DIPLOMACY",
     "EU leaders end summit with no budget deal",
     "No agreement on the €1.582tn budget or €45bn Ukraine loan; "
     "decision pushed to 17–18 Dec.",
     "REUTERS · AP", 2, "Diplomacy", "REPORTED", "NO DEAL",
     (4.4, 50.8)),
    ("hero", "skyline", "GAZA", "WAR",
     "Israeli strikes kill at least nine in Gaza",
     "Overnight strikes hit Deir Al-Balah, Gaza City and Bureij; "
     "a deputy minister among the dead.",
     "REUTERS", 4, "War", "REPORTED", "AT LEAST 9 DEAD",
     (34.4, 31.4)),
    ("hero", "rates", "SEOUL", "ECONOMY",
     "Bank of Korea raises rate to 3.25%",
     "Third hike this year, highest since Nov 2024; 2026 growth "
     "forecast raised to 3.9%.",
     "REUTERS · BOK", 8, "Economy", "OFFICIAL", "+25 BP",
     (127.0, 37.5)),

    ("grid", "bank", "BRUSSELS", "ECONOMY",
     "De Cos picked as next ECB president",
     "Ex-Bank of Spain chief succeeds Lagarde, Feb 2027.",
     "REUTERS", 2, "Economy", "OFFICIAL", "FEB 2027", (4.4, 50.8)),
    ("grid", "train", "LONDON", "LABOUR",
     "Tube drivers begin eight 24-hour strikes",
     "Walkout from 12:00 UTC; Circle, Piccadilly shut.",
     "REUTERS · TFL", 2, "Labour", "REPORTED", "12:00 UTC",
     (-0.12, 51.5)),
    ("grid", "chess", "GENEVA", "SPORT",
     "Chess Game 3 drawn after 60 moves",
     "Sindarov, Gukesh level 1.5–1.5; third draw.",
     "FIDE · CHESS.COM", 2, "Sport", "OFFICIAL", "1.5–1.5",
     (6.1, 46.2)),
    ("grid", "flame", "KHARKIV", "WAR",
     "Russian drone kills two in apartment block",
     "Shahed hit 15th floor ~03:00 UTC; 3 injured.",
     "KYIV POST · DSNS", 3, "War", "REPORTED", "03:00 UTC",
     (36.2, 50.0)),
    ("grid", "shield", "KUWAIT", "WAR",
     "Two Italian technicians killed in drone attack",
     "Italy, Kuwait blame Iran; Tehran denies it.",
     "REUTERS", 4, "War", "REPORTED", "IRAN DENIES", (47.9, 29.4)),
    ("grid", "drop", "JAZAN", "ENERGY",
     "Aramco refinery hit, one worker killed",
     "Projectile hit 400,000 bpd plant; ops halted.",
     "REUTERS", 4, "Energy", "REPORTED", "400K BPD", (42.6, 16.9)),
    ("grid", "ball", "DETROIT", "SPORT",
     "Bears beat Lions 39–35 on Thanksgiving",
     "Williams to Odunze with 3 seconds left.",
     "AP", 0, "Sport", "OFFICIAL", "3 SEC LEFT", (-83.0, 42.3)),
    ("grid", "scroll", "NEW DELHI", "POLITICS",
     "India marks 77th Constitution Day",
     "Murmu at Supreme Court; 30,000+ in Mysuru.",
     "PIB", 6, "Politics", "OFFICIAL", "77TH", (77.2, 28.6)),
    ("grid", "rocket", "ORBIT", "SPACE",
     "Progress MS-36 docks with the space station",
     "Docked at Rassvet 12:08 UTC; 2,427 kg cargo.",
     "ROSCOSMOS · INTERFAX", 10, "Space", "OFFICIAL", "12:08 UTC",
     None),
    ("grid", "chart", "TOKYO", "MARKETS",
     "Asia shares rebound at Thursday close",
     "Nikkei +0.9%, KOSPI +0.3%; US markets shut.",
     "AP", 8, "Markets", "REPORTED", "+0.9%", None),
    ("grid", "missile", "KYIV", "WAR",
     "Ballistic attack injures seven in Kyiv",
     "Seven injured, two seriously, overnight.",
     "KMVA · KYIV POST", 3, "War", "REPORTED", "7 INJURED",
     (30.5, 50.4)),
    ("grid", "virus", "KINSHASA", "HEALTH",
     "Ebola cases pass 12,000 in DR Congo",
     "12,021 cases, 5,904 deaths; Bunia posts empty.",
     "PANA · WHO", 5, "Health", "REPORTED", "12,021 CASES",
     (22.0, -3.0)),

    ("also", "", "Xichang", "",
     "Long March 2D launches Yaogan-49 satellites", "", "",
     8, "Space", "REPORTED", "", (102.0, 27.9)),
    ("also", "", "Mumbai", "",
     "city marks 18 years since 26/11 attacks", "", "",
     6, "Society", "REPORTED", "", (72.9, 19.1)),
    ("also", "", "Beijing", "",
     "defence ministry tells Japan to stop stirring trouble", "", "",
     8, "Diplomacy", "REPORTED", "", (116.4, 39.9)),
    ("also", "", "Beijing", "",
     "Asian economies hit back at new US tariff plans", "", "",
     8, "Trade", "REPORTED", "", (116.4, 39.9)),
    ("also", "", "Bogor", "",
     "search resumes for 13 trapped miners, 13 dead", "", "",
     7, "Disaster", "REPORTED", "", (106.8, -6.6)),
    ("also", "", "Port Vila", "",
     "M4.7 quake strikes near Vanuatu capital", "", "",
     9, "Disaster", "REPORTED", "", (168.3, -17.7)),
    ("also", "", "Auckland", "",
     "Fisher & Paykel lifts profit guidance 37%", "", "",
     9, "Business", "REPORTED", "", (174.8, -36.8)),
    ("also", "", "Canberra", "",
     "private capex jumps 12.2% on data centres", "", "",
     9, "Economy", "REPORTED", "", (149.1, -35.3)),
    ("also", "", "Ryazan", "",
     "Ukrainian drones hit oil refinery, one injured", "", "",
     3, "War", "REPORTED", "", (39.7, 54.6)),
    ("also", "", "Berlin", "",
     "trial opens of woman accused of spying for Russia", "", "",
     2, "Justice", "REPORTED", "", (13.4, 52.5)),
    ("also", "", "Odesa", "",
     "Ukraine says Russia hit two grain ships", "", "",
     3, "War", "CLAIM", "", (30.7, 46.5)),
    ("also", "", "East Coast", "",
     "Thanksgiving storm cuts power, cancels flights", "", "",
     0, "Disaster", "REPORTED", "", (-75.0, 38.5)),
    ("also", "", "West Palm Beach", "",
     "Trump demands probe of GDP figures", "", "",
     0, "Economy", "CLAIM", "", (-80.0, 26.8)),
    ("also", "", "Buenos Aires", "",
     "Congress backs central-bank charter reform", "", "",
     1, "Economy", "REPORTED", "", (-58.4, -34.6)),
    ("also", "", "Ghubeish", "",
     "drone strike on truck kills at least 11", "", "",
     5, "War", "REPORTED", "", (28.5, 11.5)),
    ("also", "", "Geneva", "",
     "UNCTAD: seaborne trade 12.3bn tons in 2025", "", "",
     10, "Trade", "REPORTED", "", (6.1, 46.2)),
    ("also", "", "Global", "",
     "WHO backs new oral gonorrhoea drug", "", "",
     10, "Health", "REPORTED", "", None),
    ("also", "", "Port-au-Prince", "",
     "WHO chief brings $1m hospital equipment", "", "",
     0, "Health", "REPORTED", "", (-72.3, 18.5)),
]

REGION_NAMES = ["N AMERICA", "S AMERICA", "W EUROPE", "E EUROPE",
                "MID EAST", "AFRICA", "S ASIA", "SE ASIA", "E ASIA",
                "OCEANIA", "GLOBAL"]
REGION_SHORT = ["N.AM", "S.AM", "W.EU", "E.EU", "M.EAST", "AFRICA",
                "S.ASIA", "SE.ASIA", "E.ASIA", "OCEANIA", "GLOBAL"]

HEROES = [(s[1], s[2], s[3], s[4], s[5], s[6], s[10], 0.0)
          for s in STORIES if s[0] == "hero"]
HERO_CONF = [s[9] for s in STORIES if s[0] == "hero"]
GRID = [(s[1], s[2], s[3], s[4], s[5], s[6])
        for s in STORIES if s[0] == "grid"]
GRID_CONF = [s[9] for s in STORIES if s[0] == "grid"]
GRID_BANNER = [s[10] for s in STORIES if s[0] == "grid"]
ALSO = [(s[2], s[4]) for s in STORIES if s[0] == "also"]
REGIONS = [s[7] for s in STORIES]
FIELDS = [s[8] for s in STORIES]
PINS = [(i + 1, s[11][0], s[11][1], 0, 0)
        for i, s in enumerate(STORIES) if s[11] is not None]
ALSO_CLAIM = {i + 1 for i, s in enumerate(STORIES)
              if s[0] == "also" and s[9] == "CLAIM"}
NO_PIN = [i + 1 for i, s in enumerate(STORIES) if s[11] is None]
