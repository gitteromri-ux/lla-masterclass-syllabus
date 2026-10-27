# V46 round 4: (1) remove baked slide counters from every slide, (2) add 4 slides (risks, Blue Zones, creme brulee, fork),
# (3) Blue Zones text moved clear of the logo. Run once after copying the new JPGs into assets/ (see commit). Then build-logo.py 22 23 24 25.
import cv2,numpy as np,glob,sys
def wipe(im,box,thr=40,dil=4):
    x0,y0,x1,y1=box;sub=im[y0:y1,x0:x1];bg=cv2.medianBlur(sub,61).astype(int)
    m=((np.abs(sub.astype(int)-bg).max(2))>thr).astype(np.uint8)*255;m=cv2.dilate(m,np.ones((2*dil+1,2*dil+1),np.uint8))
    full=np.zeros(im.shape[:2],np.uint8);full[y0:y1,x0:x1]=m
    return cv2.inpaint(im,full,5,cv2.INPAINT_TELEA)
STD=(1722,982,1842,1032)
BOX={'n15':(1722,1022,1842,1058),'n17':(1722,1002,1842,1058),'n13':(1722,1004,1842,1052),'n22':(1690,984,1870,1036),'n23':(1690,984,1870,1036),'n21':(1722,982,1842,1032)}
for f in sorted(glob.glob('assets/n[0-2][0-9]-*.*')):
    k=f[7:10]
    if k in('n24','n25'):continue
    im=cv2.imread(f);im=wipe(im,BOX.get(k,STD),thr=45 if k in('n13','n15','n17','n05','n10','n19') else 30)
    cv2.imwrite(f,im,[cv2.IMWRITE_JPEG_QUALITY,95] if f.endswith('jpg') else [])
    print(f)

# Blue Zones: the intro paragraph (top right) moves 100 px lower so the larger logo has its own space
src=cv2.imread('../../deck-review/v13/dark-07.jpg');im=cv2.imread('assets/n23-bluezones.jpg')
box=(1170,95,1850,235);im=wipe(im,box,thr=25,dil=5)
x0,y0,x1,y1=box;sub=src[y0:y1,x0:x1];bg=cv2.medianBlur(sub,61).astype(int)
m=((np.abs(sub.astype(int)-bg).max(2))>8).astype(np.uint8)*255;m=cv2.dilate(m,np.ones((5,5),np.uint8))
a=cv2.GaussianBlur(m.astype(np.float32)/255,(0,0),1.0)[...,None];dy=100
reg=im[y0+dy:y1+dy,x0:x1].astype(np.float32);im[y0+dy:y1+dy,x0:x1]=np.clip(reg*(1-a)+sub.astype(np.float32)*a,0,255).astype(np.uint8)
cv2.imwrite('assets/n23-bluezones.jpg',im,[cv2.IMWRITE_JPEG_QUALITY,95])
