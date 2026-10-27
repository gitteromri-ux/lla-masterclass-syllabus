# V46 round 3b: slide 20 (Why. Intention. Resources.) right column rebuilt as one clean aligned column.
# Input: the previous n20 asset (backup /workspace/e46/n20_before.jpg). Circles/title/logo untouched.
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
exec(open('build-v46-round2.py').read().split('# ================= slide 16')[0].split("A='assets/'")[1].join(["A='assets/'",""]) if False else "")
OUTFIT='/usr/share/fonts/truetype/sand-box/google/Outfit/Outfit-VariableFont_wght.ttf'
PFI='../../backup-deck/fonts/PlayfairDisplay-Italic.ttf'
def F(path,size,axes=None):
    f=ImageFont.truetype(path,size)
    if axes:f.set_variation_by_axes(axes)
    return f
def wipe(im,box,thr=5,dil=4):
    x0,y0,x1,y1=box;sub=im[y0:y1,x0:x1];bg=cv2.medianBlur(sub,61).astype(int)
    m=((np.abs(sub.astype(int)-bg).max(2))>thr).astype(np.uint8)*255;m=cv2.dilate(m,np.ones((2*dil+1,2*dil+1),np.uint8))
    full=np.zeros(im.shape[:2],np.uint8);full[y0:y1,x0:x1]=m
    return cv2.inpaint(im,full,5,cv2.INPAINT_TELEA)
im=cv2.imread('/workspace/e46/n20_before.jpg');H,W=im.shape[:2]
im=wipe(im,(1135,225,1880,1080))
X=1160;MAXW=706
HF=F(PFI,52,[400]);BF=F(OUTFIT,30,[300]);CF=F(OUTFIT,28,[360])
def wrap(t,f,w):
    return t.split('|')
blocks=[('Intention',(150,196,255),'The sentence on the wall. I want my healthspan|to match my lifespan.'),
        ('Why',(130,236,206),'The engine when the novelty fades. Being here|to show my son another possibility for how we age.'),
        ('Resources',(255,214,140),'Time, money, and relationships, the real amounts.|An hour in the morning. About twelve dollars a day.')]
y=285;items=[]
for h,c,b in blocks:
    items.append((X,y,h,HF,c,'ls'));by=y
    for ln in wrap(b,BF,MAXW):
        by+=50 if ln==wrap(b,BF,MAXW)[0] else 46
        items.append((X,by,ln,BF,(206,215,230),'ls'))
    y=by+96
y=y-96+104
for ln in wrap('When all three align you stop asking “What should I do?”|and start asking “Does this fit?”',CF,MAXW):
    items.append((X,y,ln,CF,(236,241,250),'ls'));y+=42
y-=42
print('last baseline',y)
lay=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(lay)
for x,yy,s,f,c,a in items:d.text((x,yy),s,font=f,fill=tuple(c)+(255,),anchor=a,features=['-liga','-calt'])
L=np.array(lay).astype(np.float32);al=cv2.GaussianBlur(L[...,3:]/255,(0,0),0.4).reshape(H,W,1)
im=np.clip(im.astype(np.float32)*(1-al)+L[...,:3][...,::-1]*al,0,255).astype(np.uint8)
CT=F(OUTFIT,29,[300]);lay=Image.new('RGBA',(W,H),(0,0,0,0));ImageDraw.Draw(lay).text((1830,1017),'20 / 21',font=CT,fill=(172,182,204,255),anchor='rs')
L=np.array(lay).astype(np.float32);al=cv2.GaussianBlur(L[...,3:]/255,(0,0),0.4).reshape(H,W,1)
im=np.clip(im.astype(np.float32)*(1-al)+L[...,:3][...,::-1]*al,0,255).astype(np.uint8)
cv2.imwrite('assets/n20-why.jpg',im,[cv2.IMWRITE_JPEG_QUALITY,95])
