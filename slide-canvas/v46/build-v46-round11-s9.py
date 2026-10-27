# slide 9 (n07-bridge) ROUND 11: base a4bc235 (white icing). Drips removed, natural rounded cap (elliptical top + short band with a soft feathered lower edge),
# pink top layer visible in true colour beneath it, layer edges straight through every layer, no rectangular block.
import cv2,numpy as np,subprocess,sys
G='/workspace/lla-masterclass-syllabus'
def git(c,f):
    b=subprocess.check_output(['git','-C',G,'show',f'{c}:slide-canvas/v46/assets/{f}']);return cv2.imdecode(np.frombuffer(b,np.uint8),1)
A=git('a4bc235','n07-bridge.jpg');C=git('c12bece','n07-bridge.jpg');CUR=git('HEAD','n07-bridge.jpg')
M=cv2.imread('/workspace/r5/icing_mask.png',0)>0
H,W=A.shape[:2];xs=np.arange(W);yy=np.arange(H)[:,None]
u=np.clip((xs-545.0)/365.0,-1,1)
st=356+10*(1-u*u)
# --- layer edges per row (from the undimmed layers, black drips excluded), straightened
def edge(img,y,side):
    row=img[y].astype(int);lum=row.max(1)
    rng=range(150,300) if side==0 else range(870,960)
    pts=[x for x in rng if lum[x]>85 and lum[min(x+3,W-1)]>85 and lum[x-3 if side==1 else x]>0]
    return (min(pts) if side==0 else max(pts)) if pts else None
eL=[];eR=[]
for y in range(404,690):
    l=edge(A,y,0);r=edge(A,y,1)
    if l is not None and 198<=l<=212:eL.append(l)
    if r is not None and 878<=r<=892:eR.append(r)
XL=int(np.median(eL));XR=int(np.median(eR));print('layer edges',XL,XR,len(eL),len(eR))
# --- icing mask + the right-hand drips the registration missed
hsv=cv2.cvtColor(A,cv2.COLOR_BGR2HSV);Hh,Ss,Vv=[hsv[...,i].astype(int) for i in range(3)]
cand=((Ss<125)&(Vv>160)&(Hh<=24)&(Hh>=8)).astype(np.uint8);cand[:,:780]=0;cand[:,1000:]=0
fa=cand[400:490].mean(0);fb=cand[556:612].mean(0);extra=np.zeros_like(M)
for c in np.where(fa>0.6)[0]:extra[392:(612 if fb[c]>0.6 else 500),c]=True
Z=(M|extra);Z[:,:150]=False;Z[:,1000:]=False
atop=np.full(W,999)
for x in range(150,1000):
    r=np.where(~Z[200:,x])[0]
    if len(r):atop[x]=200+r[0]
dripcol=atop>340
good=np.where(~dripcol)[0];good=good[(good>XL)&(good<XR)]
atop_i=np.interp(np.arange(W),good,atop[good]).astype(np.float32)
yb=262+26*(1-u*u)
yb=cv2.GaussianBlur(yb.astype(np.float32)[None,:],(0,0),6)[0]
print('cap edge y: sides %.0f centre %.0f'%(yb[XL+5],yb[545]))
base=np.where((yy<400)[...,None],C,A)
# --- cap: real cap (A) down to row 258, then its own side wall extended downwards inside the cap's real silhouette
xl250=np.where(M[250])[0].min();xr250=np.where(M[250])[0].max();print('cap silhouette at y=250',xl250,xr250)
Af=A.astype(np.float32);wall=Af[246:259].mean(0);wall_l=cv2.GaussianBlur(wall[None],(0,0),sigmaX=6)[0]
hpA=Af-cv2.GaussianBlur(Af,(0,0),2.5);rng=np.random.RandomState(5)
capimg=A.copy()
for y in range(259,int(yb.max())+10):
    sy=244+int(rng.randint(0,14));seg=hpA[sy,xl250:xr250+1];cap_=np.zeros_like(wall_l);cap_[xl250:xr250+1]=np.roll(seg,int(rng.randint(-200,200)),axis=0)
    capimg[y]=np.clip(wall_l+cap_,0,255).astype(np.uint8)
