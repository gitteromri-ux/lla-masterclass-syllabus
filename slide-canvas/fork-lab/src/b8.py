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
for y0,y1,x0 in [(265,360,1290),(385,480,1280),(500,595,1225),(620,712,1225)]:
    s=R[y0:y1,x0:1900];mk=((s.max(2)-s.min(2))>60)&(s.max(2)>140)
    cnt=mk.sum(1);good=np.where(cnt>0.45*cnt.max())[0]
    rows.append((y0+(good.min()+good.max())/2,x0+np.where(mk.any(0))[0].min()))
print(rows)
GAP=32
C=np.load('C.npy')
R[505:521,1238:1275]=C[505:521,1238:1275]
R[418:432,1262:1300]=C[418:432,1262:1300]
for x0,y0,x1,y1 in [(1150,398,1301,460),(1150,500,1262,520),(1236,505,1302,540),(1230,280,1312,345)]:
    sub=R[y0:y1,x0:x1];sat=sub.max(2)-sub.min(2);t=((sat>60)&(sub.max(2)>140)).astype(np.uint8)
    t=cv2.dilate(t,np.ones((5,5),np.uint8)).astype(np.float32)[...,None]
    R[y0:y1,x0:x1]=sub*t+C[y0:y1,x0:x1]*(1-t)
TH=90
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
ca=cv2.erode(cc[...,3],np.ones((5,5),np.uint8));ca=cv2.GaussianBlur(ca,(0,0),0.8)[...,None]
clock=np.dstack([O[oy:oy+h,ox:ox+w][...,::-1],ca])
dumb=np.array(Image.open('c_dumb.png')).astype(np.float32)
br=np.array(Image.open('c_broc.png').convert('RGBA')).astype(np.float32);br[...,3]=np.clip((br[...,3]-60)/170,0,1)*255
br[...,:3]*=0.62;g=br[...,:3].mean(2,keepdims=True);br[...,:3]=g+(br[...,:3]-g)*0.8
cg=np.array(Image.open('c_cgm.png')).astype(np.float32);sen=cg[:,:98];ph=cg[:,98:]
for nm,c,(cy,xl) in [('clock',clock,rows[0]),('dumb',dumb,rows[1]),('broc',br,rows[2])]:
    print(nm,place(toh(c,TH),cy,xl-GAP))
cy,xl=rows[3]
p=place(toh(ph,70),cy,xl-GAP-20);print('phone',p)
senR=cv2.rotate(np.ascontiguousarray(sen),cv2.ROTATE_90_CLOCKWISE)
print('sensor',place(toh(senR,TH),cy,p[0]-8))
hfS=cv2.imread('base.png').astype(np.float32)[560:700,1300:1460];hfS=hfS-cv2.GaussianBlur(hfS,(0,0),3)
x0,y0,x1,y1=1282,262,1308,362
sub=R[y0:y1,x0:x1];sat=sub.max(2)-sub.min(2);t=((sat>60)&(sub.max(2)>140))
mm=np.zeros(R.shape[:2],np.uint8);mm[y0:y1,x0:x1]=(~t)*255
inp=R.copy();pp=O[y0:y1,1340:1366].copy();ref=np.concatenate([R[y0:y1,x0-6:x0],R[y0:y1,x1:x1+6]],1).mean(1,keepdims=True);pm=pp.mean(1,keepdims=True);gain=cv2.GaussianBlur((ref/np.maximum(pm,1)).astype(np.float32),(0,0),6).reshape(-1,1,3);inp[y0:y1,x0:x1]=pp*gain
a=cv2.GaussianBlur(mm.astype(np.float32)/255,(0,0),1.2)[...,None];R=R*(1-a)+inp*a
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
g=np.exp(-(((xx-1560)/330)**2+((yy-470)/260)**2));g[:,:1260]*=np.clip((xx[:,:1260]-1180)/80,0,1);g[740:]=0
g=cv2.GaussianBlur(g,(0,0),20);g[742:]=0
sat=R.max(2)-R.min(2);tx=cv2.dilate((((sat>60)&(R.max(2)>140))).astype(np.uint8),np.ones((3,3),np.uint8)).astype(np.float32)
tx=cv2.GaussianBlur(tx,(0,0),0.8)
dk=1-0.42*g*(1-tx);R=R*dk[...,None]
x0,y0,x1,y1=1560,780,1920,1080
sub=R[y0:y1,x0:x1];tm_=(sub.max(2)>110).astype(np.float32);tm_=cv2.dilate(tm_,np.ones((7,7),np.uint8))
v=1-tm_
def ncb(img,s_):return cv2.GaussianBlur(img*v[...,None],(0,0),s_)/np.maximum(cv2.GaussianBlur(v,(0,0),s_)[...,None],1e-3)
new=sub-ncb(sub,8)+ncb(sub,45)
fe=np.ones((y1-y0,x1-x0),np.float32);fe[:20]*=np.linspace(0,1,20)[:,None];fe[:,:20]*=np.linspace(0,1,20)[None,:]
fe=(fe*v)[...,None];R[y0:y1,x0:x1]=sub*(1-fe)+new*fe
cv2.imwrite('z18.png',np.clip(R,0,255).astype(np.uint8)[250:720,1000:1500]);cv2.imwrite('new.png',np.clip(np.round(R),0,255).astype(np.uint8))
