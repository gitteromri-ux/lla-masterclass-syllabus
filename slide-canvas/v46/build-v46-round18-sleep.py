# V46 round 18 (Omri): slide 10 (n08-sleep.jpg), from the previous live image (assets/src/n08-sleep-before-r17.jpg, md5 471a1d49...):
# (1) '8 hour opportunity' under the 9 PM-5 AM bar at secondary-label / body size, (2) the '48%' stat enlarged (x1.55) and the text next to it enlarged (x1.5). Same words, same style, nothing else.
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
O=cv2.imread('assets/src/n08-sleep-before-r17.jpg');H,W=O.shape[:2];Of=O.astype(np.float32)
OF='/usr/share/fonts/truetype/sand-box/google/Outfit/Outfit-VariableFont_wght.ttf'
# ---- erase the old stat + text (smooth card gradient -> low-res inpaint, feathered)
box=np.zeros((H,W),bool);box[800:930,175:1000]=True
mx=Of.max(2);m=((mx>120)&box).astype(np.uint8)
m=cv2.dilate(m,np.ones((9,9),np.uint8))
s=3;sm=cv2.resize(O,(W//s,H//s),interpolation=cv2.INTER_AREA);mm=cv2.resize(m*255,(W//s,H//s),interpolation=cv2.INTER_NEAREST)
fill=cv2.inpaint(sm,mm,7,cv2.INPAINT_TELEA);fill=cv2.GaussianBlur(fill,(0,0),1.2);fill=cv2.resize(fill,(W,H),interpolation=cv2.INTER_CUBIC).astype(np.float32)
rng=np.random.RandomState(9);fill+=rng.randn(H,W,1).astype(np.float32)*1.5
ms=cv2.GaussianBlur(m.astype(np.float32),(0,0),1.5)[...,None]
bg=Of*(1-ms)+fill*ms
# ---- stat: premultiplied foreground (orig - bg*(1-a)), scaled x1.55 about its own left/centre
sx0,sy0,sx1,sy1=180,806,388,922
def cov(reg,bgr):
    d=(reg.max(2)-bgr.max(2));top=np.percentile(reg.max(2)[reg.max(2)>150],90)
    return np.clip(d/(top-bgr.max(2)+1e-3),0,1)
reg=Of[sy0:sy1,sx0:sx1];bgr=bg[sy0:sy1,sx0:sx1];a=cov(reg,bgr)[...,None]
pm=np.clip(reg-bgr*(1-a),0,255)
K=1.55;nw,nh=round((sx1-sx0)*K),round((sy1-sy0)*K)
pm2=cv2.resize(pm,(nw,nh),interpolation=cv2.INTER_LANCZOS4);a2=np.clip(cv2.resize(a[...,0],(nw,nh),interpolation=cv2.INTER_LANCZOS4),0,1)[...,None]
cy=870;X=sx0+8;Y=int(cy-(nh*(((864-sy0)/(sy1-sy0)))))   # original stat centre y~864
out=bg.copy()
out[Y:Y+nh,X:X+nw]=out[Y:Y+nh,X:X+nw]*(1-a2)+pm2
# ---- text next to the stat (same Outfit light, x1.5), vertically centred on the stat
sz=28*1.5;f=ImageFont.truetype(OF,round(sz*4));f.set_variation_by_axes([230])
t='lower mortality risk \u2014 the most regular sleepers'
tx=X+nw+34;by=Y+round(62*K)                          # baseline where the old text sat relative to the stat
lay2=Image.new('L',(1100*4,170*4),0);ImageDraw.Draw(lay2).text(((tx-420)*4,(by-790)*4),t,font=f,fill=255,anchor='ls')
la=np.array(lay2.resize((1100,170),Image.LANCZOS)).astype(np.float32)[...,None]/255
reg=out[790:960,420:1520];out[790:960,420:1520]=reg*(1-la)+np.array([245,229,218],np.float32)*la
# ---- '8 hour opportunity' under the bar, body size (Outfit, light blue-white label colour)
f2=ImageFont.truetype(OF,38*4);f2.set_variation_by_axes([400])
s8='8 hour opportunity';cx,top=1350,652
lay=Image.new('L',(700*4,90*4),0);ImageDraw.Draw(lay).text((20*4,60*4),s8,font=f2,fill=255,anchor='ls')
a8=np.array(lay.resize((700,90),Image.LANCZOS)).astype(np.float32)/255
ys,xs=np.where(a8>0.3);x0=int(cx-(xs.min()+xs.max())/2);y0=top-ys.min()
reg=out[y0:y0+90,x0:x0+700];out[y0:y0+90,x0:x0+700]=reg*(1-a8[...,None])+np.array([250,238,226],np.float32)*a8[...,None]
print('stat',X,Y,nw,nh,'text from',tx,'baseline',by,'8h at',x0,y0)
cv2.imwrite('assets/n08-sleep.jpg',np.clip(out,0,255).astype(np.uint8),[cv2.IMWRITE_JPEG_QUALITY,95])
