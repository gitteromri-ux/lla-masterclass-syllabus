# V46 round 2 (runs ONCE on the current assets, after build-logo.py + build-v46-edits.py): slide 16 relayout, slide 20 Venn,
# slide 15 link, slide 14 V2 label, slide 10 plate (zero alcohol). Backups of the previous assets: /workspace/assets_r2bak
import sys,os,cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
A='assets/'
INTER='../../backup-deck/fonts/Inter.ttf'
OUTFIT='/usr/share/fonts/truetype/sand-box/google/Outfit/Outfit-VariableFont_wght.ttf'
PFI='../../backup-deck/fonts/PlayfairDisplay-Italic.ttf'
PFR='../../backup-deck/fonts/PlayfairDisplay.ttf'
def rd(n):return cv2.imread(A+n)
def wr(im,n):cv2.imwrite(A+n,im,[cv2.IMWRITE_JPEG_QUALITY,95] if n.endswith('jpg') else [])
def F(path,size,axes=None):
    f=ImageFont.truetype(path,size)
    if axes:f.set_variation_by_axes(axes)
    return f
def T(im,items,blur=0.0):
    H,W=im.shape[:2];lay=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(lay)
    for it in items:
        x,y,s,f,c,a=it[:6];ft=it[6] if len(it)>6 else None
        d.text((x,y),s,font=f,fill=tuple(c)+(255,),anchor=a,features=ft)
    L=np.array(lay).astype(np.float32);al=L[...,3:]/255
    if blur>0:al=cv2.GaussianBlur(al,(0,0),blur).reshape(H,W,1)
    rgb=L[...,:3][...,::-1]
    return np.clip(im.astype(np.float32)*(1-al)+rgb*al,0,255).astype(np.uint8)
def wipe(im,box,thr=40,dil=3):
    """inpaint only bright/high-contrast strokes (text) inside box"""
    x0,y0,x1,y1=box;sub=im[y0:y1,x0:x1];bg=cv2.medianBlur(sub,61).astype(int)
    m=((np.abs(sub.astype(int)-bg).max(2))>thr).astype(np.uint8)*255;m=cv2.dilate(m,np.ones((2*dil+1,2*dil+1),np.uint8))
    full=np.zeros(im.shape[:2],np.uint8);full[y0:y1,x0:x1]=m
    return cv2.inpaint(im,full,5,cv2.INPAINT_TELEA)
def move_text(src,dst,box,dy,thr=8,dx=0):
    x0,y0,x1,y1=box;sub=src[y0:y1,x0:x1];bg=cv2.medianBlur(sub,61).astype(int)
    m=((np.abs(sub.astype(int)-bg).max(2))>thr).astype(np.uint8)*255;m=cv2.dilate(m,np.ones((5,5),np.uint8))
    a=cv2.GaussianBlur(m.astype(np.float32)/255,(0,0),1.0)[...,None]
    reg=dst[y0+dy:y1+dy,x0+dx:x1+dx].astype(np.float32);dst[y0+dy:y1+dy,x0+dx:x1+dx]=np.clip(reg*(1-a)+sub.astype(np.float32)*a,0,255).astype(np.uint8);return dst
def scale_text(src,dst,box,sc,anchor_to,thr=30):
    """re-sample the glyph pixels in box by sc (about its left-centre/bottom-centre) -> placed so bottom-centre = anchor_to"""
    x0,y0,x1,y1=box;sub=src[y0:y1,x0:x1];bg=cv2.medianBlur(sub,61).astype(int)
    m=((np.abs(sub.astype(int)-bg).max(2))>thr).astype(np.float32);m=cv2.GaussianBlur(m,(0,0),0.8)
    ink=sub.astype(np.float32)*m[...,None]
    w,h=round((x1-x0)*sc),round((y1-y0)*sc)
    ink=cv2.resize(ink,(w,h),interpolation=cv2.INTER_CUBIC);am=cv2.resize(m,(w,h),interpolation=cv2.INTER_CUBIC)
    a=np.clip(am,0,1)[...,None];fg=np.where(a>1e-3,ink/np.maximum(a,1e-3),0)
    X=int(anchor_to[0]-w/2);Y=int(anchor_to[1]-h)
    reg=dst[Y:Y+h,X:X+w].astype(np.float32);dst[Y:Y+h,X:X+w]=np.clip(reg*(1-a)+fg*a,0,255).astype(np.uint8);return dst
