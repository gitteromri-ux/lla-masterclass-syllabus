# V46 round 16 (Omri override): Julie's option B of the Movement Week slide (n14-movement-week.jpg stays byte-identical).
# Built from the ORIGINAL n14 image: every original tile and the 'Twice' block stay exactly where they are. One WHITE box per day, 'Mobility & balance' only,
# placed directly below that day's lowest existing tile (same size 225x109, radius 16, 16 px gap, Outfit bold 27px like the tiles' headline line).
import cv2,numpy as np
from playwright.sync_api import sync_playwright
src=cv2.imread('assets/n14-movement-week.jpg');H,W=src.shape[:2];B=src.astype(np.float32)
XS=[119,362,604,847,1089,1332,1574];TW=225;TH=109;ROW=[467,592,717]   # tile rows (originals at 467 and 592; third slot = 592+109+16)
LOWEST=[0,0,1,0,1,0,0]                                            # Wed and Fri have a second tile (Zone 2 or HIIT)
def rrect(w,h,r,ss=4):
    big=np.zeros((h*ss,w*ss),np.uint8)
    cv2.rectangle(big,(r*ss,0),(w*ss-r*ss,h*ss),255,-1);cv2.rectangle(big,(0,r*ss),(w*ss,h*ss-r*ss),255,-1)
    for cx in (r*ss,w*ss-r*ss):
        for cy in (r*ss,h*ss-r*ss):cv2.circle(big,(cx,cy),r*ss,255,-1)
    return (cv2.resize(big,(w,h),interpolation=cv2.INTER_AREA).astype(np.float32)/255.)[...,None]
m=rrect(TW,TH,16)
t=np.linspace(0,1,TH)[:,None,None];grad=np.broadcast_to(np.array([255,255,255],np.float32)*(1-t)+np.array([247,242,238],np.float32)*t,(TH,TW,3))   # white, a hair greyer at the bottom
boxes=[]
for x,l in zip(XS,LOWEST):
    y=ROW[l+1];boxes.append((x,y));B[y:y+TH,x:x+TW]=B[y:y+TH,x:x+TW]*(1-m)+grad*m
OF='file:///usr/share/fonts/truetype/sand-box/google/Outfit/Outfit-VariableFont_wght.ttf'
th=''.join('<div class="t" style="left:%dpx;top:%dpx"><b>Mobility &amp;</b><b>balance</b></div>'%(x+20,y) for x,y in boxes)
html='''<html><head><style>@font-face{font-family:OF;font-weight:100 900;src:url(%s)}html,body{margin:0;background:transparent}
.t{position:absolute;height:%dpx;display:flex;flex-direction:column;justify-content:center;white-space:nowrap;font-family:OF;font-size:27px;line-height:34px;color:#06122B}.t b{font-weight:700}</style></head><body>%s</body></html>'''%(OF,TH,th)
open('/tmp/mw.html','w').write(html)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--allow-file-access-from-files']);pg=b.new_page(viewport={'width':W,'height':H});pg.goto('file:///tmp/mw.html');pg.wait_for_timeout(700)
    pg.screenshot(path='/tmp/mw_txt.png',omit_background=True);b.close()
tt=cv2.imread('/tmp/mw_txt.png',cv2.IMREAD_UNCHANGED);al=tt[...,3:4].astype(np.float32)/255.
O=B*(1-al)+tt[...,:3].astype(np.float32)*al
cv2.imwrite('assets/n27-movement-week-julie.jpg',np.clip(O,0,255).astype(np.uint8),[cv2.IMWRITE_JPEG_QUALITY,95])
print('ok',boxes)
