# Erase every baked-in LLA logo and composite the official artwork (closers/img/lla-logo.png)
# at one fixed top-right position on every slide. Run after build-numbers.py and build-fixes.py.
import cv2,numpy as np,glob,sys
SRC='../closers/img/lla-logo.png'
L=cv2.imread(SRC,cv2.IMREAD_UNCHANGED)
A=L[:,:,3].astype(np.float32)/255
G=cv2.cvtColor(L[:,:,:3],cv2.COLOR_BGR2GRAY).astype(np.float32)*A
EXTRA={}
# slides whose old logo sat on photo texture under text: clone a clean neighbouring patch instead of smoothing
CLONE={}
TOPOPEN={'n15':(50,934,330,1080)}
def clone(im,b,dx,F=8):
    x0,y0,x1,y1=b;src=im[y0:y1,x0+dx:x1+dx].astype(np.float32);dst=im[y0:y1,x0:x1].astype(np.float32)
    h,w=dst.shape[:2];yy=np.minimum(np.arange(h),np.arange(h)[::-1]);xx=np.minimum(np.arange(w),np.arange(w)[::-1])
    a=np.minimum(np.clip(yy/F,0,1)[:,None],np.clip(xx/F,0,1)[None,:]);a[:F]=np.clip(np.arange(F)/1.5,0,1)[:,None]*np.clip(xx/F,0,1)[None,:]
    im[y0:y1,x0:x1]=(src*a[...,None]+dst*(1-a[...,None])).astype(np.uint8);return im
SCRIM={'n09':0.88,'n14':0.8,'n18':0.8,'n15':0.45}
LW,LX,LY=200,1666,39   # at 1920 width: logo width, left, top
def find(Gi):
    best=(-1,0,0)
    for w in range(120,300,2):
        t=cv2.resize(G,(w,round(w*L.shape[0]/L.shape[1])),interpolation=cv2.INTER_AREA)
        r=cv2.matchTemplate(Gi,t,cv2.TM_CCOEFF_NORMED);_,m,_,p=cv2.minMaxLoc(r)
        if m>best[0]:best=(m,w,p)
    return best
def logo_at(w):
    h=round(w*L.shape[0]/L.shape[1])
    return cv2.resize(L,(w,h),interpolation=cv2.INTER_AREA)
def darkfill(im,b,F):
    # fill with the surrounding dark tone (sampled below/left/right, not from the text above), keep text pixels
    x0,y0,x1,y1=b;H0,W0=im.shape[:2]
    ring=np.concatenate([im[y1:min(H0,y1+F),x0:x1].reshape(-1,3),im[y0+F:y1,max(0,x0-F):x0].reshape(-1,3),im[y0+F:y1,x1:x1+F].reshape(-1,3)])
    c=np.median(ring,0).astype(np.float32)
    X0,Y0,X1,Y1=max(0,x0-F),y0-2,min(W0,x1+F),min(H0,y1+F);reg=im[Y0:Y1,X0:X1].astype(np.float32)
    g=cv2.cvtColor(im[Y0:Y1,X0:X1],cv2.COLOR_BGR2GRAY);txt=cv2.GaussianBlur(cv2.dilate((g>70).astype(np.uint8),np.ones((5,5),np.uint8)).astype(np.float32),(0,0),1)
    m=np.zeros(g.shape,np.float32);m[0:y1-Y0,x0-X0:x1-X0]=1;a=cv2.GaussianBlur(m,(0,0),F/2.5);a[:,:]=np.where(m>0,np.maximum(a,cv2.GaussianBlur(m,(0,0),F/2.5)),a)
    a[:2]=0;txt[5:]=0;a=a*(1-txt);rng=np.random.default_rng(2);fill=c+rng.normal(0,1.2,g.shape)[...,None]
    im[Y0:Y1,X0:X1]=np.clip(fill*a[...,None]+reg*(1-a[...,None]),0,255).astype(np.uint8);return im
