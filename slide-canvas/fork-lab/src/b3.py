import cv2,numpy as np
from PIL import Image,ImageDraw
O=cv2.imread('o.png').astype(np.float32);R=np.load('R_right.npy');plate=np.load('plate.npy');tm=np.load('tm.npy')
H,W=O.shape[:2]
def dil(m,k):return cv2.dilate(m,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(k,k)))
def matte(x0,y0,x1,y1):
    s=O[y0:y1,x0:x1];b=plate[y0:y1,x0:x1]
    m=(dil(tm[y0:y1,x0:x1],3)>0).astype(np.float32)
    lum=s.max(2);bl=b.max(2);tl=np.percentile(lum[m>0],98)
    al=np.clip((lum-bl)/np.maximum(tl-bl,25),0,1)*m
    col=np.clip((s-b*(1-al[...,None]))/np.maximum(al[...,None],0.08),0,255)
    return np.dstack([col,al[...,None]*255])
CX0,CY0,CX1,CY1=84,540,628,858;RAD=26
# card base: text-free plate behind (left), blurred + darkened glass
P=plate.copy()
bl=cv2.GaussianBlur(P,(0,0),22)[CY0:CY1,CX0:CX1]
hh,ww=CY1-CY0,CX1-CX0
yy,xx=np.mgrid[0:hh,0:ww].astype(np.float32)
navy=np.array([46,28,16],np.float32)   # BGR
t=(yy/hh)[...,None]
glass=bl*0.30+navy*0.62*(1+0.10*(1-t))+ (1-t)*6
mask=np.zeros((hh,ww),np.uint8)
cv2.rectangle(mask,(RAD,0),(ww-RAD,hh),255,-1);cv2.rectangle(mask,(0,RAD),(ww,hh-RAD),255,-1)
for cx,cy in [(RAD,RAD),(ww-RAD-1,RAD),(RAD,hh-RAD-1),(ww-RAD-1,hh-RAD-1)]:cv2.circle(mask,(cx,cy),RAD,255,-1,cv2.LINE_AA)
mk=mask.astype(np.float32)/255
# drop shadow (depth)
sh=np.zeros((H,W),np.float32);sh[CY0:CY1,CX0:CX1]=mk;M=np.float32([[1,0,0],[0,1,16]])
sh=cv2.GaussianBlur(cv2.warpAffine(sh,M,(W,H)),(0,0),22)
ramp=np.clip((859-np.arange(W))/8,0,1)[None,:];sh=np.maximum(sh*ramp,0)
# R left part: restore text-free plate in left text area first
lm=np.zeros((H,W),np.uint8);lm[CY0-30:CY1+30,0:CX1+40]=255
a=cv2.GaussianBlur((tm&lm).astype(np.float32)/255,(0,0),2.5)[...,None]
R=R*(1-a)+plate*a

# bevel: top highlight edge, bottom darker edge
edge=mk-cv2.erode(mk,np.ones((3,3),np.uint8))
top=np.clip(1-yy/(hh*0.6),0,1)
rim=np.array([200,190,90],np.float32)*(edge*top*0.32)[...,None]
glass=glass+rim+ (edge*top*14)[...,None]+ (edge*(1-top)*8)[...,None]
inner=cv2.GaussianBlur(mk,(0,0),10);glass*= (0.92+0.08*inner)[...,None]
def rrmask(x0,y0,x1,y1,r,S=4):
    w,h=x1-x0,y1-y0;m=Image.new('L',(w*S,h*S),0);ImageDraw.Draw(m).rounded_rectangle((0,0,w*S-1,h*S-1),radius=r*S,fill=255)
    return np.array(m.resize((w,h),Image.LANCZOS)).astype(np.float32)/255
def ring(x0,y0,x1,y1,r,t=1.6):
    a=rrmask(x0,y0,x1,y1,r);k=int(round(t));Sm=cv2.erode(a,np.ones((2*k+1,2*k+1),np.uint8))
    return np.clip(a-Sm,0,1)
def glass(N,box,r,tint,tint_a,edge_a,blur=16):
    x0,y0,x1,y1=box;sub=N[y0:y1,x0:x1];bl=cv2.GaussianBlur(sub,(0,0),blur)
    m=rrmask(x0,y0,x1,y1,r)[...,None]
    t=np.array(tint[::-1],np.float32)
    fill=bl*(1-tint_a)+t*tint_a*0.55+bl*0.0
    # gentle vertical sheen
    g=np.linspace(1.12,0.9,y1-y0)[:,None,None];fill=fill*g
    out=sub*(1-m)+fill*m
    e=ring(x0,y0,x1,y1,r)[...,None]*edge_a;out=out*(1-e)+(t*0.55+np.array([255,255,255],np.float32)*0.45)*e
    N[y0:y1,x0:x1]=out;return N
TINT=(226,170,80)
R*=(1-0.5*sh[...,None])
gm=np.zeros((H,W),np.float32);gm[CY0:CY1,CX0:CX1]=ring(CX0,CY0,CX1,CY1,RAD,3)
gl=cv2.GaussianBlur(gm,(0,0),9)*ramp;R+=gl[...,None]*np.array(TINT[::-1],np.float32)[None,None]*0.9
R=glass(R,(CX0,CY0,CX1,CY1),RAD,TINT,0.34,0.6)
# ---- text: stat block scaled 1.07, change nothing 1.0
def paste(R,lay,x,y,sc=1.0):
    if sc!=1.0:lay=cv2.resize(lay,(int(round(lay.shape[1]*sc)),int(round(lay.shape[0]*sc))),interpolation=cv2.INTER_CUBIC)
    lay=np.clip(lay,0,255);h,w=lay.shape[:2];A=lay[...,3:]/255
    R[y:y+h,x:x+w]=R[y:y+h,x:x+w]*(1-A)+lay[...,:3]*A
st=matte(88,378,560,572)
ci=matte(88,580,560,668)
cn=matte(88,702,505,838)
TX=108;SC=0.82
paste(R,st,TX,340+222,SC)          # ~ 340..498
paste(R,cn,TX,340+222+int(194*SC)+8,SC)
# ---- woman
wm=np.array(Image.open('woman.png')).astype(np.float32);wm=wm[...,[2,1,0,3]]
wm=wm[25:,90:665]
sc=168/wm.shape[1];wm=cv2.resize(wm,(int(wm.shape[1]*sc),int(wm.shape[0]*sc)),interpolation=cv2.INTER_AREA)
WX=CX1-10-wm.shape[1];WY=CY0+16
hcut=CY1-WY;wm=wm[:hcut].copy()
# clip to card mask & soft fade at bottom
cm=mk[WY-CY0:WY-CY0+wm.shape[0],WX-CX0:WX-CX0+wm.shape[1]]
fade=np.clip((wm.shape[0]-np.arange(wm.shape[0]))/60,0,1)[:,None]
wm[...,3]*=cm*fade
T=np.zeros((H,W),np.float32);T[382:382+int(290*SC),TX:TX+int(472*SC)]=st[:,:,3].max() and 0
wm[...,:3]=np.clip(wm[...,:3]*1.18+6,0,255)
paste(R,wm,WX,WY)
print('woman',WX,WY,wm.shape,'text right',TX+int((560-88)*SC))
# ---- protect Blueprint region: original pixels
R[742:1080,860:1920]=O[742:1080,860:1920]
out=np.clip(np.round(R),0,255).astype(np.uint8)
cv2.imwrite('new.png',out);np.save('plateL.npy',plate)
