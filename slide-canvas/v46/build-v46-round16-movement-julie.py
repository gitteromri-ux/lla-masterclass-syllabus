# V46 round 16: Julie's option B for the Movement Week slide (n14-movement-week.jpg stays byte-identical).
# Julie: "add a mobility & balance block every day. Make it first ... title it 'mobility & balance' while tea brews".
# -> n27-movement-week-julie.jpg: a full-width daily band (Mon to Sun) as the FIRST row under the day labels; every original tile moves down one band-height, unchanged.
import cv2,numpy as np
from playwright.sync_api import sync_playwright
src=cv2.imread('assets/n14-movement-week.jpg');H,W=src.shape[:2];F=src.astype(np.float32)
XS=[119,362,604,847,1089,1332,1574];TW=225;ROWS=[(467,109),(592,109)]
BAND_Y,BAND_H,GAP=467,109,16;SHIFT=BAND_H+GAP;TSHIFT=72
def rrect(x,y,w,h,r,pad=0,ss=4):
    m=np.zeros((H*1,W*1),np.uint8)
    big=np.zeros((h*ss+2*pad*ss,w*ss+2*pad*ss),np.uint8)
    cv2.rectangle(big,(r*ss,0),(big.shape[1]-r*ss,big.shape[0]),255,-1);cv2.rectangle(big,(0,r*ss),(big.shape[1],big.shape[0]-r*ss),255,-1)
    for cx in (r*ss,big.shape[1]-r*ss):
        for cy in (r*ss,big.shape[0]-r*ss): cv2.circle(big,(cx,cy),r*ss,255,-1)
    return cv2.resize(big,(w+2*pad,h+2*pad),interpolation=cv2.INTER_AREA).astype(np.float32)/255.