def boxfill(im,b,F,top_open=False):
    # smooth fill of a rectangle from its surroundings (coarse inpaint), feathered, with matched grain
    x0,y0,x1,y1=b;H0,W0=im.shape[:2];E=3*F
    X0,Y0,X1,Y1=max(0,x0-E),max(0,y0-E),min(W0,x1+E),min(H0,y1+E)
    reg=im[Y0:Y1,X0:X1].copy();m=np.zeros(reg.shape[:2],np.uint8);m[y0-Y0:y1-Y0,x0-X0:x1-X0]=255
    k=4;sm=cv2.resize(reg,None,fx=1/k,fy=1/k,interpolation=cv2.INTER_AREA);mm=cv2.resize(m,(sm.shape[1],sm.shape[0]),interpolation=cv2.INTER_NEAREST)
    mm=cv2.dilate(mm,np.ones((3,3),np.uint8))
    if top_open:mm[:(y1-Y0)//k]=np.maximum(mm[:(y1-Y0)//k],mm.max(0)[None,:])
    fill=cv2.inpaint(sm,mm,5,cv2.INPAINT_TELEA)
    fill=cv2.GaussianBlur(cv2.resize(fill,(reg.shape[1],reg.shape[0]),interpolation=cv2.INTER_CUBIC),(0,0),3).astype(np.float32)
    ring=(cv2.dilate(m,np.ones((2*F+1,2*F+1),np.uint8))>0)&(m==0)
    d_=(reg[ring].astype(np.float32)-cv2.GaussianBlur(reg,(0,0),3)[ring].astype(np.float32));sd=min(2.5,1.4826*float(np.median(np.abs(d_))))
    rng=np.random.default_rng(1);fill+=rng.normal(0,sd,fill.shape[:2])[...,None]
    a=cv2.GaussianBlur(m.astype(np.float32)/255,(0,0),F/2);a=np.maximum(a,m/255.0)[...,None]
    im[Y0:Y1,X0:X1]=np.clip(fill*a+reg*(1-a),0,255).astype(np.uint8);return im
for f in sorted(glob.glob('assets/n[0-2][0-9]-*.*')):
    if len(sys.argv)>1 and not any(f.startswith('assets/n'+k) for k in sys.argv[1:]):continue
    im=cv2.imread(f)
    if im.shape[1]!=1920:im=cv2.resize(im,(1920,1080),interpolation=cv2.INTER_LANCZOS4)  # one presentation size for every slide
    H0,W0=im.shape[:2];s=W0/1920
    Gi=cv2.cvtColor(cv2.resize(im,(1920,round(H0/s))),cv2.COLOR_BGR2GRAY).astype(np.float32)
    m,w,(x,y)=find(Gi)
    if f[7:10] in TOPOPEN:
        im=darkfill(im,tuple(round(v*s) for v in TOPOPEN[f[7:10]]),round(44*s));m=-m
    if f[7:10] in CLONE:
        b,dx=CLONE[f[7:10]];im=clone(im,tuple(round(v*s) for v in b),round(dx*s));m=-m
    if m>0.6:
        lg=logo_at(round(w*s));x,y=round(x*s),round(y*s);h,ww=lg.shape[:2]
        P=round(8*s);x0,y0,x1,y1=max(0,x-P),max(0,y-P),min(W0,x+ww+P),min(H0,y+h+P)
        im=boxfill(im,(x0,y0,x1,y1),round(10*s))
    for b in EXTRA.get(f[7:10],[]):im=boxfill(im,tuple(round(v*s) for v in b),round(6*s))
    if f[7:10] in SCRIM:   # bright/busy backdrop: soft feathered navy shade so the logo (incl. blue eTeacher) reads
        Hh,Ww=im.shape[:2];yy,xx=np.mgrid[0:Hh,0:Ww].astype(np.float32);cx,cy=(LX+LW/2)*s,(LY+45)*s
        d=((xx-cx)/(170*s))**2+((yy-cy)/(95*s))**2;al=(SCRIM[f[7:10]]*np.exp(-d*1.6))[...,None]
        im=np.clip(im*(1-al)+np.array([40,18,8],np.float32)*al,0,255).astype(np.uint8)
    lg=logo_at(round(LW*s));h,ww=lg.shape[:2];X,Y=round(LX*s),round(LY*s)
    a=lg[:,:,3:].astype(np.float32)/255
    im[Y:Y+h,X:X+ww]=(lg[:,:,:3]*a+im[Y:Y+h,X:X+ww]*(1-a)).astype(np.uint8)
    cv2.imwrite(f,im,[cv2.IMWRITE_JPEG_QUALITY,95] if f.endswith('jpg') else [])
    print(f,'removed' if abs(m)>0.6 else 'none',round(m,2),w)
