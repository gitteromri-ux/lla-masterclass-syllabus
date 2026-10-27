import cv2,numpy as np
from PIL import Image
R=cv2.imread('new6.png').astype(np.float32);O=cv2.imread('o.png').astype(np.float32)
H,W=R.shape[:2]
def put(R,rgba,x,y,sh_op=0.5):
    h,w=rgba.shape[:2];A=rgba[...,3:]/255;rgb=rgba[...,2::-1]
    s=cv2.GaussianBlur(A[...,0],(0,0),3.5);s=cv2.warpAffine(s,np.float32([[1,0,-7],[0,1,6]]),(w,h))[...,None]
    R[y:y+h,x:x+w]*=1-sh_op*s*(1-A);R[y:y+h,x:x+w]=R[y:y+h,x:x+w]*(1-A)+rgb*A
def ld(f,sc=1.0,crop=None):
    c=np.array(Image.open(f).convert('RGBA')).astype(np.float32)
    if crop:c=c[crop[1]:crop[3],crop[0]:crop[2]]
    if sc!=1:c=cv2.resize(c,(int(c.shape[1]*sc),int(c.shape[0]*sc)),interpolation=cv2.INTER_AREA if sc<1 else cv2.INTER_CUBIC)
    return np.pad(c,((24,24),(24,24),(0,0)))
def bb(c):
    ys,xs=np.where(c[...,3]>40);return xs.min(),ys.min(),xs.max(),ys.max()
# measure headlines on rendered pixels
rows=[]
for y0,y1,x0 in [(265,360,1290),(385,480,1290),(500,595,1250),(620,712,1240)]:
    s=R[y0:y1,x0:1900];mk=((s.max(2)-s.min(2))>60)&(s.max(2)>140)
    cnt=mk.sum(1);good=np.where(cnt>0.45*cnt.max())[0]
    rows.append((y0+(good.min()+good.max())/2,x0+np.where(mk.any(0))[0].min()))
print(rows)
GAP=32
# 1 clock: native original pixels (integer shift, no resampling)
cc=np.array(Image.open('c_clock.png')).astype(np.float32);ox,oy=1250,255
A=(cc[...,3:]/255);a0,b0,a1,b1=bb(cc)
cy,xl=rows[0];dx=int(round(xl-GAP-(ox+a1)));dy=int(round(cy-(oy+(b0+b1)/2)))
h,w=A.shape[:2];patch=O[oy:oy+h,ox:ox+w]
x,y=ox+dx,oy+dy
s=cv2.GaussianBlur(A[...,0],(0,0),3.5);s=cv2.warpAffine(s,np.float32([[1,0,-7],[0,1,6]]),(w,h))[...,None]
R[y:y+h,x:x+w]*=1-0.45*s*(1-A);R[y:y+h,x:x+w]=R[y:y+h,x:x+w]*(1-A)+patch*A
print('clock',x+a0,y+b0,x+a1,y+b1)
# 2 weights 0.63
c=ld('c_dumb.png',0.63);a0,b0,a1,b1=bb(c);cy,xl=rows[1]
x=int(round(xl-GAP-a1));y=int(round(cy-(b0+b1)/2));put(R,c,x,y);print('dumb',x+a0,y+b0,x+a1,y+b1)
# 3 broccoli
c=np.array(Image.open('c_broc.png').convert('RGBA')).astype(np.float32)[225:731,249:785]
c[...,3]=np.clip((c[...,3]-60)/170,0,1)*255;sc=88/c.shape[0];c=cv2.resize(c,(int(c.shape[1]*sc),88),interpolation=cv2.INTER_AREA)
c[...,:3]*=0.62;g=c[...,:3].mean(2,keepdims=True);c[...,:3]=g+(c[...,:3]-g)*0.8;c=np.pad(c,((24,24),(24,24),(0,0)))
a0,b0,a1,b1=bb(c);cy,xl=rows[2];x=int(round(xl-GAP-a1));y=int(round(cy-(b0+b1)/2));put(R,c,x,y,0.6);print('broc',x+a0,y+b0,x+a1,y+b1)
# 4 CGM bigger + phone smaller
cg=np.array(Image.open('c_cgm.png')).astype(np.float32)
sen=cg[:,:98];ph=cg[:,98:]
def sc_(a,s):return np.pad(cv2.resize(a,(int(a.shape[1]*s),int(a.shape[0]*s)),interpolation=cv2.INTER_CUBIC if s>1 else cv2.INTER_AREA),((24,24),(24,24),(0,0)))
ph=sc_(ph,0.68);sen=sc_(sen,1.35);cy,xl=rows[3]
a0,b0,a1,b1=bb(ph);px=int(round(xl-GAP-a1));py=int(round(cy-(b0+b1)/2));put(R,ph,px,py)
s0,t0,s1,t1=bb(sen);sx=int(px+a0-10-s1);sy=int(round(cy-(t0+t1)/2));put(R,sen,sx,sy)
print('cgm',sx+s0,sy+t0,'phone',px+a0,py+b0,px+a1,py+b1)
cv2.imwrite('new.png',np.clip(np.round(R),0,255).astype(np.uint8))
