# slide 9 (n07-bridge) ROUND 10: NO drips. Base = a4bc235 (white icing; its soft dark cap is kept, nothing else is darkened). The layers beneath the cap are in full true colour
# (from c12bece, which has the undimmed layers; below y=400 the a4bc235 pixels are used). Drips/necks are removed (row-wise interpolation + borrowed sponge texture),
# the cap gets a clean elliptical lower edge, the pink top layer between cap and stripe is rebuilt from clean pink sponge, side drips are replaced by the clean background.
# Headline + sub-line (x>=1000) are carried over unchanged from the current slide.
import cv2,numpy as np,subprocess,sys
G='/workspace/lla-masterclass-syllabus'
def git(c,f):
    b=subprocess.check_output(['git','-C',G,'show',f'{c}:slide-canvas/v46/assets/{f}']);return cv2.imdecode(np.frombuffer(b,np.uint8),1)
A=git('a4bc235','n07-bridge.jpg');C=git('c12bece','n07-bridge.jpg');CUR=cv2.imread(sys.argv[1] if len(sys.argv)>1 else 'assets/n07-bridge.jpg')
M=cv2.imread('/workspace/r5/icing_mask.png',0)>0
H,W=A.shape[:2];xs=np.arange(W);yy=np.arange(H)[:,None]
XL,XR=203,884
u=np.clip((xs-545.0)/365.0,-1,1)
st=356+10*(1-u*u)          # top of the cream stripe under the pink layer
# right-hand cream drips missed by the registration mask
hsv=cv2.cvtColor(A,cv2.COLOR_BGR2HSV);Hh,Ss,Vv=[hsv[...,i].astype(int) for i in range(3)]
cand=((Ss<125)&(Vv>160)&(Hh<=24)&(Hh>=8)).astype(np.uint8);cand[:,:780]=0;cand[:,1000:]=0
fa=cand[400:490].mean(0);fb=cand[556:612].mean(0);extra=np.zeros_like(M)
for c in np.where(fa>0.6)[0]:extra[392:(612 if fb[c]>0.6 else 500),c]=True
Z=(M|extra);Z[:,:150]=False;Z[:,1000:]=False
yb=st+7          # cap lower edge sits on the cream stripe: the cap hides the (previously dimmed) pink top layer, nothing beneath it is darkened
# base layers: undimmed layers above y=400 (c12bece), a4bc235 below
base=np.where((yy<400)[...,None],C,A)
# cap (soft dark, from a4bc235); where the clean edge runs below the old arches, cap texture is cloned from 70 px higher
# cap body below the old arch line: the cap's own side wall (rows 244-258, full width, plain dark icing) is extended downwards; grain borrowed from the same rows
capimg=A.copy()
Af=A.astype(np.float32);wall=Af[246:259].mean(0)                         # (W,3)
wall_l=cv2.GaussianBlur(wall[None],(0,0),sigmaX=6)[0]
hpA=Af-cv2.GaussianBlur(Af,(0,0),2.5)
rng=np.random.RandomState(5)
for y in range(259,int(yb.max())+8):
    sy=244+int(rng.randint(0,14));seg=hpA[sy,XL-14:XR+10];cap_=np.zeros_like(wall_l);cap_[XL-14:XR+10]=np.roll(seg,int(rng.randint(-200,200)),axis=0)
    capimg[y]=np.clip(wall_l+cap_,0,255).astype(np.uint8)
xin_=((xs>=XL-14)&(xs<=XR+9)).astype(np.float32)[None,:]
capf=cv2.GaussianBlur(((yy<yb[None,:])*xin_).astype(np.float32),(0,0),1.3)[...,None]
B=(base.astype(np.float32)*(1-capf)+capimg.astype(np.float32)*capf).astype(np.uint8)
out=B.copy()
B=out.copy()
# 2a) side drips hanging outside the layers: replace from the clean background further out (row by row, band edge of the backdrop kept)
zz=cv2.dilate((M|extra).astype(np.uint8),np.ones((7,7),np.uint8))>0
for (xa,xb,sgn) in ((180,XL,-1),(XR+1,908,1)):
    sel=np.zeros((H,W),bool);sel[:,xa:xb]=True;sel&=(yy>=yb[None,:]-2)&(yy<500)&zz
    al=cv2.GaussianBlur(sel.astype(np.float32),(0,0),1.2)[...,None]
    sh=np.roll(B,-sgn*30,axis=1)
    out=(out.astype(np.float32)*(1-al)+sh.astype(np.float32)*al).astype(np.uint8)
