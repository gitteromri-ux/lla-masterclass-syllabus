# slide 15 (n12-sameage): (1) clean 'Muscles and bones' leader (no crossing/smear), (2) 12.4 block: header, larger power sentence + paragraph
import sys,os,cv2,numpy as np
H=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,H+'/assets/src')
from editlib import *
ARIALB='/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
im=cv2.imread('/workspace/r5/n12_before6.jpg')
# --- (1) Muscles leader: erase the long cyan diagonal + its dot (keep the white label glyphs), redraw a short clean leader
x0,y0=1600,440;x1,y1=1500,661
m=np.zeros(im.shape[:2],np.uint8);cv2.line(m,(x0,y0),(x1,y1),255,15);cv2.circle(m,(x0,y0),15,255,-1)
hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV);white=(hsv[...,1]<70)&(hsv[...,2]>185)         # keep white text pixels
m[cv2.dilate(white.astype(np.uint8),np.ones((3,3),np.uint8))>0]=0
m[:,1550:][:, :]=m[:,1550:]     # (no-op)
# do not touch the Heart-and-lungs connector stub / glyphs: only the diagonal region is masked; protect the blue horizontal stub y=533 x1500-1560
m[530:537,1498:1556]=0   # only the 3-px blue stub itself
im=cv2.inpaint(im,m,6,cv2.INPAINT_TELEA)
for b in [(1768,556,1850,586),(1760,675,1860,715),(1546,538,1559,552),(1552,506,1574,519)]:im=erase_color(im,b,d=5,r=5,grow=9)
# glow blob left of 'H'
g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY);bm=np.zeros(g.shape,np.uint8)
for (a,b,c,d) in [(1550,510,1561,548),(1550,508,1576,519)]:
    bm[b:d,a:c]=(g[b:d,a:c]>70)*255
bm=cv2.dilate(bm,np.ones((5,5),np.uint8));bm[:, 1561:][519:,:]=0
im=cv2.inpaint(im,bm,5,cv2.INPAINT_TELEA)
seg=im[506:552,1551:1561].copy();ref=im[506:552,1546:1548].mean(axis=1,keepdims=True)
blend=np.linspace(1,0.35,10)[None,:,None];im[506:552,1551:1561]=(ref*blend+seg*(1-blend)).astype(np.uint8)
# re-draw the Brain sub-line (the dot sat on its 'i')
im=erase(im,(1555,420,1905,460),d=22,r=4);im=erase(im,(1555,420,1905,460),d=10,r=4)
fl=font(ARIAL,24);im=text(im,(1560,428),"Weights, mobility and balance",fl,(233,166,90),anchor='la')
# new short leader: dot on the arm, short diagonal, then the existing horizontal stub at y=662
lay=np.zeros(im.shape[:2]+(4,),np.float32)
col=(255,224,137)   # BGR of cyan 137,224,255
dot=(1535,610);knee=(1500,662)
cv2.line(lay,dot,knee,col+(255,),2,cv2.LINE_AA);cv2.circle(lay,dot,8,col+(255,),-1,cv2.LINE_AA)
glow=cv2.GaussianBlur(lay,(0,0),4);a=np.clip(lay[...,3:]/255+glow[...,3:]/255*0.8,0,1)
rgb=np.where(lay[...,3:]>1,lay[...,:3],glow[...,:3]/np.maximum(glow[...,3:]/255,1e-3)*0+np.array(col,np.float32))
im=np.clip(im.astype(np.float32)*(1-a)+rgb*a,0,255).astype(np.uint8)
# --- (2) 12.4 block
im=move(im,(895,728,1125,832),0,-26,d=20)
im=erase(im,(822,832,1198,990),d=30,r=5);im=erase(im,(822,832,1198,990),d=12,r=5)
cx=1007
gold=(240,190,112);white=(244,246,250)
im=text(im,(cx,866),"12.4-year age gap",font(ARIALB,34),white,anchor='ms')
pf=font(ARIAL,25)
for i,l in enumerate(wrap("The gap between how long Americans live and how long they live in good health.",pf,350)):
    im=text(im,(cx,904+i*32),l,pf,(232,236,243),anchor='ms')
im=text(im,(cx,1006),"The widest in the world.",font(ARIALB,29),gold,anchor='ms')
sf=font(ARIAL,21)
for i,l in enumerate(wrap("Worldwide, 9.6. Mayo Clinic, 183 countries, December 2024.",sf,350)):
    im=text(im,(cx,1038+i*27),l,sf,(190,200,215),anchor='ms')
cv2.imwrite('assets/n12-sameage.jpg',im,[cv2.IMWRITE_JPEG_QUALITY,95])
cv2.imwrite('/workspace/r5/n12_v6a.png',im[250:1080,700:1920])
