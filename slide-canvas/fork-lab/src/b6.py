import cv2,numpy as np
from PIL import Image
F=cv2.imread('new.png').astype(np.float32);O=cv2.imread('o.png');B=cv2.imread('base.png').astype(np.float32)
H,W=O.shape[:2];tm=np.load('tm.npy')
m=np.zeros((H,W),np.uint8)
for n,(ox,oy) in {'clock':(1250,255),'dumb':(1040,330),'cgm':(1020,490)}.items():
    a=np.array(Image.open('c_%s.png'%n))[...,3];h,w=a.shape
    am=(a>8).astype(np.uint8)*255
    sub=O[oy:oy+h,ox:ox+w].astype(np.float32).mean(2);med=cv2.medianBlur(O[oy:oy+h,ox:ox+w],31).astype(np.float32).mean(2)
    dark=((med-sub)>10).astype(np.uint8)*255
    near=cv2.dilate(am,np.ones((41,41),np.uint8))
    d1=cv2.dilate(am,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(17,17)));sh=np.zeros_like(d1);sh[18:,:w-24]=d1[:-18,24:]
    mm=d1|cv2.dilate(sh,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(25,25)))|(cv2.dilate(dark,np.ones((9,9),np.uint8))&near)
    m[oy:oy+h,ox:ox+w]|=mm
m[405:447,1200:1298]=255;m[496:516,1240:1330]=255
rt=tm.copy();rt[:, :1180]=0;rt[:200]=0;rt[740:]=0
m|=cv2.dilate(rt,np.ones((3,3),np.uint8))
C=cv2.inpaint(O,m,5,cv2.INPAINT_TELEA).astype(np.float32)
src=B[560:700,1300:1460];hf=src-cv2.GaussianBlur(src,(0,0),3)
hf2=np.concatenate([hf,hf[::-1]],0);hf2=np.concatenate([hf2,hf2[:,::-1]],1)
tile=np.tile(hf2,(H//280+1,W//320+1,1))[:H,:W]
mf=cv2.GaussianBlur(m.astype(np.float32)/255,(0,0),1.5)[...,None]
C=cv2.GaussianBlur(C,(0,0),1.2)*mf+C*(1-mf);C=C+tile*mf*1.0
reg=np.zeros((H,W),np.float32);reg[228:738,1000:1900]=1
for cy,xl in [(312,1390),(432,1301),(547,1263),(666,1253)]:
    reg[int(cy-31):int(cy+31),xl-6:]=0
reg=cv2.GaussianBlur(reg,(0,0),1.5)[...,None]
out=F*(1-reg)+C*reg
cv2.imwrite('new6.png',np.clip(out,0,255).astype(np.uint8))
cv2.imwrite('z12.png',np.clip(out,0,255).astype(np.uint8)[220:740,1000:1700])
