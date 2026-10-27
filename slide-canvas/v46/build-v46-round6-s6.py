# slide 6 (n05-icing): remove the smeared/doubled logo area and place ONE clean logo (same size/position as every slide).
import cv2,numpy as np
im=cv2.imread('/workspace/r5/n05_before6.jpg')           # = assets/n05-icing.jpg at ef65643
L=cv2.imread('../closers/img/lla-logo.png',cv2.IMREAD_UNCHANGED);LW,LX,LY=340,1526,28
h=round(LW*L.shape[0]/L.shape[1]);print('logo h',h,'bottom',LY+h)
rng=np.random.default_rng(7)
EDGE=133   # top edge of the glass chart panel
def fill(y0,y1,x0,x1,refL,refR=None):
    L_=im[y0:y1,refL[0]:refL[1]].astype(np.float32).mean(1)
    R_=im[y0:y1,refR[0]:refR[1]].astype(np.float32).mean(1) if refR else L_
    t=np.linspace(0,1,x1-x0)[None,:,None]
    blk=L_[:,None,:]*(1-t)+R_[:,None,:]*t+rng.normal(0,0.9,(y1-y0,x1-x0,1))
    return np.clip(blk,0,255)
PR=1850   # right end of the glass panel's top edge
a=fill(0,EDGE-1,1496,1884,(1470,1494),(1890,1912));im[0:EDGE-1,1496:1884]=a.astype(np.uint8)
b=fill(EDGE+2,LY+h+6,1496,PR,(1470,1494));ramp=np.ones(PR-1496,np.float32);ramp[-28:]=np.linspace(1,0,28)
o_=im[EDGE+2:LY+h+6,1496:PR].astype(np.float32);im[EDGE+2:LY+h+6,1496:PR]=(b*ramp[None,:,None]+o_*(1-ramp[None,:,None])).astype(np.uint8)
edge=im[EDGE-1:EDGE+2,1470:1494].astype(np.float32).mean(1)
im[EDGE-1:EDGE+2,1496:PR-28]=np.repeat(edge[:,None,:],PR-28-1496,1).astype(np.uint8)
lg=cv2.resize(L,(LW,h),interpolation=cv2.INTER_AREA);al=lg[:,:,3:].astype(np.float32)/255
im[LY:LY+h,LX:LX+LW]=(lg[:,:,:3]*al+im[LY:LY+h,LX:LX+LW]*(1-al)).astype(np.uint8)
cv2.imwrite('assets/n05-icing.jpg',im,[cv2.IMWRITE_JPEG_QUALITY,95])
cv2.imwrite('/workspace/r5/n05_zoom_b.png',cv2.resize(im[0:330,1380:1920],None,fx=2,fy=2,interpolation=cv2.INTER_CUBIC))
