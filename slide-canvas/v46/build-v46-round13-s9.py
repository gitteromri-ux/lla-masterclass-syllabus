# slide 9 ROUND 12 (restart from a4bc235 as the user specified); ROUND 11: base a4bc235 (white icing). Drips removed, natural rounded cap (elliptical top + short band with a soft feathered lower edge),
# pink top layer visible in true colour beneath it, layer edges straight through every layer, no rectangular block.
import cv2,numpy as np,subprocess,sys
G='/workspace/lla-masterclass-syllabus'
def git(c,f):
    b=subprocess.check_output(['git','-C',G,'show',f'{c}:slide-canvas/v46/assets/{f}']);return cv2.imdecode(np.frombuffer(b,np.uint8),1)
import importlib.util,os
_sp=importlib.util.spec_from_file_location('unveil',os.path.join(os.path.dirname(os.path.abspath(__file__)),'build-v46-slide9-unveil.py'));_um=importlib.util.module_from_spec(_sp);_sp.loader.exec_module(_um)
A0=git('a4bc235','n07-bridge.jpg');CUR=git('HEAD','n07-bridge.jpg')
A=_um.build_U(A0)      # same photo with the top dark veil removed (background + sponge + stripe in true brightness); icing cap stays dark; bottom untouched
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
    l=edge(A0,y,0);r=edge(A0,y,1)
    if l is not None and 198<=l<=212:eL.append(l)
    if r is not None and 878<=r<=892:eR.append(r)
XL=int(np.median(eL));XR=int(np.median(eR));print('layer edges',XL,XR,len(eL),len(eR))
# --- icing mask + the right-hand drips the registration missed
hsv=cv2.cvtColor(A0,cv2.COLOR_BGR2HSV);Hh,Ss,Vv=[hsv[...,i].astype(int) for i in range(3)]
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

atop_s=cv2.GaussianBlur(atop_i[None,:],(0,0),8)[0]
print('cap lower edge at drip-free columns: min %.0f max %.0f'%(atop[good].min(),atop[good].max()))
_Wr=cv2.warpAffine(cv2.imread(G+'/slide-canvas/images/github-round-9-12.jpg'),np.load('/workspace/r5/M.npy')*1.5,(1920,1080),flags=cv2.INTER_CUBIC);_hw=cv2.cvtColor(_Wr,cv2.COLOR_BGR2HSV)
Zw=(Z&(((_hw[...,0]<=35)|(_hw[...,0]>=165))&(_hw[...,2]>150)&(_hw[...,1]<95))).astype(np.uint8)
Zw=cv2.morphologyEx(Zw,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8));Zw[420:]=Z[420:]
Zdf=cv2.GaussianBlur(cv2.dilate(Zw,np.ones((7,7),np.uint8)).astype(np.float32),(0,0),1.0)
icD=(yy<(atop[None,:]+4))&(yy<420)&np.ones((H,W),bool)
B=A.copy()
# --- outside the cake edges: cap lip + side drips below the dome become backdrop (fade over 25 px)
zz=cv2.dilate((M|extra).astype(np.uint8),np.ones((7,7),np.uint8))>0
out=B.copy()
for sgn in(-1,1):
    sel=np.zeros((H,W),bool);ys=np.arange(H)
    ramp=np.clip((ys[:,None]-(atop_s[None,:]-6))/25.0,0,1)
    if sgn==-1:sel[:,XL-40:XL-1]=True
    else:sel[:,XR+2:XR+41]=True
    keep=zz.copy();keep[:400]=True          # above the orange layer everything outside the cake edge is backdrop
    sel&=keep;sel[:200]=False;sel[560:]=False
    al=cv2.GaussianBlur(sel.astype(np.float32),(0,0),1.1)*ramp;al=al[...,None]
    sh=np.roll(B,-sgn*32,axis=1)
    out=(out.astype(np.float32)*(1-al)+sh.astype(np.float32)*al).astype(np.uint8)
