# V46: small cake icon, top-left of each pillar slide. Cake pixels are cropped from the V46 cake slide itself (n04, untouched),
# so the layer colours are exact; the discussed pillar's layer is lit in that pillar's text colour from the cake slide.
import cv2,numpy as np
S=4;IW=108;PAD=14                    # icon width at 1x, glow padding at 1x
cake=cv2.imread('/workspace/e46/n04_orig.jpg')   # untouched copy of assets/n04-cake.jpg
Y0,Y1,X0,X1=205,752,165,1015
crop=cake[Y0:Y1,X0:X1]
ch,cw=crop.shape[:2];w=IW*S;h=round(w*ch/cw)
c=cv2.resize(crop,(w,h),interpolation=cv2.INTER_AREA).astype(np.float32)
m=(crop.max(2)>14).astype(np.uint8);m[500:]=(crop[500:].max(2)>75).astype(np.uint8);m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((25,25),np.uint8))
n,l,st,_=cv2.connectedComponentsWithStats(m);k=1+np.argmax(st[1:,4]);m=(l==k).astype(np.float32)
m=cv2.resize(m,(w,h),interpolation=cv2.INTER_AREA);m=cv2.GaussianBlur(m,(0,0),1.5)
sc=h/ch
# layer rows on the V46 cake slide (full-res y) -> crop rows
BANDS={'icing':(214,352),'stress':(372,470),'movement':(488,590),'food':(598,684),'sleep':(684,722),'menopause':(722,752)}
COL={'icing':(236,150,160),'stress':(226,196,146),'movement':(170,196,124),'food':(104,140,214),'sleep':(244,236,220),'menopause':(226,184,166)}
def icon(name):
    y0,y1=[(v-Y0)*sc for v in BANDS[name]];rgb=np.array(COL[name][::-1],np.float32)
    yy=np.arange(h,dtype=np.float32)[:,None]
    band=np.clip(np.minimum(yy-y0,y1-yy)/6+0.5,0,1)*np.ones((1,w),np.float32)*(m>0.3)
    band=cv2.GaussianBlur(band,(0,0),2.0)
    g=cv2.cvtColor(c.astype(np.uint8),cv2.COLOR_BGR2GRAY).astype(np.float32)[...,None]
    dim=(c*0.50+g*0.10)                       # the rest of the cake: dim, slightly desaturated
    T={'icing':0.7,'sleep':0.85,'menopause':0.85}.get(name,0.30);lit=np.clip(c*(0.75 if name in('icing','sleep','menopause') else 1.30)+rgb*T,0,255)         # the pillar's layer: full colour, a touch brighter
    img=dim*(1-band[...,None])+lit*band[...,None]
    P=PAD*S;H2,W2=h+2*P,w+2*P
    canvas=np.zeros((H2,W2,3),np.float32);canvas[P:P+h,P:P+w]=img
    al=np.zeros((H2,W2),np.float32);al[P:P+h,P:P+w]=m
    bm=np.zeros((H2,W2),np.float32);bm[P:P+h,P:P+w]=band
    glow=cv2.GaussianBlur(bm,(0,0),9)
    rim=np.clip(cv2.GaussianBlur(bm,(0,0),3)*1.4-0.15,0,1)
    gain=2.6 if name in('sleep','menopause') else 1.3
    gl=np.clip(glow*gain,0,1)[...,None]
    out=canvas*(1-gl*0.0)+rgb*gl*0.75
    out=np.where(al[...,None]>0.5,canvas+rgb*(gl*0.35),out)   # inside the cake only a gentle tint, outside a coloured halo
    a=np.clip(np.maximum(al,gl[...,0]*0.85),0,1)
    out=cv2.resize(out,(W2//S,H2//S),interpolation=cv2.INTER_AREA);a=cv2.resize(a,(W2//S,H2//S),interpolation=cv2.INTER_AREA)
    return np.clip(out,0,255).astype(np.uint8),a
if __name__=='__main__':
    sheet=np.zeros((120,6*160,3),np.uint8)
    for i,nm in enumerate(BANDS):
        o,a=icon(nm);np.save('assets/icons/%s.npy'%nm,np.dstack([o,(a*255).astype(np.uint8)]))
        cv2.imwrite('assets/icons/%s.png'%nm,np.dstack([o,(a*255).astype(np.uint8)]))
        tile=np.zeros((120,160,3),np.uint8);tile[:,:]=(40,22,10);hh,ww=a.shape
        tile[5:5+hh,5:5+ww]=(o*a[...,None]+tile[5:5+hh,5:5+ww]*(1-a[...,None])).astype(np.uint8);sheet[:,i*160:(i+1)*160]=tile
    cv2.imwrite('/workspace/e46/icons_sheet_c3.png',cv2.resize(sheet,None,fx=2,fy=2,interpolation=cv2.INTER_CUBIC))

def place(name,slide,x=12,y=6,clear=None):
    ic=cv2.imread('assets/icons/%s.png'%name,cv2.IMREAD_UNCHANGED);im=cv2.imread('assets/'+slide)
    if clear:   # slides that already carry a baked corner cake: flatten it first
        x0,y0,x1,y1=clear;ring=np.concatenate([im[y0-6:y0,x0:x1].reshape(-1,3),im[y1:y1+6,x0:x1].reshape(-1,3)]);im[y0:y1,x0:x1]=np.median(ring,0).astype(np.uint8)
    h,w=ic.shape[:2];a=ic[...,3:4].astype(np.float32)/255
    im[y:y+h,x:x+w]=np.clip(im[y:y+h,x:x+w]*(1-a)+ic[...,:3]*a,0,255).astype(np.uint8)
    cv2.imwrite('assets/'+slide,im,[cv2.IMWRITE_JPEG_QUALITY,95]);print(slide,name)
