# V46 script-conflict fixes. Run LAST: build-numbers.py -> build-fixes.py -> build-logo.py -> build-v46-edits.py
# Edits only the exact words/numbers listed; text is re-rendered with matched font, size, colour and position.
import sys,os,cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,'assets/src')
from editlib import erase,erase_color,fill_interp,extract,paste
A='assets/';SRC=os.environ.get('V46_SRC',A)  # SRC lets us re-run from pre-edit copies while developing
INTER='../../backup-deck/fonts/Inter.ttf'
OUTFIT='/usr/share/fonts/truetype/sand-box/google/Outfit/Outfit-VariableFont_wght.ttf'
PFI='../../backup-deck/fonts/PlayfairDisplay-Italic.ttf'
PFR='../../backup-deck/fonts/PlayfairDisplay.ttf'
def rd(n):return cv2.imread(SRC+n)
def wr(im,n):
    cv2.imwrite(A+n,im,[cv2.IMWRITE_JPEG_QUALITY,95] if n.endswith('jpg') else [])
def F(path,size,axes=None):
    f=ImageFont.truetype(path,size)
    if axes:f.set_variation_by_axes(axes)
    return f
def T(im,items,blur=0.0):
    """items: (x,y_baseline,text,font,(r,g,b),anchor) ; rendered on a layer, optional softening, composited"""
    H,W=im.shape[:2];lay=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(lay)
    for it in items:
        x,y,s,f,c,a=it[:6];ft=it[6] if len(it)>6 else None
        d.text((x,y),s,font=f,fill=tuple(c)+(255,),anchor=a,features=ft)
    L=np.array(lay).astype(np.float32);al=L[...,3:]/255
    if blur>0:
        al=cv2.GaussianBlur(al,(0,0),blur)[...,None] if al.ndim==3 else cv2.GaussianBlur(al,(0,0),blur)
        al=al.reshape(H,W,1)
    rgb=L[...,:3][...,::-1]
    return np.clip(im.astype(np.float32)*(1-al)+rgb*al,0,255).astype(np.uint8)
def vfill(im,box,k=6,sx=4):
    # smooth backgrounds: rebuild a rectangle by interpolating each column between the rows just above and below it
    x0,y0,x1,y1=box;T_=im[y0-k:y0,x0:x1].astype(np.float32).mean(0);B_=im[y1:y1+k,x0:x1].astype(np.float32).mean(0)
    T_=cv2.GaussianBlur(T_[None],(0,0),sx)[0];B_=cv2.GaussianBlur(B_[None],(0,0),sx)[0]
    u=np.linspace(0,1,y1-y0)[:,None,None];reg=T_[None]*(1-u)+B_[None]*u
    reg+=np.random.default_rng(3).normal(0,0.7,reg.shape[:2])[...,None]
    im[y0:y1,x0:x1]=np.clip(reg,0,255).astype(np.uint8);return im
def base_for(f,s,top):  # baseline y so that text bbox top lands on `top`
    return top-f.getbbox(s,anchor='ls')[1]
def want(k):return len(sys.argv)<2 or k in sys.argv[1:]

# ---- 4. slide 1: remove "2023", use the script's "second place" wording
if want('1'):
    im=rd('n01-title.jpg');im=vfill(im,(150,748,1770,848))
    f=F(INTER,32.2,[14,350]);col=(150,163,182)
    l1='Took second place a few years ago. Structural engineer. Twenty-five years as the scientist and the';l2='experiment.'
    b1=base_for(F(INTER,32.2,[14,350]),'Second slowest ager in the world, 2023. Structural engineer. Twenty-five years as the scientist and the',756)
    b2=base_for(f,'experiment.',805)
    im=T(im,[(960,b1,l1,f,col,'ms'),(960,b2,l2,f,col,'ms')],blur=0.7);wr(im,'n01-title.jpg')

