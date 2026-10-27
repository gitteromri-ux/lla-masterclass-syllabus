# slide 15 round 12: write the age gap ONCE, large, orange Playfair italic; paragraph / power line / source re-spaced under it
import sys,os,cv2,numpy as np
H=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,H+'/assets/src')
from editlib import *
ARIAL='/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
ARIALB='/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
PFI='/usr/share/fonts/truetype/sand-box/google/Playfair Display/PlayfairDisplay-Italic-VariableFont_wght.ttf'
im=cv2.imread('/workspace/n12_before_r12.jpg')
box=(806,690,1208,1074)
x0,y0,x1,y1=box;f32=im.astype(np.float32)
Lc=np.median(f32[y0:y1,x0+12:x0+28],1);Rc=np.median(f32[y0:y1,x1-28:x1-12],1)
Lc=cv2.GaussianBlur(Lc[:,None,:],(0,0),sigmaX=0.1,sigmaY=10)[:,0];Rc=cv2.GaussianBlur(Rc[:,None,:],(0,0),sigmaX=0.1,sigmaY=10)[:,0]
t=np.linspace(0,1,x1-x0)[None,:,None];bg=Lc[:,None,:]*(1-t)+Rc[:,None,:]*t
bg=bg+np.random.RandomState(3).randn(y1-y0,x1-x0,1).astype(np.float32)*0+cv2.GaussianBlur(np.random.RandomState(4).randn(y1-y0,x1-x0).astype(np.float32),(0,0),0.8)[...,None]*1.4
a=np.ones((y1-y0,x1-x0),np.float32);a[:,:12]=np.linspace(0,1,12)[None];a[:,-12:]=np.linspace(1,0,12)[None];a[:10]*=np.linspace(0,1,10)[:,None];a[-10:]*=np.linspace(1,0,10)[:,None]
f32[y0:y1,x0:x1]=f32[y0:y1,x0:x1]*(1-a[...,None])+bg*a[...,None];im=np.clip(f32,0,255).astype(np.uint8)
cx=1007;orange=(232,178,104);gold=(240,190,112)
S=int(sys.argv[1]) if len(sys.argv)>1 else 52
f=font(PFI,S,400)
im=text(im,(cx,806),"12.4-year age gap",f,orange,anchor='ms')
pf=font(ARIAL,25)
for i,l in enumerate(wrap("The gap between how long Americans live and how long they live in good health.",pf,350)):
    im=text(im,(cx,862+i*32),l,pf,(232,236,243),anchor='ms')
im=text(im,(cx,974),"The widest in the world.",font(ARIALB,29),gold,anchor='ms')
sf=font(ARIAL,21)
for i,l in enumerate(wrap("Worldwide, 9.6. Mayo Clinic, 183 countries, December 2024.",sf,350)):
    im=text(im,(cx,1016+i*27),l,sf,(190,200,215),anchor='ms')
cv2.imwrite('assets/n12-sameage.jpg',im,[cv2.IMWRITE_JPEG_QUALITY,95])
cv2.imwrite('/workspace/s15_r12_blk_c.png',im[660:1080,760:1260])
cv2.imwrite('/workspace/s15_r12_full_c.png',im)
print(f.getlength("12.4-year age gap"))
