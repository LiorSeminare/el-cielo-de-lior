from PIL import Image, ImageDraw, ImageFilter
import math

W,H = 1900, 1500
img = Image.new('RGB',(W,H))
d = ImageDraw.Draw(img)

# --- navy wall with vertical gradient + vignette ---
top=(24,34,58); bot=(13,19,36)
for y in range(H):
    t=y/H
    c=tuple(int(top[i]+(bot[i]-top[i])*t) for i in range(3))
    d.line([(0,y),(W,y)],fill=c)

# soft warm lamp glow upper-left
glow=Image.new('L',(W,H),0); gd=ImageDraw.Draw(glow)
for r in range(700,0,-8):
    a=int(70*(1-r/700)**2)
    gd.ellipse([280-r,180-r,280+r,180+r],fill=a)
warm=Image.new('RGB',(W,H),(255,214,150))
img=Image.composite(warm,img,glow)
img=img.filter(ImageFilter.GaussianBlur(60))
base=img.copy()

# subtle plaster noise
import random
random.seed(7)
noise=Image.effect_noise((W,H),18).convert('L')
img=Image.composite(Image.new('RGB',(W,H),(70,86,120)),base,noise.point(lambda p: p//5))

d=ImageDraw.Draw(img)

# --- floor hint (wood) bottom 14% ---
fy=int(H*0.86)
wood_top=(52,38,28); wood_bot=(30,21,15)
for y in range(fy,H):
    t=(y-fy)/(H-fy)
    c=tuple(int(wood_top[i]+(wood_bot[i]-wood_top[i])*t) for i in range(3))
    d.line([(0,y),(W,y)],fill=c)
# skirting line
d.line([(0,fy),(W,fy)],fill=(90,70,50),width=3)

# --- poster (A3 3508x4961 -> fit) ---
ph=int(H*0.66); pw=int(ph*3508/4961)
poster=Image.open('event_geminidas_a3.png').resize((pw,ph),Image.LANCZOS)

cx,cy = W//2, int(H*0.47)
# mat + frame
mat_pad=int(pw*0.09)
frame_w=int(pw*0.055)

# shadow (soft, offset right-down)
sh=Image.new('RGBA',(W,H),(0,0,0,0)); sd=ImageDraw.Draw(sh)
sd.rectangle([cx-pw//2-mat_pad-frame_w+18, cy-ph//2-mat_pad-frame_w+22,
              cx+pw//2+mat_pad+frame_w+18, cy+ph//2+mat_pad+frame_w+22],fill=(0,0,0,150))
sh=sh.filter(ImageFilter.GaussianBlur(30))
img=Image.alpha_composite(img.convert('RGBA'),sh).convert('RGB')
d=ImageDraw.Draw(img)

# frame (warm wood)
fx0,fy0=cx-pw//2-mat_pad-frame_w, cy-ph//2-mat_pad-frame_w
fx1,fy1=cx+pw//2+mat_pad+frame_w, cy+ph//2+mat_pad+frame_w
# wood gradient stripes
for i,x in enumerate(range(fx0,fx1)):
    t=(x-fx0)/(fx1-fx0)
    c=(int(122+30*math.sin(t*40)),int(88+22*math.sin(t*40+1)),int(58+14*math.sin(t*40+2)))
    d.line([(x,fy0),(x,fy1)],fill=c)
d.rectangle([fx0,fy0,fx1,fy1],outline=(40,27,16),width=2)

# mat
mx0,my0=fx0+frame_w,fy0+frame_w; mx1,my1=fx1-frame_w,fy1-frame_w
d.rectangle([mx0,my0,mx1,my1],fill=(240,236,228))
d.rectangle([mx0,my0,mx1,my1],outline=(215,210,198),width=1)

# poster paste
px0,py0=cx-pw//2, cy-ph//2
img.paste(poster,(px0,py0))
# thin inner shadow on poster edges
d.rectangle([px0,py0,px0+2,py0+ph],fill=(180,175,165))
d.rectangle([px0,py0,px0+pw,py0+2],fill=(180,175,165))

# glass sheen: diagonal light band
sheen=Image.new('L',(W,H),0); sdw=ImageDraw.Draw(sheen)
sdw.polygon([(fx0, fy1),(fx0+int(pw*0.35), fy1),(fx1, fy0+int(ph*0.15)),(fx1, fy0+int(ph*0.55))],fill=26)
sheen=sheen.filter(ImageFilter.GaussianBlur(25))
img=Image.composite(Image.new('RGB',(W,H),(255,255,255)),img,sheen)

img.save('event_geminidas_cuadro.jpg',quality=88)
print('ok', img.size)