# ---- 2. slide 2: "Dementia. Alzheimer's. Parkinson's." -> script: vascular dementia (dad), Parkinson's (mom); same 3-line block
if want('2'):
    im=rd('n02-why.jpg');im=vfill(im,(100,484,470,700),k=8,sx=6)
    f=F(PFI,61.5,[400]);col=(222,233,255)
    im=T(im,[(120,542,'Vascular',f,col,'ls'),(120,615,'dementia.',f,col,'ls'),(120,689,'Parkinson’s.',f,col,'ls')],blur=0.0);wr(im,'n02-why.jpg')

def shift_paste(im,box,dx,d=14):
    """copy the glyph pixels in box (matched against local background) to a spot dx px to the right (sub-pixel ok)"""
    p,a=extract(im,box,d=d);M=np.float32([[1,0,dx],[0,1,0]]);x0,y0,x1,y1=box;w=x1-x0+int(np.ceil(abs(dx)))+2
    pp=cv2.warpAffine(np.pad(p,((0,0),(0,w-(x1-x0)),(0,0)),mode='edge'),M,(w,y1-y0),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
    aa=cv2.warpAffine(np.pad(a,((0,0),(0,w-(x1-x0)))),M,(w,y1-y0),flags=cv2.INTER_CUBIC)
    return paste(im,pp,aa,(x0,y0))

# ---- 3. slide 3: "I age about six." -> "I age about 6.5."  and source "(Duke, 2025)" -> "(Duke, 2022)"
if want('3'):
    im=rd('n03-dunedin.jpg')
    f=F(PFI,80,[400]);x6=120+f.getlength('I age about ')
    im=vfill(im,(int(x6)-8,376,650,474),k=5,sx=4)
    im=T(im,[(x6+7,446,'6.5.',f,(252,254,255),'ls',['lnum'])],blur=0.9)
    # last digit of the year: clone the preceding "2" over the "5"
    im=vfill(im,(654,1040,672,1068),k=3,sx=2);im=shift_paste(im,(639,1038,655,1070),16.5)
    wr(im,'n03-dunedin.jpg')

def bubble_clone(im,src_c,dst_c,core=37.5,Rg=96,Rb=(100,112)):
    """copy a glowing bubble: opaque core + radial glow profile measured on the source (label side excluded), added to the new local background"""
    sx,sy=map(int,src_c);dx,dy=map(int,dst_c);E=Rb[1]+2
    P=im[sy-E:sy+E+1,sx-E:sx+E+1].astype(np.float32);yy,xx=np.mgrid[-E:E+1,-E:E+1];r=np.hypot(xx,yy);ang=np.degrees(np.arctan2(yy,xx))
    ok=np.abs(ang)>40  # exclude the label side (right)
    def ringmean(A,r0,r1):
        m=(r>=r0)&(r<r1)&ok;return np.median(A[m],0)
    bgS=ringmean(P,*Rb)
    prof=np.zeros((Rg+1,3),np.float32)
    for k in range(int(core),Rg+1):
        prof[k]=ringmean(P,k,k+1)-bgS
    Q=im[dy-E:dy+E+1,dx-E:dx+E+1].astype(np.float32);bgD=ringmean(Q,*Rb)
    # glow only where the destination ring is background-like: apply as additive profile
    g=np.zeros_like(Q);ri=np.clip(r.astype(int),0,Rg);gm=(r>=core-1)&(r<=Rg);g[gm]=prof[ri[gm]]
    # keep destination's own background texture, add glow; core copied opaque
    out=Q+g
    a=np.clip((core-r)/1.5+0.5,0,1)[...,None];out=out*(1-a)+P*a
    im[dy-E:dy+E+1,dx-E:dx+E+1]=np.clip(out,0,255).astype(np.uint8);return im

# ---- 8a. slide 5: add hyperbaric oxygen (same amber bubble + label style as NAD drips / Stem cells)
if False:  # slide 5 hyperbaric bubble reverted (Omri 05:48); n05 stays pristine
    im=rd('n05-icing.jpg');im=bubble_clone(im,(1229,661),(1450,497))
    f=F(INTER,31,[14,400]);im=T(im,[(1507,508,'Hyperbaric oxygen',f,(250,254,255),'ls')],blur=0.0);wr(im,'n05-icing.jpg')

# ---- 5. slide 11: "every diet agrees on." -> "every doctor agrees on."
if want('11'):
    im=rd('n11-sugar.jpg');im=vfill(im,(655,152,1500,262),k=6,sx=6)
    f=F(PFI,90,[400]);ox=668-f.getbbox('every',anchor='ls')[0]-2
    im=T(im,[(ox,238,'every doctor agrees on.',f,(147,207,250),'ls')],blur=0.0);wr(im,'n11-sugar.jpg')

# ---- 11. slide 13: order grip -> steps -> balance; drop the wrong "Mayo Clinic, 2024" from the balance claim (script gives no source)
if want('13'):
    im=rd('n13-movement.jpg')
    B1=(90,910,640,1010);B2=(690,910,1240,1010)
    p1,a1=extract(im,B1,d=24);p2,a2=extract(im,B2,d=24)
    for b in (B1,B2):
        im=erase_color(im,b,d=10);im=erase_color(im,b,d=6)
    im=paste(im,p1,a1,(B1[0]+600,B1[1]));im=paste(im,p2,a2,(B2[0]-600,B2[1]))
    im=vfill(im,(1741,980,1812,1008),k=3,sx=2)      # "Mayo"
    im=vfill(im,(1290,1009,1415,1046),k=3,sx=2)     # "Clinic, 2024"
    wr(im,'n13-movement.jpg')

# ---- 1. slide 19: "for ten years" -> "for over twenty-five years" (re-wrapped to keep clear of the cake photo)
if want('19'):
    im=rd('n19-cake.jpg');im=vfill(im,(100,660,930,720),k=5,sx=6)
    f=F(INTER,39,[14,360]);col=(236,245,255);top=669
    b2=base_for(f,'for ten years. Three questions did.',top);pitch=57
    im=T(im,[(120,b2,'for over twenty-five years.',f,col,'ls'),(120,b2+pitch,'Three questions did.',f,col,'ls')],blur=0.7);wr(im,'n19-cake.jpg')

COL20=(206,215,230);X20=1159
# ---- 9. slide 20: "Time, energy, money, relationships" -> "Time, money, and relationships"
if want('20'):
    im=rd('n20-why.jpg');im=vfill(im,(1150,772,1790,818),k=5,sx=6)
    f=F(OUTFIT,34,[300]);col=COL20
    im=T(im,[(X20,base_for(f,'Time, energy, money, relationships, the',780)-2,'Time, money, and relationships, the',f,col,'ls',['-liga','-calt','-dlig'])],blur=0.6);wr(im,'n20-why.jpg')

# ---- 10. slide 21: the three actions become the script's three actions
def wipe_text(im,box,thr=95,dil=4):
    x0,y0,x1,y1=box;sub=im[y0:y1,x0:x1];bg=cv2.medianBlur(sub,61).astype(int)
    m=((np.abs(sub.astype(int)-bg).max(2))>5).astype(np.uint8)*255;m=cv2.dilate(m,np.ones((2*dil+1,2*dil+1),np.uint8))
    full=np.zeros(im.shape[:2],np.uint8);full[y0:y1,x0:x1]=m
    return cv2.inpaint(im,full,5,cv2.INPAINT_TELEA)
if want('21'):
    im=rd('n21-takeaway.png')
    for b in ((1392,300,1868,426),(1374,440,1868,580),(1356,590,1868,728)):im=wipe_text(im,b)
    S=F(INTER,25.2,[14,340]);sc=(189,214,233)
    def blk(x,dot_y,ss,olds):
        o=[]
        for k,s_ in enumerate(ss):o.append((x,dot_y+9+36*k,s_,S,sc,'ls'))
        return o
    it=[]
    it+=blk(1400,325,['Track your sleep, monitor','your glucose, or sign up for','our Academy class.'],0)      # moon
    it+=blk(1380,465,['Commit to a 5-minute','movement break.'],0)                                      # kettlebell
    it+=blk(1362,614,['Add one green vegetable','to dinner.'],0)                                         # glucose sensor (closest art)
    im=T(im,it,blur=0.0);wr(im,'n21-takeaway.png')

# ---- 8b. slide 18: add "Nicotinamide riboside" as the FIRST item of card 3 (card grows by one list row = 44 px)
if want('18'):
    im=rd('n18-testing.jpg');ys=558;D=44;x0b,x1b=1262,1816;yb=884
    out=im.copy().astype(np.float32);src=im.astype(np.float32)
    w=np.ones(x1b-x0b,np.float32);rp=np.linspace(0,1,14);w[:14]=rp;w[-14:]=rp[::-1]
    blk=src[ys:yb,x0b:x1b];dst=slice(ys+D,yb+D)
    out[dst,x0b:x1b]=out[dst,x0b:x1b]*(1-w[None,:,None])+blk*w[None,:,None]
    out=np.clip(out,0,255).astype(np.uint8)
    out=vfill(out,(x0b,ys,x1b,ys+D),k=4,sx=0.8)
    f=F(INTER,28,[14,350]);b=base_for(f,'Vitamin D3 + K2',574)
    out=T(out,[(1317,b,'Nicotinamide riboside',f,(253,248,255),'ls')],blur=0.5);wr(out,'n18-testing.jpg')

# ---- 12. slide 16: "Midday" -> "11:00 AM"; add the 4:00 PM dinner stop (dot + label) between 1:00 PM and 6:00 PM
def add_dot(im,cx,cy,r,col,halo=0.30,hs=7):
    H,W=im.shape[:2];yy,xx=np.mgrid[0:H,0:W].astype(np.float32);d=np.hypot(xx-cx,yy-cy)
    core=np.clip(r+0.5-d,0,1)[...,None]
    hl=(halo*np.exp(-np.clip(d-r,0,None)/hs)*(d>r-1))[...,None]
    c=np.array(col[::-1],np.float32)[None,None];o=im.astype(np.float32)
    o=o*(1-hl)+c*hl;o=o*(1-core)+c*core
    return np.clip(o,0,255).astype(np.uint8)
if want('16'):
    im=rd('n16-protocol.jpg')
    im=vfill(im,(796,468,926,512),k=5,sx=3)
    PT=F(PFR,34,[530]);OS=F(OUTFIT,25.5,[410]);wh=(253,254,254);gr=(224,231,252)
    im=add_dot(im,1200,631.5,17.7,(47,155,254))
    im=T(im,[(860,500,'11:00 AM',PT,wh,'ms'),(1200,500,'4:00 PM',PT,wh,'ms'),(1200,535,'Dinner',OS,gr,'ms')],blur=0.5);wr(im,'n16-protocol.jpg')

# ---- 6/7. slide 14: the script's week (no sauna) + the "twice as effective as a 30-minute workout" claim
def rr_mask(h,w,r,inf=0):
    m=np.zeros((h*4,w*4),np.uint8);cv2.rectangle(m,(0,0),(w*4-1,h*4-1),0,-1)
    cv2.rectangle(m,(r*4,0),(w*4-1-r*4,h*4-1),255,-1);cv2.rectangle(m,(0,r*4),(w*4-1,h*4-1-r*4),255,-1)
    for cx,cy in((r,r),(w-1-r,r),(r,h-1-r),(w-1-r,h-1-r)):cv2.circle(m,(cx*4+2,cy*4+2),r*4+2,255,-1)
    return cv2.resize(m,(w,h),interpolation=cv2.INTER_AREA).astype(np.float32)[...,None]/255
def tile_copy(dst,src,sx,sy,dx,dy,w=225,h=111,r=18):
    m=rr_mask(h,w,r);p=src[sy:sy+h,sx:sx+w].astype(np.float32);d=dst[dy:dy+h,dx:dx+w].astype(np.float32)
    dst[dy:dy+h,dx:dx+w]=np.clip(d*(1-m)+p*m,0,255).astype(np.uint8);return dst
def bg_restore(im,box,rad=12,blur=7):
    x0,y0,x1,y1=box;m=np.zeros(im.shape[:2],np.uint8);m[y0:y1,x0:x1]=255
    f=cv2.inpaint(im,m,rad,cv2.INPAINT_NS).astype(np.float32)
    g=f.copy();g[y0:y1,x0:x1]=cv2.GaussianBlur(f[y0:y1,x0:x1],(0,0),blur,borderType=cv2.BORDER_REPLICATE);f=g
    a=np.maximum(m.astype(np.float32)/255,cv2.GaussianBlur(cv2.dilate(m,np.ones((17,17),np.uint8)).astype(np.float32)/255,(0,0),4.0))[...,None]
    o=im.astype(np.float32)
    nz=np.random.default_rng(5).normal(0,1.0,im.shape[:2])[...,None]
    return np.clip(o*(1-a)+(f+nz)*a,0,255).astype(np.uint8)
if want('14'):
    P=rd('n14-movement-week.jpg');im=P.copy()
    COLX=[120,363,605,848,1090,1333];Y1=467;Y2=592;TW=225
    WH=(253,255,255);WS=(232,244,255);DB=(8,26,62);DS=(14,38,72);DT=(8,28,52);DTS=(18,44,66)
    TF=F(OUTFIT,27,[680]);SF=F(OUTFIT,27.4,[400])
    def sub(im,x0,y0,h,text,col,ext=0):   # redraw only the 2nd line of a tile
        im=vfill(im,(x0+14,y0+58,x0+TW-14,y0+h-12),k=2,sx=1.0)
        return T(im,[(x0+20,y0+82,text,SF,col,'ls')],blur=0.4)
    def both(im,x0,y0,h,t1,t2,c1,c2):
        im=vfill(im,(x0+14,y0+22,x0+TW-14,y0+h-12),k=6,sx=1.0)
        return T(im,[(x0+20,y0+49,t1,TF,c1,'ls'),(x0+20,y0+82,t2,SF,c2,'ls')],blur=0.4)
    # sauna / mobility / balance tiles out (rebuild the dark photo background behind them)
    for x0,h in ((COLX[0],78),(COLX[1],78),(COLX[3],78),(COLX[5],111)):
        im=bg_restore(im,(x0-8,Y2-6,x0+TW+8,Y2+h+8))
    # row 1
    im=tile_copy(im,P,COLX[1],Y1,COLX[0],Y1)                      # Mon: VO2 max (the existing VO2 tile)
    im=tile_copy(im,P,COLX[0],Y1,COLX[1],Y1)                      # Tue: Weights tile
    im=sub(im,COLX[1],Y1,111,'lower body',WS)
    im=sub(im,COLX[2],Y1,111,'upper body',WS)                     # Wed
    im=tile_copy(im,P,COLX[0],Y1,COLX[3],Y1)                      # Thu: Weights tile
    im=sub(im,COLX[3],Y1,111,'lower body',WS)
    im=sub(im,COLX[4],Y1,111,'upper body',WS)                     # Fri
    im=both(im,COLX[5],Y1,111,'Hike or walk','with a friend',DT,DTS)   # Sat
    # row 2: Zone 2 or HIIT cardio on Wed and Fri (the existing teal Zone 2 tile)
    for x0 in (COLX[2],COLX[4]):
        im=tile_copy(im,P,COLX[3],Y1,x0,Y2)
        im=both(im,x0,Y2,111,'Zone 2 or HIIT','cardio',DT,DTS)
    # claim line
    im=vfill(im,(110,830,1120,935),k=6,sx=6)
    NF=F(PFR,96,[400]);CF=F(OUTFIT,30,[300])
    nb=918;nw=NF.getlength('Twice')
    im=T(im,[(125-NF.getbbox('T',anchor='ls')[0],nb,'Twice',NF,(198,244,254),'ls'),
             (125+NF.getbbox('Twice',anchor='ls')[2]+22-CF.getbbox('a',anchor='ls')[0],892,'as effective as a 30-minute workout: short movement breaks',CF,(220,232,249),'ls')],blur=0.5)
    wr(im,'n14-movement-week.jpg')
