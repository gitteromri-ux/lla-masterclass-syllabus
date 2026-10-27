# slide 15 ROUND 8: leader lines re-pointed to the real anatomy.
#   Brain  -> top of the skull (hair crown) ; Heart and lungs -> left-centre chest ; Muscles and bones -> her right arm (forearm, image left)
# Old lines/dots/glow are inpainted away; new thin lines in the same style (2 px + soft glow + round dot). Labels/text untouched.
import cv2,numpy as np,sys
OUT=sys.argv[1] if len(sys.argv)>1 else 'assets/n12-sameage.jpg'
im=cv2.imread('/workspace/r5/n12_before8.jpg')
H,W=im.shape[:2]
def poly(m,pts,w):
    for a,b in zip(pts[:-1],pts[1:]):cv2.line(m,a,b,255,w,cv2.LINE_AA)
from skimage.restoration import inpaint_biharmonic
def geo(pts,w,dots,rad):
    b=np.zeros((H,W),np.uint8)
    for a,c in zip(pts[:-1],pts[1:]):cv2.line(b,a,c,255,w)
    for d in dots:cv2.circle(b,d,rad,255,-1)
    return b
white=(im.min(2)>205);wd=cv2.dilate(white.astype(np.uint8),np.ones((3,3),np.uint8))>0
med=cv2.medianBlur(im,41).astype(int)
dif=(np.abs(im.astype(int)-med).max(2)>10).astype(np.uint8)*255
G1=geo([(1480,176),(1497,398)],21,[(1480,176)],17);G1[392:406,1503:]=0   # keep the brain stub (y=399)
G2=geo([(1466,327),(1486,452)],21,[(1466,327)],17)
G3=geo([(1535,610),(1500,662)],21,[(1535,610)],16);G3[652:672,1498:1557]=255
G=G1|G2|G3;G[:,1557:]=0
m=cv2.bitwise_and(G,dif);m=cv2.dilate(m,np.ones((5,5),np.uint8));m[wd]=0
# wide soft glow left behind by the old diagonal muscles leader and its dot (dark shirt: smooth fill is exact enough)
W4=np.zeros((H,W),np.uint8);cv2.line(W4,(1552,548),(1492,664),255,34);cv2.circle(W4,(1535,607),28,255,-1)
W4[:546]=0;W4[:,1557:]=0;W4[wd]=0
m=m|W4
y0,y1,x0,x1=150,700,1380,1560
crop=im[y0:y1,x0:x1].astype(np.float32)/255;mk=m[y0:y1,x0:x1]>0
res=inpaint_biharmonic(crop,mk,channel_axis=-1)
rng=np.random.RandomState(7);res=res+rng.randn(*res.shape).astype(np.float32)*0.006
im[y0:y1,x0:x1]=np.where(mk[...,None],np.clip(res*255,0,255),im[y0:y1,x0:x1]).astype(np.uint8)
# neck / jaw / strap strip along the old brain & heart lines: clone from the clean mirror side about the face axis x=1446 (feathered), instead of a smooth fill
axis=1446
Mc=cv2.dilate(m,np.ones((13,13),np.uint8));Mc[:200]=0;Mc[452:]=0;Mc[:,:1458]=0;Mc[:,1520:]=0
al=cv2.GaussianBlur(Mc.astype(np.float32)/255,(0,0),3.0)[...,None]*0.9
xs_=np.arange(W);mx=np.clip(2*axis-xs_,0,W-1)
mir=im[:,mx]
# keep the filled tones (low frequencies), borrow only the fine texture (high frequencies) from the mirror side
low=cv2.GaussianBlur(im.astype(np.float32),(0,0),5);mf=mir.astype(np.float32);hp=mf-cv2.GaussianBlur(mf,(0,0),5)
al=cv2.GaussianBlur(Mc.astype(np.float32)/255,(0,0),3.0)[...,None]
im=np.clip(im.astype(np.float32)*(1-al)+(low+hp)*al,0,255).astype(np.uint8)
# right eye (was under the old dot): mirror the clean left eye+brow about the face axis x=1446, feathered
ex0,ex1,ey0,ey1=1394,1436,148,198
src_=im[ey0:ey1,ex0:ex1][:,::-1].copy()                      # mirrored left eye
dx0=2*1446-ex1+1;dst=im[ey0:ey1,dx0:dx0+(ex1-ex0)].astype(np.float32)
yy,xx=np.mgrid[0:ey1-ey0,0:ex1-ex0];ell=np.clip(1-(((xx-(ex1-ex0)/2)/(0.5*(ex1-ex0)))**2+((yy-(ey1-ey0)/2)/(0.5*(ey1-ey0)))**2),0,1)
al=(np.clip(ell*2.2,0,1)**1.2)[...,None]
# match brightness of the host skin
hostm=dst.mean((0,1));srcm=src_.astype(np.float32).mean((0,1))
sc=src_.astype(np.float32)*(hostm/srcm)
im[ey0:ey1,dx0:dx0+(ex1-ex0)]=np.clip(dst*(1-al)+sc*al,0,255).astype(np.uint8)
# ---- new leaders
def leader(img,pts,dot,col,glow=1.0):
    lay=np.zeros((H,W),np.float32);poly_l=np.zeros((H,W),np.uint8)
    for a,b in zip(pts[:-1],pts[1:]):cv2.line(poly_l,a,b,255,2,cv2.LINE_AA)
    cv2.circle(poly_l,dot,8,255,-1,cv2.LINE_AA)
    core=poly_l.astype(np.float32)/255
    g=cv2.GaussianBlur(core,(0,0),4)*0.9*glow
    a=np.clip(core+g*(1-core),0,1)[...,None]
    colv=np.array(col,np.float32)
    # glow lighter-tinted, core full colour
    c=np.where(core[...,None]>0.05,colv,colv)
    f=img.astype(np.float32);return np.clip(f*(1-a)+c*a,0,255).astype(np.uint8)
ORG=(94,163,240);BLU=(242,184,118);CYA=(255,224,137)
im=leader(im,[(1474,92),(1505,92),(1505,399),(1553,399)],(1474,92),ORG)
im=leader(im,[(1488,468),(1499,533),(1553,533)],(1488,468),BLU)
im=leader(im,[(1544,662),(1553,662)],(1544,662),CYA)  # Muscles and bones: short leader ending on her near (image-right) arm
cv2.imwrite(OUT,im,[cv2.IMWRITE_JPEG_QUALITY,95])
cv2.imwrite('/workspace/r5/s15_r8_full.png',im[40:1000,1180:1920])
