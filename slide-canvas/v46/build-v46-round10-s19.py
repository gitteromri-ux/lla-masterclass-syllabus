# slide 19 (n16-protocol) ROUND 10: whole-slide re-lay of the protocol band. Photo background, title, palette kept.
# - ticks proportional to time (5 AM .. 9 PM), every label (time + action) centred on its tick, one level row of times above and below, identical time->action gap, one-line actions
# - eating window lit as a neon band (8 AM - 6 PM) with its label centred on it
# - bottom area redrawn as two separate neon chunks (sentence-case headings), italic line kept
import cv2,numpy as np,subprocess
from PIL import Image,ImageDraw,ImageFont
G='/workspace/lla-masterclass-syllabus'
src=cv2.imdecode(np.frombuffer(subprocess.check_output(['git','-C',G,'show','HEAD:slide-canvas/v46/assets/n16-protocol.jpg']),np.uint8),1)
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
lit=(bl*(0.20+0.30*gy*gx))[...,None]*np.array([40,150,255],np.float32)/255
F=255-(255-F)*(1-lit)
# outer glow + neon outline
ol=np.zeros((H,W),np.uint8);pill(ol,X0,Y0,X1,Y1,3)
a=cv2.GaussianBlur(ol.astype(np.float32)/255,(0,0),0.8)
g=cv2.GaussianBlur(ol.astype(np.float32)/255,(0,0),14)[...,None]*2.6+cv2.GaussianBlur(ol.astype(np.float32)/255,(0,0),4)[...,None]*1.4
cb=np.array(LB,np.float32)/255
F=255-(255-F)*(1-np.clip(g,0,0.85)*cb)
F=F*(1-a[...,None])+(np.array(LB,np.float32)*0.8+255*0.2)*a[...,None]
# ---------------- 3) timeline line + nodes (proportional to time)
hrs=[5,7,8,10,11,13,16,18,20,21]
cols={5:(91,108,255),7:(43,200,224),8:(47,155,254),10:(47,155,254),11:(47,155,254),13:(78,210,197),16:(47,155,254),18:(47,155,254),20:(95,108,255),21:(138,158,253)}
# one continuous gradient line (colours interpolated between the node colours)
xs_=np.arange(W,dtype=np.float32);px=[T(h) for h in hrs]
colx=np.stack([np.interp(xs_,px,[cols[h][k] for h in hrs]) for k in range(3)],1).astype(np.float32)[None]   # (1,W,3)
lm=np.zeros((H,W),np.uint8);cv2.line(lm,(int(T(5)),611),(int(T(21)),611),255,6,cv2.LINE_AA)
la=lm.astype(np.float32)/255
lg=(cv2.GaussianBlur(la,(0,0),7)[...,None]*0.55+cv2.GaussianBlur(la,(0,0),2.3)[...,None]*0.33)
F=255-(255-F)*(1-np.clip(lg,0,1)*colx/255)
F=F*(1-la[...,None])+(colx+(255-colx)*0.35)*la[...,None]
for h in hrs:
    x=int(round(T(h)));c=cols[h]
    if h==21:
        F=neon_dot(F,x,611,c,r=22,glow=1.2,sig=16)
    else:F=neon_dot(F,x,611,c,r=15,glow=0.9,sig=11)
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
        F=comp(F,textmask(t,x,tb,TF),ct,glow=0.28,gsig=8,shadow=0.5)
        F=comp(F,textmask(a_,x,ab,AF),ca,glow=0,shadow=0.55)
        # short tick hairline from the node toward its label
        y0,y1=(611-24,611-44) if up else (611+24,611+44)
        F=neon_line(F,[(int(round(x)),y0),(int(round(x)),y1)],ct,w=2,glow=0.35,sig=5)
# eating window label centred on the band
cxb=(X0+X1)/2
EF=fnt(OF,26,500)
F=comp(F,textmask("10-hour eating window · 8 AM – 6 PM",cxb,553,EF),LB,glow=0.9,gsig=8,shadow=0.5)
# ---------------- 5) bottom: two neon chunks
HF=fnt(PF,32,500);BF=fnt(OF,24,500);IF=fnt(PFI,27,400)
def seq(F,items,x,y,gap_arrow=70):
    for i,(txt,col) in enumerate(items):
        F=neon_dot(F,int(x),y,col,r=6,glow=1.0,sig=10);x+=22
        a=textmask(txt,x,y+8,BF,anchor='ls');w=BF.getlength(txt)
        F=comp(F,a,col,glow=0.75,gsig=7,shadow=0.4);x+=w
        if i<len(items)-1:
            x+=18;F=neon_line(F,[(int(x),y),(int(x+gap_arrow),y)],LB,w=2,glow=0.8,sig=7)
            cv2_pts=[(int(x+gap_arrow),y)]
            # arrow head
            for sgn in(-1,1):F=neon_line(F,[(int(x+gap_arrow),y),(int(x+gap_arrow-9),y+sgn*6)],LB,w=2,glow=0.6,sig=5)
            x+=gap_arrow+18
    return F,x
LX=120
F=comp(F,textmask("Built backward from bedtime",LX,893,HF,anchor='ls'),PALE,glow=0.55,gsig=9,shadow=0.4)
F=neon_line(F,[(LX,909),(LX+330,909)],LB,w=2,glow=0.9,sig=8)
F,xe=seq(F,[("Lights out 9 PM",PALE),("Kitchen closes 6 PM",ORANGE),("Window opens 8 AM",ORANGE)],LX+4,958)
F=comp(F,textmask("My 5 AM might be your 6:30. Borrow the order, not the clock.",LX,1018,IF,anchor='ls'),CREAM,glow=0.0,shadow=0.5)
RX=1190
F=comp(F,textmask("Order of operations",RX,893,HF,anchor='ls'),PALE,glow=0.55,gsig=9,shadow=0.4)
F=neon_line(F,[(RX,909),(RX+250,909)],LB,w=2,glow=0.9,sig=8)
F,xe2=seq(F,[("Sleep",(110,160,255)),("Food",ORANGE),("Movement",LB),("Stress",CREAM)],RX+4,958,gap_arrow=52)
print('left seq end',xe,'right seq end',xe2)
# divider between the two chunks
dv=np.zeros((H,W),np.float32)
for y in range(868,1000):
    t=(y-868)/132.0;al=np.sin(np.pi*t)**0.8;dv[y,1118:1120]=al
g=cv2.GaussianBlur(dv,(0,0),8)[...,None]*1.5+cv2.GaussianBlur(dv,(0,0),2)[...,None]
F=255-(255-F)*(1-np.clip(g,0,1)*np.array(LB,np.float32)/255)
F=F*(1-dv[...,None])+np.array([200,235,255],np.float32)*dv[...,None]
out=cv2.cvtColor(np.clip(F,0,255).astype(np.uint8),cv2.COLOR_RGB2BGR)
cv2.imwrite('assets/n16-protocol.jpg',out,[cv2.IMWRITE_JPEG_QUALITY,95])
cv2.imwrite('/workspace/s19_r10_e.png',out)
