# V46 round 17 (Julie): slide 20 (n15-stress.jpg): move the meditating woman to the right side (same size). Chart, title, subtitle and credit stay exactly where they are (restored from the current image);
# the area she leaves is rebuilt from the surrounding wall / floor. Edited from the current live image.
import cv2,numpy as np,sys
OUT='assets/n15-stress.jpg'
O=cv2.imread('assets/src/n15-stress-before-r17.jpg'); H,W=O.shape[:2];Of=O.astype(np.float32)
DX=int(sys.argv[1]) if len(sys.argv)>1 else 740
R=O[...,2].astype(int);G=O[...,1].astype(int);B=O[...,0].astype(int)
roi=np.zeros((H,W),bool);roi[150:1080,380:1100]=True
white=np.minimum(np.minimum(R,G),B)>105
teal=(G>150)&(G-R>60)
purp=(B>140)&(R>70)&(B-G>45)&(B-R>20)
# chart / text pixels, restricted to where chart and text really are (never her hands, clothes or hair)
tb=np.zeros((H,W),bool)
for (ya,yb,xa,xb) in [(150,290,380,1100),(288,335,380,1300),(395,430,380,480),(795,835,535,670),(795,835,920,1010),(860,945,380,880)]: tb[ya:yb,xa:xb]=True
leg=np.zeros((H,W),bool);leg[860:945,380:880]=True
white=white&tb&~(leg&(np.minimum(np.minimum(R,G),B)<=130))
S=(white|((teal|purp)&roi))
S[985:1030,1240:1830]|=(np.minimum(np.minimum(R,G),B)>80)[985:1030,1240:1830]   # credit line
# --- chart translucent fill (below the cortisol curve, above the axis): linear vertical gradient; model measured from the wall column x=260
T=np.array([206,220,82],np.float32)                         # BGR of the fill colour
alpha_y=np.clip(0.00174*(782-np.arange(H)),0,0.5).astype(np.float32)
yc=np.full(W,-1,np.int32)
for x in range(380,1010):
    ys=np.where(teal[300:800,x])[0]
    if len(ys): yc[x]=300+int(np.median(ys))
Fm=np.zeros((H,W),bool)
for x in range(380,1010):
    if yc[x]>0: Fm[yc[x]+4:779,x]=True
A=(alpha_y[:,None]*Fm)[...,None]
clean=np.where(Fm[...,None],(Of-A*T)/(1-A),Of)
up=clean[776].copy();dn=clean[783].copy()      # the axis hairline is 2 px (rows 779-780): bridge it vertically
for y in range(777,783):
    t=(y-776)/7.0;clean[y,190:1010]=up[190:1010]*(1-t)+dn[190:1010]*t
