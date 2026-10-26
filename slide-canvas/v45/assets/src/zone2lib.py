import cv2,numpy as np
def build(src_movement):
    im=cv2.imread(src_movement);x0,x1,y0,y1=960,1434,250,890
    orig=im[y0:y1,x0:x1].astype(float);H,W=orig.shape[:2]
    g=cv2.imread(''+__import__('os').path.dirname(__file__)+'/zone2-two-people.jpg');s=H/g.shape[0]
    g=cv2.resize(g,(round(g.shape[1]*s),H),interpolation=cv2.INTER_AREA);cx=(g.shape[1]-W)//2;g=g[:,cx:cx+W].astype(float)
    # estimate overlay from original: navy color & alpha per row using sky-free assumption -> fixed ramp
    navy=np.array([48,21,7],float) # BGR
    t=np.clip((np.arange(H)/H-0.50)/0.42,0,1);a=(t*t*(3-2*t))*0.93
    comp=g*(1-a[:,None,None])+navy*a[:,None,None]
    # text from original: bright text over dark region in caption zone
    gray=cv2.cvtColor(orig.astype(np.uint8),cv2.COLOR_BGR2GRAY).astype(int)
    bg=cv2.medianBlur(gray.astype(np.uint8),21).astype(int)
    m=((gray-bg)>25).astype(np.uint8);m[:430]=0
    m=cv2.dilate(m,np.ones((3,3),np.uint8)).astype(float);m=cv2.GaussianBlur(m,(3,3),0)
    out=comp*(1-m[...,None])+orig*m[...,None]
    im[y0:y1,x0:x1]=np.clip(out,0,255).astype(np.uint8)
    return im
