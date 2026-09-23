#!/usr/bin/env python3
# Semilla Cósmica - natal chart wheel sample (CARTA-05). Local render, real ephemeris.
import sys, math
import swisseph as swe
from PIL import Image, ImageDraw, ImageFont

def parse_args(argv):
    p = {'year': 2026, 'month': 8, 'day': 26, 'hour': 0.733,  # local UTC-3 (03:44 UTC)
         'place': 'La Plata, Argentina', 'lat': -34.9206, 'lon': -57.9545,
         'name': 'LIOR', 'sub': '26 de agosto de 2026 · 00:44 h · La Plata',
         'out': 'carta_wheel_sample.png'}
    for a in argv:
        k, v = a.split('=', 1)
        p[k] = v
    p['lat'] = float(p['lat']); p['lon'] = float(p['lon']); p['hour'] = float(p['hour'])
    for kk in ('year', 'month', 'day'):
        p[kk] = int(p[kk])
    return p

P = parse_args(sys.argv[1:])
JD = swe.julday(P['year'], P['month'], P['day'], P['hour'] + 3.0)

FDIR = '/usr/share/fonts/truetype/'
def font(name, size):
    try: return ImageFont.truetype(FDIR + name, size)
    except: return ImageFont.load_default()

F_GLYPH = font('dejavu/DejaVuSans.ttf', 80)
F_SIGN  = font('dejavu/DejaVuSans.ttf', 58)
F_DEG   = font('dejavu/DejaVuSans.ttf', 44)
F_HNUM  = font('dejavu/DejaVuSans.ttf', 40)
F_TITLE = font('liberation/LiberationSerif-Bold.ttf', 84)
F_SUB   = font('liberation/LiberationSerif-Regular.ttf', 42)
F_MICRO = font('liberation/LiberationSerif-Italic.ttf', 30)
F_BRAND = font('liberation/LiberationSerif-Italic.ttf', 36)

GOLD  = (197, 160, 89)
CREAM = (247, 241, 227)
FRAME = (24, 22, 30)
INK   = (52, 48, 40)
LINE  = (120, 112, 96)

W = H = 2000
CX = CY = W // 2

SIGNS = ['♈','♉','♊','♋','♌','♍','♎','♏','♐','♑','♒','♓']
PLANETS = [('Sol', swe.SUN, '☉'), ('Luna', swe.MOON, '☽'), ('Mercurio', swe.MERCURY, '☿'),
           ('Venus', swe.VENUS, '♀'), ('Marte', swe.MARS, '♂'), ('Júpiter', swe.JUPITER, '♃'),
           ('Saturno', swe.SATURN, '♄'), ('Urano', swe.URANUS, '♅'),
           ('Neptuno', swe.NEPTUNE, '♆'), ('Plutón', swe.PLUTO, '♇')]

img = Image.new('RGB', (W, H), FRAME)
d = ImageDraw.Draw(img)
d.rectangle([40, 40, W-40, H-40], outline=GOLD, width=4)
d.rectangle([75, 75, W-75, H-75], fill=CREAM)

# chart top
def center(y, text, f, fill):
    tw = d.textlength(text, font=f)
    d.text(((W - tw)/2, y), text, font=f, fill=fill)

center(120, 'NATAL CHART · ' + P['name'], F_TITLE, INK)
center(240, P['sub'], F_SUB, (110, 100, 85))

# geometry: title block occupies top ~300px; wheel center lower
CX, CY = W//2, 1080
R_OUT, R_ZIN, R_ZOUT = 560, 500, 560
R_ASP, R_TIK = 340, 490

# houses (Placidus)
cusps, ascmc = swe.houses(JD, P['lat'], P['lon'], b'P')
asc_lon = ascmc[0] % 360.0

def wheel_xy(lon, r):
    offset = (lon - asc_lon) % 360.0
    a = math.radians(180.0 + offset)
    return CX + r*math.cos(a), CY - r*math.sin(a)  # canvas y down

# rings
d.ellipse([CX-R_OUT, CY-R_OUT, CX+R_OUT, CY+R_OUT], outline=INK, width=4)
d.ellipse([CX-R_ZIN, CY-R_ZIN, CX+R_ZIN, CY+R_ZIN], outline=INK, width=3)
d.ellipse([CX-R_ASP, CY-R_ASP, CX+R_ASP, CY+R_ASP], outline=(180, 172, 152), width=2)

# zodiac ring: signs with glyph, alternating subtle fill
swe.set_topo(P['lon'], P['lat'], 0)
flags = swe.FLG_SWIEPH | swe.FLG_TOPOCTR
for i in range(12):
    a0 = wheel_xy(i*30, R_ZOUT)
    a1 = wheel_xy(i*30, R_ZIN)
    d.line([a0, a1], fill=INK, width=3)
    gx, gy = wheel_xy(i*30 + 15, (R_ZIN+R_ZOUT)/2)
    d.text((gx-28, gy-30), SIGNS[i], fill=GOLD if i % 2 else INK, font=F_SIGN)

