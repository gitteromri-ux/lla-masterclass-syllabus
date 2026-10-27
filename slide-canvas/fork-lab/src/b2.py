import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
F='/workspace/lla-masterclass-syllabus/deck2/fonts/'
O=cv2.imread('o.png').astype(np.float32);B=cv2.imread('base.png').astype(np.float32)
H,W=O.shape[:2];rng=np.random.default_rng(7)
def dil(m,k):return cv2.dilate(m,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(k,k)))
def tmask(x0,y0,x1,y1,th=140,sat=60):
    m=np.zeros((H,W),np.uint8);s=O[y0:y1,x0:x1]
    m[y0:y1,x0:x1]=(((s.max(2)>th)|((s.max(2)-s.min(2))>sat))*255).astype(np.uint8);return m
RT=[(1385,244,1900,340,-12),(1300,365,1905,510,-25),(1250,548,1905,688,-45)]
LT=(85,375,600,672); LC=(85,700,520,840)
tm=np.zeros((H,W),np.uint8)
for x0,y0,x1,y1,_ in RT: tm|=tmask(x0,y0,x1,y1)
tm|=tmask(*LT);tm|=tmask(*LC)
tm=dil(tm,9)
# gain map base->O (normalized conv), excluding text & object zones
ex=tm.copy()
for r in [(1040,240,1400,680),(860,690,1920,1080),(0,0,1920,230),(1180,240,1420,370)]:
    cv2.rectangle(ex,r[:2],r[2:],255,-1)
v=(ex==0).astype(np.float32)
def nc(img,s):
    return cv2.GaussianBlur(img*v[...,None],(0,0),s)/np.maximum(cv2.GaussianBlur(v,(0,0),s)[...,None],1e-3)
G=(nc(O,18)+1)/(nc(B,18)+1)
plate=B*G
a=cv2.GaussianBlur(tm.astype(np.float32)/255,(0,0),2.5)[...,None]
P=O*(1-a)+plate*a
cv2.imwrite('P_dbg.png',np.clip(P,0,255).astype(np.uint8))
# ---- remove objects: alpha from cutouts, dilated + shadow toward lower-left
cuts={'clock':(1250,255),'dumb':(1040,330),'cgm':(1020,490)}
om=np.zeros((H,W),np.uint8);L={}
for n,(ox,oy) in cuts.items():
    c=np.array(Image.open('c_%s.png'%n)).astype(np.float32);L[n]=(c,ox,oy)
    al=(c[...,3]>8).astype(np.uint8)*255;h,w=al.shape
    m=dil(al,15);sh=np.zeros_like(m);sh[16:,:w-20]=m[:-16,20:];m=m|dil(sh,21)
    om[oy:oy+h,ox:ox+w]|=m
