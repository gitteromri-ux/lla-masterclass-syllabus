import cv2,numpy as np
from PIL import Image
R=cv2.imread('new.png').astype(np.float32);H,W=R.shape[:2]
B=cv2.imread('base.png').astype(np.float32);hf=B[560:700,1300:1460];hf=hf-cv2.GaussianBlur(hf,(0,0),3)
hf2=np.concatenate([hf,hf[::-1]],0);hf2=np.concatenate([hf2,hf2[:,::-1]],1);tile=np.tile(hf2,(H//280+1,W//320+1,1))[:H,:W]
# laptop shrink
a=np.array(Image.open('c_laptopX.png'))[...,3].astype(np.float32)/255;a[:,356:]=0
ox,oy=850,735;h,w=a.shape
ys,xs=np.where(a>0.3);top,bot,lft,rgt=ys.min(),ys.max(),xs.min(),xs.max()
lap=np.dstack([R[oy:oy+h,ox:ox+w],a[...,None]*255])
m=np.zeros((H,W),np.uint8);m[oy:oy+h,ox:ox+w]=(cv2.dilate((a>0.05).astype(np.uint8),np.ones((5,5),np.uint8))*255)
inp=cv2.inpaint(np.clip(R,0,255).astype(np.uint8),m,7,cv2.INPAINT_TELEA).astype(np.float32)+tile*0.8
mf=cv2.GaussianBlur(m.astype(np.float32)/255,(0,0),1.5)[...,None];R=R*(1-mf)+inp*mf
sc=0.82
L2=cv2.resize(lap,(int(w*sc),int(h*sc)),interpolation=cv2.INTER_AREA)
# anchor bottom-right of laptop bbox
nx=int(round(ox+rgt-rgt*sc));ny=int(round(oy+bot-bot*sc))
hh,ww=L2.shape[:2];A=L2[...,3:]/255
R[ny:ny+hh,nx:nx+ww]=R[ny:ny+hh,nx:nx+ww]*(1-A)+L2[...,:3]*A
print('laptop new bbox',nx+int(lft*sc),ny+int(top*sc),nx+int(rgt*sc),ny+int(bot*sc))
# remove 26/27
x0,y0,x1,y1=1735,1018,1835,1062
p=R[y0:y1,x0-110:x1-110].copy();al=np.zeros((y1-y0,x1-x0),np.float32);al[6:-6,6:-6]=1;al=cv2.GaussianBlur(al,(0,0),3)[...,None]
R[y0:y1,x0:x1]=R[y0:y1,x0:x1]*(1-al)+p*al
out=np.clip(np.round(R),0,255).astype(np.uint8);cv2.imwrite('new.png',out)
cv2.imwrite('z32.png',out[700:1080,820:1920])
