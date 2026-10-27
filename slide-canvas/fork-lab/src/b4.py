import cv2,numpy as np
R=cv2.imread('new.png').astype(np.float32);O=cv2.imread('o.png').astype(np.float32);B=cv2.imread('base.png').astype(np.float32);plate=np.load('plateL.npy')
H,W=R.shape[:2]
def feather(x0,y0,x1,y1,f):
    m=np.zeros((H,W),np.float32);m[y0+f:y1-f,x0+f:x1-f]=1;return cv2.GaussianBlur(m,(0,0),f/2)[...,None]
# 4 clock: original pixels
a=feather(1228,228,1385,352,8);R=R*(1-a)+O*a
# 6 footer label left
a=feather(30,1010,420,1065,6);R=R*(1-a)+plate*a
# 2 laptop zoom gallery from base plate
src=np.float32([[912,716],[1160,716],[1160,880],[912,880]])
dst=np.float32([[880,762],[1182,762],[1182,958],[880,958]])
M=cv2.getPerspectiveTransform(src,dst)
g=cv2.warpPerspective(B,M,(W,H),flags=cv2.INTER_CUBIC)
x0,y0,x1,y1=880,762,1182,958
R[y0:y1,x0:x1]=g[y0:y1,x0:x1]
# logo tile = bottom-right tile (3 cols x 2 rows within top ~85% of screen)
th=int((y1-y0)*0.83/2);tw=(x1-x0)//3
tx0=1083;ty0=882-36;tx1=1179;ty1=934
R[ty0:ty1,tx0:tx1]=np.array([70,36,16],np.float32)
L=cv2.imread('/workspace/lla-masterclass-syllabus/slide-canvas/v46/assets/src/fork-v46/closing-graphics/lla-logo-original.png',-1).astype(np.float32)
def putlogo(R,cx,cy,w):
    l=cv2.resize(L,(w,int(L.shape[0]*w/L.shape[1])),interpolation=cv2.INTER_AREA)
    h=l.shape[0];x=int(cx-w/2);y=int(cy-h/2);A=l[...,3:]/255
    R[y:y+h,x:x+w]=R[y:y+h,x:x+w]*(1-A)+l[...,:3]*A
putlogo(R,(tx0+tx1)/2,(ty0+ty1)/2,int((tx1-tx0)*0.84))
# 3 phone logo: clear & paste sharp
bgc=O[786:792,1240:1300].reshape(-1,3).mean(0)
R[790:834,1226:1318]=bgc
putlogo(R,1272,812,88)
out=np.clip(np.round(R),0,255).astype(np.uint8);cv2.imwrite('new.png',out)
cv2.imwrite('n12.png',cv2.resize(out[730:1040,850:1380],None,fx=1.6,fy=1.6))
