# slide 19 (n16-protocol) [round 7: single-line labels bottom-aligned with the two-line ones]: timeline raised 22 px (smooth vertical warp, no seams), upper time texts lowered 20 px
# -> line-to-upper-text gap == line-to-lower-text gap (100 px each, measured from the line centre)
import sys,os,cv2,numpy as np
H=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,H+'/assets/src')
exec(open(H+'/build-v46-round5.py').read().split("want=lambda")[0].split("from editlib import *")[1])
src=cv2.imread('/workspace/r5/n16_before6.jpg')
UP=22;DN=20
h,w=src.shape[:2];ys=np.arange(h,dtype=np.float32)
ramp=lambda y,a,b:np.clip((y-a)/(b-a),0,1)
wt=ramp(ys,506,550)*(1-ramp(ys,658,702));wt=wt*wt*(3-2*wt)
sy=(ys+UP*wt).astype(np.float32)
mapy=np.repeat(sy[:,None],w,1);mapx=np.repeat(np.arange(w,dtype=np.float32)[None,:],h,0)
warped=cv2.remap(src,mapx,mapy,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
im=warped.copy()
# upper labels: two-line items move down DN; the single-line items (Dinner, Kitchen closes, Lights out) move DN + one text line (37 px) so every label ends at the same distance from the line
LINE=37
for box,dy in [((100,368,1040,505),DN),((1040,368,1880,505),DN+LINE)]:
    a,bg=lift(src,im,box,dy,k=101,thr=26,dil=9);put(src,im,box,dy,a)
cv2.imwrite('assets/n16-protocol.jpg',im,[cv2.IMWRITE_JPEG_QUALITY,95])
