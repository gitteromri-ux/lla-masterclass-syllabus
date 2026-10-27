import cv2,numpy as np
N=cv2.imread('new.png').astype(np.float32);H,W=N.shape[:2]
k=lambda n:cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(n,n))
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
sn=N.max(2)-N.min(2);hl=((sn>60)&(N.max(2)>140));hl[:,:1300]=0
K=cv2.dilate(hl.astype(np.uint8),k(13)).astype(np.float32);K=np.maximum(K,(np.hypot(xx-1242,yy-313)<49).astype(np.float32))
road=((sn<28)&(N.mean(2)>60)&(N.mean(2)<165)).astype(np.float32);Z=np.zeros_like(road);Z[180:742,980:1920]=1
M=cv2.GaussianBlur(cv2.morphologyEx(road,cv2.MORPH_CLOSE,k(9))*Z,(0,0),4)*(1-cv2.GaussianBlur(K,(0,0),2))
S=cv2.GaussianBlur(N,(0,0),5);rng=np.random.default_rng(1);S+=cv2.GaussianBlur(rng.normal(0,4,(H,W)).astype(np.float32),(0,0),0.6)[...,None]
R=N*(1-M[...,None])+S*M[...,None];o=np.clip(R,0,255).astype(np.uint8);cv2.imwrite('new.png',o)
cv2.imwrite('zoom2_clock.png',cv2.resize(o[200:370,1150:1570],None,fx=2.4,fy=2.4))
for n,(x,y) in {'dumb':(1000,330),'broc':(1000,470),'cgm':(980,590)}.items():cv2.imwrite(f'zoom2_{n}.png',cv2.resize(o[y:y+170,x:x+420],None,fx=2.4,fy=2.4))