# house cusps
for h in range(1, 13):
    c = cusps[h - 1] % 360.0
    p0 = wheel_xy(c, R_ZIN)
    p1 = wheel_xy(c, R_ASP)
    d.line([p0, p1], fill=(90, 84, 120) if h in (1, 4, 7, 10) else (150, 144, 128), width=3 if h in (1, 4, 7, 10) else 2)
    # house number at mid of house h
    nxt = cusps[h % 12] % 360.0
    span = (nxt - c) % 360.0
    mid = wheel_xy(c + span/2, 365)
    d.text((mid[0]-13, mid[1]-22), str(h), fill=(120, 114, 98), font=F_HNUM)

# ASC / MC labels
ax, ay = wheel_xy((asc_lon - 4) % 360.0, R_OUT + 26)
d.text((ax-70, ay-18), 'ASC', fill=INK, font=F_HNUM)
mcx, mcy = wheel_xy((ascmc[1] % 360.0 + 4) % 360.0, R_OUT + 26)
d.text((mcx-30, mcy-18), 'MC', fill=INK, font=F_HNUM)

# planets
positions = []
for name, pid, glyph in PLANETS:
    rec = swe.calc_ut(JD, pid, flags)[0]
    lon, spd = rec[0], rec[3]
    sign_i = int(lon // 30) % 12
    deg_in = lon % 30.0
    positions.append((name, glyph, lon, sign_i, deg_in, spd < 0))

# spread glyph angles (min 10 deg separation), glyphs live OUTSIDE the zodiac ring
positions.sort(key=lambda t: t[2])
spaced = [t[2] for t in positions]
for _ in range(80):
    moved = False
    for i in range(len(spaced)):
        for j in range(i+1, len(spaced)):
            gap = (spaced[j] - spaced[i]) % 360.0
            if gap < 10.0:
                push = (10.0 - gap)/2
                spaced[i] = (spaced[i] - push) % 360.0
                spaced[j] = (spaced[j] + push) % 360.0
                moved = True
    if not moved: break

R_TICK0, R_TICK1 = R_OUT, R_OUT + 38
R_GLYPH, R_DEG = R_OUT + 75, R_OUT + 130
for (name, glyph, lon, sign_i, deg_in, rx), lon_s in zip(positions, spaced):
    p0 = wheel_xy(lon, R_TICK0)
    p1 = wheel_xy(lon, R_TICK1)
    d.line([p0, p1], fill=INK, width=2)
    pg = wheel_xy(lon_s, R_GLYPH)
    d.line([wheel_xy(lon, R_TICK1), pg], fill=(170, 160, 140), width=1)
    d.text((pg[0]-38, pg[1]-42), glyph, fill=INK, font=F_GLYPH)
    deg_txt = f"{int(deg_in)}°{SIGNS[sign_i]}" + (' ℞' if rx else '')
    pt = wheel_xy(lon_s, R_DEG)
    d.text((pt[0]-48, pt[1]+2), deg_txt, fill=(80, 74, 60), font=F_DEG)

# numeric collision self-check (glyph centers vs each other, vs ASC/MC labels)
import itertools
bad = []
for (a, b) in itertools.combinations(range(len(spaced)), 2):
    dd = min((spaced[a]-spaced[b]) % 360.0, (spaced[b]-spaced[a]) % 360.0)
    if dd < 7.0: bad.append((positions[a][0], positions[b][0], round(dd,1)))
print('glyph-glyph collisions:', bad if bad else 'none')

# aspects (inner): conj 8, opp 8, trine 7, square 6, sextile 4
ASPECTS = [(0, 8, (96, 90, 74), 6), (180, 8, (176, 84, 76), 6),
           (120, 7, (70, 104, 144), 5), (90, 6, (176, 84, 76), 4),
           (60, 4, (70, 104, 144), 3)]
lons = [t[2] for t in positions]
for i in range(len(lons)):
    for j in range(i+1, len(lons)):
        diff = abs(lons[i] - lons[j]) % 360.0
        diff = min(diff, 360 - diff)
        for ang, orb, col, wd in ASPECTS:
            if abs(diff - ang) <= orb:
                pa = wheel_xy(lons[i], R_ASP - 8)
                pb = wheel_xy(lons[j], R_ASP - 8)
                d.line([pa, pb], fill=col, width=wd)
                break

# bottom text
center(1830, 'calculated with Swiss Ephemeris · Placidus houses', F_MICRO, (130, 120, 100))
center(1880, 'Semilla Cósmica', F_BRAND, GOLD)

img.save(P['out'], dpi=(300, 300))
print('saved', P['out'], 'asc', round(asc_lon, 1), 'sun', round(positions[0][2], 1))
