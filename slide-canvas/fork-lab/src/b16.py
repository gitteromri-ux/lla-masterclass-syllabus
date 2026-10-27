import cv2,numpy as np
P=cv2.imread('s12.png').astype(np.float32);R=cv2.imread('s14.png').astype(np.float32);H,W=R.shape[:2]
k=lambda n:cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(n,n));yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
cm=np.clip(47-np.hypot(xx-1242,yy-313),0,1)[...,None];R=R*(1-cm)+np.minimum(R*1.3,255)*cm
sn=P.max(2)-P.min(2);hl=((sn>60)&(P.max(2)>140));hl[:,:1240]=0;hl[742:]=0
a=cv2.GaussianBlur(cv2.dilate(hl.astype(np.uint8),k(3)).astype(np.float32),(0,0),0.6)[...,None];R=R*(1-a)+P*a
o=np.clip(R,0,255).astype(np.uint8);cv2.imwrite('new.png',o)
for i,y in enumerate([270,390,505,625]):cv2.imwrite(f'zoom6_r{i}.png',cv2.resize(o[y:y+85,1000:1660],None,fx=1.5,fy=1.5))
cv2.imwrite('zoom6_all.png',o[100:760,950:1920])
