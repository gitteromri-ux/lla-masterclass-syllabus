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
strip=na[250:250+240,0:300].copy()                       # plate-free slate
def slate(hh):
    t=np.concatenate([strip,strip[:,::-1]],1);t=np.concatenate([t]*(w0//600+2),1)[:,:w0]
    t=np.concatenate([t,t[::-1]],0)[:max(hh,1)] if hh<=2*240 else t
    return t[:hh]
top=slate(pt+40);bot=slate(max(pb,0)+40)
full=np.zeros((1080,w0,3),np.uint8);full[pt:pt+h0]=na
def fe(n):return np.linspace(0,1,n)[:,None,None]
full[:pt+40]=(full[:pt+40]*0).astype(np.uint8)+0
tp=np.zeros((pt+40,w0,3),np.float32);tp[:]=top
bl=full[pt:pt+40].astype(np.float32)
tp[pt:pt+40]=tp[pt:pt+40]*(1-fe(40))+bl*fe(40)
full[:pt+40]=tp.astype(np.uint8)
bt=bot.astype(np.float32);ob=na[h0-40:].astype(np.float32)
bt[:40]=ob*(1-fe(40))+bt[:40]*fe(40)
full[pt+h0-40:]=bt[:1080-(pt+h0-40)].astype(np.uint8)
na=full
layer=Image.new('RGB',old.size);layer.paste(Image.fromarray(na),(ox,0))
A=np.zeros((1080,1920),np.float32)
xs=np.arange(1920)[None,:];ys=np.arange(1080)[:,None]
ax=np.clip((xs-800)/200,0,1);ay=1.0
A=ax*ay;A[:, :ox]=0
# keep the old logo block
lg=np.zeros((1080,1920),np.float32);lg[10:215,1500:1900]=1;lg=cv2.GaussianBlur(lg,(0,0),14)
A=A*(1-lg)
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
im.save(D+'assets/n10-plate.jpg',quality=95)
