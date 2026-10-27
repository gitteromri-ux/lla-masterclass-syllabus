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
C=np.load('C.npy')
for x0,y0,x1,y1 in [(1190,400,1300,432),(1240,505,1310,545)]:
    sub=R[y0:y1,x0:x1];sat=sub.max(2)-sub.min(2);t=((sat>60)&(sub.max(2)>140)).astype(np.uint8)
    t=cv2.dilate(t,np.ones((5,5),np.uint8)).astype(np.float32)[...,None]
    R[y0:y1,x0:x1]=sub*t+C[y0:y1,x0:x1]*(1-t)
TH=46
pt=R[362:392,1185:1298].copy();al=np.ones((30,113),np.float32);al=cv2.GaussianBlur(np.pad(al[4:-4,4:-4],4),(0,0),2)[...,None]
sub=R[398:428,1185:1298];sat=sub.max(2)-sub.min(2);keep=cv2.dilate(((sat>60)&(sub.max(2)>140)).astype(np.uint8),np.ones((5,5),np.uint8)).astype(np.float32)[...,None]
a2=al*(1-keep);R[398:428,1185:1298]=sub*(1-a2)+pt*a2
def tight(c):
    a0,b0,a1,b1=bb(c);return c[b0:b1+1,a0:a1+1]
def toh(c,h):
    c=tight(c);s=h/c.shape[0];c=cv2.resize(c,(max(1,int(round(c.shape[1]*s))),h),interpolation=cv2.INTER_AREA)
    return np.pad(c,((24,24),(24,24),(0,0)))
def place(c,cy,right,op=0.5):
    a0,b0,a1,b1=bb(c);x=int(round(right-a1));y=int(round(cy-(b0+b1)/2));put(R,c,x,y,op);return x+a0,y+b0,x+a1,y+b1
cc=np.array(Image.open('c_clock.png')).astype(np.float32);ox,oy=1250,255;h,w=cc.shape[:2]
clock=np.dstack([O[oy:oy+h,ox:ox+w][...,::-1],cc[...,3:]])
dumb=np.array(Image.open('c_dumb.png')).astype(np.float32)
br=np.array(Image.open('c_broc.png').convert('RGBA')).astype(np.float32);br[...,3]=np.clip((br[...,3]-60)/170,0,1)*255
br[...,:3]*=0.62;g=br[...,:3].mean(2,keepdims=True);br[...,:3]=g+(br[...,:3]-g)*0.8
cg=np.array(Image.open('c_cgm.png')).astype(np.float32);sen=cg[:,:98];ph=cg[:,98:]
for nm,c,(cy,xl) in [('clock',clock,rows[0]),('dumb',dumb,rows[1]),('broc',br,rows[2])]:
    print(nm,place(toh(c,TH),cy,xl-GAP))
cy,xl=rows[3]
p=place(toh(ph,38),cy,xl-GAP);print('phone',p)
print('sensor',place(toh(sen,TH),cy,p[0]-8))
cv2.imwrite('z18.png',np.clip(R,0,255).astype(np.uint8)[250:720,1000:1500]);cv2.imwrite('new.png',np.clip(np.round(R),0,255).astype(np.uint8))