fill=cv2.inpaint(np.clip(P,0,255).astype(np.uint8),om,9,cv2.INPAINT_TELEA).astype(np.float32)
# real asphalt texture from clean patch
src=B[560:700,1300:1460];hf=src-cv2.GaussianBlur(src,(0,0),4)
tile=np.tile(hf,(H//140+1,W//160+1,1))[:H,:W]
fill=fill+tile
am=cv2.GaussianBlur(om.astype(np.float32)/255,(0,0),3)[...,None]
P=P*(1-am)+fill*am
R=P.copy()
# ---- right text moved via matte vs plate
def matte(x0,y0,x1,y1,mask):
    s=O[y0:y1,x0:x1];b=plate[y0:y1,x0:x1]
    m=(dil(mask[y0:y1,x0:x1],3)>0).astype(np.float32)
    lum=s.max(2);bl=b.max(2)
    tl=np.percentile(lum[m>0],98) if m.sum() else 255
    al=np.clip((lum-bl)/np.maximum(tl-bl,25),0,1)*m
    col=np.clip((s-b*(1-al[...,None]))/np.maximum(al[...,None],0.08),0,255)
    return col,al
HD=[(1385,244,1800,302,248-249,0),(1300,365,1700,428,378-372,1304-1307),(1250,548,1700,608,638-556,1250-1257)]
HC=[np.array([255,165,180],np.float32),np.array([255,190,110],np.float32),None]
ROWC=[310,428,664]
for (x0,y0,x1,y1,dy,dx),hc,rc in zip(HD,HC,ROWC):
    col,al=matte(x0,y0,x1,y1,tm);A=al[...,None]
    ys=np.where((al>0.3).any(1))[0];dy=int(round(rc-(y0+(ys.min()+ys.max())/2)));print('head',rc,dy)
    if hc is not None:
        l=col.max(2,keepdims=True);col=np.clip(l/np.percentile(l[al>0.9],60)*hc,0,255)
    R[y0+dy:y1+dy,x0+dx:x1+dx]=R[y0+dy:y1+dy,x0+dx:x1+dx]*(1-A)+col*A
def put(R,rgba,x,y,shadow=True,sh_op=0.5):
    h,w=rgba.shape[:2];A=rgba[...,3:]/255;rgb=rgba[...,2::-1] if rgba.shape[2]==4 else None
    if shadow:
        s=cv2.GaussianBlur(A[...,0],(0,0),3.5);M=np.float32([[1,0,-7],[0,1,6]])
        s=cv2.warpAffine(s,M,(w,h));s=np.clip(s*1.0,0,1)[...,None]
        R[y:y+h,x:x+w]*=1-sh_op*s*(1-A)
    R[y:y+h,x:x+w]=R[y:y+h,x:x+w]*(1-A)+rgb*A
def obj(n,sc):
    c,ox,oy=L[n];h,w=c.shape[:2];c=cv2.resize(c,(int(round(w*sc)),int(round(h*sc))),interpolation=cv2.INTER_AREA)
    a=(c[...,3]>20);ys,xs=np.where(a);return c,xs.min(),ys.min(),xs.max(),ys.max()
GAP=36
rows=[]
for n,sc,cy,tl in rows:
    c,a0,b0,a1,b1=obj(n,sc);x=int(tl-88-(a0+a1)/2);y=int(cy-(b0+b1)/2);put(R,c,x,y);print(n,x+a0,y+b0,x+a1,y+b1)
# CGM bigger, phone smaller
c,ox,oy=L['cgm'];sen=c[:,:98].copy();ph=c[:,98:].copy()
def bb(a):
    ys,xs=np.where(a[...,3]>20);return xs.min(),ys.min(),xs.max(),ys.max()
def sc_(a,s):return cv2.resize(a,(int(a.shape[1]*s),int(a.shape[0]*s)),interpolation=cv2.INTER_CUBIC if s>1 else cv2.INTER_AREA)
ph=sc_(ph,0.68);sen=sc_(sen,1.35)
cy=664;tl=1250
PUT_SUGAR=False
a0,b0,a1,b1=bb(ph);s0_,t0_,s1_,t1_=bb(sen);gw=(s1_-s0_)+10+(a1-a0);px=int(tl-30-a1);py=int(cy-(b0+b1)/2);0
s0,t0,s1,t1=bb(sen);sx=int(px+a0-10-s1);sy=int(cy+8-(t0+t1)/2);0
print('sensor',sx+s0,sy+t0,sx+s1,sy+t1,'phone',px+a0,py+b0,px+a1,py+b1)
# ---- veg headline
pf=F+'PlayfairDisplay-Italic.ttf'
f=ImageFont.truetype(pf,49)
try:f.set_variation_by_axes([600])
except Exception as e:print('var',e)
bb=f.getbbox('Watch your sugar.');print('wys bbox',bb)
# green color from Start moving headline
s=O[370:412,1305:1600];g=s[((s[...,1]-s[...,2])>60)];gc=np.median(g[g[:,1]>np.percentile(g[:,1],80)],0);print('green',gc)
VT=546-24; VX=1262
txt=Image.new('L',(600,140),0);d=ImageDraw.Draw(txt)
# position so glyph top aligns like sugar headline: sugar glyph top 555 for left 1262
d.text((10-bb[0]+ (1262-1257) ,20-bb[1]),'Add a vegetable.',font=f,fill=255)
al=np.array(txt).astype(np.float32)/255;A=al[...,None]
y0=VT-20;x0=VX-10
R[y0:y0+140,x0:x0+600]=R[y0:y0+140,x0:x0+600]*(1-A)+gc*A
vb=np.where(al>0.3);print('veg',x0+vb[1].min(),y0+vb[0].min(),x0+vb[1].max(),y0+vb[0].max())
# ---- broccoli
bc=np.array(Image.open('c_broc.png').convert('RGBA')).astype(np.float32)
bc=bc[225:731,249:785];bc[...,3]=np.clip((bc[...,3]-60)/170,0,1)*255;th=88;sc=th/bc.shape[0]
bc=cv2.resize(bc,(int(bc.shape[1]*sc),th),interpolation=cv2.INTER_AREA)
bc[...,:3]=bc[...,:3]*0.62;g=bc[...,:3].mean(2,keepdims=True);bc[...,:3]=g+(bc[...,:3]-g)*0.8
bc[...,2]*=1.04  # (RGB order here: slight cool)  
bc[...,0]*=0.97
bc=np.pad(bc,((20,20),(20,20),(0,0)))
vcy=(VT+VT+48)/2
bx=int(VX-88-bc.shape[1]/2);by=int(546-bc.shape[0]/2)
0;print('broc',bx,by,bx+bc.shape[1],by+th)
np.save('R_right.npy',R)
np.save('plate.npy',plate);np.save('tm.npy',tm)
cv2.imwrite('v.png',np.clip(R,0,255).astype(np.uint8))
