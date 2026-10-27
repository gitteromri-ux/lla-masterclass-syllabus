# V46 round 17 (Julie): slide 12 (n09-food.jpg): remove the 'ON MY PLATE' section (label + five pills). Area rebuilt from the exact background model used by build-v46-round6-s11.py (food-pillars-bg.jpg, blurred, navy shade); feathered edge.
import cv2,numpy as np,sys
cur=cv2.imread('assets/n09-food.jpg');H,W=cur.shape[:2]
bg=cv2.imread('assets/src/food-pillars-bg.jpg')
s=max(W/bg.shape[1],H/bg.shape[0]);bg=cv2.resize(bg,(round(bg.shape[1]*s),round(bg.shape[0]*s)),interpolation=cv2.INTER_CUBIC)
bg=bg[(bg.shape[0]-H)//2:(bg.shape[0]-H)//2+H,(bg.shape[1]-W)//2:(bg.shape[1]-W)//2+W]
bg=cv2.GaussianBlur(bg,(0,0),3.2).astype(np.float32)
navy=np.array([48,20,8],np.float32);yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
shade=0.62+0.18*(yy/H);N=bg*(1-shade[...,None])+navy*shade[...,None];N=N*0.80+navy*0.20
al=np.clip(1-yy/330,0,1)**1.4*0.55;N=N*(1-al[...,None])+navy*al[...,None]
if len(sys.argv)>1:
    for b in ((0,40,1920,120),(0,940,1920,1060),(0,800,100,930),(1800,800,1920,930)):
        x0,y0,x1,y1=b;print(b,'mean abs diff',np.abs(cur[y0:y1,x0:x1].astype(float)-N[y0:y1,x0:x1]).mean(),'signed',(cur[y0:y1,x0:x1].astype(float)-N[y0:y1,x0:x1]).mean((0,1)))
    sys.exit()
m=np.zeros((H,W),np.float32);m[784:944,96:1824]=1      # label + pills (+ glow); cards end at y=732 now
m=cv2.GaussianBlur(m,(0,0),3)[...,None]
# match the original's fine grain/jpeg softness: tiny noise
rng=np.random.RandomState(3);Nn=N+rng.randn(H,W,1).astype(np.float32)*1.2
out=cur.astype(np.float32)*(1-m)+Nn*m
cv2.imwrite('assets/n09-food.jpg',np.clip(out,0,255).astype(np.uint8),[cv2.IMWRITE_JPEG_QUALITY,95])
