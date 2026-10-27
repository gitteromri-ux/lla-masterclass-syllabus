import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
from counterlib import textmask,INTER,tw,draw_tracked
PF='/usr/share/fonts/truetype/sand-box/google/Playfair Display/PlayfairDisplay-VariableFont_wght.ttf'
ARIAL='/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
def erase(img,box,d=28,r=4):
    m=textmask(img,box,d);return cv2.inpaint(img,m,r,cv2.INPAINT_TELEA)
def erase_color(img,box,d=14,r=5,grow=7):
    x0,y0,x1,y1=box;sub=cv2.copyMakeBorder(img,30,30,30,30,cv2.BORDER_REFLECT)[y0:y1+60,x0:x1+60];bg=cv2.medianBlur(sub,51).astype(float)
    diff=np.abs(sub.astype(float)-bg).max(2)[30:-30,30:-30]
    m=np.zeros(img.shape[:2],np.uint8);m[y0:y1,x0:x1]=cv2.dilate((diff>d).astype(np.uint8)*255,np.ones((grow,grow),np.uint8))
    return cv2.inpaint(img,m,r,cv2.INPAINT_TELEA)
def fill_interp(img,box,feather=6):
    x0,y0,x1,y1=box;out=img.copy().astype(float)
    L=img[y0:y1,x0-4:x0].astype(float).mean(1);R=img[y0:y1,x1:x1+4].astype(float).mean(1)
    t=np.linspace(0,1,x1-x0)[None,:,None];patch=L[:,None,:]*(1-t)+R[:,None,:]*t
    T=img[y0-4:y0,x0:x1].astype(float).mean(0);B=img[y1:y1+4,x0:x1].astype(float).mean(0)
    u=np.linspace(0,1,y1-y0)[:,None,None];vp=T[None]*(1-u)+B[None]*u
    out[y0:y1,x0:x1]=(patch+vp)/2
    return np.clip(cv2.GaussianBlur(out,(0,0),0.6) if False else out,0,255).astype(np.uint8)
def extract(img,box,d=20):
    """return (rgb patch, alpha) of foreground in box using local bg"""
    x0,y0,x1,y1=box;sub=cv2.copyMakeBorder(img,30,30,30,30,cv2.BORDER_REFLECT)[y0:y1+60,x0:x1+60]
    bg=cv2.medianBlur(sub,51).astype(float);diff=np.abs(sub.astype(float)-bg).max(2)
    a=np.clip((diff-d/2)*255/max(1,d),0,255).astype(np.uint8)[30:-30,30:-30]
    return img[y0:y1,x0:x1].copy(),a
def paste(img,patch,alpha,xy):
    x,y=xy;h,w=alpha.shape;a=(alpha.astype(float)/255)[...,None]
    reg=img[y:y+h,x:x+w].astype(float);img[y:y+h,x:x+w]=np.clip(patch*a+reg*(1-a),0,255).astype(np.uint8);return img
def move(img,box,dx,dy,d=20,mode='interp'):
    p,a=extract(img,box,d);x0,y0,x1,y1=box
    img=erase_color(img,box,d=max(6,d//2))
    return paste(img,p,a,(x0+dx,y0+dy))
def _full(img,box,a):
    m=np.zeros(img.shape[:2],np.uint8);x0,y0,x1,y1=box;m[y0:y1,x0:x1]=cv2.dilate((a>10).astype(np.uint8)*255,np.ones((5,5),np.uint8));return m
def font(path,size,w=None):
    f=ImageFont.truetype(path,size)
    if w:
        try:f.set_variation_by_axes([w])
        except Exception:pass
    return f
def text(img,xy,s,f,color,anchor='ls',track=0):
    pil=Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB));d=ImageDraw.Draw(pil)
    if track: 
        x,y=xy
        if anchor[0]=='r':x-=tw(s,f,track)
        if anchor[0]=='m':x-=tw(s,f,track)/2
        draw_tracked(d,(x,y-f.getmetrics()[0] if anchor[1]=='s' else y),s,f,color,track)
    else: d.text(xy,s,font=f,fill=color,anchor=anchor)
    return cv2.cvtColor(np.array(pil),cv2.COLOR_RGB2BGR)
def wrap(s,f,width):
    words=s.split();lines=[];cur=''
    for w in words:
        t=(cur+' '+w).strip()
        if f.getlength(t)<=width or not cur:cur=t
        else:lines.append(cur);cur=w
    lines.append(cur);return lines
STD=dict(size=28,color=(160,175,200),right=1820,bottom=1018,track=-1.16)
def std_counter(img,n,total=21,bottom=None,right=None):
    H,W=img.shape[:2];s=W/1920
    f=font(INTER,STD['size']*s);t=f'{n:02d} / {total}'
    b=(bottom if bottom is not None else STD['bottom'])*s;r=(right or STD['right'])*s
    pil=Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB));d=ImageDraw.Draw(pil);tr=STD['track']*s
    w=tw(t,f,tr)-f.getbbox(t[0])[0]-(f.getlength(t[-1])-f.getbbox(t[-1])[2])
    draw_tracked(d,(r-w-f.getbbox(t[0])[0],b-f.getbbox(t)[3]),t,f,STD['color'],tr)
    return cv2.cvtColor(np.array(pil),cv2.COLOR_RGB2BGR)