B=out.copy()
# --- drips inside the cake: fill with the SAME rows from clean neighbouring columns (row-wise interpolation + sponge texture from the best clean neighbour)
D0=Z&(yy>=atop_s[None,:]-10)&np.broadcast_to(dripcol[None,:],Z.shape)
D0[:,:XL+1]=False;D0[:,XR-16:]=False
Dn=(cv2.dilate(D0.astype(np.uint8),np.ones((7,25),np.uint8))>0)|((cv2.dilate(D0.astype(np.uint8),np.ones((7,37),np.uint8))>0)&(yy<425))
Dw=(cv2.dilate(D0.astype(np.uint8),np.ones((7,39),np.uint8))>0)|((cv2.dilate(D0.astype(np.uint8),np.ones((7,49),np.uint8))>0)&(yy<425))
D=Dn.copy();D[:,700:]=Dw[:,700:]
D&=(yy>=atop_s[None,:]-10);D[:,:XL+1]=False;D[:,XR-16:]=False
n,lab,stt,_=cv2.connectedComponentsWithStats(D.astype(np.uint8),connectivity=8)
hpimg=B.astype(np.float32)-cv2.GaussianBlur(B.astype(np.float32),(0,0),4)
hpimg[cv2.dilate(D.astype(np.uint8),np.ones((9,9),np.uint8))>0]=0
hpimg[cv2.dilate(Z.astype(np.uint8),np.ones((5,5),np.uint8))>0]=0

_mn=A.astype(np.float32).min(2);_dc=cv2.dilate(dripcol.astype(np.uint8)[None,:],np.ones((1,31),np.uint8))[0]>0
_px=[];_py=[]
for _x in range(XL+3,XR-6):
    if _dc[_x]:continue
    _col=cv2.GaussianBlur(_mn[:,_x-2:_x+3].mean(1)[:,None],(0,0),1.5)[:,0];_r=np.where(_col[430:580]>110)[0]
    if len(_r):_px.append(_x);_py.append(430+_r[0])
_py=np.array(_py,np.float32);_px=np.array(_px,np.float32)
from scipy.ndimage import median_filter
_py=median_filter(_py,size=9).astype(np.float32)
_px=np.concatenate([[0],_px,[1000]]);_py=np.concatenate([[_py[0]],_py,[_py[-1]]]);print('stripe curve pts',len(_px),_py[::40])
def yt(x):return np.interp(x,_px,_py)
_hs=cv2.cvtColor(A,cv2.COLOR_BGR2HSV);_cm=(_hs[...,1]<60)&(_hs[...,2]>170)
_qx=[];_qy=[]
for _x in range(XL+3,XR-6):
    if _dc[_x]:continue
    _c=_cm[330:410,_x-2:_x+3].mean(1)>0.6;_r=np.where(_c)[0]
    if len(_r):_qx.append(_x);_qy.append(330+_r[-1])
