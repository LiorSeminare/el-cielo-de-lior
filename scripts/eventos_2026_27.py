import swisseph as swe
from datetime import datetime, timedelta, timezone

TZ = timezone(timedelta(hours=-3))
def jd_local(y,m,d,hh=0,mm=0):
    return swe.julday(y,m,d,hh+mm/60.0)
def to_local(jd):
    y,mo,d,h = swe.revjul(jd)
    dt = datetime(y,mo,d) + timedelta(hours=h)
    return (dt + timedelta(hours=-3)).strftime('%a %d %b %Y %H:%M') + ' ART'

start = swe.julday(2026,10,1,0.0)
end   = swe.julday(2027,4,1,0.0)

print("=== FASES LUNARES (oct 2026 - mar 2027) ===")
jd = start - 1
while jd < end:
    jd, ret = swe.lun_eclipse_when(start if jd<start else jd+0.1, swe.FLG_MOSEPH, 0) if False else (jd,0)
    break
# moon phases: scan angle
jd = start - 0.5
step = 0.05
prev = None
phase_names = {0:'Luna nueva',90:'Cuarto creciente',180:'Luna llena',270:'Cuarto menguante'}
last_print = None
angle_prev = None
while jd < end:
    jd += step
    ang = (swe.get_ayanamsa if False else 0)
    m = swe.calc_ut(jd, swe.MOON, swe.FLG_MOSEPH)[0][0]
    s = swe.calc_ut(jd, swe.SUN, swe.FLG_MOSEPH)[0][0]
    elong = (m - s) % 360
    if angle_prev is not None:
        for target, name in phase_names.items():
            a0, a1 = angle_prev, elong
            if (a1 - a0) % 360 >= (target - a0) % 360 and (target - a0) % 360 < 360*step/ (jd - (jd-step)) if False else False:
                pass
    angle_prev = elong
print("(scanning properly)")
