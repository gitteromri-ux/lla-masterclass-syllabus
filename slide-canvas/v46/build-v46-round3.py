# V46 round 3: slide 9 (Food) - four distinctly tinted glass cards over a food photo; text/layout/logo/chips unchanged.
# Runs once on the current n09 asset (backup /workspace/e46/n09_before.jpg). Text pixels are lifted from the old render.
import cv2,numpy as np,sys
from PIL import Image,ImageDraw,ImageFont
OUTFIT='/usr/share/fonts/truetype/sand-box/google/Outfit/Outfit-VariableFont_wght.ttf'
O=cv2.imread('/workspace/e46/n09_before.jpg');H,W=O.shape[:2]
bg=cv2.imread('assets/src/food-pillars-bg.jpg')
# cover-fit, soft focus, darken into the deck's navy
s=max(W/bg.shape[1],H/bg.shape[0]);bg=cv2.resize(bg,(round(bg.shape[1]*s),round(bg.shape[0]*s)),interpolation=cv2.INTER_CUBIC)
bg=bg[(bg.shape[0]-H)//2:(bg.shape[0]-H)//2+H,(bg.shape[1]-W)//2:(bg.shape[1]-W)//2+W]
bg=cv2.GaussianBlur(bg,(0,0),3.2).astype(np.float32)
navy=np.array([48,20,8],np.float32)   # BGR deep navy
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
shade=0.62+0.18*(yy/H)           # darker toward the bottom
N=bg*(1-shade[...,None])+navy*shade[...,None]
N=N*0.80+navy*0.20
# header scrim keeps the title/kicker/logo calm
al=np.clip(1-yy/330,0,1)**1.4*0.55;N=N*(1-al[...,None])+navy*al[...,None]
def rrmask(x0,y0,x1,y1,r,S=4):
    w,h=x1-x0,y1-y0;m=Image.new('L',(w*S,h*S),0);ImageDraw.Draw(m).rounded_rectangle((0,0,w*S-1,h*S-1),radius=r*S,fill=255)
    return np.array(m.resize((w,h),Image.LANCZOS)).astype(np.float32)/255
def ring(x0,y0,x1,y1,r,t=1.6):
    a=rrmask(x0,y0,x1,y1,r);k=int(round(t));Sm=cv2.erode(a,np.ones((2*k+1,2*k+1),np.uint8))
    return np.clip(a-Sm,0,1)
def glass(N,box,r,tint,tint_a,edge_a,blur=16):
    x0,y0,x1,y1=box;sub=N[y0:y1,x0:x1];bl=cv2.GaussianBlur(sub,(0,0),blur)
    m=rrmask(x0,y0,x1,y1,r)[...,None]
    t=np.array(tint[::-1],np.float32)
    fill=bl*(1-tint_a)+t*tint_a*0.55+bl*0.0
    # gentle vertical sheen
    g=np.linspace(1.12,0.9,y1-y0)[:,None,None];fill=fill*g
    out=sub*(1-m)+fill*m
    e=ring(x0,y0,x1,y1,r)[...,None]*edge_a;out=out*(1-e)+(t*0.55+np.array([255,255,255],np.float32)*0.45)*e
    N[y0:y1,x0:x1]=out;return N
TINTS=[(36,196,180),(58,128,250),(128,98,236),(190,104,226)]   # teal, blue, violet, purple (RGB)
CARDX=[120,547,974,1401];CY0,CY1,CW=380,784,398
for x0,t in zip(CARDX,TINTS):N=glass(N,(x0,CY0,x0+CW,CY1),28,t,0.34,0.32)
CH=[(120,453),(472,753),(772,1062),(1081,1479),(1498,1787)]
for a,b in CH:N=glass(N,(a,846,b,917),36,(150,170,210),0.12,0.16,blur=10)
# bars + numbers in each card's own colour
def lerp(c1,c2,u):return tuple(c1[i]*(1-u)+c2[i]*u for i in range(3))
lay=Image.new('RGBA',(W*2,H*2),(0,0,0,0));d=ImageDraw.Draw(lay)
fnt=ImageFont.truetype(OUTFIT,62);fnt.set_variation_by_axes([600])
for k,(x0,t) in enumerate(zip(CARDX,TINTS)):
    lt=tuple(min(255,v+70) for v in t)
    bx0,bx1=x0+41,x0+358
    for i in range(bx1-bx0):
        u=i/(bx1-bx0);c=lerp(t,lt,u);d.rectangle(((bx0+i)*2,421*2,(bx0+i+1)*2,431*2),fill=tuple(int(v) for v in c)+(255,))
    # round the bar ends
    d.ellipse((bx0*2-10,421*2,bx0*2+10,431*2),fill=tuple(int(v) for v in t)+(255,));d.ellipse((bx1*2-10,421*2,bx1*2+10,431*2),fill=tuple(int(v) for v in lt)+(255,))
    x=(x0+41)*2
    for ch in '0%d'%(k+1):
        d.text((x,480*2),ch,font=fnt,fill=tuple(min(255,v+95) for v in t)+(255,),anchor='ls');x+=fnt.getlength(ch)+11
L=np.array(lay.resize((W,H),Image.LANCZOS)).astype(np.float32);a=L[...,3:]/255
N=N*(1-a)+L[...,:3][...,::-1]*a
# lift text from the old render
def lift(N,box,pad=0):
    x0,y0,x1,y1=box;sub=O[y0:y1,x0:x1];b=cv2.medianBlur(sub,61).astype(np.float32)
    dd=np.abs(sub.astype(np.float32)-b).max(2);ref=max(30,np.percentile(dd,99.7))
    al=np.clip((dd-5)/(ref*0.8-5),0,1);al=cv2.GaussianBlur(al,(0,0),0.5)[...,None]
    fg=np.clip((sub.astype(np.float32)-b*(1-al))/np.maximum(al,0.05),0,255);fg=np.where(al>0.05,fg,0)
    N[y0:y1,x0:x1]=N[y0:y1,x0:x1]*(1-al)+fg*al;return N
N=lift(N,(100,60,700,250))
for x0 in CARDX:N=lift(N,(x0+20,495,x0+380,775))
for a_,b_ in CH:N=lift(N,(a_+16,852,b_-16,912))
N=lift(N,(110,795,520,832));N=lift(N,(1720,985,1850,1030))
N=np.clip(N,0,255).astype(np.uint8)
cv2.imwrite('assets/n09-food.jpg',N,[cv2.IMWRITE_JPEG_QUALITY,95])
