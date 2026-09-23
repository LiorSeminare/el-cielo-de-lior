#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""El Cuaderno de Tu Cielo / The Notebook of Your Sky.
Parametric natal-chart reading notebook (EN) built from REAL ephemeris (pyswisseph).
Companion PDF for LA CARTA (Semilla Cosmica). Run:
  python3 cuaderno.py name="Ari Test" year=1995 month=10 day=10 hour=7.35 tz=3 \
      lat=-34.9206 lon=-57.9545 place="La Plata, Argentina" out=cuaderno_test.pdf
"""
import sys, math
import swisseph as swe
from PIL import Image, ImageDraw, ImageFont

# ---------- args ----------
def parse_args(argv):
    p = dict(name='Friend', year=1995, month=10, day=10, hour=12.0, tz=3,
             lat=-34.9206, lon=-57.9545, place='La Plata, Argentina',
             out='cuaderno_test.pdf', gender_n='their')
    for a in argv:
        k, v = a.split('=', 1)
        p[k] = v
    for k in ('lat', 'lon', 'hour', 'tz'):
        p[k] = float(p[k])
    for k in ('year', 'month', 'day'):
        p[k] = int(p[k])
    return p

P = parse_args(sys.argv[1:])
JD = swe.julday(P['year'], P['month'], P['day'], P['hour'] + P['tz'])

# ---------- fonts / palette ----------
FDIR = '/usr/share/fonts/truetype/'
def font(name, size):
    try:
        return ImageFont.truetype(FDIR + name, size)
    except Exception:
        return ImageFont.load_default()

GOLD  = (176, 138, 74)
CREAM = (247, 241, 227)
INK   = (46, 42, 36)
SOFT  = (110, 100, 85)
RULE  = (172, 158, 130)

W, H = 1240, 1754
MX = 96                     # side margin

# ---------- compute chart ----------
flags = swe.FLG_SWIEPH
cusps, ascmc = swe.houses(JD, P['lat'], P['lon'], b'P')
asc_lon, mc_lon = ascmc[0] % 360.0, ascmc[1] % 360.0

SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo',
         'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
GLYPHS = ['♈','♉','♊','♋','♌','♍','♎','♏','♐','♑','♒','♓']
ZODIAC = {
 'Aries': ('cardinal fire', 'the spark. You start things, and the starting is the point'),
 'Taurus': ('fixed earth', 'the ground. You build things that last, and you enjoy them slowly'),
 'Gemini': ('mutable air', 'the question. You learn by asking, and one thread always leads to five more'),
 'Cancer': ('cardinal water', 'the tide. You feel first and understand later, and you protect what you love'),
 'Leo': ('fixed fire', 'the flame. You need to make something of yourself, and you are most alive when seen'),
 'Virgo': ('mutable earth', 'the craft. You care by improving things, one real detail at a time'),
 'Libra': ('cardinal air', 'the scales. You see every side, and fairness matters to you more than winning'),
 'Scorpio': ('fixed water', 'the depth. You do not skim: whatever you touch, you touch all the way down'),
 'Sagittarius': ('mutable fire', 'the horizon. You need meaning, room, and somewhere ahead to move toward'),
 'Capricorn': ('cardinal earth', 'the climb. You take the long way up, and you do not drop what you carry'),
 'Aquarius': ('fixed air', 'the pattern. You see the system everyone else is standing inside of'),
 'Pisces': ('mutable water', 'the sea. You absorb the room before you notice it, and you feel what is unsaid'),
}

PLANET_DEFS = [
 ('Sun', swe.SUN, '☉', 'your core: what you are when nobody is grading you'),
 ('Moon', swe.MOON, '☽', 'your inner weather: what you need to feel safe'),
 ('Mercury', swe.MERCURY, '☿', 'your mind: how you think, learn and say things'),
 ('Venus', swe.VENUS, '♀', 'your love and taste: what you find beautiful and how you bond'),
 ('Mars', swe.MARS, '♂', 'your drive: how you want, fight and go after things'),
 ('Jupiter', swe.JUPITER, '♃', 'your growth: where life keeps offering you more'),
 ('Saturn', swe.SATURN, '♄', 'your teacher: where life asks for patience and pays with mastery'),
 ('Uranus', swe.URANUS, '♅', 'your outlier: where you are different, on purpose or not'),
 ('Neptune', swe.NEPTUNE, '♆', 'your dream: where you dissolve, imagine and sometimes lose the shore'),
 ('Pluto', swe.PLUTO, '♇', 'your depth: where you transform by going through, not around'),
]

positions = {}
for name, pid, glyph, desc in PLANET_DEFS:
    rec = swe.calc_ut(JD, pid, flags)[0]
    positions[name] = dict(lon=rec[0] % 360.0, retro=rec[3] < 0,
                           glyph=glyph, desc=desc)
rec = swe.calc_ut(JD, swe.MEAN_NODE, flags)[0]
positions['North Node'] = dict(lon=rec[0] % 360.0, retro=True, glyph='☊',
                               desc='your direction: the road that feels wrong and is right')

def house_of(lon):
    """Placidus house (1..12) containing ecliptic longitude lon."""
    for i in range(12):
        a = cusps[i] % 360.0
        b = cusps[(i + 1) % 12] % 360.0
        span = (b - a) % 360.0
        if span == 0:
            span = 360.0
        if (lon - a) % 360.0 < span:
            return i + 1
    return 12

for k in positions:
    v = positions[k]
    v['sign'] = SIGNS[int(v['lon'] // 30) % 12]
    v['deg'] = v['lon'] % 30.0
    v['house'] = house_of(v['lon'])
ASC = dict(sign=SIGNS[int(asc_lon // 30) % 12], deg=asc_lon % 30.0, glyph='AC', house=1,
           desc='your door: the self people meet first')
MC = dict(sign=SIGNS[int(mc_lon // 30) % 12], deg=mc_lon % 30.0, glyph='MC', house=10,
          desc='your call: the direction your life is visibly pulled toward')

# house cusps signs (for the houses table)
house_cusp_sign = [SIGNS[int((c % 360.0) // 30) % 12] for c in cusps]

# ---------- aspects ----------
ASPECTS = [(0, 'conjunction', 8.0, 'fusion'), (60, 'sextile', 5.0, 'opening'),
           (90, 'square', 7.0, 'friction'), (120, 'trine', 7.0, 'flow'),
           (180, 'opposition', 8.0, 'pendulum')]
MAJOR = {'Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Saturn', 'North Node', 'ASC'}
found_aspects = []
keys = list(PLANET_DEFS and [n for n, *_ in PLANET_DEFS]) + ['North Node', 'ASC', 'MC']
src = {k: v['lon'] for k, v in positions.items()}
src['ASC'] = asc_lon; src['MC'] = mc_lon
for i in range(len(keys)):
    for j in range(i + 1, len(keys)):
        a, b = keys[i], keys[j]
        d = abs((src[a] - src[b]) % 360.0)
        d = min(d, 360.0 - d)
        for ang, nm, orb, kind in ASPECTS:
            o = orb + (1.5 if 'Sun' in (a, b) or 'Moon' in (a, b) else 0)
            if abs(d - ang) <= o:
                found_aspects.append(dict(a=a, b=b, name=nm, kind=kind,
                                          orb=abs(d - ang),
                                          weight=(3 if a in MAJOR else 1) + (3 if b in MAJOR else 1) - abs(d - ang)))
found_aspects.sort(key=lambda x: -x['weight'])
top_aspects = []
seen_pairs = set()
for f in found_aspects:
    pk = frozenset((f['a'], f['b']))
    if pk in seen_pairs:
        continue
    seen_pairs.add(pk)
    top_aspects.append(f)
    if len(top_aspects) == 5:
        break

# ---------- copy ----------
SIGN_TEXT = {
 'Aries': 'Aries wants a beginning. It is honest, quick and brave, and it would rather act and be wrong than wait and wonder. Its shadow is impatience: burning the bridge before crossing it.',
 'Taurus': 'Taurus wants what is real. It is steady, loyal and physical, and it trusts slow things: good food, long work, a promise kept. Its shadow is stubbornness: holding on after the holding stopped helping.',
 'Gemini': 'Gemini wants to know. It is curious, quick-tongued and playful, and it thinks by talking and reading and poking at things. Its shadow is scattering: ten open doors and no room entered.',
 'Cancer': 'Cancer wants to keep. It feels the mood of a room before anyone speaks, it remembers everything, and it protects its people like a wall with a heartbeat. Its shadow is the shell: hiding the very feelings it wants met.',
 'Leo': 'Leo wants to shine for real. It is warm, generous and dramatic in the best sense, and it knows that being seen is a human need, not a vanity. Its shadow is the audience: needing the applause to feel real.',
 'Virgo': 'Virgo wants to help properly. It notices the detail everyone missed, it improves what it loves, and its care is practical: soup, fixes, plans. Its shadow is the harsh inner editor, aimed first at itself.',
 'Libra': 'Libra wants balance. It is fair, charming and allergic to ugliness, and it can hold two opposite truths at once without dropping either. Its shadow is the deferred decision: keeping peace where honesty was needed.',
 'Scorpio': 'Scorpio wants truth. It does not skim: it bonds all the way down or not at all, it keeps its own counsel, and it can walk through fire on purpose. Its shadow is control: testing loyalty instead of trusting it.',
 'Sagittarius': 'Sagittarius wants the horizon. It is honest, hopeful and restless, it needs meaning more than comfort, and it learns by going. Its shadow is the leap: promising the mountain and skipping the map.',
 'Capricorn': 'Capricorn wants to build. It takes the long way up without complaining, it respects real work, and its loyalty shows as deeds, not speeches. Its shadow is the boss that never rests: worth proven by exhaustion.',
 'Aquarius': 'Aquarius wants the pattern. It sees the system everyone else is standing inside of, it is loyal to ideas and to people in its own odd, loyal way. Its shadow is distance: watching life from the observatory.',
 'Pisces': 'Pisces wants to merge. It absorbs the room before it notices it, it dreams in full color, and its kindness has no fence. Its shadow is the dissolve: drifting until the shore is far behind.',
}
HOUSE_TEXT = {
 1: 'the house of the self: your body, your first impression, the way you enter a room.',
 2: 'the house of worth: your money, your body as yours, and what makes you feel valuable.',
 3: 'the house of the mind: siblings, neighborhood, learning, the everyday talk that shapes you.',
 4: 'the house of roots: home, family, the private floor your life is built on.',
 5: 'the house of play: creativity, romance, children, the joy that exists for no reason.',
 6: 'the house of the everyday: work, health, routines, the small repeated acts that become a life.',
 7: 'the house of the other: partners, close one-on-one bonds, and what you meet through them.',
 8: 'the house of depth: intimacy, shared money, crisis and rebirth, the stuff under the floorboards.',
 9: 'the house of the horizon: travel, study, belief, the long questions with no short answers.',
 10: 'the house of the call: career, public self, the direction people can see your life moving in.',
 11: 'the house of the tribe: friendships, groups, causes, the future you are building with others.',
 12: 'the house of the hidden: solitude, dreams, karma, everything that works best behind the curtain.',
}
SIGN_WORK = {
 'Aries': 'your work here is to start bravely and stay long enough to see it through.',
 'Taurus': 'your work here is to trust your pace; slow is not the same as stuck.',
 'Gemini': 'your work here is to finish at least one thread before starting the next five.',
 'Cancer': 'your work here is to say the feeling out loud instead of guarding it.',
 'Leo': 'your work here is to be seen without performing: the real you is the show.',
 'Virgo': 'your work here is to let good enough be good enough sometimes.',
 'Libra': 'your work here is to decide, even when a choice means someone briefly dislikes it.',
 'Scorpio': 'your work here is to let people in without testing them first.',
 'Sagittarius': 'your work here is to keep the meaning AND do the Tuesday-sized steps.',
 'Capricorn': 'your work here is to rest without earning it first.',
 'Aquarius': 'your work here is to let a few people all the way past the glass.',
 'Pisces': 'your work here is to keep one foot on the shore while you swim.',
}
PAIR_TEXT = {
 frozenset(('Sun','Moon')): 'the conversation between who you are and what you need.',
 frozenset(('Sun','Moon','Mercury')): 'how your head and your heart negotiate.',
}
KIND_TEXT = {
 'conjunction': 'The two sit on the same spot of your sky: you cannot pull them apart, and their mix is a signature of who you are.',
 'sextile': 'The two help each other quietly: when you use one, the other comes along for free.',
 'square': 'The two push against each other, and that friction is an engine: it is uncomfortable exactly until it makes you strong.',
 'trine': 'The two flow together so naturally you may not notice the gift: talent that feels like breathing, easy to take for granted.',
 'opposition': 'The two live at opposite ends of your sky and take turns running your life. The work, and the prize, is holding both at once.',
 'pendulum': 'The two live at opposite ends of your sky and take turns running your life. The work, and the prize, is holding both at once.',
}

# ---------- drawing helpers ----------
def new_page():
    img = Image.new('RGB', (W, H), CREAM)
    d = ImageDraw.Draw(img)
    d.rectangle([28, 28, W-28, H-28], outline=GOLD, width=3)
    d.rectangle([40, 40, W-40, H-40], outline=GOLD, width=1)
    return img, d

F_TITLE = font('liberation/LiberationSerif-Bold.ttf', 66)
F_H1    = font('liberation/LiberationSerif-Bold.ttf', 46)
F_H2    = font('liberation/LiberationSerif-Bold.ttf', 34)
F_BODY  = font('liberation/LiberationSerif-Regular.ttf', 30)
F_IT    = font('liberation/LiberationSerif-Italic.ttf', 29)
F_SMALL = font('liberation/LiberationSerif-Regular.ttf', 24)
F_GLYPH = font('dejavu/DejaVuSans.ttf', 56)

def center(d, y, text, f, fill=INK):
    tw = d.textlength(text, font=f)
    d.text(((W - tw) / 2, y), text, font=f, fill=fill)
    return y + (f.size if hasattr(f, 'size') else 20)

def wrap(d, text, f, width):
    words, lines, cur = text.split(), [], ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if d.textlength(t, font=f) <= width:
            cur = t
        else:
            lines.append(cur); cur = w_
    if cur:
        lines.append(cur)
    return lines

def para(d, y, text, f=F_BODY, fill=INK, width=W-2*MX, lead=1.5, indent=0):
    for ln in wrap(d, text, f, width):
        d.text((MX + indent, y), ln, font=f, fill=fill)
        y += int(f.size * lead)
    return y

def para_indent(d, y, text, f=F_BODY, fill=INK, width=W-2*MX, lead=1.5):
    return para(d, y, text, f, fill, width, lead)

def hr(d, y):
    d.line([MX, y, W-MX, y], fill=RULE, width=2)
    return y + 18

def footer(d, page):
    center(d, H-86, f'Semilla Cósmica · the notebook of your sky · page {page}', F_SMALL, SOFT)

def placement_block(d, y, title, glyph, sign, house, extra, lead_in=''):
    d.text((MX, y), glyph, font=F_GLYPH, fill=GOLD)
    gw = d.textlength(glyph, font=F_GLYPH)
    d.text((MX + max(100, gw + 22), y + 6), title, font=F_H2, fill=INK)
    y += 78
    line = f'{sign} · house {house}' if house else sign
    y = para(d, y, line.upper(), F_SMALL, SOFT)
    y += 6
    y = para(d, y, extra)
    return y + 14

def planet_body(name):
    v = positions[name]
    s = SIGN_TEXT[v['sign']]
    work = SIGN_WORK[v['sign']]
    retro = ' (retrograde: it works inward, privately, from the inside out)' if v['retro'] else ''
    first = s.split('.')[0]          # e.g. 'Libra wants balance'
    text = (f'Your {name} is in {v["sign"]}, in house {v["house"]}{retro}. '
            f'{name} is {v["desc"]}. In your sky it wears the shape of {v["sign"]}: {first} — '
            f'{ZODIAC[v["sign"]][1]}. ')
    return text + f'So: {work}'

def planet_aspect_line(name):
    best = None
    for f in found_aspects:
        if name in (f['a'], f['b']) and (best is None or f['weight'] > best['weight']):
            best = f
    if not best:
        return None
    other = best['b'] if best['a'] == name else best['a']
    verb = 'conjunct' if best['name'] == 'conjunction' else best['name']
    return (f'One conversation shapes this planet the most: {name} {verb} {other} '
            f'(orb {best["orb"]:.1f}°). {KIND_TEXT[best["name"]]}')

PLANET_QUESTIONS = {
 'Sun': ['When was the last time you did something well with nobody watching?',
         'Where in your week does your {sign} side get to act, not just plan?',
         'If house {house} is your stage, what are you performing there right now?'],
 'Moon': ['What does your body do first when a day goes wrong?',
          'Which place makes you feel {sign}-safe: is it a person, a room, a routine?',
          'What does house {house} need from you this week, quietly?'],
 'Mercury': ['Who do you think best next to, and why that person?',
             'Where does your {sign} mind overtalk instead of over-listen?',
             'What is one question in house {house} you keep postponing?'],
 'Venus': ['What did you last find beautiful without deciding to?',
           'How does your {sign} love ask to be loved back?',
           'What would generous look like in house {house} this month?'],
 'Mars': ['What do you fight for that you never call a fight?',
          'When your {sign} anger arrives, where does it go?',
          'Which want in house {house} deserves a first step this week?'],
 'Jupiter': ['Where has life kept offering you more, and where have you said no out of habit?',
             'What does {sign} faith look like in practice, not in words?',
             'What could you grow in house {house} if you let it get big?'],
 'Saturn': ['What hard thing have you already mastered that you give yourself no credit for?',
            'Where does {sign} caution protect you, and where does it just delay you?',
            'What is house {house} patiently teaching you this year?'],
}

pages = []
pn = 0

# ===== 1. COVER =====
img, d = new_page()
pn += 1
y = center(d, 300, 'THE NOTEBOOK', F_TITLE)
y = center(d, y + 16, 'OF YOUR SKY', F_TITLE)
y = center(d, y + 40, 'a reading written from your real chart', F_IT, SOFT)
# big three glyphs row
row = positions['Sun']['glyph'] + '  ' + positions['Moon']['glyph'] + '  ' + 'AC'
center(d, y + 70, row, font('dejavu/DejaVuSans.ttf', 92), GOLD)
y = center(d, y + 230, P['name'].upper(), F_H1, INK)
y = center(d, y + 24, f'{P["day"]:02d}/{P["month"]:02d}/{P["year"]} · {P["place"]}', F_BODY, SOFT)
y = center(d, y + 30, f'Sun in {positions["Sun"]["sign"]} · Moon in {positions["Moon"]["sign"]} · Rising in {ASC["sign"]}', F_BODY, SOFT)
y = center(d, y + 90, 'computed with real ephemeris · no generic sun-sign horoscopes', F_SMALL, SOFT)
footer(d, pn); pages.append(img)

# ===== 1b. THE MANDALA (your wheel) =====
def draw_wheel(img, d, WS_L=1500):
    """Natal wheel drawn inline: zodiac ring, house cusps, planets, aspect lines."""
    CX = CY = WS_L // 2
    R_OUT, R_ZIN, R_PL, R_ASP = 620, 520, 398, 340
    INKw = (46, 42, 36)
    d.ellipse([CX-R_OUT, CY-R_OUT, CX+R_OUT, CY+R_OUT], outline=INKw, width=4)
    d.ellipse([CX-R_ZIN, CY-R_ZIN, CX+R_ZIN, CY+R_ZIN], outline=INKw, width=3)
    d.ellipse([CX-R_ASP, CY-R_ASP, CX+R_ASP, CY+R_ASP], outline=(180, 172, 152), width=2)
    F_sg = font('dejavu/DejaVuSans.ttf', 44)
    F_pl = font('dejavu/DejaVuSans.ttf', 40)
    F_hn = font('dejavu/DejaVuSans.ttf', 30)
    # zodiac ring: Aries rising at left (9 o'clock), counterclockwise
    def xy(lon, r):
        ang = math.radians(180.0 - lon)
        return CX + r * math.cos(ang), CY - r * math.sin(ang)
    for i in range(12):
        a1 = 180.0 - i * 30.0
        x1, y1 = xy(i * 30.0, R_OUT); x2, y2 = xy(i * 30.0, R_ZIN)
        d.line([x1, y1, x2, y2], fill=INKw, width=2)
        gx, gy = xy(i * 30.0 + 15, (R_OUT + R_ZIN) / 2)
        d.text((gx - 22, gy - 26), GLYPHS[i], font=F_sg, fill=INKw)
    # house cusps + numbers
    for i in range(12):
        x1, y1 = xy(cusps[i] % 360.0, R_OUT); x2, y2 = xy(cusps[i] % 360.0, R_ASP)
        d.line([x1, y1, x2, y2], fill=(120, 112, 96), width=2)
        mid = (cusps[i] % 360.0 + ((cusps[(i+1) % 12] - cusps[i]) % 360.0) / 2) % 360.0
        hx, hy = xy(mid, R_ZIN - 46)
        d.ellipse([hx - 24, hy - 24, hx + 24, hy + 24], fill=CREAM)
        d.text((hx - 12, hy - 16), str(i + 1), font=F_hn, fill=(120, 112, 96))
    # planets: spread to avoid overlaps (min 9 degrees apart)
    plot = []
    items = [(k, v['lon'], v['glyph']) for k, v in positions.items()]
    items.sort(key=lambda t: t[1])
    disp = []
    for k, lon, g in items:
        dlon = lon
        while any(min(abs(dlon - p), 360 - abs(dlon - p)) < 9 for p in disp):
            dlon = (dlon + 9) % 360
        disp.append(dlon)
        plot.append((k, lon, g, dlon))
    for k, lon, g, dlon in plot:
        px, py = xy(dlon, R_PL)
        d.text((px - 20, py - 22), g, font=F_pl, fill=(176, 138, 74))
        # tick to true position
        tx, ty = xy(lon, R_ASP + 2)
        t2x, t2y = xy(lon, R_ASP - 12)
        d.line([tx, ty, t2x, t2y], fill=(176, 138, 74), width=2)
    # aspect lines between the five strongest
    for f_ in top_aspects:
        la = next((l for k, l, g, dl in plot if k == f_['a']), None)
        lb = next((l for k, l, g, dl in plot if k == f_['b']), None)
        if la is None or lb is None:
            continue
        ax, ay = xy(la, R_ASP - 30); bx, by = xy(lb, R_ASP - 30)
        col = (176, 138, 74) if f_['name'] in ('trine', 'sextile') else (150, 90, 80)
        d.line([ax, ay, bx, by], fill=col, width=2)

# ===== 1b. THE MANDALA (your wheel) =====
img, d = new_page(); pn += 1
y = center(d, 110, 'YOUR MANDALA', F_H1)
y = center(d, y + 8, 'the wheel of your sky, drawn from real ephemeris', F_IT, SOFT)
# wheel drawn on its own square canvas, pasted scaled: nothing cropped
WS = 1500
wheel_img = Image.new('RGB', (WS, WS), CREAM)
wd = ImageDraw.Draw(wheel_img)
wd.rectangle([14, 14, WS-14, WS-14], outline=GOLD, width=3)
draw_wheel(wheel_img, wd)
WS_OUT = 1060
wheel = wheel_img.resize((WS_OUT, WS_OUT))
img.paste(wheel, ((W - WS_OUT)//2, 380))
d = ImageDraw.Draw(img)
footer(d, pn); pages.append(img)

# ===== 2. HOW TO READ =====
img, d = new_page(); pn += 1
y = center(d, 150, 'HOW TO READ THIS NOTEBOOK', F_H1)
y = hr(d, y + 30)
y = para(d, y + 10,
 'Most horoscopes are written for a twelfth of the world at a time. This notebook is not. '
 'Everything here was computed for one exact moment and place: yours. The positions of the planets, '
 'the houses, the angles — all calculated from real astronomical ephemeris, the same kind professional '
 'astrologers use. What is written below is yours alone.')
y = para(d, y + 18,
 'A chart is a map, not a sentence. It does not say what will happen to you; it describes the terrain '
 'you were born into: your strengths, your frictions, the roads that feel natural and the ones that '
 'feel wrong precisely because they lead somewhere you need to go.')
y = para(d, y + 18,
 'How to use it: do not read it all at once. Take one page a day, or one a week. Sit with it. '
 'Astrology works best as a mirror, not an instruction manual: read a page, then watch your own week '
 'for it. The lines that sting a little are usually the true ones.')
y = para(d, y + 18,
 'One honesty note: no chart forces anything. You are the one holding the pen. The sky proposes; you dispose.')
y = para(d, y + 30, 'This notebook is a companion to your star map. The map shows the sky you were born under; '
 'the notebook is what that sky has to say.', F_IT, SOFT)
y = hr(d, y + 16)
y = para(d, y + 4, 'YOUR FIRST WEEK WITH IT', F_H2, GOLD)
for tip in ['Day 1: read only the MANDALA and the BIG THREE. Let the shape land before the words.',
            'Day 2: your Sun and Moon pages. Ask, for each line: does this feel like me, or like an instruction?',
            'Day 3: the HOUSES chapter. It is the map of where things happen.',
            'Day 4: the five conversations (aspects). Read them slowly; they explain the push-pull.',
            'Day 5: the conclusion and IN PLAIN WORDS. If you read nothing else twice, read those twice.',
            'Day 6-7: leave it alone. Then come back to the one page that kept calling you.']:
    y = para(d, y + 8, chr(183) + ' ' + tip, F_SMALL, SOFT)
footer(d, pn); pages.append(img)

# ===== 3. BIG THREE =====
img, d = new_page(); pn += 1
y = center(d, 130, 'YOUR BIG THREE', F_H1)
y = hr(d, y + 24)
y = placement_block(d, y + 10, 'SUN · WHO YOU ARE', positions['Sun']['glyph'],
    positions['Sun']['sign'], positions['Sun']['house'],
    f'The Sun is the center of the chart, the way the actual sun is the center of the sky. '
    f'Yours is in {positions["Sun"]["sign"]}: {ZODIAC[positions["Sun"]["sign"]][1]}. '
    f'{SIGN_TEXT[positions["Sun"]["sign"]].split(". ")[1]}. It lives in house {positions["Sun"]["house"]}, '
    f'{HOUSE_TEXT[positions["Sun"]["house"]]} {SIGN_WORK[positions["Sun"]["sign"]].capitalize()}')
y = placement_block(d, y + 6, 'MOON · WHAT YOU NEED', positions['Moon']['glyph'],
    positions['Moon']['sign'], positions['Moon']['house'],
    f'The Moon is your inner life: what makes you feel safe, held and at home in yourself. '
    f'Yours is in {positions["Moon"]["sign"]}: {ZODIAC[positions["Moon"]["sign"]][1]}. '
    f'{SIGN_TEXT[positions["Moon"]["sign"]].split(". ")[1]}. It lives in house {positions["Moon"]["house"]}, '
    f'{HOUSE_TEXT[positions["Moon"]["house"]]} {SIGN_WORK[positions["Moon"]["sign"]].capitalize()}')
y = placement_block(d, y + 6, 'RISING · HOW YOU ENTER', 'AC',
    ASC['sign'], 1,
    f'Your rising sign (Ascendant) is the door of the chart: the self people meet before they know you. '
    f'Yours is {ASC["sign"]}: {ZODIAC[ASC["sign"]][1]}. '
    f'{SIGN_TEXT[ASC["sign"]].split(". ")[1]}. It colors everything: the same Sun reads differently '
    f'through a different door. Your Midheaven, the visible peak of your sky, is in {MC["sign"]}.')
footer(d, pn); pages.append(img)

# ===== 4-9. THE PLANETS =====
planet_pages = [
 ('THE SUN', 'Sun'),
 ('THE MOON', 'Moon'),
 ('MERCURY · YOUR MIND', 'Mercury'),
 ('VENUS · YOUR LOVE AND TASTE', 'Venus'),
 ('MARS · YOUR DRIVE', 'Mars'),
 ('JUPITER · YOUR GROWTH', 'Jupiter'),
 ('SATURN · YOUR TEACHER', 'Saturn'),
]
for title, key in planet_pages:
    img, d = new_page(); pn += 1
    v = positions[key]
    y = center(d, 130, title, F_H1)
    # glyph drawn with DejaVu (Liberation has no planet glyphs) — no tofu boxes
    F_SUB_GLYPH = font('dejavu/DejaVuSans.ttf', 30)
    sub = f'{v["sign"].upper()} · HOUSE {v["house"]}' + (' · RETROGRADE' if v['retro'] else '')
    gw2 = d.textlength(v['glyph'], font=F_SUB_GLYPH)
    sw = d.textlength(sub, font=F_SMALL)
    x0 = (W - (gw2 + 18 + sw)) / 2
    d.text((x0, y + 10), v['glyph'], font=F_SUB_GLYPH, fill=SOFT)
    d.text((x0 + gw2 + 18, y + 12), sub, font=F_SMALL, fill=SOFT)
    y = hr(d, y + 70)
    y = para(d, y + 8, planet_body(key))
    # house paragraph: the ONLY place the house text appears on this page
    y = para(d, y + 16, 'House ' + str(v['house']) + ' tells you where this plays out day to day: ' + HOUSE_TEXT[v['house']] +
             ' When in doubt, look there: that is the stage where this part of you performs.')
    aline = planet_aspect_line(key)
    if aline:
        y = para(d, y + 16, aline)
    # questions to fill the page and make it a notebook, not a pamphlet
    y = hr(d, y + 12)
    y = para(d, y + 4, 'FOR YOUR NOTES', F_H2, GOLD)
    for q in PLANET_QUESTIONS[key]:
        y = para(d, y + 8, '· ' + q.format(sign=v['sign'], house=v['house']))
    for _ in range(4):
        y = hr(d, y + 30)
    footer(d, pn); pages.append(img)

# ===== 10. URANUS / NEPTUNE / PLUTO =====
img, d = new_page(); pn += 1
y = center(d, 130, 'THE SLOW THREE', F_H1)
y = hr(d, y + 24)
y = para(d, y + 6, 'Uranus, Neptune and Pluto move slowly; everyone born in your years shares their signs. '
 'What is yours alone is the HOUSE each falls in: the room of your life where the slow current runs.')
for key in ('Uranus', 'Neptune', 'Pluto'):
    v = positions[key]
    y = placement_block(d, y + 12, key.upper(), v['glyph'], v['sign'], v['house'],
        f'Everyone your age has {key} in {v["sign"]}. Yours sits in house {v["house"]}: '
        f'{HOUSE_TEXT[v["house"]]} That is where {v["desc"]} gets tested and renewed. '
        f'{SIGN_WORK[v["sign"]].capitalize()}')
footer(d, pn); pages.append(img)

# ===== 11. NODES =====
img, d = new_page(); pn += 1
y = center(d, 130, 'NORTH NODE · SOUTH NODE', F_H1)
nn, sn = positions['North Node'], positions['North Node']
south_sign = SIGNS[(SIGNS.index(nn['sign']) + 6) % 12]
y = hr(d, y + 24)
y = placement_block(d, y + 10, 'NORTH NODE · YOUR DIRECTION', '☊',
    nn['sign'], nn['house'],
    f'The North Node is not a planet; it is a direction. It points at the road that feels uncomfortable, '
    f'unfamiliar and right. Yours is in {nn["sign"]}, house {nn["house"]}: {HOUSE_TEXT[nn["house"]]} '
    f'Growing toward it means doing your work: {SIGN_WORK[nn["sign"]]} '
    f'Especially when the old way feels safer.')
y = placement_block(d, y + 6, 'SOUTH NODE · YOUR DEFAULT', '☋',
    south_sign, None,
    f'Directly opposite sits the South Node, in {south_sign}: {ZODIAC[south_sign][1]}. '
    f'It is where you come with built-in skill and built-in comfort — and where staying forever '
    f'becomes a retreat. The art is not to reject it, but to use it as a base camp, not a home.')
y = hr(d, y + 12)
y = para(d, y + 4, 'FOR YOUR NOTES', F_H2, GOLD)
for q in ['Where does the old {sn} habit feel safe but small?'.format(sn=south_sign),
          'What would one brave step toward {nn} look like this month, in house {h}?'.format(nn=nn['sign'], h=nn['house']),
          'Who in your life models the {nn} road for you?'.format(nn=nn['sign'])]:
    y = para(d, y + 8, chr(183) + ' ' + q)
for _ in range(3):
    y = hr(d, y + 28)
footer(d, pn); pages.append(img)

# ===== 12. HOUSES CHAPTER (two pages) =====
img, d = new_page(); pn += 1
y = center(d, 130, 'YOUR TWELVE HOUSES', F_H1)
y = hr(d, y + 24)
y = para(d, y + 6, 'The houses are the rooms of a life. Each one opens onto a different area; the sign on its '
 'cusp is the style of the door, and the planets inside it are the guests who live there. Here is the '
 'floor plan of your sky, room by room:', F_IT, SOFT)
y += 14
F_ROW = font('liberation/LiberationSerif-Bold.ttf', 26)
F_ROWs = font('liberation/LiberationSerif-Regular.ttf', 21)
for i in range(12):
    h_num = i + 1
    if y > H - 150:
        break
    guests = [k for k, v in positions.items() if v['house'] == h_num]
    d.text((MX, y), f'{h_num:>2}.', font=F_ROW, fill=GOLD)
    d.text((MX + 62, y), f'{house_cusp_sign[i]}', font=F_ROW, fill=INK)
    d.text((MX + 62 + 190, y), HOUSE_TEXT[h_num].split(':')[0] + ':', font=F_SMALL, fill=SOFT)
    y += 34
    extra = ''
    if guests:
        extra = 'Guests: ' + ', '.join(guests) + '.'
    else:
        extra = 'No planets: this room runs quietly, led by the sign alone.'
    y = para(d, y + 2, extra, F_ROWs, SOFT)
    y += 6
y = para(d, y + 8, f'The angles: your Ascendant is {ASC["sign"]} ({ASC["deg"]:.1f}°) and your Midheaven is '
 f'{MC["sign"]} ({MC["deg"]:.1f}°). The first is the door you enter by; the second is the direction '
 'your life is seen climbing toward.', F_IT, SOFT)
footer(d, pn); pages.append(img)

# ===== 12b. STELLIUMS =====
img, d = new_page(); pn += 1
y = center(d, 130, 'WHERE YOUR SKY CROWDS', F_H1)
y = hr(d, y + 24)
y = para(d, y + 6, 'A stellium is when three or more planets crowd into one sign or one house. It is a traffic jam '
 'of energy: that one room of your life carries a loud, complicated, defining weight. Some charts have one; '
 'many do not. Both are normal.', F_IT, SOFT)
y += 16
sign_count = {}
house_count = {}
PLANET_ONLY = [k for k, _pid, _g, _d in PLANET_DEFS]   # North Node is NOT a planet
for k in PLANET_ONLY:
    v = positions[k]
    sign_count[v['sign']] = sign_count.get(v['sign'], 0) + 1
    house_count[v['house']] = house_count.get(v['house'], 0) + 1
any_stellium = False
for sgn, n in sign_count.items():
    if n >= 3:
        any_stellium = True
        members = [k for k in PLANET_ONLY if positions[k]['sign'] == sgn]
        extras = [k for k in positions if k not in PLANET_ONLY and positions[k]['sign'] == sgn]
        y = para(d, y + 10, f'A STELLIUM IN {sgn.upper()} · {n} planets', F_H2, GOLD)
        note = (f' (plus your North Node, which is a point, not a planet)' if extras else '')
        y = para(d, y + 8, f'{", ".join(members)} all sit in {sgn}{note}. That sign is not a flavor in your chart; '
            f'it is a climate. {SIGN_TEXT[sgn]} When life gets loud, it usually gets loud here first.')
for hse, n in house_count.items():
    if n >= 3:
        any_stellium = True
        members = [k for k in PLANET_ONLY if positions[k]['house'] == hse]
        extras = [k for k in positions if k not in PLANET_ONLY and positions[k]['house'] == hse]
        y = para(d, y + 10, f'A STELLIUM IN HOUSE {hse} · {n} planets', F_H2, GOLD)
        note = (f' (plus your North Node, which is a point, not a planet)' if extras else '')
        y = para(d, y + 8, f'{", ".join(members)} all live in house {hse}{note}: {HOUSE_TEXT[hse]} '
            f'This room of your life is a charged center of gravity: whatever happens anywhere in you, '
            f'it tends to come home to here.')
if not any_stellium:
    y = para(d, y + 14, 'Your chart has no stellium: its energy is spread across the sky instead of pooled. '
        'That is not a lack; it is a breadth. You carry many rooms with one or two voices each, '
        'and no single area swallows the rest. The pages on the planets and the five conversations '
        'describe where your real weight lives.')
y = para(d, y + 16, 'A note on honesty: stelliums are read with judgment, not counted like scores. '
 'What matters is whether the crowding matches your lived experience. If it does, reread that page on hard days.', F_IT, SOFT)
footer(d, pn); pages.append(img)

# ===== 13. FIVE ASPECTS =====
img, d = new_page(); pn += 1
y = center(d, 130, 'FIVE CONVERSATIONS IN YOUR SKY', F_H1)
y = hr(d, y + 24)
y = para(d, y + 6, 'Planets in a chart talk to each other. The strongest of these conversations are the aspects: '
 'the angles between planets. These five shape you the most, ordered by weight.', F_IT, SOFT)
y += 10
for f_ in top_aspects:
    a, b = f_['a'], f_['b']
    title = f'{a} {f_["name"].upper()} {b} (orb {f_["orb"]:.1f}°)'
    y = placement_block(d, y + 8, title, '✦', '', None, '')
    y -= 8
    pair = PAIR_TEXT.get(frozenset((a, b)), f'the conversation between {a.lower()} and {b.lower()}.')
    y = para(d, y, KIND_TEXT[f_['name']] + ' In your chart this is ' + pair)
footer(d, pn); pages.append(img)

# ===== 14. CLOSING =====
img, d = new_page(); pn += 1
y = center(d, 220, 'HOW TO KEEP YOUR SKY', F_H1)
y = hr(d, y + 30)
y = para(d, y + 10,
 'A sky is not a verdict; it is a garden. Some of what you read here grows on its own. '
 'Some of it needs water. Pick one line from this notebook — the one you underlined in your head — '
 'and practice it for a month. Not forever. A month.')
y = para(d, y + 18,
 'Then come back on your birthday: your sky is the same; you will not be. '
 'That is the quiet trick of a natal chart. It is a fixed mirror for a moving person.')
y = para(d, y + 18,
 'And when someone asks what that poster on your wall is, you can tell them: '
 'that is the exact sky, computed to the minute, over the exact place I was born. '
 'This notebook is what it said back.')
y = hr(d, y + 16)
y = para(d, y + 4, 'SMALL RITUALS THAT KEEP A SKY ALIVE', F_H2, GOLD)
for r in ['On your birthday, reread the IN PLAIN WORDS page first. The year will have answered some of it.',
          'When a page stings, do not close the notebook: write the date next to the line. Stings age into insight.',
          'Once a season, look up at the real sky and find one thing from your chart in it. The map is not the territory, but they do know each other.']:
    y = para(d, y + 8, '· ' + r, F_SMALL, SOFT)
y = center(d, y + 40, '✦', font('dejavu/DejaVuSans.ttf', 44), GOLD)
y = center(d, y + 40, 'Semilla Cósmica', F_H2, INK)
y = center(d, y + 14, 'skies that are sown, moments that are looked at', F_IT, SOFT)
y = center(d, y + 14, 'etsy.com/shop/LaSemillaCosmica', F_SMALL, SOFT)
footer(d, pn); pages.append(img)

# ---------- conclusions by area (v2) ----------
HOUSE_SHORT = {
 1: 'in the open: your presence arrives before your words do',
 2: 'on the ground floor of life: what you own, what you earn, what makes you feel worth something',
 3: 'in the everyday mind: talk, learning, the streets you know by heart',
 4: 'in the roots: home, family, the private floor everything rests on',
 5: 'in the play: creation, romance, and the joy that exists for no reason',
 6: 'in the everyday: work, health, and the small repeated acts that become a life',
 7: 'in the mirror of the other: partners and close one-on-one bonds',
 8: 'in the deep end: intimacy, crisis, and what transforms by going through',
 9: 'in the far field: travel, study, belief, the long questions',
 10: 'in the open sky of your life: the career, the direction people can see',
 11: 'in the tribe: friends, groups, causes, the future built with others',
 12: 'behind the curtain: solitude, dreams, and everything that works best unseen',
}
LOVE_SIGN = {
 'Aries': 'you love the way a match strikes: fast, bright, and honest about wanting',
 'Taurus': 'you love the way earth loves: slowly, physically, and for keeps',
 'Gemini': 'you love with your mind first: the conversation is the courtship',
 'Cancer': 'you love like a tide: you wrap around people and you remember everything',
 'Leo': 'you love generously and out loud: you want to be chosen, visibly',
 'Virgo': 'you love in details: the soup, the fix, the plan that says I pay attention',
 'Libra': 'you love in pairs: fairness, beauty, and someone to hold the other end of the seesaw',
 'Scorpio': 'you love all the way down or not at all: half-love reads as no love',
 'Sagittarius': 'you love with room in it: a partner should be a road, not a fence',
 'Capricorn': 'you love like a builder: loyalty shown in deeds, tested by time',
 'Aquarius': 'you love like a friend first: freedom inside the bond, loyalty to the odd ones',
 'Pisces': 'you love like water: you take the shape of the person, sometimes until you disappear',
}
WORK_SIGN = {
 'Aries': 'you go after things by starting them: courage first, plan second',
 'Taurus': 'you work like slow stone: nothing flashy, and nothing moved',
 'Gemini': 'you work with five irons in the fire, and your best ideas arrive mid-sentence',
 'Cancer': 'you work to protect: the job is personal, the team is family',
 'Leo': 'you work to make something worth seeing, and praise lands as fuel',
 'Virgo': 'you work by improving: you find the flaw everyone missed and you fix it',
 'Libra': 'you work through people: deals, balance, the elegance of a fair arrangement',
 'Scorpio': 'you work like a diver: one deep project at a time, all the way to the bottom',
 'Sagittarius': 'you work toward the horizon: give it the meaning and the miles do themselves',
 'Capricorn': 'you work like a mountain road: switchbacks, altitude, arrival',
 'Aquarius': 'you work like a systems-thinker: fix the machine, not just the leak',
 'Pisces': 'you work like a dreamer who delivers: inspiration first, then the craft to land it',
}
FAM_SIGN = {
 'Aries': 'you need to feel brave in your own house',
 'Taurus': 'you need calm you can touch: food, softness, things that stay',
 'Gemini': 'you need talk in the house: a mind beside you, questions at dinner',
 'Cancer': 'you need to be the keeper, and to be kept',
 'Leo': 'you need to be someone\'s delight, not just someone\'s helper',
 'Virgo': 'you need order you made yourself: a clean shore in a wavy world',
 'Libra': 'you need peace in the room more than you will ever admit',
 'Scorpio': 'you need to trust the people behind the door: shallow comfort feels like none',
 'Sagittarius': 'you need a window: even a safe home wants a horizon',
 'Capricorn': 'you need to be useful to be calm; rest feels earned or not at all',
 'Aquarius': 'you need a little distance even from the people you love most',
 'Pisces': 'you need a shore: somewhere soft to come back to after absorbing the day',
}
MIND_SIGN = {
 'Aries': 'your mind moves fast and decides fast, and it would rather be wrong now than late',
 'Taurus': 'your mind is a slow carpenter: it measures twice and builds to last',
 'Gemini': 'your mind is a hungry magpie: it collects questions, words and shiny connections',
 'Cancer': 'your mind thinks in memories: every idea arrives attached to a feeling',
 'Leo': 'your mind thinks in stories: it wants the idea that can be told',
 'Virgo': 'your mind is an editor: it finds the flaw, the typo, the detail everyone missed',
 'Libra': 'your mind weighs both sides so well that deciding becomes the hard part',
 'Scorpio': 'your mind is a detective: it does not accept the surface of anything',
 'Sagittarius': 'your mind thinks in big pictures: details bore it, meaning feeds it',
 'Capricorn': 'your mind is an engineer: it wants structure, proof, and a plan that survives Monday',
 'Aquarius': 'your mind is a pattern-finder: it sees the system while everyone is inside it',
 'Pisces': 'your mind thinks sideways: it arrives at truth by dream, hunch and image',
}
MONEY_SIGN = {
 'Aries': 'money grows for you when you move first and count later',
 'Taurus': 'money grows the slow way: saved, planted, compounding in silence',
 'Gemini': 'money grows through your mouth and your hands: talk, trade, teach, sell',
 'Cancer': 'money grows around home and the people you feed: care turning into income',
 'Leo': 'money grows in the spotlight: what you make and show, people pay for',
 'Virgo': 'money grows through skill: get really good at one serviceable thing',
 'Libra': 'money grows in partnership: deals, pairs, half of something bigger',
 'Scorpio': 'money grows in the deep end: other people\'s money, big risks, total rebuys',
 'Sagittarius': 'money grows on horizons: abroad, in books, in anything that widens you',
 'Capricorn': 'money grows with time on your side: long climbs, real positions',
 'Aquarius': 'money grows in the new: technology, groups, the thing nobody does yet',
 'Pisces': 'money grows where you give shape to the invisible: art, care, imagination',
}
KIND_PLAIN = {
 'conjunction': 'they are fused: press one button and both go off together',
 'sextile': 'they quietly help each other: use one and the other comes along free',
 'square': 'they push against each other, and that friction is where your strength gets made',
 'trine': 'they flow together so naturally the gift is easy to miss',
 'opposition': 'they take turns running the show, and your work is holding both at once',
}

def cusp_sign(h):
    return SIGNS[int((cusps[h-1] % 360.0) // 30) % 12]

def area_aspect(planets):
    best = None
    for f in found_aspects:
        if f['a'] in planets or f['b'] in planets:
            if best is None or f['weight'] > best['weight']:
                best = f
    return best

def area_paragraph(key):
    """Returns (named_text, plain_text): named names the signs, plain does not."""
    if key == 'ego':
        sign, house = positions['Sun']['sign'], positions['Sun']['house']
        named = f'Your ego is {sign}: {ZODIAC[sign][1]}. It does its work {HOUSE_SHORT[house]}.'
        f = area_aspect({'Sun', 'ASC'})
        if f:
            named += f' The strongest current in it is the {f["name"]} of {f["a"]} and {f["b"]}: {KIND_PLAIN[f["name"]]}.'
        plain = f'{HOUSE_SHORT[house]}. And {SIGN_WORK[sign][:-1]}.'
    elif key == 'amor':
        sign, house = positions['Venus']['sign'], positions['Venus']['house']
        h7 = cusp_sign(7)
        named = f'You love the way {sign} loves: {LOVE_SIGN[sign]}. It does its work {HOUSE_SHORT[house]}.'
        named += f' Partnership opens in {h7}: {ZODIAC[h7][1]}.'
        f = area_aspect({'Venus'})
        if f:
            named += f' And it answers to the {f["name"]} of {f["a"]} and {f["b"]}: {KIND_PLAIN[f["name"]]}.'
        plain = f'{LOVE_SIGN[sign]}, {HOUSE_SHORT[house]}. And {SIGN_WORK[sign][:-1]}.'
    elif key == 'trabajo':
        sign, house = positions['Mars']['sign'], positions['Mars']['house']
        mc_s = SIGNS[int(mc_lon // 30) % 12]
        named = f'You work the way {sign} works: {WORK_SIGN[sign]}. It does its work {HOUSE_SHORT[house]}.'
        named += f' The visible direction of your life is a {mc_s} direction: {ZODIAC[mc_s][1]}.'
        f = area_aspect({'Mars'})
        if f:
            named += f' Its strongest current is the {f["name"]} of {f["a"]} and {f["b"]}: {KIND_PLAIN[f["name"]]}.'
        plain = f'{WORK_SIGN[sign]}, {HOUSE_SHORT[house]}. And {SIGN_WORK[sign][:-1]}.'
    elif key == 'dinero':
        sign, house = positions['Jupiter']['sign'], positions['Jupiter']['house']
        h2 = cusp_sign(2)
        named = f'For you, {MONEY_SIGN[sign]}, and Jupiter carries it {HOUSE_SHORT[house]}.'
        named += f' The house of worth opens in {h2}: {ZODIAC[h2][1]}.'
        plain = f'{MONEY_SIGN[sign]}. And {SIGN_WORK[sign][:-1]}.'
    elif key == 'familia':
        sign, house = positions['Moon']['sign'], positions['Moon']['house']
        h4 = cusp_sign(4)
        named = f'Inside, {FAM_SIGN[sign]}. Your inner weather lives {HOUSE_SHORT[house]}.'
        named += f' Your roots open in {h4}: {ZODIAC[h4][1]}.'
        f = area_aspect({'Moon'})
        if f:
            named += f' And it answers to the {f["name"]} of {f["a"]} and {f["b"]}: {KIND_PLAIN[f["name"]]}.'
        plain = f'{FAM_SIGN[sign]}, {HOUSE_SHORT[house]}. And {SIGN_WORK[sign][:-1]}.'
    else:  # mente
        sign, house = positions['Mercury']['sign'], positions['Mercury']['house']
        h3 = cusp_sign(3)
        named = f'{MIND_SIGN[sign][0].upper()}{MIND_SIGN[sign][1:]}. It does its work {HOUSE_SHORT[house]}.'
        if positions['Mercury']['retro']:
            named += ' It runs retrograde: it works inward, privately, from the inside out.'
        named += f' The everyday mind opens in {h3}: {ZODIAC[h3][1]}.'
        f = area_aspect({'Mercury'})
        if f:
            named += f' And it answers to the {f["name"]} of {f["a"]} and {f["b"]}: {KIND_PLAIN[f["name"]]}.'
        plain = f'{MIND_SIGN[sign]}, {HOUSE_SHORT[house]}. And {SIGN_WORK[sign][:-1]}.'
    return named, plain

AREAS = [
 ('ego', 'Ego'), ('amor', 'Amor'), ('trabajo', 'Trabajo'),
 ('dinero', 'Dinero'), ('familia', 'Familia'), ('mente', 'Mente'),
]
area_data = {k: area_paragraph(k) for k, _ in AREAS}

AREA_LABEL = {'ego': 'SELF', 'amor': 'LOVE', 'trabajo': 'WORK', 'dinero': 'MONEY',
              'familia': 'FAMILY', 'mente': 'MIND'}
AREA_TIP = {
 'ego': 'One practice this month: do one thing well with nobody watching. That is your Sun off duty.',
 'amor': 'One practice: name what you need out loud, once, before resenting it quietly. Venus rewards the brave.',
 'trabajo': 'One practice: pick the smallest real step toward the big thing, and take it on a Tuesday. Mars respects Tuesdays.',
 'dinero': 'One practice: track what you earn and what you spend for thirty days. Jupiter grows where attention goes.',
 'familia': 'One practice: this week, ask someone in your home what they need, and just listen. The Moon keeps score of care.',
 'mente': 'One practice: carry one question around for three days before answering it. Mercury gets wiser when it waits.',
}
for i in range(0, len(AREAS), 2):
    img, d = new_page(); pn += 1
    y = center(d, 130, 'THE CONCLUSION' if i == 0 else 'THE CONCLUSION, CONTINUED', F_H1)
    y = hr(d, y + 26)
    for k, label in AREAS[i:i+2]:
        named, _plain = area_data[k]
        y = center(d, y + 8, AREA_LABEL[k], F_H2, GOLD)
        y = para(d, y + 14, named)
        y = para(d, y + 8, AREA_TIP[k], F_IT, SOFT)
        y = hr(d, y + 12)
    footer(d, pn); pages.append(img)

# final: the whole thing, no astro names
img, d = new_page(); pn += 1
y = center(d, 130, 'IN PLAIN WORDS', F_H1)
y = center(d, y + 14, 'no planet names from here on. just you.', F_IT, SOFT)
y = hr(d, y + 22)
PLAIN_NOUN = {'ego': 'How you show up', 'amor': 'How you love', 'trabajo': 'How you work',
              'dinero': 'How worth and money come', 'familia': 'Family and roots', 'mente': 'How your mind runs'}
for k, _ in AREAS:
    _n, plain = area_data[k]
    if plain.endswith('..'):
        plain = plain[:-1]
    y = para(d, y + 6, PLAIN_NOUN[k] + ': ' + plain, F_BODY)
    y += 6
center(d, y + 26, 'If you keep one page of this notebook, keep this one. This is the chart, translated.', F_IT, SOFT)
footer(d, pn); pages.append(img)

# ---------- final: a note from the one who drew your sky ----------
img, d = new_page(); pn += 1
y = center(d, 170, 'A NOTE FROM THE ONE WHO DREW YOUR SKY', F_H1)
y = hr(d, y + 26)
y = para(d, y + 10,
 'I want to be honest with you about what this is. I did not write this notebook for a category of '
 'people. I wrote it for one person: you, at this address, at this minute of this morning. '
 'Every degree on these pages was computed; nothing was guessed. But the words around the numbers '
 'were chosen with care, and the care is the part that is real on my side of the paper.')
y = para(d, y + 18,
 'Here is what I hope happens next. Somewhere in these pages there is a line that will find you '
 'on an ordinary afternoon, maybe a month from now, maybe a year. It will not feel like news; '
 'it will feel like permission. Permission to be slow, or stubborn, or deep, or hungry for meaning — '
 'whatever your sky already is, without apologizing. When that line finds you, underline it. '
 'It was always yours.')
y = para(d, y + 18,
 'And if you ever want the sky of a moment that mattered to you — not a birth, but a beginning, '
 'a goodbye, a night you want to keep — that can be drawn too. Skies are how we keep time '
 'when clocks are not enough.')
y = center(d, y + 40, '✦', font('dejavu/DejaVuSans.ttf', 44), GOLD)
y = center(d, y + 30, 'con cariño, from my desk to yours', F_IT, SOFT)
y = center(d, y + 12, 'Lior Seminare · Semilla Cósmica', F_H2, INK)
y = center(d, y + 14, 'etsy.com/shop/LaSemillaCosmica', F_SMALL, SOFT)
footer(d, pn); pages.append(img)

# ---------- save ----------
pages[0].save(P['out'], save_all=True, append_images=pages[1:], resolution=150)
print('OK', P['out'], len(pages), 'pages')
for k, v in positions.items():
    print(f'  {k:11s} {v["sign"]:12s} h{v["house"]:<2d} {v["deg"]:5.1f}° {"R" if v["retro"] else ""}')
print(f'  ASC {ASC["sign"]} {ASC["deg"]:.1f}  MC {MC["sign"]} {MC["deg"]:.1f}')
for f_ in top_aspects:
    print(f'  aspect {f_["a"]} {f_["name"]} {f_["b"]} orb {f_["orb"]:.1f}')