Sd=cv2.dilate(S.astype(np.uint8),cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
Si=cv2.dilate(S.astype(np.uint8),cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(13,13)))
Sf=cv2.dilate(S.astype(np.uint8),cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9)))
face=np.zeros((H,W),bool);face[285:345,560:860]=True
Si=np.where(face,Sf,Si).astype(np.uint8)
clean_in=cv2.inpaint(np.clip(clean,0,255).astype(np.uint8),Si*255,4,cv2.INPAINT_TELEA).astype(np.float32)
cf=cv2.inpaint(np.clip(clean,0,255).astype(np.uint8),(Sf*face)*255,3,cv2.INPAINT_NS).astype(np.float32)
clean_in[285:345,560:860]=cf[285:345,560:860]
# --- woman outline (full-res), tightened with GrabCut
poly=np.array([(250,95),(330,82),(400,95),(430,140),(440,190),(425,240),(400,275),(390,300),(430,310),(445,335),(462,380),(480,450),(496,520),(503,575),(520,588),(560,590),(650,588),(692,625),(698,690),(680,730),(650,745),(675,765),(660,785),(560,800),(470,830),(330,860),(200,840),(130,800),(110,740),(115,690),(165,660),(175,600),(185,520),(185,430),(190,340),(215,305),(240,290),(215,250),(205,200),(215,150),(235,115)],np.int32)+np.array([380,150],np.int32)
pm=np.zeros((H,W),np.uint8);cv2.fillPoly(pm,[poly],255)
gm=np.full((H,W),cv2.GC_BGD,np.uint8)
gm[cv2.dilate(pm,np.ones((25,25),np.uint8))>0]=cv2.GC_PR_BGD
gm[pm>0]=cv2.GC_PR_FGD
gm[cv2.erode(pm,np.ones((31,31),np.uint8))>0]=cv2.GC_FGD
x0,y0,x1,y1=380,200,1160,1060
bgd=np.zeros((1,65));fgd=np.zeros((1,65))
sub=np.clip(clean_in[y0:y1,x0:x1]*2.5,0,255).astype(np.uint8)
gsub=gm[y0:y1,x0:x1].copy()
cv2.grabCut(sub,gsub,None,bgd,fgd,4,cv2.GC_INIT_WITH_MASK)
Mw=np.zeros((H,W),np.uint8);Mw[y0:y1,x0:x1]=((gsub==cv2.GC_FGD)|(gsub==cv2.GC_PR_FGD))
Mw=Mw|(cv2.erode(pm,np.ones((21,21),np.uint8))>0).astype(np.uint8)   # interior always solid (no see-through face / body)
Mw=cv2.morphologyEx(Mw,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8));Mw=cv2.morphologyEx(Mw,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
cv2.imwrite("/workspace/s20_clean.png",np.clip(clean_in,0,255).astype(np.uint8)[150:1080,380:1300])
Mw=np.where(cv2.dilate(pm,np.ones((3,3),np.uint8))>0,Mw,0).astype(np.uint8)
cv2.imwrite('/workspace/s20_M.png',Mw*255)
rug=np.zeros((H,W),bool);rug[780:,1020:]=True;rug[780:885,985:]=True;ci=clean_in
rug&=(ci[...,2]>=ci[...,0]-5)&(ci.sum(2)>130)
Mw[rug]=0
gb=cv2.GaussianBlur(clean_in,(0,0),2.0);wedge=np.zeros((H,W),bool);wedge[820:885,985:1095]=True;wedge[885:915,1015:1095]=True;wedge&=(gb[...,1]>=31)   # the pale rug beside her right knee is not part of her
Mw[wedge]=0
Mw=cv2.morphologyEx(Mw,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
Mw=cv2.erode(Mw,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)))
Msoft=cv2.GaussianBlur(Mw.astype(np.float32),(0,0),1.4)
# --- rebuild the vacated area (low-res inpaint of the cleaned image + fine grain)
V=cv2.dilate(Mw,np.ones((21,21),np.uint8))
# row-wise interpolation between the untouched wall / floor on both sides of the gap (keeps the horizontal wall, skirting and floor lines straight), then a light vertical smoothing
fill=clean_in.copy();Vb=V>0
for y in range(H):
    row=Vb[y]
    if not row.any():continue
    xs=np.where(row)[0];st=np.r_[0,np.where(np.diff(xs)>1)[0]+1];en=np.r_[st[1:],len(xs)]
    for i0,i1 in zip(st,en):
        a_,b_=xs[i0],xs[i1-1]
        L=clean_in[y,max(0,a_-12):a_-2].mean(0);Rr=clean_in[y,b_+3:b_+13].mean(0)
        t=np.linspace(0,1,b_-a_+1)[:,None];fill[y,a_:b_+1]=L*(1-t)+Rr*t
fl=fill.copy();vb=cv2.GaussianBlur(fill,(0,0),sigmaX=0.1,sigmaY=3)
fill=np.where(Vb[...,None],vb,fill)
rng=np.random.RandomState(7);fill+=rng.randn(H,W,1).astype(np.float32)*1.6
Vs=cv2.GaussianBlur(V.astype(np.float32),(0,0),2.5)[...,None]
res=clean_in*(1-Vs)+fill*Vs
# --- paste the woman at her new place
Ms=np.roll(Msoft,DX,axis=1)[...,None];Wp=np.roll(clean_in,DX,axis=1)
res=res*(1-Ms)+Wp*Ms
# --- put the chart fill back (original model) and every chart/text stroke back exactly from the current image
res=np.where(Fm[...,None],res*(1-A)+A*T,res)
Z=cv2.dilate(np.maximum(V,np.roll(Mw,DX,axis=1)),np.ones((15,15),np.uint8))
Zs=cv2.GaussianBlur(Z.astype(np.float32),(0,0),2.0)[...,None]
Ss=cv2.GaussianBlur(Sd.astype(np.float32),(0,0),0.8)[...,None]
res=res*(1-Ss)+Of*Ss
ax=np.median(Of[779:781,600:700],axis=(0,1));res[779:781,190:1010]=ax      # axis hairline, uniform colour (not her hands)
out=Of*(1-Zs)+res*Zs
cv2.imwrite(OUT,np.clip(out,0,255).astype(np.uint8),[cv2.IMWRITE_JPEG_QUALITY,95])
