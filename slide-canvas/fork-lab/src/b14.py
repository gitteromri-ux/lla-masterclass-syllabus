import cv2,numpy as np
N=cv2.imread('new.png').astype(np.float32);H,W=N.shape[:2]
k=lambda n:cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(n,n))
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
Y=N.mean(2);sn=N.max(2)-N.min(2)
obj=((sn>60)&(N.max(2)>140)).astype(np.uint8);obj[:,:1290]=0
obj=np.maximum(obj,(np.hypot(xx-1242,yy-313)<50).astype(np.uint8))
obj[340:742,1000:1300]=np.maximum(obj[340:742,1000:1300],((Y[340:742,1000:1300]<45)|(Y[340:742,1000:1300]>160)).astype(np.uint8))
obj=cv2.dilate(obj,k(15))
Yc=cv2.inpaint(np.clip(Y,0,255).astype(np.uint8),obj*255,9,cv2.INPAINT_TELEA).astype(np.float32)
L=cv2.GaussianBlur(Yc,(0,0),35)
T=np.percentile(Yc[600:740,1650:1900],50);print('T',T)
Tm=np.minimum(L,T*1.05+ 0*L)
reg=np.zeros((H,W),np.float32);reg[130:742,1220:1920]=1;reg=cv2.GaussianBlur(reg,(0,0),55);reg[742:]=0
gain=np.where(L>0,Tm/np.maximum(L,1),1);gain=1-(1-gain)*reg
tx=((sn>60)&(N.max(2)>140)).astype(np.uint8);tx[:,:1290]=0;O=cv2.GaussianBlur(cv2.dilate(tx,k(3)).astype(np.float32),(0,0),1)
gain=gain*(1-O)+np.maximum(gain,0.9)*O  # keep headlines/objects near own level
R=N*gain[...,None];o=np.clip(R,0,255).astype(np.uint8);cv2.imwrite('new.png',o)
cv2.imwrite('zoom4_all.png',o[100:760,950:1920]);cv2.imwrite('zoom4_row1.png',cv2.resize(o[180:360,1180:1700],None,fx=2,fy=2))
