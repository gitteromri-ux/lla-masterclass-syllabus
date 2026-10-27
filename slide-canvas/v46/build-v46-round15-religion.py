# V46 round 15: (1) plate slide (n10-plate.jpg) headline -> 'What does it look like in real life?' (same Playfair italic 96px, -0.02em, cream + blue, same position, only the headline changes);
# (2) NEW statement slide n26-religion.jpg: 'Take the religion out of your diet.' large, navy bg, LLA logo top-right (lifted from n02-why.jpg).
# text is rendered by headless Chrome with the deck's Playfair Display Italic; the original plate image comes from git (commit before this round).
import cv2,numpy as np,subprocess,sys,random
from playwright.sync_api import sync_playwright
G='/workspace/lla-masterclass-syllabus'
FONT='file:///usr/share/fonts/truetype/sand-box/google/Playfair%20Display/PlayfairDisplay-Italic-VariableFont_wght.ttf'
CREAM='#F0EFED';BLUE='#9DC7E5'
def gitimg(c,f):
    b=subprocess.check_output(['git','-C',G,'show',f'{c}:slide-canvas/v46/assets/{f}']);return cv2.imdecode(np.frombuffer(b,np.uint8),1)
def render(lines,out,size,tr=-0.02,W=1920,H=1080):
    html='<html><head><style>@font-face{font-family:PF;font-style:italic;font-weight:400 900;src:url(%s)}html,body{margin:0;background:transparent}.l{position:absolute;white-space:nowrap;font-family:PF;font-style:italic;font-weight:400;font-size:%dpx;letter-spacing:%sem;line-height:1}</style></head><body>'%(FONT,size,tr)
    for i,(t,x,by,col) in enumerate(lines):
        pos='left:%spx'%x if x!='center' else 'left:0;width:%dpx;text-align:center'%W
        html+='<div class="l" id="l%d" style="%s;top:0;color:%s">%s</div>'%(i,pos,col,t)
    open('/tmp/r15t.html','w').write(html+'</body></html>')
    with sync_playwright() as p:
        b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--allow-file-access-from-files']);pg=b.new_page(viewport={'width':W,'height':H});pg.goto('file:///tmp/r15t.html');pg.wait_for_timeout(700)
        for i,(t,x,by,col) in enumerate(lines):
            top=pg.evaluate("""([i,by])=>{const e=document.getElementById('l'+i);const s=document.createElement('span');s.style.cssText='display:inline-block;width:1px;height:0px;vertical-align:baseline';e.appendChild(s);const r=s.getBoundingClientRect();const rr=e.getBoundingClientRect();s.remove();return by-(r.top-rr.top)}""",[i,by])
            pg.evaluate("([i,top])=>{document.getElementById('l'+i).style.top=top+'px'}",[i,top])
        pg.screenshot(path=out,omit_background=True);b.close()
    t=cv2.imread(out,cv2.IMREAD_UNCHANGED);return t[...,:3].astype(np.float32),t[...,3:4].astype(np.float32)/255.
# ---------- (1) plate headline
BGC=np.array([25,11,5],np.float32)      # flat navy of the plate slide (BGR), measured
plate=gitimg('be118da','n10-plate.jpg') if len(sys.argv)<2 else cv2.imread(sys.argv[1])
H,W=plate.shape[:2];P=plate.astype(np.float32)
m=np.zeros((H,W),np.float32);m[183:404,100:781]=1;m[:, 781:801]=0;m[183:404,781:801]=np.linspace(1,0,20)[None,:]
m=cv2.GaussianBlur(m,(0,0),1.0)[...,None]
P=P*(1-m)+BGC[None,None,:]*m
rgb,a=render([('What does it look',129.5,272,CREAM),('like in real life?',127.5,375,BLUE)],'/tmp/r15_plate_txt.png',96)
P=P*(1-a)+rgb*a
cv2.imwrite('assets/n10-plate.jpg',np.clip(P,0,255).astype(np.uint8),[cv2.IMWRITE_JPEG_QUALITY,95])
# ---------- (2) statement slide
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
glow=np.clip(1-(((xx-1000)/1100)**2+((yy-620)/700)**2),0,1)**1.5
S=np.zeros((H,W,3),np.float32)+BGC;S+=glow[...,None]*np.array([20,9,2],np.float32)
rgb,a=render([('Take the religion',  'center',500,CREAM),('out of your diet.','center',700,BLUE)],'/tmp/r15_stmt_txt.png',176)
S=S*(1-a)+rgb*a
# LLA logo: lifted from n02-why.jpg (same position on every slide), bg-keyed so it sits on this slide's own background
n02=cv2.imread('assets/n02-why.jpg').astype(np.float32);y0,y1,x0,x1=14,196,1500,1912
patch=n02[y0:y1,x0:x1];bgest=np.stack([cv2.medianBlur(np.clip(patch[...,c],0,255).astype(np.uint8),45) for c in range(3)],-1).astype(np.float32)
diff=(patch-bgest).max(2);al=np.clip((diff-5)/28.0,0,1);al=cv2.GaussianBlur(al,(0,0),0.6)[...,None]
reg=S[y0:y1,x0:x1];S[y0:y1,x0:x1]=reg*(1-al)+patch*al
cv2.imwrite('assets/n26-religion.jpg',np.clip(S,0,255).astype(np.uint8),[cv2.IMWRITE_JPEG_QUALITY,95])
print('done')
