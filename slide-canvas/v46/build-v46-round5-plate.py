# slide 12 (n10-plate): new plate photo = greens + vegetables, wild blueberries, salmon (matches 'On my plate' + script). Layout/text/labels kept.
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
D='/workspace/lla-masterclass-syllabus/slide-canvas/v46/'
old=Image.open('/workspace/r5/n10_before.jpg').convert('RGB')
new=Image.open(D+'assets/src/plate-greens-berries-salmon.jpg').convert('RGB').transpose(Image.FLIP_LEFT_RIGHT)
sc=1.875*0.774
nw,nh=int(new.width*sc*1920/1920*1.0),int(new.height*sc)
new=new.resize((int(1920*0.774),int(1080*0.774)),Image.LANCZOS)
ox,oy=738,131
canvas=old.copy().convert('RGB');na=np.array(new);pt=oy;pb=1080-(oy+na.shape[0])
h0=na.shape[0];w0=na.shape[1]
rngq=np.random.default_rng(11)
def quilt(hh):
    """plate-free slate texture, hh rows x w0 cols: random patches from the left/right strips, cross-faded"""
    src=[na[250:250+max(hh,160),0:330],na[250:250+max(hh,160),1160:1486]]
    out=np.zeros((hh,w0,3),np.float32);x=0;k=0;F=40
    while x<w0:
        p=src[k%2][:hh].astype(np.float32);p=p[:, ::-1] if (k//2)%2 else p
        pw=p.shape[1];x1=min(w0,x+pw)
        a=np.ones(x1-x);
        if x>0:a[:F]=np.linspace(0,1,F)
        out[:,x:x1]=out[:,x:x1]*(1-a[None,:,None])+p[:,:x1-x]*a[None,:,None]
        if x1>=w0:break
        x=x1-F;k+=1
    return out
top=quilt(pt+40);bot=quilt(max(pb,0)+40)
full=np.zeros((1080,w0,3),np.float32);full[pt:pt+h0]=na
def fe(n):return np.linspace(0,1,n)[:,None,None]
tp=top.copy();tp[pt:pt+40]=tp[pt:pt+40]*(1-fe(40))+na[:40].astype(np.float32)*fe(40);full[:pt+40]=tp
bt=bot.copy();bt[:40]=na[h0-40:].astype(np.float32)*(1-fe(40))+bt[:40]*fe(40)
full[pt+h0-40:]=bt[:1080-(pt+h0-40)]
full=np.clip(full,0,255).astype(np.uint8)
na=full
layer=Image.new('RGB',old.size);layer.paste(Image.fromarray(na),(ox,0))
A=np.zeros((1080,1920),np.float32)
xs=np.arange(1920)[None,:];ys=np.arange(1080)[:,None]
ax=np.clip((xs-800)/200,0,1);ay=1.0
A=ax*ay;A[:, :ox]=0
# keep the old logo block

o=np.array(canvas).astype(np.float32);n=np.array(layer).astype(np.float32)
res=(o*(1-A[...,None])+n*A[...,None]).astype(np.uint8)
im=Image.fromarray(res);dr=ImageDraw.Draw(im,'RGBA')
PF=ImageFont.truetype('/usr/share/fonts/truetype/sand-box/google/Playfair Display/PlayfairDisplay-Italic-VariableFont_wght.ttf',58)
try:PF.set_variation_by_axes([500])
except Exception:pass
IN=ImageFont.truetype('/home/box/.local/share/fonts/google/Inter%5Bopsz,wght%5D.ttf',29)
def label(x,y,title,sub,col):
    dr.text((x,y),title,font=PF,fill=col)
    dr.text((x+2,y+80),sub,font=IN,fill=(236,242,250))
def leader(p0,p1,col):
    dr.line([p0,p1],fill=col+(235,),width=3);dr.ellipse((p1[0]-6,p1[1]-6,p1[0]+6,p1[1]+6),fill=col+(255,))
BL=(110,176,232);AM=(244,180,96);GR=(84,212,152)
label(1143,98,'Whole food','the default',BL)
label(1062,892,'Protein','the floor',AM)
label(1610,882,'Fiber','the lever',GR)
import json;P=json.load(open('/workspace/r5/plate_pts.json'))
leader(tuple(P['whole'][0]),tuple(P['whole'][1]),BL)
leader(tuple(P['prot'][0]),tuple(P['prot'][1]),AM)
leader(tuple(P['fiber'][0]),tuple(P['fiber'][1]),GR)
import cv2 as _c
arr=np.array(im);L=_c.imread(D+'../closers/img/lla-logo.png',_c.IMREAD_UNCHANGED);LW,LX,LY=340,1526,28
hh_=round(LW*L.shape[0]/L.shape[1]);lg_=_c.resize(L,(LW,hh_),interpolation=_c.INTER_AREA);al_=lg_[:,:,3:].astype(np.float32)/255
rgb=lg_[:,:,2::-1]
yy_,xx_=np.mgrid[0:1080,0:1920].astype(np.float32);K=LW/200;cx,cy=LX+LW/2,LY+45*K
d_=((xx_-cx)/(170*K))**2+((yy_-cy)/(95*K))**2;sc=(0.6*np.exp(-d_*1.6))[...,None]
arr=np.clip(arr*(1-sc)+np.array([8,18,40],np.float32)*sc,0,255).astype(np.uint8)
arr[LY:LY+hh_,LX:LX+LW]=(rgb*al_+arr[LY:LY+hh_,LX:LX+LW]*(1-al_)).astype(np.uint8)
Image.fromarray(arr).save(D+'assets/n10-plate.jpg',quality=95)
