# slide 9 (n07-bridge): base = git file from c12bece^ (restored byte-identical), then ONLY
# (a) an elegant soft dark shade over the icing drips that run over the bright layers, matched to the tone of the already-shaded icing cap (not black)
# (b) a larger headline (same font/colours, resampled) with the sub line kept aligned under it.
import cv2,numpy as np
N=cv2.imread('assets/n07-bridge.jpg')
M=cv2.imread('/workspace/r5/icing_mask.png',0)>0     # icing mask (cap + drips), slide px, from the round-5 registration
cap=M.copy();cap[:230]=False;cap[330:]=False
capc=np.median(N[cap].reshape(-1,3),0);print('cap tone',capc)
# right-hand drips (warm shaded cream) missed by the round-5 mask
hsv=cv2.cvtColor(N,cv2.COLOR_BGR2HSV);Hh,Ss,Vv=[hsv[...,i].astype(int) for i in range(3)]
cand=((Ss<125)&(Vv>160)&(Hh<=24)&(Hh>=8)).astype(np.uint8);cand[:,:780]=0
fa=cand[400:490].mean(0);fb=cand[556:612].mean(0)
cols=np.where(fa>0.6)[0]
extra=np.zeros_like(M)
for c in cols:
    yb=612 if fb[c]>0.6 else 500
    extra[392:yb,c]=True
extra=cv2.dilate(extra.astype(np.uint8),np.ones((5,5),np.uint8))>0
print('extra drip cols',cols.min() if len(cols) else None,cols.max() if len(cols) else None)
M=M|extra
low=M.copy();low[:392]=False                         # drips below the shaded band
a=cv2.GaussianBlur(low.astype(np.float32),(0,0),1.6)[...,None]*0.86
out=N.astype(np.float32)*(1-a)+capc.astype(np.float32)*a
# soften the transition at the band edge
im=np.clip(out,0,255).astype(np.uint8)
# --- headline larger
def ink(sub,thr=40):
    bg=cv2.medianBlur(sub,61).astype(int);return (np.abs(sub.astype(int)-bg).max(2)>thr)
hb=(1020,205,1850,480);sb=(1020,530,1850,720)
src=im.copy()
def wipe(img,box,thr=40,dil=5):
    x0,y0,x1,y1=box;m=cv2.dilate(ink(img[y0:y1,x0:x1],thr).astype(np.uint8)*255,np.ones((2*dil+1,2*dil+1),np.uint8))
    full=np.zeros(img.shape[:2],np.uint8);full[y0:y1,x0:x1]=m;return cv2.inpaint(img,full,5,cv2.INPAINT_TELEA)
im=wipe(im,hb)   # sub-line is NOT touched (stays at its original position)
# crop the ink bbox of the headline
x0,y0,x1,y1=hb;sub=src[y0:y1,x0:x1];m=ink(sub).astype(np.uint8)
ys,xs=np.where(m>0);bx0,bx1,by0,by1=xs.min()-6,xs.max()+6,ys.min()-6,ys.max()+6;print('headline bbox',x0+bx0,x0+bx1,y0+by0,y0+by1)
al=cv2.GaussianBlur(cv2.dilate(m,np.ones((3,3),np.uint8)).astype(np.float32),(0,0),0.8)
S=1.15;pw,ph=bx1-bx0,by1-by0;nw,nh=round(pw*S),round(ph*S)
inkimg=(sub.astype(np.float32)*al[...,None])[by0:by1,bx0:bx1];a_=al[by0:by1,bx0:bx1]
inkimg=cv2.resize(inkimg,(nw,nh),interpolation=cv2.INTER_CUBIC);a_=np.clip(cv2.resize(a_,(nw,nh),interpolation=cv2.INTER_CUBIC),0,1)[...,None]
fg=np.where(a_>1e-3,inkimg/np.maximum(a_,1e-3),0)
NX=985;NY=y0+by0-8
reg=im[NY:NY+nh,NX:NX+nw].astype(np.float32);im[NY:NY+nh,NX:NX+nw]=np.clip(reg*(1-a_)+fg*a_,0,255).astype(np.uint8)
print('new headline',NX,NX+nw,NY,NY+nh)
x0,y0,x1,y1=sb;ss=src[y0:y1,x0:x1];sm=ink(ss,30).astype(np.uint8);ys,xs=np.where(sm>0);print('sub (unchanged) bbox x',x0+xs.min(),x0+xs.max(),'y',y0+ys.min(),y0+ys.max())
cv2.imwrite('assets/n07-bridge.jpg',im,[cv2.IMWRITE_JPEG_QUALITY,95])
cv2.imwrite('/workspace/r5/s9_v6a.png',im[100:900,100:1920])
