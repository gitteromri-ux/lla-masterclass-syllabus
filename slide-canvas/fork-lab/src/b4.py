import cv2,numpy as np
R=cv2.imread('new.png').astype(np.float32);O=cv2.imread('o.png').astype(np.float32);B=cv2.imread('base.png').astype(np.float32);plate=np.load('plateL.npy')
H,W=R.shape[:2]
def feather(x0,y0,x1,y1,f):
    m=np.zeros((H,W),np.float32);m[y0+f:y1-f,x0+f:x1-f]=1;return cv2.GaussianBlur(m,(0,0),f/2)[...,None]
# 4 clock: original pixels
a=feather(1240,250,1372,362,10);R=R*(1-a)+O*a
# 6 footer label left
a=feather(30,1010,420,1065,6);R=R*(1-a)+plate*a
# 2 laptop: real Zoom mockup (lla-masterclass-assets/zoom-meeting-ui-chat.jpg)
Z=cv2.imread('zmu.jpg').astype(np.float32)
x0,y0,x1,y1=880,762,1182,958
sw,sh_=x1-x0,y1-y0
crop=Z[:,515:1938]
s_=sh_/crop.shape[0];zw=int(round(crop.shape[1]*s_))
zr=cv2.resize(crop,(zw,sh_),interpolation=cv2.INTER_AREA)
bgc=Z[1040:1075,520:1900].reshape(-1,3).mean(0)
scr=np.zeros((sh_,sw,3),np.float32)+bgc
ox=(sw-zw)//2;scr[:,ox:ox+zw]=zr
R[y0:y1,x0:x1]=scr
L=cv2.imread('/workspace/lla-masterclass-syllabus/slide-canvas/v46/assets/src/fork-v46/closing-graphics/lla-logo-original.png',-1).astype(np.float32)
def putlogo(R,cx,cy,w):
    l=cv2.resize(L,(w,int(L.shape[0]*w/L.shape[1])),interpolation=cv2.INTER_AREA)
    h=l.shape[0];x=int(cx-w/2);y=int(cy-h/2);A=l[...,3:]/255
    R[y:y+h,x:x+w]=R[y:y+h,x:x+w]*(1-A)+l[...,:3]*A
# 3 phone logo: clear & paste sharp
bgc=O[786:792,1240:1300].reshape(-1,3).mean(0)
R[790:834,1226:1318]=bgc
putlogo(R,1272,812,88)
out=np.clip(np.round(R),0,255).astype(np.uint8)
m=np.zeros(out.shape[:2],np.uint8);m[404:424,1112:1190]=255
import numpy as _n
fix=cv2.inpaint(out,m,5,cv2.INPAINT_TELEA);g=_n.random.default_rng(1).normal(0,5,out.shape).astype(_n.float32)
fx=_n.clip(fix.astype(_n.float32)+g,0,255).astype(_n.uint8);out[404:424,1112:1190]=fx[404:424,1112:1190]
cv2.imwrite('new.png',out)
cv2.imwrite('n12.png',cv2.resize(out[730:1040,850:1380],None,fx=1.6,fy=1.6))