# cap shape: A's own cap (natural dome) down to row 262, rolled in smoothly to the layer edges over its last rows; lower edge = soft ellipse
shape=np.zeros((H,W),np.float32)
left=np.zeros(H);right=np.zeros(H)
for y in range(H):
    mx=np.where(M[y,150:1000])[0]
    if y<250 and len(mx):l0=150+mx.min();r0=150+mx.max()
    else:l0=xl250;r0=xr250
    t=np.clip((y-236)/40.0,0,1);t=t*t*(3-2*t)
    left[y]=l0+(XL-4-l0)*t if y>=236 else l0;right[y]=r0+(XR+4-r0)*t if y>=236 else r0
for y in range(120,int(yb.max())+6):
    inside=(xs>=left[y])&(xs<=right[y])&(y<yb)
    shape[y,inside]=1
# soft shading of the band (darker toward the lower edge) + feathered edge
band=(np.arange(H)[:,None]>=250)&(np.arange(H)[:,None]<yb[None,:])
tt=np.clip((np.arange(H)[:,None]-250)/np.maximum(yb[None,:]-250,1),0,1)
capimg=(capimg.astype(np.float32)*np.where(band,1-0.10*tt**1.5,1)[...,None]).astype(np.uint8)
shape=cv2.GaussianBlur(shape,(0,0),2.0)[...,None]
# pink top layer, rebuilt in true colour: row colours + pore grain from a clean pink patch of the real layer
P=C[296:346,312:402].astype(np.float32);ph=P.shape[0]
rowcol=P.mean(1)                                    # (57,3) tone per row above the stripe (bottom row touches the stripe)
hpP=P-cv2.GaussianBlur(P,(0,0),3)
rng2=np.random.RandomState(11);pink=base.astype(np.float32).copy()
pm=np.zeros((H,W),np.float32)
for x in range(XL,XR+1):pm[int(yb[x])-6:int(st[x])+1,x]=1
sd=float(hpP.std())
noise=cv2.GaussianBlur(rng2.randn(H,W).astype(np.float32),(0,0),1.1)*sd*2.2
rowt=np.zeros((H,W,3),np.float32)
for x in range(XL,XR+1):
    y1=int(st[x])
    for y in range(int(yb[x])-6,y1+1):
        r=min(max(y1-y,0),ph-1);rowt[y,x]=rowcol[r]
pink=rowt+noise[...,None]
# pores: dark soft specks scattered like the real sponge
pores=np.zeros((H,W),np.float32)
for _ in range(2000):
    px=int(rng2.randint(XL,XR));py=int(rng2.randint(266,366))
    cv2.circle(pores,(px,py),int(rng2.choice([1,1,2,2,3])),1.0,-1)
pores=cv2.GaussianBlur(pores,(0,0),0.9)
pink=pink*(1-0.30*pores[...,None])
pa=cv2.GaussianBlur(pm,(0,0),1.0)[...,None]
shade=(0.92+0.08*(1-u*u))[None,:,None]
base=(base.astype(np.float32)*(1-pa)+np.clip(pink*shade,0,255)*pa).astype(np.uint8)
B=(base.astype(np.float32)*(1-shape)+capimg.astype(np.float32)*shape).astype(np.uint8)
out=B.copy()
# --- side drips / lip outside the layer edges: replace from the clean backdrop (row-wise shift keeps the backdrop band edge)
zz=cv2.dilate((M|extra).astype(np.uint8),np.ones((7,7),np.uint8))>0
for sgn in(-1,1):
    sel=np.zeros((H,W),bool)
    for y in range(230,520):
        if sgn==-1:sel[y,xl250-14:int(left[y]) if y<yb[int(left[y])] else XL]=True
        else:sel[y,int(right[y])+1 if y<yb[int(right[y])] else XR+1:xr250+14]=True
    sel&=zz
    al=cv2.GaussianBlur(sel.astype(np.float32),(0,0),1.1)[...,None]
    sh=np.roll(B,-sgn*32,axis=1)
    out=(out.astype(np.float32)*(1-al)+sh.astype(np.float32)*al).astype(np.uint8)
