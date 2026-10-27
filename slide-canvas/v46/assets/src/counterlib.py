import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
INTER='/workspace/lla-masterclass-syllabus/backup-deck/fonts/Inter.ttf'
OUTFIT='/usr/share/fonts/truetype/sand-box/google/Outfit/Outfit-VariableFont_wght.ttf'
def textmask(img,box,d=28,pad=4):
    x0,y0,x1,y1=box;X0,Y0,X1,Y1=max(0,x0-20),max(0,y0-20),min(img.shape[1],x1+20),min(img.shape[0],y1+20)
    g=cv2.cvtColor(img[Y0:Y1,X0:X1],cv2.COLOR_BGR2GRAY).astype(int)
    bg=cv2.medianBlur(g.astype(np.uint8),31).astype(int)
    m=np.zeros(img.shape[:2],np.uint8)
    sub=((g-bg)>d).astype(np.uint8)*255
    m[Y0:Y1,X0:X1]=sub;keep=np.zeros_like(m);keep[y0-pad:y1+pad,x0-pad:x1+pad]=1;m*=keep
    return cv2.dilate(m,np.ones((5,5),np.uint8))
def color_of(img,mask):
    px=img[mask>0].reshape(-1,3).astype(int);lum=px.sum(1)
    top=px[lum>=np.percentile(lum,85)];return tuple(int(v) for v in top.mean(0)[::-1])
def ink_bbox(img,box,d=28):
    x0,y0,x1,y1=box;X0,Y0=x0-20,y0-20
    g=cv2.cvtColor(img[Y0:y1+20,X0:x1+20],cv2.COLOR_BGR2GRAY).astype(int)
    bg=cv2.medianBlur(g.astype(np.uint8),31).astype(int);s=((g-bg)>d)
    s[:y0-Y0]=0;s[y1-Y0:]=0;s[:,:x0-X0]=0;s[:,x1-X0:]=0
    ys,xs=np.nonzero(s);return xs.min()+X0,ys.min()+Y0,xs.max()+X0+1,ys.max()+Y0+1
def draw_tracked(d,xy,txt,font,fill,track):
    x,y=xy
    for ch in txt:
        d.text((x,y),ch,font=font,fill=fill);x+=font.getlength(ch)+track
def tw(txt,font,track):return sum(font.getlength(c) for c in txt)+track*(len(txt)-1)
def replace(img,box,old,new,fontpath=INTER,align='right',wght=None,d=28,color=None,bbox=None):
    """box loose region around old text. returns new img (BGR)"""
    bx=bbox or ink_bbox(img,box,d);m=textmask(img,box,d)
    col=color or color_of(img,m)
    img=cv2.inpaint(img,m,4,cv2.INPAINT_TELEA)
    h=bx[3]-bx[1]
    # fit font size so that digit height of '0' == h
    for size in np.arange(6,80,0.25):
        f=ImageFont.truetype(fontpath,int(round(size)) if False else size)
        if wght: 
            try:f.set_variation_by_axes([wght])
            except Exception:pass
        bb=f.getbbox(old);
        if bb[3]-bb[1]>=h:break
    track=((bx[2]-bx[0])-(f.getbbox(old)[2]-f.getbbox(old)[0]))/(len(old)-1) if len(old)>1 else 0
    # recompute natural width with per-char metric
    natural=tw(old,f,0)-f.getbbox(old[0])[0]-(f.getlength(old[-1])-f.getbbox(old[-1])[2])
    track=((bx[2]-bx[0])-natural)/(len(old)-1)
    pil=Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB));dr=ImageDraw.Draw(pil)
    wn=tw(new,f,track)-f.getbbox(new[0])[0]-(f.getlength(new[-1])-f.getbbox(new[-1])[2])
    x=(bx[2]-wn if align=='right' else bx[0])-f.getbbox(new[0])[0]
    y=bx[3]-f.getbbox(old)[3]
    draw_tracked(dr,(x,y),new,f,col,track)
    return cv2.cvtColor(np.array(pil),cv2.COLOR_RGB2BGR),dict(bbox=bx,size=float(size),track=round(track,2),color=col)
