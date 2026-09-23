#!/usr/bin/env python3
# El Cielo de Lior - square 2400x2400 sky map (CIELO-NAC-01)
# Derived from poster_a3.py. Real star data: HYG + Swiss Ephemeris.
import sys, math, csv, json
import swisseph as swe
from PIL import Image, ImageDraw, ImageFont

def parse_args(argv):
    p = {
        'year': 2019, 'month': 4, 'day': 12, 'hour': 21.5,
        'place': 'Buenos Aires, Argentina', 'lat': -34.6037, 'lon': -58.3816,
        'title': 'LA NOCHE EN QUE TODO EMPEZO',
        'highlight': 'Ori', 'highlight_label': 'ORION',
        'out': 'cielo_cuadrado_sample.png',
    }
    extra_title = []
    for a in argv:
        if '=' not in a:
            extra_title.append(a); continue
        k, v = a.split('=', 1)
        p[k] = v
    if extra_title: p['title'] = ' '.join(extra_title)
    p['lat'] = float(p['lat']); p['lon'] = float(p['lon']); p['hour'] = float(p['hour'])
    for kk in ('year', 'month', 'day'):
        p[kk] = int(p[kk])
    return p

P = parse_args(sys.argv[1:])
LAT, LON = P['lat'], P['lon']
JD = swe.julday(P['year'], P['month'], P['day'], P['hour'] + 3.0)

FDIR = '/usr/share/fonts/truetype/'
def font(name, size):
    try: return ImageFont.truetype(FDIR + name, size)
    except: return ImageFont.load_default()

F_TITLE = font('liberation/LiberationSerif-Bold.ttf', 108)
F_SUB   = font('liberation/LiberationSerif-Regular.ttf', 52)
F_DATE  = font('liberation/LiberationSerif-Regular.ttf', 64)
F_SMALL = font('liberation/LiberationSerif-Regular.ttf', 40)
F_MICRO = font('liberation/LiberationSerif-Italic.ttf', 34)
F_CARD  = font('liberation/LiberationSerif-Regular.ttf', 44)
F_CARDH = font('liberation/LiberationSerif-Bold.ttf', 42)
F_BRAND = font('liberation/LiberationSerif-Italic.ttf', 46)

GOLD  = (197, 160, 89)
CREAM = (247, 241, 227)
FRAME = (24, 22, 30)
SKY   = (10, 12, 26)
INK   = (52, 48, 40)

stars = {}
with open('/workspace/sky/hygdata_v41.csv') as f:
    for row in csv.DictReader(f):
        try: mag = float(row['mag'])
        except: continue
        if mag > 5.6: continue
        hip = int(row['hip']) if row['hip'] else None
        ra = (float(row['ra']) * 15.0) % 360.0
        rec = {'ra': ra, 'dec': float(row['dec']), 'mag': mag, 'ci': row.get('ci') or ''}
        if hip is not None: stars[hip] = rec

clines = []
geod = json.load(open('/workspace/sky/constellations.lines.json'))
for feat in geod['features']:
    if feat['geometry']['type'] != 'MultiLineString': continue
    segs = [[(float(x[0]), float(x[1])) for x in poly] for poly in feat['geometry']['coordinates']]
    clines.append((feat.get('id', ''), segs))

def altaz(ra, dec):
    lst = (swe.sidtime(JD) + LON/15.0) % 24.0
    ha = math.radians((lst*15.0 - ra + 360.0) % 360.0)
    d_, phi = math.radians(dec), math.radians(LAT)
    sin_alt = math.sin(d_)*math.sin(phi) + math.cos(d_)*math.cos(phi)*math.cos(ha)
    alt = math.asin(max(-1, min(1, sin_alt)))
    y = -math.sin(ha)*math.cos(d_)
    x = math.sin(d_)*math.cos(phi) - math.cos(d_)*math.sin(phi)*math.cos(ha)
    az = math.degrees(math.atan2(y, x)) % 360.0
    return math.degrees(alt), az

W = H = 2400
CX, CY, RMAX = W//2, 1230, 740

def proj(alt, az):
    r = (90.0 - alt)/90.0 * RMAX
    a = math.radians(az)
    return CX + r*math.sin(a), CY - r*math.cos(a)

img = Image.new('RGB', (W, H), FRAME)
d = ImageDraw.Draw(img)
d.rectangle([50, 50, W-50, H-50], outline=GOLD, width=4)
d.rectangle([85, 85, W-85, H-85], fill=CREAM)

d.ellipse([CX-RMAX-28, CY-RMAX-28, CX+RMAX+28, CY+RMAX+28], fill=(210, 200, 178))
d.ellipse([CX-RMAX, CY-RMAX, CX+RMAX, CY+RMAX], fill=SKY)
d.ellipse([CX-RMAX, CY-RMAX, CX+RMAX, CY+RMAX], outline=(60, 66, 96), width=2)

for lbl, az in (('N', 0), ('E', 90), ('S', 180), ('O', 270)):
    x, y = proj(-3.0, az)
    d.text((x-16, y-28), lbl, fill=(112, 104, 88), font=F_CARDH)