_qy=median_filter(np.array(_qy,np.float32),size=9).astype(np.float32);_qx=np.array(_qx,np.float32)
_qx=np.concatenate([[0],_qx,[1000]]);_qy=np.concatenate([[_qy[0]],_qy,[_qy[-1]]]);print('upper stripe bottom curve',_qy[::40])
def yt2(x):return np.interp(x,_qx,_qy)
def shifted(img,d,align=True,curve=None):
    curve=curve or yt
    gx,gy=np.meshgrid(np.arange(W,dtype=np.float32),np.arange(H,dtype=np.float32))
    xs_=np.clip(gx+d,0,W-1).astype(np.float32);off=((curve(xs_)-curve(gx)) if align else np.zeros_like(gx)).astype(np.float32)
    return cv2.remap(img,xs_,(gy+off).astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
def fin(comp):
    global B,Dcur,hpimg
    Dcur[comp]=False;B=out.copy()
    hpimg=B.astype(np.float32)-cv2.GaussianBlur(B.astype(np.float32),(0,0),4)
    hpimg[cv2.dilate(Dcur.astype(np.uint8),np.ones((9,9),np.uint8))>0]=0
    hpimg[cv2.dilate(Z.astype(np.uint8),np.ones((5,5),np.uint8))>0]=0
A32=A.astype(np.float32);lpA=cv2.GaussianBlur(A32,(0,0),4).mean(2);hpA2=A32-cv2.GaussianBlur(A32,(0,0),2.0)
cr=A32[:, 775:792].min(2).mean(1);cream=np.where(cr[420:520]>150)[0]
stripe_lo,stripe_hi=(420+cream.min()-6,420+cream.max()+6) if len(cream) else (0,0);print('stripe rows',stripe_lo,stripe_hi)
Dcur=D.copy();todo=list(range(1,n));Dfat=cv2.dilate(D.astype(np.uint8),np.ones((1,25),np.uint8))>0
def fill(i):
    global out,B,Dcur,hpimg
    x,y,w,h,ar=stt[i]
    if ar<60:return True
    comp=cv2.dilate((lab==i).astype(np.uint8),np.ones((1,9),np.uint8))>0
    ring=cv2.dilate(comp.astype(np.uint8),np.ones((9,9),np.uint8)).astype(bool)&~comp&~Dcur
    ry,rx=np.where(ring);best=None;cy_,cx_=np.where(comp)
    for strict in (True,False):
        for s_ in range(w+8,w+140,4):
            for sg in(-1,1):
                d=sg*s_
                if (rx+d).min()<XL+4 or (rx+d).max()>=XR-4:continue
                if Dcur[cy_,np.clip(cx_+d,0,W-1)].any():continue
                if strict and Dfat[cy_,np.clip(cx_+d,0,W-1)].any():continue
                err=np.abs(B[ry,rx+d].astype(int)-B[ry,rx].astype(int)).mean()+0.02*s_
                if best is None or err<best[0]:best=(err,d)
        if best is not None:break
    if best is None:return False
    d=best[1];print('comp',x,y,w,h,'shift',d,'err %.1f'%best[0])
    low=np.zeros((H,W,3),np.float32);shc=np.roll(B,-d,axis=1).astype(np.float32)
    LR={}
    for yv in range(y,y+h):
        xs_=np.where(comp[yv])[0]
        if len(xs_)==0:continue
        xa,xb=xs_.min(),xs_.max();Lv=Rv=None
        for o in ((26,12,6) if yv<425 else (12,6)):
            if Lv is None and xa-o>=XL+1 and not (Dcur|icD)[yv,xa-o:xa-o+8].any():Lv=np.median(B[yv,xa-o:xa-o+8].astype(np.float32),0)
            if Rv is None and xb+o+1<=XR-4 and not (Dcur|icD)[yv,xb+o-7:xb+o+1].any():Rv=np.median(B[yv,xb+o-7:xb+o+1].astype(np.float32),0)
        if Lv is None and Rv is None:
            LR[yv]=(xa,xb,None,None);continue
        if Lv is None:Lv=Rv
        if Rv is None:Rv=Lv
        LR[yv]=(xa,xb,Lv,Rv)
    _val=[k for k in sorted(LR) if LR[k][2] is not None]
    for k in sorted(LR):
        if LR[k][2] is None:
            if _val:
                kk=min(_val,key=lambda q:(abs(q-k)+(0 if q>k else 3)))
                LR[k]=(LR[k][0],LR[k][1],LR[kk][2],LR[kk][3])
            else:
                xa,xb=LR[k][:2];low[k,xa:xb+1]=cv2.GaussianBlur(shc[k:k+1],(0,0),sigmaX=4)[0][xa:xb+1];del LR[k]
    ks=sorted(LR)
    if ks:
        from scipy.ndimage import gaussian_filter1d
        LL=gaussian_filter1d(np.array([LR[k][2] for k in ks]),3.0,axis=0,mode='nearest');RR=gaussian_filter1d(np.array([LR[k][3] for k in ks]),3.0,axis=0,mode='nearest')
        for i,yv in enumerate(ks):
            xa,xb=LR[yv][:2];t=np.linspace(0,1,xb-xa+1)[:,None];low[yv,xa:xb+1]=LL[i][None]*(1-t)+RR[i][None]*t
    low=cv2.GaussianBlur(low,(0,0),sigmaX=0.1,sigmaY=0.7)
    gain=1.0 if (x==250 and w==71) else 1.0
    cand_=np.clip(low+np.roll(hpimg,-d,axis=1)*gain,0,255)
    al=cv2.GaussianBlur(cv2.erode(comp.astype(np.uint8),np.ones((5,5),np.uint8)).astype(np.float32),(0,0),1.2)
    ramp=np.clip((np.arange(H)[:,None]-(atop_s[None,:]-10))/25.0,0,1);ramp=ramp*ramp*(3-2*ramp)
    al=al*ramp
    _f=np.clip((yy-346)/6.0,0,1);al=(al*(Zdf*(1-_f)+_f))[...,None]
    out=(out.astype(np.float32)*(1-al)+cand_*al).astype(np.uint8)
    if (x>700) or (x<230 and y>=390):
        nar=cv2.dilate(D0.astype(np.uint8),np.ones((7,71),np.uint8),anchor=(14,3))>0
        mk=nar&(cv2.dilate(comp.astype(np.uint8),np.ones((1,61),np.uint8))>0);mk[:392]=False;mk[:,XR-12:]=False;mk[:,:XL+3]=False;mk=(mk*255).astype(np.uint8)
        if mk.any():
            ys_,xs2=np.where(mk>0);cx2=(xs2.min()+xs2.max())//2;cy2=(ys_.min()+ys_.max())//2
            srcim=shifted(B,d,align=(y+h>500))
            cl=cv2.seamlessClone(srcim,out,mk.copy(),(int(cx2),int(cy2)),cv2.NORMAL_CLONE)
            a_=cv2.GaussianBlur(mk.astype(np.float32)/255,(0,0),1.0)[...,None]
            a_=np.clip(a_*1.0,0,1)
            out=(out.astype(np.float32)*(1-a_)+cl.astype(np.float32)*a_).astype(np.uint8)
            # restore the sponge's fine grain in the cloned strip from a truly clean strip of the same layer rows (original photo)
            ysm,xsm=np.where(mk>0);bestd=None
            for s2 in range(60,330,4):
                for sg in(-1,1):
                    d2=sg*s2
                    if xsm.min()+d2<XL+6 or xsm.max()+d2>=XR-24:continue
                    if Dfat[ysm,xsm+d2].any() or Z[ysm,xsm+d2].any():continue
                    e2=np.abs(lpA[ysm,xsm+d2]-lpA[ysm,xsm]).mean()
                    if bestd is None or e2<bestd[0]:bestd=(e2,d2)
            print('  grain source shift',bestd)
            if bestd:
                d2=bestd[1];hs=shifted(hpA2,d2,align=(y+h>500))
                lowc=cv2.GaussianBlur(out.astype(np.float32),(0,0),2.0)
                ys_idx=np.arange(H)[:,None]
                keep=np.ones((H,1,1),np.float32)
                wgt=cv2.GaussianBlur((mk>0).astype(np.float32),(0,0),1.5)[...,None]*keep
                grain=np.clip(lowc+hs,0,255)
                out=(out.astype(np.float32)*(1-wgt)+grain*wgt).astype(np.uint8)
    if (x>700):
        mk2=cv2.dilate(comp.astype(np.uint8),np.ones((1,61),np.uint8))>0;mk2[:346]=False;mk2[398:]=False;mk2[:,XR-12:]=False;mk2[:,:XL+3]=False
        mk2&=(yy>=atop_s[None,:]+20)
        mk2=(mk2*255).astype(np.uint8)
        if mk2.sum()>255*200:
            ys_,xs2=np.where(mk2>0);cx2=(xs2.min()+xs2.max())//2;cy2=(ys_.min()+ys_.max())//2
            cl=cv2.seamlessClone(shifted(B,d,align=True,curve=yt2),out,mk2.copy(),(int(cx2),int(cy2)),cv2.NORMAL_CLONE)
            a_=np.clip(cv2.GaussianBlur(mk2.astype(np.float32)/255,(0,0),1.0)[...,None],0,1)
            out=(out.astype(np.float32)*(1-a_)+cl.astype(np.float32)*a_).astype(np.uint8)
    fin(comp);return True

for _p in range(4):
    todo=[i for i in todo if not fill(i)]
    print('pass',_p,'left',todo)
    if not todo:break

# --- cream stripe across the first long drip (x~250-320): rebuild it from the stripe on both sides, edges interpolated, so it stays continuous
def _stripe_edges(x):
    col=cv2.GaussianBlur(cream_m[:,x-1:x+2].mean(1).astype(np.float32)[:,None],(0,0),1)[:,0]
    r=np.where(col[430:575]>0.5)[0]
    br=np.where(np.diff(r)>1)[0];e=r[br[0]] if len(br) else r[-1]
    return 430+r[0],430+e
_hsv=cv2.cvtColor(A,cv2.COLOR_BGR2HSV);cream_m=(_hsv[...,1]<55)&(_hsv[...,2]>190)
def stripe_fix(xl,xr,xa,xb):
    tl,bl=_stripe_edges(xl);tr,br_=_stripe_edges(xr);print('stripe edges L',tl,bl,'R',tr,br_)
    Af=A.astype(np.float32);res=out.astype(np.float32).copy()
    L=Af[:,xl-2:xl+3].mean(1);R=Af[:,xr-2:xr+3].mean(1)
    for x in range(xa,xb+1):
        al=(x-xl)/float(xr-xl);yT=tl+(tr-tl)*al;yB=bl+(br_-bl)*al
        for y in range(int(yT)-14,int(yB)+16):
            s_=(y-yT)/(yB-yT)
            yl=tl+s_*(bl-tl);yr=tr+s_*(br_-tr)
            vl=L[int(np.floor(yl))]*(1-(yl-np.floor(yl)))+L[int(np.floor(yl))+1]*(yl-np.floor(yl))
            vr=R[int(np.floor(yr))]*(1-(yr-np.floor(yr)))+R[int(np.floor(yr))+1]*(yr-np.floor(yr))
            v=vl*(1-al)+vr*al
            w=1.0 if (yT-2<=y<=yB+2) else max(0,1-(min(abs(y-yT+2),abs(y-yB-2))/5.0))
            res[y,x]=res[y,x]*(1-w)+v*w
    return np.clip(res,0,255).astype(np.uint8)
out=stripe_fix(238,331,246,324)
res=CUR.copy();res[:, :1000]=out[:, :1000]
res=out.copy();res[:, :1000]=out[:, :1000]
res=CUR.copy();res[:, :1000]=out[:, :1000]
# brown outline along the sponge/icing edges (shadow line of the photo): lift the thin dark band toward the local sponge colour, keep the grain
res=res.astype(np.float32)
Zh=Zw.copy();Zh[:,1000:]=0
dist=cv2.distanceTransform((1-Zh).astype(np.uint8),cv2.DIST_L2,5)
spong=((cv2.dilate(Zh,np.ones((15,15),np.uint8))==0)&(yy<346)&(yy>150)&(np.arange(W)[None,:]>XL+2)&(np.arange(W)[None,:]<XR-2)).astype(np.float32)
num=cv2.GaussianBlur(res*spong[...,None],(0,0),9);den=cv2.GaussianBlur(spong,(0,0),9)
ref=num/np.maximum(den[...,None],1e-3)
lp=cv2.GaussianBlur(res,(0,0),2.5);hp=res-lp
lumr=ref.mean(2);lum1=cv2.GaussianBlur(res,(0,0),1.0).mean(2)
din=cv2.distanceTransform(Zh.astype(np.uint8),cv2.DIST_L2,5)
band=((dist<=9)&(dist>0))|((din<=3)&(din>0))
band=band&(yy<346)&(yy>150)&(np.arange(W)[None,:]>XL+2)&(np.arange(W)[None,:]<XR-2)&(den>0.02)
wd=np.clip((0.88*lumr-lum1)/(0.22*np.maximum(lumr,1)),0,1)*band
wd=cv2.GaussianBlur(wd.astype(np.float32),(0,0),1.3)[...,None]
tgt=ref+hp*0.8
res=np.clip(res*(1-wd)+tgt*wd,0,255)
res=res.astype(np.uint8)
res2=CUR.copy();res2[:, :1000]=res[:, :1000];res=res2
# faint dark vertical line (old drip edge shadow) crossing the upper cream stripe at x~452: bridge it from both sides, keep grain
_f=res.astype(np.float32);_y0,_y1=350,398
_L=_f[_y0:_y1,441:446].mean(1);_R=_f[_y0:_y1,463:468].mean(1)
_t=((np.arange(447,462)-446)/16.0)[None,:,None]
_fill=_L[:,None,:]*(1-_t)+_R[:,None,:]*_t
_hp=_f[_y0:_y1,420:435]-cv2.GaussianBlur(_f,(0,0),2.5)[_y0:_y1,420:435]
_w=np.ones((1,15,1),np.float32);_w[0,:3,0]=np.linspace(0.2,1,3);_w[0,-3:,0]=np.linspace(1,0.2,3)
_f[_y0:_y1,447:462]=_f[_y0:_y1,447:462]*(1-_w)+(_fill+_hp*0.6)*_w
res=np.clip(_f,0,255).astype(np.uint8)
OUT=sys.argv[1] if len(sys.argv)>1 else 'assets/n07-bridge.jpg'
cv2.imwrite(OUT,res,[cv2.IMWRITE_JPEG_QUALITY,95])
cv2.imwrite('/workspace/s9_r13_c.png',res[90:800,100:1920])
