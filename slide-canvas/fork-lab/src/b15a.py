import cv2,numpy as np
P=cv2.imread('s12.png').astype(np.float32);N=cv2.imread('s12.png').astype(np.float32);H,W=N.shape[:2]
k=lambda n:cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(n,n))
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
sn=P.max(2)-P.min(2);hl=((sn>60)&(P.max(2)>140));hl[:,:1240]=0;hl[742:]=0
K=cv2.dilate(hl.astype(np.uint8),k(13)).astype(np.float32);K=np.maximum(K,(np.hypot(xx-1242,yy-313)<49).astype(np.float32))
road=((sn<28)&(P.mean(2)>60)&(P.mean(2)<165)).astype(np.float32);Z=np.zeros_like(road);Z[250:742,980:1920]=1
M=cv2.GaussianBlur(cv2.morphologyEx(road,cv2.MORPH_CLOSE,k(9))*Z,(0,0),3)*(1-cv2.GaussianBlur(np.maximum(K,cv2.dilate(((P.mean(2)<60)|(P.mean(2)>165)|(sn>28)).astype(np.uint8)*(Z>0),k(9)).astype(np.float32)),(0,0),2))
# texture synth from dark road
src=cv2.imread('pre15.png').astype(np.float32)[600:740,1650:1900];hf=src-cv2.GaussianBlur(src,(0,0),4)
rng=np.random.default_rng(7);T=np.zeros((H,W,3),np.float32);Wt=np.zeros((H,W),np.float32)
p=48;win=np.outer(np.hanning(p),np.hanning(p)).astype(np.float32)+1e-3
for y in range(140,760,p//2):
  for x in range(940,1920,p//2):
    sy=rng.integers(0,src.shape[0]-p);sx=rng.integers(0,src.shape[1]-p);pt=hf[sy:sy+p,sx:sx+p]
    if rng.random()<.5:pt=pt[:,::-1]
    hh=min(p,H-y);ww=min(p,W-x);T[y:y+hh,x:x+ww]+=pt[:hh,:ww]*win[:hh,:ww,None];Wt[y:y+hh,x:x+ww]+=win[:hh,:ww]
T/=np.maximum(Wt,1e-3)[...,None];T*=1.6
base=cv2.GaussianBlur(N,(0,0),6)
R=N*(1-M[...,None])+(base+T)*M[...,None]
cv2.imwrite('s15.png',np.clip(R,0,255).astype(np.uint8))
