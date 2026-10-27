# V46 round 18 (Omri): slide 20 (n15-stress.jpg): NEW meditating woman FACING THE CAMERA (frontal, symmetric, cross-legged, eyes closed), generated with the same room / window scene (assets/src/stress-plate-frontal.jpg).
# The generated plate replaces the photo background (no trace of the previous woman anywhere); the title, tag, subtitle, cortisol chart, legend, credit and the official logo are put back pixel-for-pixel from the previous live image
# (assets/src/n15-stress-before-r17.jpg, md5 3dec755e...), the chart's translucent fill re-applied with the measured model.
import cv2,numpy as np
O=cv2.imread('assets/src/n15-stress-before-r17.jpg');H,W=O.shape[:2];Of=O.astype(np.float32)
P=cv2.imread('assets/src/stress-plate-frontal.jpg')
# --- plate placement: woman the same size as before (~765 px tall), right half
SC=0.91;OX,OY=300,97
pw,ph=round(1920*SC),round(1080*SC)
Ps=cv2.resize(P,(pw,ph),interpolation=cv2.INTER_CUBIC).astype(np.float32)
base=np.zeros((H,W,3),np.float32)
base[OY:OY+ph,OX:]=Ps[:,:W-OX]
base[OY:OY+ph,:OX]=Ps[:,:1]*1.0            # dark wall continues to the left edge
base[:OY]=base[OY:OY+1]                    # window mullions / wall continue to the top edge
rng=np.random.RandomState(5);base+=rng.randn(H,W,1).astype(np.float32)*1.4
# soft darkening on the left so the text sits on a calm dark field (as on the previous slide)
xx=np.arange(W,dtype=np.float32)[None,:,None];navy=np.array([48,20,8],np.float32)
al=np.clip(1-xx/1200,0,1)**1.3*0.30;base=base*(1-al)+navy*al
# --- overlay (everything that is not the photo) from the previous live image
R=O[...,2].astype(int);G=O[...,1].astype(int);B=O[...,0].astype(int);mn=np.minimum(np.minimum(R,G),B)
boxes=[(50,115,60,600),(145,292,50,1000),(286,336,50,1300),(392,432,50,480),(485,525,95,175),(755,790,95,175),(795,835,150,1010),(858,948,100,885),(985,1030,1240,1830),(480,785,168,188)]
tb=np.zeros((H,W),bool)
for ya,yb,xa,xb in boxes: tb[ya:yb,xa:xb]=True
white=(mn>105)&tb
white[286:336,1000:1300]&=(mn[286:336,1000:1300]>150)
white[480:785,168:188]=(mn[480:785,168:188]>80)
roi=np.zeros((H,W),bool);roi[300:800,170:1015]=True
teal=(G>150)&(G-R>60)&roi
purp=(B>140)&(R>70)&(B-G>45)&(B-R>20)&roi
teal2=(G>150)&(G-R>60);teal2[:, :]&=False;teal2[868:940,100:140]=((G>150)&(G-R>60))[868:940,100:140]   # legend swatches (teal / purple)
S=white|teal|purp|teal2|((G>100)&(G-R>45)&(B>115)&np.zeros((H,W),bool))
purp2=np.zeros((H,W),bool);purp2[868:940,100:140]=((B>140)&(R>70)&(B-G>45)&(B-R>20))[868:940,100:140];S|=purp2
S[779:781,178:1006]=True
# the tag dot (teal) at the top-left
dot=(G>150)&(G-R>60);dm=np.zeros((H,W),bool);dm[55:115,50:110]=True;S|=(((G>110)&(G-R>40))&dm)
dm3=np.zeros((H,W),bool);dm3[65:105,110:146]=True;dm2=((G>90)&(G-R>30)&dm3);ys_,xs_=np.where(dm2);cy_,cx_=int(ys_.mean()),int(xs_.mean());rr=np.zeros((H,W),np.uint8);cv2.circle(rr,(cx_,cy_),11,1,-1);S|=rr>0   # the tag dot (disc)
S[900:950,175:900]=False   # legend line 2 is re-typeset below (the old one had a baked-in smudge under 'Six months')   # drop the old smudge under 'Six months' (not part of the text)
# --- chart fill (below the curve, above the axis): measured linear model
T=np.array([206,220,82],np.float32);alpha_y=np.clip(0.00174*(782-np.arange(H)),0,0.5).astype(np.float32)
Fm=np.zeros((H,W),bool)
for x in range(180,1008):
    ys=np.where(teal[480:790,x])[0]
    if len(ys): Fm[480+ys.max():779,x]=True
A=(alpha_y[:,None]*Fm)[...,None]
res=base*(1-A)+A*T
# --- logo: same scrim + official artwork as build-logo.py
LW,LX,LY=340,1526,28;K=LW/200
Lg=cv2.imread('../closers/img/lla-logo.png',cv2.IMREAD_UNCHANGED);lh=round(LW*Lg.shape[0]/Lg.shape[1]);Lg=cv2.resize(Lg,(LW,lh),interpolation=cv2.INTER_AREA)
yy,xx2=np.mgrid[0:H,0:W].astype(np.float32);d=((xx2-(LX+LW/2))/(170*K))**2+((yy-(LY+45*K))/(95*K))**2;sc=(0.45*np.exp(-d*1.6))[...,None]
res=res*(1-sc)+navy*sc
a=Lg[:,:,3:].astype(np.float32)/255;res[LY:LY+lh,LX:LX+LW]=Lg[:,:,:3]*a+res[LY:LY+lh,LX:LX+LW]*(1-a)
# --- strokes back, exactly from the previous image
Sw=cv2.GaussianBlur(cv2.dilate(S.astype(np.uint8),np.ones((3,3),np.uint8)).astype(np.float32),(0,0),0.7)[...,None]
res=res*(1-Sw)+Of*Sw
from PIL import Image,ImageDraw,ImageFont
f4=ImageFont.truetype('/usr/share/fonts/truetype/sand-box/google/Outfit/Outfit-VariableFont_wght.ttf',28*4);f4.set_variation_by_axes([400])
lay=Image.new('L',(W*4//4*4,90*4),0)
lay=Image.new('L',(1000*4,90*4),0);ImageDraw.Draw(lay).text(((188-100)*4,(933-880)*4),'Six months of daily meditation \u2014 normalized, and still is',font=f4,fill=255,anchor='ls')
la=(np.array(lay.resize((1000,90),Image.LANCZOS)).astype(np.float32)/255)[...,None]
reg=res[880:970,100:1100];res[880:970,100:1100]=reg*(1-la)+np.array([246,228,222],np.float32)*la   # BGR of (222,228,246)
cv2.imwrite('assets/n15-stress.jpg',np.clip(res,0,255).astype(np.uint8),[cv2.IMWRITE_JPEG_QUALITY,95])