B=out.copy()
# 2b) drips under the pink layer: row-wise interpolation of the clean neighbours + sponge texture borrowed from a clean neighbour
D=Z&(yy>=yb[None,:]-2)
D[:,:XL]=False;D[:,XR+1:]=False
D0=D.copy()
D=(cv2.dilate(D0.astype(np.uint8),np.ones((7,25),np.uint8))>0)|((cv2.dilate(D0.astype(np.uint8),np.ones((7,37),np.uint8))>0)&(yy<425))
D&=(yy>=yb[None,:]-2);D[:,:XL-2]=False;D[:,XR-24:]=False
n,lab,stt,_=cv2.connectedComponentsWithStats(D.astype(np.uint8),connectivity=8)
hpimg=B.astype(np.float32)-cv2.GaussianBlur(B.astype(np.float32),(0,0),4)
hpimg[cv2.dilate(D.astype(np.uint8),np.ones((9,9),np.uint8))>0]=0
for i in range(1,n):
    x,y,w,h,ar=stt[i]
    if ar<60:continue
    comp=cv2.dilate((lab==i).astype(np.uint8),np.ones((1,9),np.uint8))>0;ring=cv2.dilate(comp.astype(np.uint8),np.ones((9,9),np.uint8)).astype(bool)&~comp&~D
    ry,rx=np.where(ring);cy,cxx=np.where(comp);best=None
    for s_ in range(w+8,w+140,4):
        for sg in(-1,1):
            d=sg*s_
            if (rx+d).min()<XL+4 or (rx+d).max()>=XR-4:continue
            err=np.abs(B[ry,rx+d].astype(int)-B[ry,rx].astype(int)).mean()+0.02*s_
            if best is None or err<best[0]:best=(err,d)
    if best is None:print('no source for comp',x,y,w,h);continue
    d=best[1];print('comp',x,y,w,h,'shift',d,'err %.1f'%best[0])
    low=np.zeros((H,W,3),np.float32)
    for yv in range(y,y+h):
        xs_=np.where(comp[yv])[0]
        if len(xs_)==0:continue
        xa,xb=xs_.min(),xs_.max()
        Lv=np.median(B[yv,xa-12:xa-4].astype(np.float32),0) if xa-12>=XL-1 and not D[yv,xa-12:xa-4].any() else None
        Rv=np.median(B[yv,xb+5:xb+13].astype(np.float32),0) if xb+13<=XR-12 and not D[yv,xb+5:xb+13].any() else None
        if Lv is None and Rv is None:continue
        if Lv is None:Lv=Rv
        if Rv is None:Rv=Lv
        t=np.linspace(0,1,xb-xa+1)[:,None]
        low[yv,xa:xb+1]=Lv[None]*(1-t)+Rv[None]*t
    low=cv2.GaussianBlur(low,(0,0),sigmaX=0.1,sigmaY=0.7)
    cand_=np.clip(low+np.roll(hpimg,-d,axis=1),0,255)
    al=cv2.GaussianBlur(cv2.erode(comp.astype(np.uint8),np.ones((5,5),np.uint8)).astype(np.float32),(0,0),1.2)[...,None]
    out=(out.astype(np.float32)*(1-al)+cand_*al).astype(np.uint8)
res=CUR.copy();res[:, :1000]=out[:, :1000]
cv2.imwrite('assets/n07-bridge.jpg',res,[cv2.IMWRITE_JPEG_QUALITY,95])
cv2.imwrite('/workspace/s9_r10_s.png',res[100:760,100:1000])