for cid, segs in clines:
    is_hi = (cid == P['highlight'])
    col = GOLD if is_hi else (62, 74, 118)
    wdt = 4 if is_hi else 2
    for seg in segs:
        prev = None
        for ra, dec in seg:
            alt, az = altaz(ra, dec)
            cur = proj(alt, az) if alt > 0.5 else None
            if prev and cur: d.line([prev[0], prev[1], cur[0], cur[1]], fill=col, width=wdt)
            prev = cur

def star_color(ci):
    try: c = float(ci)
    except: return (235, 238, 250)
    if c < -0.05: return (168, 194, 255)
    if c > 0.35: return (255, 216, 176)
    return (235, 238, 250)

for s in stars.values():
    alt, az = altaz(s['ra'], s['dec'])
    if alt < -1: continue
    x, y = proj(alt, az)
    m = s['mag']
    r = max(1.5, 6.5 - m*1.1)
    d.ellipse([x-r, y-r, x+r, y+r], fill=star_color(s['ci']))

swe.set_topo(LON, LAT, 0)
flags = swe.FLG_SWIEPH | swe.FLG_TOPOCTR | swe.FLG_EQUATORIAL
sun = swe.calc_ut(JD, swe.SUN, flags)[0]
moon = swe.calc_ut(JD, swe.MOON, flags)[0]
elon = (moon[0] - sun[0]) % 360.0
k = (1 + math.cos(math.radians(abs(180 - elon)))) / 2.0
waxing = elon < 180

PLANETS = [('Mercurio', swe.MERCURY), ('Venus', swe.VENUS), ('Marte', swe.MARS),
           ('Jupiter', swe.JUPITER), ('Saturno', swe.SATURN)]
visible_planets = []
for name, pid in PLANETS:
    rec = swe.calc_ut(JD, pid, flags)[0]
    alt, az = altaz(rec[0], rec[1])
    if alt > 2:
        visible_planets.append(name)
        x, y = proj(alt, az)
        r = 8
        d.ellipse([x-r, y-r, x+r, y+r], fill=GOLD)
        d.text((x+18, y-20), name.upper(), fill=GOLD, font=F_SMALL)

malt, maz = altaz(moon[0], moon[1])
if malt > -5:
    x, y = proj(malt, maz)
    mr = 52
    d.ellipse([x-mr, y-mr, x+mr, y+mr], fill=(52, 54, 72), outline=(120, 126, 150), width=2)
    lit_sign = 1 if waxing else -1
    if lit_sign > 0:
        d.pieslice([x-mr, y-mr, x+mr, y+mr], -90, 90, fill=(226, 223, 211))
    else:
        d.pieslice([x-mr, y-mr, x+mr, y+mr], 90, 270, fill=(226, 223, 211))
    tx = mr*(2*k - 1)
    if k >= 0.5:
        d.ellipse([x-abs(tx), y-mr, x+abs(tx), y+mr], fill=(226, 223, 211))
    else:
        d.ellipse([x-abs(tx), y-mr, x+abs(tx), y+mr], fill=(52, 54, 72))
    d.ellipse([x-mr, y-mr, x+mr, y+mr], outline=(150, 155, 175), width=2)

def center(y, text, f, fill, dy=0):
    tw = d.textlength(text, font=f)
    d.text(((W - tw)/2, y + dy), text, font=f, fill=fill)

# title above dome, data below
center(140, P['title'], F_TITLE, INK)
MONTHS = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
hh = int(P['hour']); mm = int(round((P['hour']-hh)*60))
date_line = f"{P['day']} de {MONTHS[P['month']-1]} de {P['year']}  ·  {hh:02d}:{mm:02d} h  ·  {P['place']}"
center(258, date_line, F_SMALL, (110, 100, 85))

if P['highlight']:
    hx, hy = CX, CY + RMAX + 70
    lab = P['highlight_label'] + '  ·  ESTRELLAS REALES DE ESA NOCHE'
    tw = d.textlength(lab, font=F_CARDH)
    d.text((CX - tw/2, hy), lab, fill=INK, font=F_CARDH)

phase_name = ('llena' if k > 0.93 else 'gibosa creciente' if waxing and k > 0.5 else
              'cuarto creciente' if waxing and k > 0.4 else 'creciente' if waxing else
              'gibosa menguante' if k > 0.5 else 'menguante')
card = 'Luna ' + phase_name
if visible_planets: card += '   ·   ' + ', '.join(visible_planets) + ' visibles'
center(CY + RMAX + 150, card, F_CARD, (70, 64, 54))

center(2200, 'mapa calculado con catálogo estelar real HYG + efemérides suizas', F_MICRO, (130, 120, 100))
center(2250, 'El Cielo de Lior  ·  Semilla Cósmica', F_BRAND, GOLD)

img.save(P['out'], dpi=(300, 300))
print('saved', P['out'], 'moon k', round(k, 3), 'waxing' if waxing else 'waning', 'planets', visible_planets)
