# slide 11 (n09-food): the four cards move UP 52 px (more air above 'ON MY PLATE'); everything else untouched.
import cv2,numpy as np
from PIL import Image,ImageDraw
cur=cv2.imread('assets/n09-food.jpg');H,W=cur.shape[:2]
bg=cv2.imread('assets/src/food-pillars-bg.jpg')
s=max(W/bg.shape[1],H/bg.shape[0]);bg=cv2.resize(bg,(round(bg.shape[1]*s),round(bg.shape[0]*s)),interpolation=cv2.INTER_CUBIC)
bg=bg[(bg.shape[0]-H)//2:(bg.shape[0]-H)//2+H,(bg.shape[1]-W)//2:(bg.shape[1]-W)//2+W]
bg=cv2.GaussianBlur(bg,(0,0),3.2).astype(np.float32)
navy=np.array([48,20,8],np.float32);yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
shade=0.62+0.18*(yy/H);N=bg*(1-shade[...,None])+navy*shade[...,None];N=N*0.80+navy*0.20
al=np.clip(1-yy/330,0,1)**1.4*0.55;N=N*(1-al[...,None])+navy*al[...,None]
# sanity: background between cards should equal N
gap=(slice(450,700),slice(520,545));print('bg diff in card gap',np.abs(cur[gap].astype(float)-N[gap]).mean())
def rr(w,h,r,S=4):
    m=Image.new('L',(w*S,h*S),0);ImageDraw.Draw(m).rounded_rectangle((0,0,w*S-1,h*S-1),radius=r*S,fill=255);return np.array(m.resize((w,h),Image.LANCZOS)).astype(np.float32)/255
DY=52;P=6
out=cur.astype(np.float32).copy()
cards=[(120,380,518,784),(547,380,945,784),(974,380,1372,784),(1401,380,1799,784)]
for x0,y0,x1,y1 in cards:   # erase: back to the pure background
    out[y0-P:y1+P,x0-P:x1+P]=N[y0-P:y1+P,x0-P:x1+P]
for x0,y0,x1,y1 in cards:   # paste shifted
    m=rr(x1-x0+2*P,y1-y0+2*P,28+P)[...,None]
    sub=cur[y0-P:y1+P,x0-P:x1+P].astype(np.float32)
    reg=out[y0-P-DY:y1+P-DY,x0-P:x1+P];out[y0-P-DY:y1+P-DY,x0-P:x1+P]=sub*m+reg*(1-m)
cv2.imwrite('assets/n09-food.jpg',np.clip(out,0,255).astype(np.uint8),[cv2.IMWRITE_JPEG_QUALITY,95])
cv2.imwrite('/workspace/r5/n09_v6a.png',np.clip(out,0,255).astype(np.uint8))
