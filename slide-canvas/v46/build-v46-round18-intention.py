# V46 round 18 (Omri): slide 25 (n20-why.jpg), from the previous live image (assets/src/n20-why-before-r17.jpg is the older one; base here = HEAD n20, md5 fe5e9345...):
# 'Intention' moved further left inside its circle, 'Why' moved right by the mirrored amount about the diagram axis (equal gap to each circle's outer edge). Same size/style, nothing else.
import cv2,numpy as np,subprocess,sys
OUT='assets/n20-why.jpg'
if len(sys.argv)>1: base=cv2.imread(sys.argv[1])
else: base=cv2.imdecode(np.frombuffer(subprocess.check_output(['git','show','HEAD:slide-canvas/v46/'+OUT]),np.uint8),1)
im=base;H,W=im.shape[:2];f=im.astype(np.float32)
bgR=cv2.medianBlur(im[...,2],61).astype(np.float32)
RAW=f[...,2]-bgR
def word(box,DX):
    x0,y0,x1,y1=box
    bx=np.zeros((H,W),bool);bx[y0:y1,x0:x1]=True
    a=np.clip((RAW-12)/125,0,1)*bx
    return a
def run():
    aI=word((170,395,540,485),0);aW=word((880,395,1062,485),0)
    for n,a in(('I',aI),('W',aW)):
        xs=np.where(a.max(0)>0.5)[0];print(n,'bbox x',xs.min(),xs.max())
    return aI,aW
aI,aW=run()
xi=np.where(aI.max(0)>0.5)[0];xw=np.where(aW.max(0)>0.5)[0]
L,R=131,1088                      # outer edges of the two circles at the text row
gap=28
DXI=(L+gap)-xi.min();DXW=(R-gap)-xw.max()
print('DX Intention',DXI,'DX Why',DXW)
a=np.maximum(aI,aW)
m=cv2.dilate((a>0.02).astype(np.uint8),np.ones((7,7),np.uint8))
s=2;sm=cv2.resize(im,(W//s,H//s),interpolation=cv2.INTER_AREA);mm=cv2.resize(m*255,(W//s,H//s),interpolation=cv2.INTER_NEAREST)
bg=cv2.inpaint(sm,mm,6,cv2.INPAINT_TELEA);bg=cv2.GaussianBlur(bg,(0,0),1.5);bg=cv2.resize(bg,(W,H),interpolation=cv2.INTER_CUBIC).astype(np.float32)
rng=np.random.RandomState(11);bg+=rng.randn(H,W,1).astype(np.float32)*1.2
ms=cv2.GaussianBlur(m.astype(np.float32),(0,0),1.5)[...,None]
out=f*(1-ms)+bg*ms
for aw,dx in((aI,DXI),(aW,DXW)):
    ao=aw[...,None];txt=np.clip(np.where(ao>0.25,(f-bg*(1-ao))/np.maximum(ao,0.25),f),0,255)
    a2=np.roll(aw,dx,axis=1)[...,None];t2=np.roll(txt,dx,axis=1)
    out=out*(1-a2)+t2*a2
cv2.imwrite(OUT,np.clip(out,0,255).astype(np.uint8),[cv2.IMWRITE_JPEG_QUALITY,95])
