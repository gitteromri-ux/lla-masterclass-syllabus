import cv2,numpy as np
from PIL import Image
N=cv2.imread('new.png').astype(np.float32);O=cv2.imread('o.png').astype(np.float32);H,W=N.shape[:2]
X0,Y0,X1,Y1=1180,180,1700,345
k=lambda n:cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(n,n))
# orig objects mask
m=np.zeros((H,W),np.uint8)
ca=np.array(Image.open('c_clock.png'))[...,3];h,w=ca.shape;m[255:255+h,1250:1250+w]=np.maximum(m[255:255+h,1250:1250+w],(ca>20)*255)
so=O.max(2)-O.min(2);t=((so>50)&(O.max(2)>120))|(O.min(2)>170);t[:, :1370]=False;t[:Y0]=0;t[Y1+20:]=0
m=np.maximum(m,t.astype(np.uint8)*255);m=cv2.dilate(m,k(9))
B=cv2.inpaint(np.clip(O,0,255).astype(np.uint8),m,4,cv2.INPAINT_NS).astype(np.float32)
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
g=np.exp(-(((xx-1560)/330)**2+((yy-470)/260)**2));g[:,:1260]*=np.clip((xx[:,:1260]-1180)/80,0,1);g[740:]=0
g=cv2.GaussianBlur(g,(0,0),20);B=B*(1-0.42*g)[...,None]
# keep new: headline + shadow, clock
sn=N.max(2)-N.min(2);hl=((sn>60)&(N.max(2)>140));hl[:, :1300]=0
K=cv2.dilate(hl.astype(np.uint8),k(17)).astype(np.float32)
K=np.maximum(K,(np.hypot(xx-1246,yy-319)<54).astype(np.float32))
K=cv2.GaussianBlur(K,(0,0),2.5)
E=np.zeros((H,W),np.float32);E[Y0:Y1,X0:X1]=1;E=cv2.GaussianBlur(E,(0,0),6)*(1-K)
R=N*(1-E[...,None])+B*E[...,None]
o=np.clip(R,0,255).astype(np.uint8);cv2.imwrite('new.png',o)
for n,(x,y) in {'clock':(1150,200),'dumb':(1000,330),'broc':(1000,470),'cgm':(980,590)}.items():
  cv2.imwrite(f'zoom_{n}.png',cv2.resize(o[y:y+170,x:x+420],None,fx=2.4,fy=2.4,interpolation=cv2.INTER_NEAREST))
cv2.imwrite('zoom_row1.png',o[170:360,1150:1900])
