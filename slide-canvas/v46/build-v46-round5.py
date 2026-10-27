# V46 round 5 (runs on the pre-round-5 assets saved in /workspace/r5/*_before.jpg): slide 16 text, slide 19 spacing, slide 23 text block.
import sys,os,cv2,numpy as np
H=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,H+'/assets/src')
from editlib import *
A=H+'/assets/';B='/workspace/r5/'
PFI='/usr/share/fonts/truetype/sand-box/google/Playfair Display/PlayfairDisplay-Italic-VariableFont_wght.ttf'
def para(im,lines,x,y,f,col,lh,anchor='la'):
    for i,l in enumerate(lines):im=text(im,(x,y+i*lh),l,f,col,anchor=anchor)
    return im
def wr(img,n):cv2.imwrite(A+n,img,[cv2.IMWRITE_JPEG_QUALITY,95]);print('wrote',n)
def smooth_bg(img,box,k):
    x0,y0,x1,y1=box;pad=k
    sub=cv2.copyMakeBorder(img,pad,pad,pad,pad,cv2.BORDER_REFLECT)[y0:y1+2*pad,x0:x1+2*pad]
    h,w=sub.shape[:2];s=4
    sm=cv2.resize(sub,(w//s,h//s),interpolation=cv2.INTER_AREA);sm=cv2.medianBlur(sm,max(3,(k//s)|1))
    sm=cv2.GaussianBlur(sm,(0,0),3)
    return cv2.resize(sm,(w,h),interpolation=cv2.INTER_CUBIC)[pad:pad+(y1-y0),pad:pad+(x1-x0)].astype(np.float32)
def elem_mask(img,box,k,thr,dil):
    x0,y0,x1,y1=box;sub=img[y0:y1,x0:x1].astype(np.float32);bg=smooth_bg(img,box,k)
    m=(np.abs(sub-bg).max(2)>thr).astype(np.uint8)*255
    m=cv2.dilate(m,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(dil,dil)))
    return cv2.GaussianBlur(m.astype(np.float32)/255,(0,0),2.0)[...,None],bg
def lift(src,dst,box,dy,k=101,thr=14,dil=9,erase_only=False,move=True,inp=False):
    """move the foreground elements inside box by dy: erase them from dst (replace by smooth bg) and paste at the new place."""
    x0,y0,x1,y1=box;a,bg=elem_mask(src,box,k,thr,dil)
    if inp:
        hm=(a[...,0]>0.15).astype(np.uint8)*255;full=np.zeros(src.shape[:2],np.uint8);full[y0:y1,x0:x1]=hm
        ip=cv2.inpaint(src,full,6,cv2.INPAINT_TELEA);bg=ip[y0:y1,x0:x1].astype(np.float32)
    reg=dst[y0:y1,x0:x1].astype(np.float32);dst[y0:y1,x0:x1]=np.clip(reg*(1-a)+bg*a,0,255).astype(np.uint8)
    return a,bg
def put(src,dst,box,dy,a):
    x0,y0,x1,y1=box;sub=src[y0:y1,x0:x1].astype(np.float32)
    reg=dst[y0+dy:y1+dy,x0:x1].astype(np.float32);dst[y0+dy:y1+dy,x0:x1]=np.clip(reg*(1-a)+sub*a,0,255).astype(np.uint8)
want=lambda k:len(sys.argv)<2 or k in sys.argv[1:]

if want('16'):   # slide 16: shorter paragraphs; bigger, more colourful bottom stats
    im=cv2.imread(B+'n13_before.jpg')
    caps=[(0,"Muscles, bones and your brain. Squats, push-ups, lunges."),(480,"Heart and lungs. Hard intervals, then recovery. The airport sprint."),(960,"Metabolic health and heart. Walking or hiking at a pace where you can still chat."),(1440,"Brain, joints and staying steady. The one most people forget, and the one that keeps the other three safe.")]
    f=font(ARIAL,23);cols=[(222,168,104),(234,174,192),(140,223,255),(170,204,122)]
    for (x0,s),c in zip(caps,cols):
        im=erase(im,(x0+14,749,x0+470,880),d=25,r=5)
        im=para(im,wrap(s,f,428),x0+22,752,f,c,31)
    # bottom stats
    im=erase(im,(70,895,1900,1025),d=14,r=6);im=erase_color(im,(70,895,1900,1025),d=6,r=6)
    tf=font(PFI,46,600);df=font(ARIAL,25)
    stats=[(96,"Grip strength",(255,196,102),"48 studies, three million people: the stronger the grip, the lower the risk of dying, almost in a straight line"),
           (702,"7,000 steps",(132,214,255),"a day, against 2,000: 47% lower risk of dying, 38% lower risk of dementia. The Lancet Public Health, 2025"),
           (1318,"30 seconds",(172,236,116),"on one leg. Of grip, knee strength, walking and balance, the one-leg stand fell fastest with age. Try it tonight.")]
    for x,t,c,dsc in stats:
        im=text(im,(x,944),t,tf,c)
        for i,l in enumerate(wrap(dsc,df,560)):im=text(im,(x,982+i*32),l,df,(236,242,252))
    wr(im,'n13-movement.jpg')

if want('19'):   # slide 19: no kicker, headline up, more room above the bottom rows
    src=cv2.imread(B+'n16_before.jpg');im=src.copy()
    groups=[('kick',(100,60,520,112),0,40,14,9,False),('head',(100,128,1010,352),-46,101,26,11,False),('top',(100,380,1860,540),-30,101,26,9,False),('botL',(100,788,1182,985),38,121,17,9,True),('botR',(1186,788,1870,915),38,121,17,9,True)]
    ms={}
    for n,box,dy,k,thr,dil,ip in groups:
        a,bg=lift(src,im,box,dy,k=k,thr=thr,dil=dil,inp=ip);ms[n]=a
    for n,box,dy,k,thr,dil,ip in groups:
        if dy:put(src,im,box,dy,ms[n])
    wr(im,'n16-protocol.jpg')

if want('23'):   # slide 23: right-hand text block lower, centred beside the Venn
    src=cv2.imread(B+'n20_before.jpg');im=src.copy()
    box=(1120,215,1920,962);a,bg=lift(src,im,box,64,k=71,thr=10,dil=11,inp=True);put(src,im,box,64,a)
    wr(im,'n20-why.jpg')
