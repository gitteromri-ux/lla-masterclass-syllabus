# V46 round 16: NEW slide n28-sugar-limit.jpg (right after the creme brulee slide).
# Two elements (cake removed on Omri's request): person with a CGM (hero, left), '6 teaspoons' as real sugar (right, centred under its headline, with the daily-limit label).
# photos (generated): assets/src/sugar-man.jpg, sugar-spoons6.jpg, sugar-watermelon-cake.jpg. text: headless Chrome, Playfair Display Italic + Inter. LLA logo lifted from n02-why.jpg.
import cv2,numpy as np
from playwright.sync_api import sync_playwright
W,H=1920,1080
PF='file:///usr/share/fonts/truetype/sand-box/google/Playfair%20Display/PlayfairDisplay-Italic-VariableFont_wght.ttf'
IN='file:///usr/share/fonts/truetype/sand-box/google/Inter/Inter-VariableFont_opsz,wght.ttf'
BG=np.array([25,11,5],np.float32)           # deck navy (BGR) #050B19
rd=lambda f:cv2.imread('assets/src/'+f).astype(np.float32)
def rs(img,w=None,h=None):
    s=(h/img.shape[0]) if h else (w/img.shape[1]);return cv2.resize(img,(int(img.shape[1]*s+.5),int(img.shape[0]*s+.5)),interpolation=cv2.INTER_LANCZOS4)
def feather(h,w,f,fy=None):
    fy=fy or f
    y=np.minimum(np.arange(h),np.arange(h)[::-1]).astype(np.float32);x=np.minimum(np.arange(w),np.arange(w)[::-1]).astype(np.float32)
    m=np.minimum(np.clip(y[:,None]/fy,0,1),np.clip(x[None,:]/f,0,1));m=np.clip(m,0,1);return (m*m*(3-2*m))[...,None]
S=np.zeros((H,W,3),np.float32)+BG
# soft navy glow behind the right half
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
S+= (np.clip(1-(((xx-1400)/900)**2+((yy-560)/700)**2),0,1)**1.6)[...,None]*np.array([16,7,2],np.float32)
# --- person (hero): full height, left; extended with his own navy
man=rs(rd('sugar-man.jpg'),h=H);ML=-60
mw=man.shape[1]
def bgext(img,side,n):
    col=img[:, :8] if side=='l' else img[:, -8:]
    return np.repeat(cv2.GaussianBlur(col.mean(1,keepdims=True),(0,0),40),n,1)
panel=np.concatenate([man[:, -ML:],bgext(man,'r',W-(mw+ML))],1)   # ML<0 crops the left edge
r=np.clip((np.arange(W)-800)/130.0,0,1)[None,:,None];r=r*r*(3-2*r)
base=S.copy();base[:, :panel.shape[1]]=panel
S=base*(1-r)+S*r
# CGM sensor centre (measured in the source photo: 655.6, 812.5)
sc=(655.6*H/1152+ML,812.5*H/1152)
# --- photos right
spi=rd('sugar-spoons6.jpg');q=spi.shape[0]/768.;sp=spi[0:int(768*q),int(100*q):int(920*q)];sp=rs(sp,h=580)
RCX=1400                                   # centre axis of the right half: headline, label and spoons all centred on it
SPX=int(RCX-sp.shape[1]/2);SPY=450
h,w=sp.shape[:2];m=feather(h,w,110,fy=45);reg=S[SPY:SPY+h,SPX:SPX+w];S[SPY:SPY+h,SPX:SPX+w]=reg*(1-m)+sp*m
print('spoons',SPX,sp.shape,'right edge',SPX+w)
# vignette to the deck navy
vig=np.clip(((xx-960)/1150)**2+((yy-540)/780)**2,0,1.4)[...,None]
S=S*(1-0.22*vig)+BG*(0.22*vig)*0.6
# sensor highlight ring (soft glow + thin sky ring)
ring=np.zeros((H,W),np.float32);cv2.circle(ring,(int(sc[0]),int(sc[1])),40,1.0,2,cv2.LINE_AA)
glow=cv2.GaussianBlur(ring,(0,0),7)*1.6
col=np.array([255,210,138],np.float32)  # sky #8AD2FF in BGR
S=S*(1-np.clip(glow,0,.6)[...,None])+col*np.clip(glow,0,.6)[...,None]
S=S*(1-ring[...,None]*.9)+col*ring[...,None]*.9
# leader line from the ring to the label
ln=np.zeros((H,W),np.float32);cv2.line(ln,(int(sc[0]+42),int(sc[1])),(int(sc[0]+98),int(sc[1])),1.0,2,cv2.LINE_AA);S=S*(1-ln[...,None]*.9)+col*ln[...,None]*.9
LX=int(sc[0]+108)
html='''<html><head><style>@font-face{font-family:PF;font-style:italic;font-weight:400 900;src:url(%s)}@font-face{font-family:IN;font-weight:100 900;src:url(%s)}
html,body{margin:0;background:transparent}div{position:absolute;white-space:nowrap}
.big{left:%dpx;width:1000px;text-align:center;top:205px;font-family:PF;font-style:italic;font-size:150px;letter-spacing:-0.02em;line-height:1;color:#F3EBDD}.big span{color:#8AD2FF}
.sub{left:%dpx;width:1000px;text-align:center;top:384px;font-family:IN;font-weight:400;font-size:38px;color:#F3EBDD;opacity:.92}
.cgm{left:%dpx;top:%dpx;font-family:PF;font-style:italic;font-size:52px;line-height:1;color:#8AD2FF}
.cgms{left:%dpx;top:%dpx;font-family:IN;font-weight:400;font-size:26px;color:#F3EBDD;opacity:.9}
</style></head><body>
<div class="big">6 <span>teaspoons</span></div><div class="sub">The daily limit for added sugar</div>
<div class="cgm">Your CGM</div><div class="cgms">live glucose sensor</div>
</body></html>'''%(PF,IN,RCX-500,RCX-500,LX,int(sc[1])-40,LX,int(sc[1])+16)
open('/tmp/r16.html','w').write(html)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--allow-file-access-from-files']);pg=b.new_page(viewport={'width':W,'height':H});pg.goto('file:///tmp/r16.html');pg.wait_for_timeout(800)
    pg.screenshot(path='/tmp/r16_txt.png',omit_background=True);b.close()
t=cv2.imread('/tmp/r16_txt.png',cv2.IMREAD_UNCHANGED);rgb=t[...,:3].astype(np.float32);a=t[...,3:4].astype(np.float32)/255.
sh=cv2.GaussianBlur(a[...,0],(0,0),24)[...,None];S=S*(1-0.5*sh)+BG*0.5*sh
S=S*(1-a)+rgb*a
# LLA logo
n02=cv2.imread('assets/n02-why.jpg').astype(np.float32);y0,y1,x0,x1=14,196,1500,1912
patch=n02[y0:y1,x0:x1];bgest=np.stack([cv2.medianBlur(np.clip(patch[...,c],0,255).astype(np.uint8),45) for c in range(3)],-1).astype(np.float32)
diff=(patch-bgest).max(2);al=np.clip((diff-5)/28.0,0,1);al=cv2.GaussianBlur(al,(0,0),0.6)[...,None]
reg=S[y0:y1,x0:x1];S[y0:y1,x0:x1]=reg*(1-al)+patch*al
rng=np.random.default_rng(7);S+=rng.normal(0,2.0,(H,W,1)).astype(np.float32)
cv2.imwrite('assets/n28-sugar-limit.jpg',np.clip(S,0,255).astype(np.uint8),[cv2.IMWRITE_JPEG_QUALITY,95])
print('ok')