def want(k):return len(sys.argv)<2 or k in sys.argv[1:]

# ================= slide 16 : protocol relayout (same content, colours and fonts; larger text, more air) =================
if want('16'):
    im=rd('n16-protocol.jpg');orig=im.copy()
    im=wipe(im,(100,452,990,580),thr=40);im=wipe(im,(990,452,1860,552),thr=40)
    im=wipe(im,(100,690,1860,790),thr=40)
    im=wipe(im,(990,552,1640,592),thr=40)                      # caption (re-scaled below)
    PT=F(PFR,46,[530]);OS=F(OUTFIT,31,[410]);PTb=F(PFR,40,[530]);OSb=F(OUTFIT,29,[410])
    wh=(253,254,254);gr=(214,228,253)
    tb,l1,l2=438,478,515   # above-row baselines (time, desc line 1, desc line 2)
    items=[
     (120,tb,'5:00 AM',PT,wh,'ls'),(120,l1,'Wake · water ·',OS,gr,'ls'),(120,l2,'prayer · light',OS,gr,'ls'),
     (472,tb,'8:00 AM',PT,wh,'ms'),(472,l1,'Eating window',OS,gr,'ms'),(472,l2,'opens',OS,gr,'ms'),
     (860,tb,'11:00 AM',PT,wh,'ms'),(860,l1,'Main meal, then a',OS,gr,'ms'),(860,l2,'walk',OS,gr,'ms'),
     (1200,tb,'4:00 PM',PT,wh,'ms'),(1200,l1,'Dinner',OS,gr,'ms'),
     (1462,tb,'6:00 PM',PT,wh,'ms'),(1462,l1,'Kitchen closes',OS,gr,'ms'),
     (1752,tb,'9:00 PM',PT,wh,'ms'),(1752,l1,'Lights out',OS,gr,'ms')]
    bt,bd=738,776  # below-row baselines
    items+=[
     (340,bt,'7:00 AM',PTb,wh,'ms'),(340,bd,'Movement & sauna',OSb,gr,'ms'),
     (625,bt,'10:00 AM',PTb,wh,'ms'),(625,bd,'Caffeine cut-off',OSb,gr,'ms'),
     (962,bt,'1:00 PM',PTb,wh,'ms'),(962,bd,'Stress reset',OSb,gr,'ms'),
     (1660,bt,'8:00 PM',PTb,wh,'ms'),(1660,bd,'Screens off',OSb,gr,'ms')]
    im=T(im,items,blur=0.45)
    im=scale_text(orig,im,(996,556,1620,590),1.14,(1307,583))   # "10-HOUR EATING WINDOW" caption, 14% larger
    wr(im,'n16-protocol.jpg')

