# slide 19 (n16-protocol) ROUND 16 (Omri): same re-lay as round 10 (reproduced byte-for-byte from the pre-round-10 base), then: toned-down neon, no neon outside the eating window, every dot its own colour, 'Order of operations' removed, 'Built backward' centred and enlarged.
# (base image: git show 225f020^:slide-canvas/v46/assets/n16-protocol.jpg, saved as assets/src/protocol-base.jpg)
# ROUND 10 notes: whole-slide re-lay of the protocol band. Photo background, title, palette kept.
# - ticks proportional to time (5 AM .. 9 PM), every label (time + action) centred on its tick, one level row of times above and below, identical time->action gap, one-line actions
# - eating window lit as a neon band (8 AM - 6 PM) with its label centred on it
# - bottom area redrawn as two separate neon chunks (sentence-case headings), italic line kept
import cv2,numpy as np,subprocess
from PIL import Image,ImageDraw,ImageFont
G='/workspace/lla-masterclass-syllabus'
src=cv2.imdecode(np.frombuffer(open('assets/src/protocol-base.jpg','rb').read(),np.uint8),1)
H,W=src.shape[:2]
PF='/usr/share/fonts/truetype/sand-box/google/Playfair Display/PlayfairDisplay-VariableFont_wght.ttf'
PFI='/usr/share/fonts/truetype/sand-box/google/Playfair Display/PlayfairDisplay-Italic-VariableFont_wght.ttf'
OF='/usr/share/fonts/truetype/sand-box/google/Outfit/Outfit-VariableFont_wght.ttf'
def fnt(p,s,w=None):
    f=ImageFont.truetype(p,s)
    if w:
        try:f.set_variation_by_axes([w])
        except Exception:pass
    return f
