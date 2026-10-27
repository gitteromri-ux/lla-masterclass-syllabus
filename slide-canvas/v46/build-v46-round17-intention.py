# V46 round 17 (Julie): slide 25 (n20-why.jpg): move the word 'Intention' to the left inside its circle (same size and style, nothing else).
import cv2,numpy as np
OUT='assets/n20-why.jpg';DX=-60
im=cv2.imread(OUT);H,W=im.shape[:2];f=im.astype(np.float32)
x0,y0,x1,y1=240,390,570,485
R=f[...,2]
bgR=cv2.medianBlur(im[...,2],61).astype(np.float32)   # local background red (text is light blue: red channel pops)
box=np.zeros((H,W),bool);box[y0:y1,x0:x1]=True
a=np.clip((R-bgR-12)/(125),0,1)*box            # text coverage
m=cv2.dilate((a>0.02).astype(np.uint8),np.ones((7,7),np.uint8))
# background underneath: smooth gradient -> inpaint at low res
s=2;sm=cv2.resize(im,(W//s,H//s),interpolation=cv2.INTER_AREA);mm=cv2.resize(m*255,(W//s,H//s),interpolation=cv2.INTER_NEAREST)
bg=cv2.inpaint(sm,mm,6,cv2.INPAINT_TELEA);bg=cv2.GaussianBlur(bg,(0,0),1.5);bg=cv2.resize(bg,(W,H),interpolation=cv2.INTER_CUBIC).astype(np.float32)
rng=np.random.RandomState(11);bg+=rng.randn(H,W,1).astype(np.float32)*1.2
ms=cv2.GaussianBlur(m.astype(np.float32),(0,0),1.5)[...,None]
base=f*(1-ms)+bg*ms
# the word: colour from the original text pixels, coverage a, shifted by DX
col=f.copy()
a2=np.roll(a,DX,axis=1)[...,None];c2=np.roll(col,DX,axis=1)
# recover the text colour from the blend: (pix - bg*(1-a))/a  (where a is large enough)
ao=a[...,None];txt=np.where(ao>0.25,(f-bg*(1-ao))/np.maximum(ao,0.25),f);txt=np.clip(txt,0,255)
txt2=np.roll(txt,DX,axis=1)
out=base*(1-a2)+txt2*a2
cv2.imwrite(OUT,np.clip(out,0,255).astype(np.uint8),[cv2.IMWRITE_JPEG_QUALITY,95])