# ================= slide 20 : Venn in three clearly distinct premium colours, right-aligned coloured labels, lower rows =================
if want('20'):
    im=rd('n20-why.jpg');H,W=im.shape[:2];src=im.copy()
    C=[(379,519),(840,519),(609,760)];R=260
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
    # 1. clean background where the old discs were (normalised convolution from the surrounding background)
    mask=np.zeros((H,W),np.float32)
    for cx,cy in C:mask=np.maximum(mask,(np.hypot(xx-cx,yy-cy)<R+16).astype(np.float32))
    mask[:, 1125:]=1   # keep the right column out of the estimate (text), it is handled separately
    mask[:230,:]=1     # title row
    ok=1-mask;ok3=ok[...,None]
    num=cv2.GaussianBlur(src.astype(np.float32)*ok3,(0,0),90);den=cv2.GaussianBlur(ok,(0,0),90)[...,None]
    bgest=num/np.maximum(den,1e-4)
    reg=np.zeros((H,W),np.float32)
    for cx,cy in C:reg=np.maximum(reg,(np.hypot(xx-cx,yy-cy)<R+14).astype(np.float32))
    reg[:,1125:]=0;reg[:230,:]=0;reg=cv2.GaussianBlur(reg,(0,0),3)[...,None]
    base=(src.astype(np.float32)*(1-reg)+bgest*reg)
    # 2. three discs as additive light, each with its own premium colour (BGR)
    cols=[(222,120,40),(150,190,40),(60,170,236)]   # sapphire, emerald-teal, champagne gold   (RGB 40,120,222 / 40,190,150 / 236,170,60)
    out=base.copy();rim=np.zeros((H,W),np.float32);rimc=np.zeros((H,W,3),np.float32)
    for (cx,cy),c in zip(C,cols):
        d=np.hypot(xx-cx,yy-cy);inside=np.clip(R+0.5-d,0,1)
        g=0.27+0.15*np.exp(-(((xx-(cx-30))**2+(yy-(cy-40))**2)/(2*170.0**2)))   # soft inner light
        out+=inside[...,None]*g[...,None]*np.array(c,np.float32)[None,None]*0.85
        ring=np.clip(1.6-np.abs(d-R),0,1);rimc=np.maximum(rimc,ring[...,None]*np.array([min(255,v*1.05+70) for v in c],np.float32)[None,None]*0.9)
    out=np.maximum(out,rimc)
    im=np.clip(out,0,255).astype(np.uint8)
    # 3. labels (right-aligned inside each disc, in that disc's colour)
    f=F(PFI,72,[400]);fs=F(PFI,66,[400])
    im=T(im,[(548,464,'Intention',f,(150,196,255),'rs'),(1052,464,'Why',f,(130,236,206),'rs'),(768,972,'Resources',f,(255,214,140),'rs'),
             (609,684,'Does this fit?',F(PFI,56,[400]),(255,255,255),'ms')],blur=0.4)
    # 4. right column rows lower
    im=wipe(im,(1135,225,1800,925),thr=5,dil=4)
    im=move_text(src,im,(1135,225,1800,925),22,thr=8)
    wr(im,'n20-why.jpg')

def vfill(im,box,k=6,sx=4):
    x0,y0,x1,y1=box;T_=im[y0-k:y0,x0:x1].astype(np.float32).mean(0);B_=im[y1:y1+k,x0:x1].astype(np.float32).mean(0)
    T_=cv2.GaussianBlur(T_[None],(0,0),sx)[0];B_=cv2.GaussianBlur(B_[None],(0,0),sx)[0]
    u=np.linspace(0,1,y1-y0)[:,None,None];reg=T_[None]*(1-u)+B_[None]*u
    reg+=np.random.default_rng(3).normal(0,0.7,reg.shape[:2])[...,None]
    im[y0:y1,x0:x1]=np.clip(reg,0,255).astype(np.uint8);return im

# ================= slide 10 : plate/diet slide must match the script -> remove "Zero alcohol on training days" =================
if want('10'):
    im=rd('n10-plate.jpg');im=vfill(im,(100,838,820,945),k=6,sx=8);wr(im,'n10-plate.jpg')

# ================= slide 15 : stress slide, link to our landing page where "Let's do three together." used to be =================
if want('15'):
    im=rd('n15-stress.jpg')
    f=F(PFI,29,[400])
    im=T(im,[(1120,951,'longevitylifeacademy.com/store/longevity-blueprint',f,(138,184,255),'ls')],blur=0.4);wr(im,'n15-stress.jpg')

# ================= slide 14 : option 2 Movement week -> small "V2" label on top =================
if want('14'):
    im=rd('n14-movement-week.jpg');H,W=im.shape[:2]
    S=4;lay=Image.new('RGBA',(W*S//4,H*S//4),(0,0,0,0))   # draw pill at 1x with PIL supersampled via a big temp
    x0,y0,x1,y1=700,60,800,112
    tmp=Image.new('RGBA',((x1-x0)*4,(y1-y0)*4),(0,0,0,0));d=ImageDraw.Draw(tmp)
    d.rounded_rectangle((0,0,tmp.width-1,tmp.height-1),radius=(y1-y0)*2,fill=(8,21,45,235),outline=(138,210,255,255),width=6)
    fnt=F(OUTFIT,34*4,[600]);d.text((tmp.width/2,tmp.height/2+3),'V2',font=fnt,fill=(138,210,255,255),anchor='mm')
    tmp=tmp.resize((x1-x0,y1-y0),Image.LANCZOS);a=np.array(tmp).astype(np.float32);al=a[...,3:]/255
    reg=im[y0:y1,x0:x1].astype(np.float32);im[y0:y1,x0:x1]=np.clip(reg*(1-al)+a[...,:3][...,::-1]*al,0,255).astype(np.uint8)
    wr(im,'n14-movement-week.jpg')