ORANGE=(240,163,94);CREAM=(243,235,221);LB=(138,210,255);DUSTY=(157,179,214);PALE=(214,222,236);BLUE=(0,110,255)
def pill(mask,x0,y0,x1,y1,t,val=255):
    r=(y1-y0)//2
    if t<0:cv2.rectangle(mask,(x0+r,y0),(x1-r,y1),val,-1)
    else:cv2.line(mask,(x0+r,y0),(x1-r,y0),val,t);cv2.line(mask,(x0+r,y1),(x1-r,y1),val,t)
    cv2.ellipse(mask,(x0+r,(y0+y1)//2),(r,r),0,90,270,val,t);cv2.ellipse(mask,(x1-r,(y0+y1)//2),(r,r),0,-90,90,val,t)

# ---------------- 1) erase old text / nodes / line / band outline
im=src.copy()
def erase_rect(img,box,thr=16,dil=9,r=6,k=61):
    x0,y0,x1,y1=box;sub=cv2.copyMakeBorder(img,40,40,40,40,cv2.BORDER_REFLECT)[y0:y1+80,x0:x1+80]
    bg=cv2.medianBlur(sub,k).astype(int);d=np.abs(sub.astype(int)-bg).max(2)[40:-40,40:-40]
    m=np.zeros(img.shape[:2],np.uint8);m[y0:y1,x0:x1]=cv2.dilate((d>thr).astype(np.uint8)*255,np.ones((dil,dil),np.uint8))
    return cv2.inpaint(img,m,r,cv2.INPAINT_TELEA)
for box in [(20,380,1900,530),(900,522,1700,566),(20,690,1900,832)]:
    im=erase_rect(im,box)
# nodes + line
m=np.zeros((H,W),np.uint8)
for x in (158,360,460,566,860,953,1200,1462,1658,1756):cv2.circle(m,(x,611),(66 if x>1700 else 44),255,-1)
cv2.line(m,(110,611),(1810,611),255,26)
# old band outline (thin ring around the pill 460..1462 x 572..650)
ring=np.zeros((H,W),np.uint8)
pill(ring,460,572,1462,650,9)
im=cv2.inpaint(im,cv2.bitwise_or(m,ring),7,cv2.INPAINT_TELEA)
oldband=np.zeros((H,W),np.uint8);pill(oldband,456,566,1466,656,-1)
sm=cv2.resize(im,(W//4,H//4),interpolation=cv2.INTER_AREA);mm=cv2.resize(oldband,(W//4,H//4),interpolation=cv2.INTER_NEAREST)
mm=cv2.dilate(mm,np.ones((3,3),np.uint8))
fl_=cv2.inpaint(sm,mm,9,cv2.INPAINT_TELEA);fl_=cv2.GaussianBlur(fl_,(0,0),1.5);fl_=cv2.resize(fl_,(W,H),interpolation=cv2.INTER_CUBIC)
fa_=cv2.GaussianBlur(oldband.astype(np.float32)/255,(0,0),4)[...,None]
rng0=np.random.RandomState(4);fl_=np.clip(fl_.astype(np.float32)+rng0.randn(H,W,1)*1.6,0,255)
im=(im.astype(np.float32)*(1-fa_)+fl_*fa_).astype(np.uint8)
# bottom area: whole zone inpainted at low resolution, then a soft dark floor
bm=np.zeros((H,W),np.uint8);bm[812:1040,50:1890]=255
s4=4;sm=cv2.resize(im,(W//s4,H//s4),interpolation=cv2.INTER_AREA);mm=cv2.resize(bm,(W//s4,H//s4),interpolation=cv2.INTER_NEAREST)
fill=cv2.inpaint(sm,mm,9,cv2.INPAINT_TELEA);fill=cv2.GaussianBlur(fill,(0,0),2)
fill=cv2.resize(fill,(W,H),interpolation=cv2.INTER_CUBIC)
fa=cv2.GaussianBlur(bm.astype(np.float32)/255,(0,0),6)[...,None]
rng=np.random.RandomState(2);fill=np.clip(fill.astype(np.float32)+rng.randn(H,W,1)*1.6,0,255)
im=(im.astype(np.float32)*(1-fa)+fill*fa).astype(np.uint8)
# soft dark floor under the bottom area (no edges): vertical gradient
yy=np.arange(H,dtype=np.float32)[:,None,None]
fl=np.clip((yy-790)/70.0,0,1)*0.50
im=(im.astype(np.float32)*(1-fl)).astype(np.uint8)
# ---------------- helpers (all in RGB float, composited at the end)
F=cv2.cvtColor(im,cv2.COLOR_BGR2RGB).astype(np.float32)
def textmask(txt,x,yb,font,anchor='ms',track=0.0):
    pil=Image.new('L',(W,H),0);d=ImageDraw.Draw(pil)
    if track:
        wtot=sum(font.getlength(c)+track for c in txt)-track;xx=x-wtot/2 if anchor[0]=='m' else x
        for c in txt:d.text((xx,yb),c,font=font,fill=255,anchor='ls');xx+=font.getlength(c)+track
    else:d.text((x,yb),txt,font=font,fill=255,anchor=anchor)
    return np.asarray(pil,np.float32)/255
def comp(F,a,col,glow=0.0,gsig=7,shadow=0.55):
    # dark soft shadow behind (legibility), optional neon glow, then the text itself
    if shadow:
        sh=cv2.GaussianBlur(a,(0,0),5)[...,None]*shadow;F=F*(1-sh)
    if glow:
        g=cv2.GaussianBlur(a,(0,0),gsig)[...,None]*glow+cv2.GaussianBlur(a,(0,0),2.5)[...,None]*glow*0.55
        F=255-(255-F)*(1-np.clip(g,0,1)*np.array(col,np.float32)/255)
    c=np.array(col,np.float32)
    core=c+(255-c)*0.18 if glow else c
    A=a[...,None];return F*(1-A)+core*A
def neon_line(F,pts,col,w=3,glow=0.9,sig=9,closed=False):
    m=np.zeros((H,W),np.uint8)
    for p,q in zip(pts[:-1],pts[1:]):cv2.line(m,p,q,255,w,cv2.LINE_AA)
    a=m.astype(np.float32)/255;c=np.array(col,np.float32)
    g=cv2.GaussianBlur(a,(0,0),sig)[...,None]*glow+cv2.GaussianBlur(a,(0,0),sig/3)[...,None]*glow*0.6
    F=255-(255-F)*(1-np.clip(g,0,1)*c/255)
    core=c+(255-c)*0.35;return F*(1-a[...,None])+core*a[...,None]
def neon_dot(F,x,y,col,r=8,glow=1.0,sig=12):
    m=np.zeros((H,W),np.uint8);cv2.circle(m,(x,y),r,255,-1,cv2.LINE_AA)
    a=m.astype(np.float32)/255;c=np.array(col,np.float32)
    g=cv2.GaussianBlur(a,(0,0),sig)[...,None]*glow*2.2+cv2.GaussianBlur(a,(0,0),sig/3)[...,None]*glow
    F=255-(255-F)*(1-np.clip(g,0,1)*c/255)
    core=c+(255-c)*0.45;return F*(1-a[...,None])+core*a[...,None]
# ---------------- 2) eating window band: neon
def T(h):return 215+92.8*(h-5)
X0,X1,Y0,Y1=int(T(8)),int(T(18)),572,650
band=np.zeros((H,W),np.uint8);pill(band,X0,Y0,X1,Y1,-1)
bl=cv2.GaussianBlur(band.astype(np.float32)/255,(0,0),1.2)
# lit glass fill: brighter toward the middle line
gy=np.exp(-((np.arange(H)-611)/34.0)**2)[:,None];gx=np.clip(np.minimum(np.arange(W)-X0,X1-np.arange(W))/80.0,0,1)[None,:]
lit=(bl*(0.12+0.14*gy*gx))[...,None]*np.array([40,150,255],np.float32)/255
F=255-(255-F)*(1-lit)
# outer glow + neon outline
ol=np.zeros((H,W),np.uint8);pill(ol,X0,Y0,X1,Y1,3)
a=cv2.GaussianBlur(ol.astype(np.float32)/255,(0,0),0.8)
g=cv2.GaussianBlur(ol.astype(np.float32)/255,(0,0),14)[...,None]*0.95+cv2.GaussianBlur(ol.astype(np.float32)/255,(0,0),4)[...,None]*0.5
cb=np.array(LB,np.float32)/255
F=255-(255-F)*(1-np.clip(g,0,0.45)*cb)
F=F*(1-a[...,None])+(np.array(LB,np.float32)*0.8+255*0.2)*a[...,None]
# ---------------- 3) timeline line + nodes (proportional to time)
hrs=[5,7,8,10,11,13,16,18,20,21]
cols={5:(155,123,255),7:(43,211,192),8:(47,155,254),10:(243,235,221),11:(240,163,94),13:(127,227,160),16:(246,220,140),18:(255,127,138),20:(213,139,255),21:(234,242,255)}   # ten different colours
xs_=np.arange(W,dtype=np.float32);px=[T(h) for h in hrs]
colx=np.stack([np.interp(xs_,px,[cols[h][k] for h in hrs]) for k in range(3)],1).astype(np.float32)[None]   # (1,W,3)
lm=np.zeros((H,W),np.uint8);cv2.line(lm,(int(T(5)),611),(int(T(21)),611),255,5,cv2.LINE_AA)
la=lm.astype(np.float32)/255
inwin=np.zeros((H,W),np.float32);inwin[:,int(T(8)):int(T(18))+1]=1;inwin=cv2.GaussianBlur(inwin,(0,0),10)[...,None]
lg=(cv2.GaussianBlur(la,(0,0),7)[...,None]*0.20+cv2.GaussianBlur(la,(0,0),2.3)[...,None]*0.12)*inwin   # soft light only inside the window
F=255-(255-F)*(1-np.clip(lg,0,1)*colx/255)
F=F*(1-la[...,None])+(colx+(255-colx)*0.15)*la[...,None]
def flat_dot(F,x,y,col,r):
    m=np.zeros((H,W),np.uint8);cv2.circle(m,(x,y),r,255,-1,cv2.LINE_AA);a=m.astype(np.float32)/255
    sh=cv2.GaussianBlur(a,(0,0),4)[...,None]*0.35;F=F*(1-sh)
    c=np.array(col,np.float32);return F*(1-a[...,None])+c*a[...,None]
for h in hrs:
    x=int(round(T(h)));c=cols[h];r=22 if h==21 else 15
    if 8<=h<=18:F=neon_dot(F,x,611,c,r=r,glow=0.32,sig=10)
    else:F=flat_dot(F,x,611,c,r)
# ---------------- 4) texts
TF=fnt(PF,38,500);AF=fnt(OF,24,400)
UP=[(5,"5:00 AM","Wake · water · prayer · light",ORANGE,CREAM),(8,"8:00 AM","Eating window opens",ORANGE,CREAM),(11,"11:00 AM","Main meal, then a walk",ORANGE,CREAM),
    (16,"4:00 PM","Dinner",ORANGE,CREAM),(18,"6:00 PM","Kitchen closes",ORANGE,CREAM),(21,"9:00 PM","Lights out",PALE,PALE)]
LO=[(7,"7:00 AM","Movement & sauna",ORANGE,CREAM),(10,"10:00 AM","Caffeine cut-off",CREAM,CREAM),(13,"1:00 PM","Stress reset",LB,CREAM),(20,"8:00 PM","Screens off",DUSTY,PALE)]
GAP=44
UT,UA=450,450+GAP          # upper: time baseline, action baseline
LT=749;LA=LT+GAP           # lower
for rowdefs,tb,ab,up in ((UP,UT,UA,True),(LO,LT,LA,False)):
    for h,t,a_,ct,ca in rowdefs:
        x=T(h)
        F=comp(F,textmask(t,x,tb,TF),ct,glow=(0.10 if 8<=h<=18 else 0.0),gsig=8,shadow=0.5)
        F=comp(F,textmask(a_,x,ab,AF),ca,glow=0,shadow=0.55)
        # short tick hairline from the node toward its label
        y0,y1=(611-24,611-44) if up else (611+24,611+44)
        F=neon_line(F,[(int(round(x)),y0),(int(round(x)),y1)],ct,w=2,glow=(0.12 if 8<=h<=18 else 0.0),sig=5)
# eating window label centred on the band
cxb=(X0+X1)/2
EF=fnt(OF,26,500)
F=comp(F,textmask("10-hour eating window · 8 AM – 6 PM",cxb,553,EF),LB,glow=0.30,gsig=8,shadow=0.5)
# ---------------- 5) bottom: ONE block, centred, enlarged (heading 40, steps 32, italic line 30; 'Order of operations' removed)
HF=fnt(PF,40,500);BF=fnt(OF,32,500);IF=fnt(PFI,30,400)
items=[("Lights out 9 PM",PALE),("Kitchen closes 6 PM",ORANGE),("Window opens 8 AM",ORANGE)]
DOT=26;ARW=80;PADA=22
wseq=sum(DOT+BF.getlength(t) for t,_ in items)+(len(items)-1)*(PADA*2+ARW)
CX=W/2
def seq(F,items,x,y):
    for i,(txt,col) in enumerate(items):
        F=neon_dot(F,int(x),y,col,r=8,glow=0.30,sig=9);x+=DOT
        a=textmask(txt,x,y+11,BF,anchor='ls');w=BF.getlength(txt)
        F=comp(F,a,col,glow=0.22,gsig=7,shadow=0.4);x+=w
        if i<len(items)-1:
            x+=PADA;F=neon_line(F,[(int(x),y),(int(x+ARW),y)],LB,w=2,glow=0.30,sig=7)
            for sgn in(-1,1):F=neon_line(F,[(int(x+ARW),y),(int(x+ARW-11),y+sgn*8)],LB,w=2,glow=0.25,sig=5)
            x+=ARW+PADA
    return F,x
F=comp(F,textmask("Built backward from bedtime",CX,886,HF,anchor='ms'),PALE,glow=0.2,gsig=9,shadow=0.4)
hw=HF.getlength("Built backward from bedtime");UL=int(max(hw,0)*0.62)
F=neon_line(F,[(int(CX-UL/2),906),(int(CX+UL/2),906)],LB,w=2,glow=0.30,sig=8)
F,xe=seq(F,items,CX-wseq/2+8,962)
F=comp(F,textmask("My 5 AM might be your 6:30. Borrow the order, not the clock.",CX,1022,IF,anchor='ms'),CREAM,glow=0.0,shadow=0.5)
print('seq width',wseq,'span',CX-wseq/2,xe)
out=cv2.cvtColor(np.clip(F,0,255).astype(np.uint8),cv2.COLOR_RGB2BGR)
cv2.imwrite('assets/n16-protocol.jpg',out,[cv2.IMWRITE_JPEG_QUALITY,95])