tiles=[(XS[c],ROWS[r][0]) for r,cols in ((0,range(7)),(1,(2,4))) for c in cols]
# 1) clean background: inpaint every old tile (+ its soft shadow)
mask=np.zeros((H,W),np.uint8)
for x,y in tiles: cv2.rectangle(mask,(x-3,y-3),(x+TW+3,y+109+3),255,-1)
mask=cv2.dilate(mask,np.ones((9,9),np.uint8))
# inpaint on a downscaled copy (smooth bokeh background) to avoid streaks, then upsample only inside the mask
sm=cv2.resize(src,(W//4,H//4),interpolation=cv2.INTER_AREA);mk=cv2.resize(mask,(W//4,H//4),interpolation=cv2.INTER_NEAREST)
inp=cv2.inpaint(sm,mk,9,cv2.INPAINT_TELEA);inp=cv2.GaussianBlur(inp,(0,0),3);inp=cv2.resize(inp,(W,H),interpolation=cv2.INTER_CUBIC).astype(np.float32)
mf=cv2.GaussianBlur(mask.astype(np.float32)/255.,(0,0),2)[...,None]
B=F*(1-mf)+inp*mf
# add the original's own fine grain back inside the cleaned area
rng=np.random.default_rng(3);B+=rng.normal(0,1.6,(H,W,1)).astype(np.float32)*mf
# 2) Twice block: lift text pixels, move them down TSHIFT
y0,y1,x0,x1=735,990,70,1290
reg=src[y0:y1,x0:x1].astype(np.float32);bgm=np.stack([cv2.medianBlur(np.clip(reg[...,c],0,255).astype(np.uint8),71) for c in range(3)],-1).astype(np.float32)
dif=np.abs(reg-bgm).max(2);dif[:30]=0;dif[-30:]=0;dif[:, :30]=0;dif[:, -30:]=0
tm=(dif>20).astype(np.uint8);tm=cv2.dilate(tm,np.ones((9,9),np.uint8))
tmf=cv2.GaussianBlur(tm.astype(np.float32),(0,0),2)
tmask_full=np.zeros((H,W),np.uint8);tmask_full[y0:y1,x0:x1]=tm
sm=cv2.resize(src,(W//4,H//4),interpolation=cv2.INTER_AREA);mk=cv2.resize(tmask_full,(W//4,H//4),interpolation=cv2.INTER_NEAREST)
inp2=cv2.GaussianBlur(cv2.inpaint(sm,mk,7,cv2.INPAINT_TELEA),(0,0),2);inp2=cv2.resize(inp2,(W,H),interpolation=cv2.INTER_CUBIC).astype(np.float32)
mfull=np.zeros((H,W),np.float32);mfull[y0:y1,x0:x1]=tmf;mfull=mfull[...,None]
B=B*(1-mfull)+inp2*mfull
# paste lifted text at +TSHIFT (feathered mask keeps its own anti-aliased edges)
a=np.clip(tmf*1.0,0,1)[...,None];dst=B[y0+TSHIFT:y1+TSHIFT,x0:x1]
B[y0+TSHIFT:y1+TSHIFT,x0:x1]=dst*(1-a)+reg*a
# 3) paste every original tile (with its own text) SHIFT px lower
for x,y in tiles:
    m=rrect(TW,109,TW,109,16)[...,None]
    patch=F[y:y+109,x:x+TW];yy=y+SHIFT
    B[yy:yy+109,x:x+TW]=B[yy:yy+109,x:x+TW]*(1-m)+patch*m
# 4) the new first row: one 'Mobility & balance' tile per day (same size 225x109, radius 16, pitch and look as the tiles)
t=np.linspace(0,1,BAND_H)[:,None,None];c1=np.array([126,194,247],np.float32);c2=np.array([94,163,240],np.float32)   # BGR: #F7C27E -> #F0A35E
grad=np.broadcast_to(c1*(1-t)+c2*t,(BAND_H,TW,3))
for x in XS:
    m=rrect(TW,BAND_H,TW,BAND_H,16)[...,None]
    B[BAND_Y:BAND_Y+BAND_H,x:x+TW]=B[BAND_Y:BAND_Y+BAND_H,x:x+TW]*(1-m)+grad*m
OUT=np.clip(B,0,255).astype(np.uint8)
# text (Outfit, same family as the tiles)
OF='file:///usr/share/fonts/truetype/sand-box/google/Outfit/Outfit-VariableFont_wght.ttf'
# Omri: each tile contains ONLY the words "Mobility & balance", bold, same size (27px Outfit 700) as the other tiles' headline line
tiles_html=''.join('<div class="t" style="left:%dpx"><b>Mobility &amp;</b><b>balance</b></div>'%(x+20) for x in XS)
html='''<html><head><style>@font-face{font-family:OF;font-weight:100 900;src:url(%s)}html,body{margin:0;background:transparent}
.t{position:absolute;top:%dpx;height:%dpx;display:flex;flex-direction:column;justify-content:center;white-space:nowrap;font-family:OF;font-size:27px;line-height:34px;color:#06122B}.t b{font-weight:700}.t span{font-weight:400}</style></head><body>%s</body></html>'''%(OF,BAND_Y,BAND_H,tiles_html)
open('/tmp/mw.html','w').write(html)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--allow-file-access-from-files']);pg=b.new_page(viewport={'width':W,'height':H});pg.goto('file:///tmp/mw.html');pg.wait_for_timeout(700)
    pg.screenshot(path='/tmp/mw_txt.png',omit_background=True);b.close()
tt=cv2.imread('/tmp/mw_txt.png',cv2.IMREAD_UNCHANGED);al=tt[...,3:4].astype(np.float32)/255.
Of=OUT.astype(np.float32)*(1-al)+tt[...,:3].astype(np.float32)*al
cv2.imwrite('assets/n27-movement-week-julie.jpg',np.clip(Of,0,255).astype(np.uint8),[cv2.IMWRITE_JPEG_QUALITY,95])
print('ok')
