import cv2,numpy as np
b=cv2.imread('base1920.png').astype(np.float32)
rng=np.random.default_rng(3)
def poly(pts,ox,oy):
    m=np.zeros(b.shape[:2],np.uint8);cv2.fillPoly(m,[np.array([(x+ox,y+oy) for x,y in pts],np.int32)],255);return m
# crop-space polygons (crop origin 1000,330)
P1=[(75,150),(78,108),(128,100),(132,80),(168,74),(188,50),(200,36),(250,32),(270,60),(270,112),(252,142),(216,170),(150,172),(95,170)]
P2=[(52,262),(58,238),(114,230),(116,188),(208,188),(208,312),(120,314),(80,302)]
O=(1000,330)
def dil(m,k):return cv2.dilate(m,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(k,k)))
def shift(img,dx,dy):
    M=np.float32([[1,0,dx],[0,1,dy]]);return cv2.warpAffine(img,M,(img.shape[1],img.shape[0]),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
def run(moves,out):
    base=b.copy();masks=[]
    allm=np.zeros(b.shape[:2],np.uint8)
    for P,dx,dy in moves:
        m=poly(P,*O);masks.append((m,dx,dy));allm|=dil(m,22)
    bu=b.astype(np.uint8)
    fill=cv2.inpaint(bu,allm,9,cv2.INPAINT_TELEA).astype(np.float32)
    # grain matched to asphalt
    ref=b[560:700,1300:1450];hf=ref-cv2.GaussianBlur(ref,(0,0),5);sd=hf.std()
    nz=rng.normal(0,1,b.shape).astype(np.float32);nz=cv2.GaussianBlur(nz,(0,0),1.1);nz=nz/nz.std()*sd;nz=nz.mean(2,keepdims=True)*np.ones((1,1,3),np.float32)
    fill=fill+nz*1.0
    a=cv2.GaussianBlur(allm.astype(np.float32)/255,(0,0),6)[...,None]
    res=base*(1-a)+fill*a
    for m,dx,dy in masks:
        mm=cv2.GaussianBlur(dil(m,16).astype(np.float32)/255,(0,0),4)
        pm=shift(mm,dx,dy)[...,None];pi=shift(b,dx,dy)
        res=res*(1-pm)+pi*pm
    cv2.imwrite(out,np.clip(res,0,255).astype(np.uint8))
run([(P1,18,-26),(P2,0,-22)],'base_moved.png')
cv2.imwrite('bm_crop.png',cv2.imread('base_moved.png')[230:960,1000:1450])
