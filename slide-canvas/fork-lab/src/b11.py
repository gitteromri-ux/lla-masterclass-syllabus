import cv2,numpy as np
R=cv2.imread('new.png').astype(np.float32);C=np.load('C.npy').astype(np.float32)
cx,cy,d=1242.0,313.0,80
Y,X=np.mgrid[:R.shape[0],:R.shape[1]];dist=np.hypot(X-cx,Y-cy)
fm=np.clip((d/2+14-dist)/5,0,1);fm=np.maximum(fm,((X>1262)&(X<1312)&(Y>258)&(Y<370)).astype(np.float32));fm=cv2.GaussianBlur(fm.astype(np.float32),(0,0),2)[...,None];R=R*(1-fm)+C*fm
G=cv2.imread('/cursor/stores/store-f39abc32-0760-4b19-bf30-568e546a4efa/grok-bot/agents/c61b0413-74f6-4b70-b321-85860153aec2/attachments/534a2777ecb6a2a8f2b99bb41961dab59c9ab928bab462d03527dc6f6f0e29ef.jpg').astype(np.float32)
D=90;s=D/(2*394.);g=cv2.resize(G[497-400:497+400,512-400:512+400],None,fx=s,fy=s,interpolation=cv2.INTER_LANCZOS4)
g=cv2.addWeighted(g,1.4,cv2.GaussianBlur(g,(0,0),1),-0.4,0)*np.array([0.86,0.84,0.82])
n=g.shape[0];yy,xx=np.mgrid[:n,:n];a=np.clip(394*s-np.hypot(xx-n/2,yy-n/2)+0.5,0,1)[...,None]
x0,y0=int(round(cx-n/2)),int(round(cy-n/2))
sh=cv2.GaussianBlur(np.clip(394*s+2-np.hypot(X-cx-4,Y-cy-6),0,1).astype(np.float32),(0,0),5)[...,None]*0.55;R=R*(1-sh)
R[y0:y0+n,x0:x0+n]=R[y0:y0+n,x0:x0+n]*(1-a)+g*a
o=np.clip(R,0,255).astype(np.uint8);cv2.imwrite('new.png',o)
cv2.imwrite('clock_zoom.png',cv2.resize(o[int(cy)-75:int(cy)+75,int(cx)-90:int(cx)+110],None,fx=4,fy=4,interpolation=cv2.INTER_NEAREST))
