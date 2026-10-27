# slide 19 (n16-protocol) ROUND 8 - pinpoint changes on the round-5 base (/workspace/r5/n16_before6.jpg = n16 as committed in c12bece)
#  - timeline raised 22 px (smooth warp, as before)
#  - upper time+label items: all times on ONE level row (+20 px), every item centred on its tick; single-line labels sit on the second text row
#    so the last text line of every upper item ends at the same distance from the line
#  - lower items centred on their ticks ('Movement' / '& sauna' on two lines so 7:00 AM and 10:00 AM can both be centred)
#  - logical use of the deck palette for the times/labels (recolour of the existing glyphs only)
#  - bottom: the three 'backward' pills (+ italic note) lowered 14 px; ORDER OF OPERATIONS chunk moved 44 px right and 14 px down, hairline divider between the chunks
import sys,os,cv2,numpy as np
H=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,H+'/assets/src')
exec(open(H+'/build-v46-round5.py').read().split("want=lambda")[0].split("from editlib import *")[1])
src0=cv2.imread('/workspace/r5/n16_before6.jpg')
ORANGE=(240,163,94);CREAM=(243,235,221);LB=(138,210,255);DUSTY=(157,179,214);PALE=(214,222,236)
def recolor(img,box,rgb):
    x0,y0,x1,y1=box;sub=img[y0:y1,x0:x1].astype(np.float32);mn=sub.min(2)
    lo=np.percentile(mn,4);hi=np.percentile(mn,99.7)
    a=np.clip((mn-lo)/max(hi-lo,1),0,1)
    gray=sub.mean(2);hp=gray-cv2.GaussianBlur(gray,(0,0),4)
    near=cv2.dilate((hp>28).astype(np.uint8),cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9)))
    near=cv2.GaussianBlur(near.astype(np.float32),(0,0),1.0)
    a=a*near*np.clip((a-0.18)/0.3,0,1)       # only glyph pixels, never the bokeh around them
    core=a>0.85
    W=sub[core].mean(0) if core.sum()>3 else np.array([255,255,255],np.float32)
    col=np.array(rgb[::-1],np.float32)
    out=sub+a[...,None]*(col-W)[None,None]
    img[y0:y1,x0:x1]=np.clip(out,0,255).astype(np.uint8)
S=src0.copy()
# ---- palette (time, label)
UP=[('5AM',(105,330),-53,ORANGE,CREAM,20,20),('8AM',(350,595),-13,ORANGE,CREAM,20,20),('11AM',(715,1005),0,ORANGE,CREAM,20,20),
    ('4PM',(1085,1315),0,ORANGE,CREAM,20,57),('6PM',(1335,1585),-3,ORANGE,CREAM,20,57),('9PM',(1640,1865),7,DUSTY,DUSTY,20,57)]
for n,(xa,xb),dx,ct,cl,dt,dl in UP:
    recolor(S,(xa,368,xb,421),ct);recolor(S,(xa,421,xb,505),cl)
LOW=[('7AM',(215,470),ORANGE,CREAM),('10AM',(500,760),CREAM,PALE),('1PM',(860,1065),LB,PALE),('8PM',(1560,1765),DUSTY,DUSTY)]
for n,(xa,xb),ct,cl in LOW:
    recolor(S,(xa,700,xb,748),ct);recolor(S,(xa,748,xb,795),cl)
for (xa,xb),c in [((143,364),DUSTY),((477,750),ORANGE),((869,1146),ORANGE)]:recolor(S,(xa,904,xb,932),c)   # pill texts
for (xa,xb),c in [((1214,1290),DUSTY),((1366,1438),ORANGE),((1513,1660),LB),((1736,1822),CREAM)]:recolor(S,(xa,890,xb,925),c)   # order-of-operations words (dots left alone)
# ---- timeline warp
UPW=22
h,w=S.shape[:2];ys=np.arange(h,dtype=np.float32)
ramp=lambda y,a,b:np.clip((y-a)/(b-a),0,1)
wt=ramp(ys,506,550)*(1-ramp(ys,658,702));wt=wt*wt*(3-2*wt)
mapy=np.repeat((ys+UPW*wt)[:,None].astype(np.float32),w,1);mapx=np.repeat(np.arange(w,dtype=np.float32)[None,:],h,0)
im=cv2.remap(S,mapx,mapy,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
# ---- items: (box, dx, dy, k,thr,dil)
items=[]
for n,(xa,xb),dx,ct,cl,dt,dl in UP:
    if n=='5AM':   # this item was left-aligned in the original: centre each of its three lines on the tick (x=160)
        items+=[((xa,368,xb,421),dx+9,dt),((xa,421,xb,455),dx,dl),((xa,455,xb,505),dx+9,dl)];continue
    items+= [((xa,368,xb,421),dx,dt),((xa,421,xb,505),dx,dl)]
items+=[((215,700,470,748),20,0),((215,748,358,790),73,0),((358,748,470,790),-52,37),
        ((500,700,760,748),-66,0),((500,748,760,795),-66,0),((860,700,1065,748),-4,0),((860,748,1065,795),-4,0)]
masks=[]
for box,dx,dy in items:
    a,bg=lift(S,im,box,dy,k=101,thr=26,dil=9,inp=True);masks.append(a)
def put2(srcimg,dst,box,dx,dy,a):
    x0,y0,x1,y1=box;sub=srcimg[y0:y1,x0:x1].astype(np.float32)
    reg=dst[y0+dy:y1+dy,x0+dx:x1+dx].astype(np.float32);dst[y0+dy:y1+dy,x0+dx:x1+dx]=np.clip(reg*(1-a)+sub*a,0,255).astype(np.uint8)
# bottom area
bot=[((100,872,1182,1010),0,14,(121,17,9)),((1180,832,1870,868),44,0,(121,17,9)),((1180,872,1870,935),44,14,(121,17,9))]
bmasks=[]
for box,dx,dy,(k,thr,dil) in bot:
    a,bg=lift(S,im,box,dy,k=k,thr=thr,dil=dil,inp=True);bmasks.append(a)
for (box,dx,dy),a in zip(items,masks):put2(S,im,box,dx,dy,a)
for (box,dx,dy,_),a in zip(bot,bmasks):put2(S,im,box,dx,dy,a)
# ---- hairline divider between the two bottom chunks (same dusty blue as the headings, soft)
x=1199;lay=np.zeros((h,w),np.float32);lay[846:958,x]=1.0
lay=np.maximum(lay,0)*0.42;lay=cv2.GaussianBlur(lay,(0,0),0.6)
fade=np.ones(h,np.float32);fade[846:870]=np.linspace(0,1,24);fade[934:958]=np.linspace(1,0,24);lay*=fade[:,None]
col=np.array(DUSTY[::-1],np.float32);f=im.astype(np.float32)
im=np.clip(f*(1-lay[...,None])+col*lay[...,None],0,255).astype(np.uint8)
cv2.imwrite('assets/n16-protocol.jpg',im,[cv2.IMWRITE_JPEG_QUALITY,95])
cv2.imwrite('/workspace/r5/n16_r8a.png',im[340:1060,0:1920])
