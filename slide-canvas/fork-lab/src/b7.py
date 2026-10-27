import cv2,numpy as np
from PIL import Image,ImageDraw
R=cv2.imread('new6.png').astype(np.float32)
H,W=R.shape[:2]
# ---- measure headlines on rendered pixels
rows=[]
for y0,y1,x0 in [(270,350,1290),(390,470,1290),(505,590,1250),(625,705,1240)]:
    s=R[y0:y1,x0:1900];mk=((s.max(2)-s.min(2))>60)&(s.max(2)>140)
    cnt=mk.sum(1);good=np.where(cnt>0.45*cnt.max())[0]
    cy=y0+(good.min()+good.max())/2;xl=x0+np.where(mk.any(0))[0].min()
    col=np.median(s[mk],0);rows.append((cy,xl,col));print('row',cy,xl,col)
# ---- icons (flat line, neon glow)
S=4;SZ=64;LW=4
def canvas():return Image.new('L',(SZ*S,SZ*S),0)
def clock():
    im=canvas();d=ImageDraw.Draw(im);c=SZ*S/2;r=SZ*S/2-LW*S
    d.ellipse((c-r,c-r,c+r,c+r),outline=255,width=LW*S)
    d.line((c,c,c,c-r*0.62),fill=255,width=LW*S);d.line((c,c,c+r*0.45,c+r*0.2),fill=255,width=LW*S)
    d.ellipse((c-5*S/2,c-5*S/2,c+5*S/2,c+5*S/2),fill=255);return im
def dumbbell():
    im=canvas();d=ImageDraw.Draw(im);k=S;c=SZ*S/2
    d.line((14*k,c,50*k,c),fill=255,width=LW*k)
    for x in (10,46):d.rounded_rectangle((x*k,c-14*k,(x+8)*k,c+14*k),radius=3*k,outline=255,width=LW*k)
    for x in (2,56):d.rounded_rectangle((x*k,c-8*k,(x+6)*k,c+8*k),radius=2*k,outline=255,width=LW*k)
    return im
def broccoli():
    im=canvas();d=ImageDraw.Draw(im);k=S
    for cx,cy,r in [(20,24,11),(44,24,11),(32,15,12)]:d.ellipse(((cx-r)*k,(cy-r)*k,(cx+r)*k,(cy+r)*k),outline=255,width=LW*k)
    d.line((32*k,32*k,32*k,58*k),fill=255,width=LW*k);d.line((32*k,44*k,23*k,36*k),fill=255,width=LW*k);d.line((32*k,44*k,41*k,36*k),fill=255,width=LW*k)
    return im
def cgmphone():
    im=Image.new('L',(SZ*S*2,SZ*S),0);d=ImageDraw.Draw(im);k=S
    d.ellipse((4*k,8*k,52*k,56*k),outline=255,width=LW*k);d.ellipse((22*k,26*k,34*k,38*k),outline=255,width=LW*k)
    d.rounded_rectangle((70*k,10*k,100*k,54*k),radius=5*k,outline=255,width=LW*k)
    d.line([(75*k,40*k),(81*k,32*k),(86*k,37*k),(95*k,24*k)],fill=255,width=3*k,joint='curve')
    return im
GAP=30
for (cy,xl,col),fn in zip(rows,[clock,dumbbell,broccoli,cgmphone]):
    im=fn();im=im.resize((im.width//S,im.height//S),Image.LANCZOS)
    a=np.array(im).astype(np.float32)/255
    ys,xs=np.where(a>0.2);h,w=a.shape
    x=int(round(xl-GAP-xs.max()-1));y=int(round(cy-(ys.min()+ys.max())/2))
    pad=20;A=np.pad(a,pad);x-=pad;y-=pad;h,w=A.shape
    glow=cv2.GaussianBlur(A,(0,0),6)*0.55
    reg=R[y:y+h,x:x+w]
    reg=reg+glow[...,None]*col[None,None]*0.8
    reg=reg*(1-A[...,None])+col*A[...,None]
    R[y:y+h,x:x+w]=reg
    yy,xx=np.where(A>0.5);print('icon cy',y+(yy.min()+yy.max())/2,'right',x+xx.max(),'text',cy,xl)
cv2.imwrite('new.png',np.clip(np.round(R),0,255).astype(np.uint8))