B=out.copy()
# --- drips + necks inside the layers: row-wise interpolation of clean neighbours + sponge texture from a clean neighbour
D=Z&(yy>=st[None,:]-4)&np.broadcast_to(dripcol[None,:],Z.shape)
D[:,:XL+1]=False;D[:,XR-16:]=False
D0=D.copy()
D=(cv2.dilate(D0.astype(np.uint8),np.ones((7,25),np.uint8))>0)|((cv2.dilate(D0.astype(np.uint8),np.ones((7,37),np.uint8))>0)&(yy<425))
Dw=(cv2.dilate(D0.astype(np.uint8),np.ones((7,39),np.uint8))>0)|((cv2.dilate(D0.astype(np.uint8),np.ones((7,49),np.uint8))>0)&(yy<425))
D[:,700:]=Dw[:,700:]
D&=(yy>=st[None,:]-4);D[:,:XL+1]=False;D[:,XR-16:]=False
n,lab,stt,_=cv2.connectedComponentsWithStats(D.astype(np.uint8),connectivity=8)
hpimg=B.astype(np.float32)-cv2.GaussianBlur(B.astype(np.float32),(0,0),4)
hpimg[cv2.dilate(D.astype(np.uint8),np.ones((9,9),np.uint8))>0]=0
for i in range(1,n):
    x,y,w,h,ar=stt[i]
    if ar<60:continue
    comp=cv2.dilate((lab==i).astype(np.uint8),np.ones((1,9),np.uint8))>0
    ring=cv2.dilate(comp.astype(np.uint8),np.ones((9,9),np.uint8)).astype(bool)&~comp&~D
    ry,rx=np.where(ring);best=None
    for s_ in range(w+8,w+140,4):
        for sg in(-1,1):
            d=sg*s_
            if (rx+d).min()<XL+4 or (rx+d).max()>=XR-4:continue
            err=np.abs(B[ry,rx+d].astype(int)-B[ry,rx].astype(int)).mean()+0.02*s_
            if best is None or err<best[0]:best=(err,d)
    if best is None:print('no source',x,y,w,h);continue
    d=best[1];print('comp',x,y,w,h,'shift',d,'err %.1f'%best[0])
    low=np.zeros((H,W,3),np.float32);shc=np.roll(B,-d,axis=1).astype(np.float32)
    for yv in range(y,y+h):
        xs_=np.where(comp[yv])[0]
        if len(xs_)==0:continue
        xa,xb=xs_.min(),xs_.max();Lv=Rv=None
        for o in ((26,12,6) if yv<425 else (12,6)):
            if Lv is None and xa-o>=XL+1 and not D[yv,xa-o:xa-o+8].any():Lv=np.median(B[yv,xa-o:xa-o+8].astype(np.float32),0)
            if Rv is None and xb+o+1<=XR-4 and not D[yv,xb+o-7:xb+o+1].any():Rv=np.median(B[yv,xb+o-7:xb+o+1].astype(np.float32),0)
        if Lv is None and Rv is None:
            low[yv,xa:xb+1]=cv2.GaussianBlur(shc[yv:yv+1],(0,0),sigmaX=4)[0][xa:xb+1];continue
        if Lv is None:Lv=Rv
        if Rv is None:Rv=Lv
        t=np.linspace(0,1,xb-xa+1)[:,None];low[yv,xa:xb+1]=Lv[None]*(1-t)+Rv[None]*t
    low=cv2.GaussianBlur(low,(0,0),sigmaX=0.1,sigmaY=0.7)
    cand_=np.clip(low+np.roll(hpimg,-d,axis=1),0,255)
    al=cv2.GaussianBlur(cv2.erode(comp.astype(np.uint8),np.ones((5,5),np.uint8)).astype(np.float32),(0,0),1.2)[...,None]
    out=(out.astype(np.float32)*(1-al)+cand_*al).astype(np.uint8)
res=CUR.copy();res[:, :1000]=out[:, :1000]
cv2.imwrite('assets/n07-bridge.jpg',res,[cv2.IMWRITE_JPEG_QUALITY,95])
cv2.imwrite('/workspace/s9_r11_h.png',res[90:800,100:1920])
