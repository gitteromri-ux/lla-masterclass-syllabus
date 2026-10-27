import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
FD='/workspace/lla-masterclass-syllabus/deck2/fonts/'
W,H=760,1080
def font(p,s,w=None):
    f=ImageFont.truetype(FD+p,s)
    if w:
        try:f.set_variation_by_axes([w])
        except Exception:pass
    return f
im=Image.new('RGB',(W,H),(246,249,253));d=ImageDraw.Draw(im)
# header: deep navy gradient
hh=440
for y in range(hh):
    t=y/hh;c=(int(8+10*t),int(26+34*t),int(66+52*t));d.line([(0,y),(W,y)],fill=c)
# soft accent glow in header
g=Image.new('RGB',(W,hh),(0,0,0));gd=ImageDraw.Draw(g);gd.ellipse((W-330,-120,W+120,260),fill=(40,120,190));g=g.filter(ImageFilter.GaussianBlur(70))
im.paste(Image.composite(Image.new('RGB',(W,hh),(255,255,255)),Image.new('RGB',(W,hh),(0,0,0)),Image.new('L',(W,hh),0)),(0,0))
hd=np.array(im.crop((0,0,W,hh))).astype(np.float32)+np.array(g).astype(np.float32)*0.55
im.paste(Image.fromarray(np.clip(hd,0,255).astype(np.uint8)),(0,0));d=ImageDraw.Draw(im)
logo=Image.open('closing-graphics/lla-logo-original.png').convert('RGBA');lw=430;logo=logo.resize((lw,int(logo.height*lw/logo.width)),Image.LANCZOS)
im.paste(logo,(60,34),logo)
d.text((W/2,322),'Blueprint',font=font('PlayfairDisplay-Italic.ttf',150,500),fill=(244,248,255),anchor='mm')
d.text((W/2,412),'YOUR GUIDED LONGEVITY PROTOCOL',font=font('Inter.ttf',27,600),fill=(150,205,240),anchor='mm')
# accent line
for x in range(W):
    t=x/W;d.line([(x,hh),(x,hh+10)],fill=(int(139+(68-139)*t),int(127+(184-127)*t),int(221+(166-221)*t)))
# donut
cx,cy,R,r=W//2,hh+250,175,112
cols=[(139,127,221),(28,123,255),(79,201,201),(68,184,166)]
for i,c in enumerate(cols):
    d.pieslice((cx-R,cy-R,cx+R,cy+R),-90+i*90+2,-90+(i+1)*90-2,fill=c)
d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(246,249,253))
d.text((cx,cy-14),'18',font=font('PlayfairDisplay.ttf',104,600),fill=(12,36,78),anchor='mm')
d.text((cx,cy+58),'WEEKS',font=font('Inter.ttf',27,700),fill=(60,100,150),anchor='mm')
# legend
labels=['Sleep','Nutrition','Movement','Mindset'];ly=cy+R+52
pf=font('Inter.ttf',37,650)
for i,(l,c) in enumerate(zip(labels,[cols[0],cols[3],cols[1],cols[2]])):
    x=62+(i%2)*340;y=ly+(i//2)*70
    d.rounded_rectangle((x,y-17,x+34,y+17),9,fill=c);d.text((x+50,y),l,font=pf,fill=(14,38,80),anchor='lm')
im.save('cover_flat.png')
cover=np.array(im)
# ---- place into the slide: perspective quad + thickness + shadow + glow
S=cv2.imread('base_moved.png').astype(np.float32)
# remove the old booklet
old=np.array([(1190,722),(1327,716),(1365,925),(1210,932)],np.int32)
m=np.zeros(S.shape[:2],np.uint8);cv2.fillPoly(m,[old],255);m=cv2.dilate(m,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(40,40)))
fill=cv2.inpaint(S.astype(np.uint8),m,9,cv2.INPAINT_TELEA).astype(np.float32)
ref=S[560:700,1300:1450];sd=(ref-cv2.GaussianBlur(ref,(0,0),5)).std()
nz=np.random.default_rng(5).normal(0,1,S.shape[:2]).astype(np.float32);nz=cv2.GaussianBlur(nz,(0,0),1.1);nz=(nz/nz.std()*sd)[...,None]
fill=fill+nz
a=cv2.GaussianBlur(m.astype(np.float32)/255,(0,0),7)[...,None];S=S*(1-a)+fill*a
Q=np.float32([(1196,698),(1362,688),(1376,960),(1204,980)])    # TL TR BR BL
srcq=np.float32([(0,0),(W,0),(W,H),(0,H)])
Mx=cv2.getPerspectiveTransform(srcq,Q)
out=S.copy()
# shadow
sh=np.zeros(S.shape[:2],np.float32);cv2.fillPoly(sh,[np.int32(Q+np.float32([26,20]))],1.0);sh=cv2.GaussianBlur(sh,(0,0),16)
out=out*(1-0.62*sh[...,None])
# soft cool glow behind the booklet
gl=np.zeros(S.shape[:2],np.float32);cv2.fillPoly(gl,[np.int32(Q)],1.0);gl=cv2.GaussianBlur(gl,(0,0),22)
out=out+gl[...,None]*np.array([40,26,6],np.float32)*0.9   # BGR warm-cyan lift
# thickness: left spine + bottom page block
def poly(pts,col):
    p=np.zeros(S.shape[:2],np.uint8);cv2.fillPoly(p,[np.int32(pts)],255);return p
spine=[Q[0],Q[3],Q[3]+(-13,6),Q[0]+(-13,3)]
pages=[Q[3],Q[2],Q[2]+(0,11),Q[3]+(-6,12)]
for pts,col in ((spine,(95,60,20)),(pages,(228,232,240))):
    pm=poly(pts,col)
    out[pm>0]=np.array(col,np.float32)
bg=cv2.warpPerspective(cover[...,::-1].copy(),Mx,(S.shape[1],S.shape[0]),flags=cv2.INTER_AREA|cv2.INTER_LINEAR)
cm=cv2.warpPerspective(np.full((H,W),255,np.uint8),Mx,(S.shape[1],S.shape[0]),flags=cv2.INTER_LINEAR)
cm=cv2.GaussianBlur(cm.astype(np.float32)/255,(0,0),0.8)[...,None]
# subtle sheen on the cover
yy,xx=np.mgrid[0:S.shape[0],0:S.shape[1]].astype(np.float32)
sheen=np.clip(1-np.abs(((xx-1196)/190)-((yy-690)/300)*0.9-0.35)*2.6,0,1)[...,None]*0.10
bg=np.clip(bg*(1+sheen)+sheen*40,0,255)
out=out*(1-cm)+bg*cm
# crisp light edge
edge=cv2.GaussianBlur(cv2.dilate(cm[...,0],np.ones((3,3)))-cv2.erode(cm[...,0],np.ones((3,3))),(0,0),0.7)[...,None]
out=out+edge*35
cv2.imwrite('base_final.png',np.clip(out,0,255).astype(np.uint8))
cv2.imwrite('bf_crop.png',np.clip(out,0,255).astype(np.uint8)[560:1020,1000:1500])
