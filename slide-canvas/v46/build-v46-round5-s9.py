# slide 9 (n07-bridge): only the ICING stays dimmed; the cake layers show in full colour.
# Uses the clean (undimmed) cake of the sibling option image, registered to the dimmed one.
import cv2,numpy as np
R='/workspace/lla-masterclass-syllabus/slide-canvas/'
A=cv2.imread(R+'images/github-round-9-12.jpg');N=cv2.imread('/workspace/r5/n07_before.jpg')
M=np.load('/workspace/r5/M.npy')*1.5
W=cv2.warpAffine(A,M,(1920,1080),flags=cv2.INTER_CUBIC)
Ws=cv2.addWeighted(W,1.6,cv2.GaussianBlur(W,(0,0),2.2),-0.6,0)   # restore crispness lost by upscaling
hsv=cv2.cvtColor(W,cv2.COLOR_BGR2HSV);V=hsv[...,2]
box=np.zeros(V.shape,bool);box[130:870,185:900]=True
# cake silhouette (navy background: hue~105, sat>90, V<75)
H=hsv[...,0].astype(int);Sa=hsv[...,1].astype(int);Vi=V.astype(int)
navy=(H>=92)&(H<=118)&(Sa>85)&(Vi<80)
sil=((~navy)&box).astype(np.uint8)
sil=cv2.morphologyEx(sil,cv2.MORPH_OPEN,np.ones((7,7),np.uint8))
sil=cv2.morphologyEx(sil,cv2.MORPH_CLOSE,np.ones((21,21),np.uint8))
ff=sil.copy();h,w=ff.shape;msk=np.zeros((h+2,w+2),np.uint8);cv2.floodFill(ff,msk,(0,0),2)
sil=((ff!=2)).astype(np.uint8);sil=cv2.bitwise_and(sil,box.astype(np.uint8))
# icing = cream/white frosting: cap + drips. Horizontal filling bands (full colour) are excluded.
xx=np.arange(1920)[None,:]
white=(((Sa<80)|((xx>845)&(Sa<125)))&(Vi>125)&(H<=34)&box).astype(np.uint8)
cap_end=300; bands=[(350,394),(498,550),(620,688)]
wm=white.copy()
for y0,y1 in bands: wm[y0:y1]=0
# bridge drips across each band (columns white just above and just below)
for y0,y1 in bands:
    a_=wm[max(y0-3,0)]>0;b_=white[min(y1+4,1079)]>0
    cols=a_&b_
    wm[y0:y1,cols]=1
n,lab=cv2.connectedComponents(wm,connectivity=8)
white[640:]=0;seed=np.unique(lab[170:260,300:800]);seed=seed[seed>0]
icing=np.isin(lab,seed).astype(np.uint8)
icing=cv2.morphologyEx(icing,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
# fill small holes (shaded frosting / sprinkles) and the thin right-edge drip
inv=(1-icing).astype(np.uint8)
nn,lb,st,_=cv2.connectedComponentsWithStats(inv,connectivity=4)
for i in range(1,nn):
    if st[i,cv2.CC_STAT_AREA]<2500: icing[lb==i]=1
cl=cv2.morphologyEx(icing,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9)))
icing=cl
# cap rows (above the filling band): everything on the cake that is not the purple sponge showing between drips
P=((H>=118)&(H<=178)&(Sa>=14)&(Sa<=140)&(Vi>55)).astype(np.uint8)
P=cv2.morphologyEx(P,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
P=cv2.morphologyEx(P,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(17,17)))
P=cv2.dilate(P,np.ones((3,3),np.uint8))
cap=(sil.astype(bool)&~P.astype(bool)); cap[350:]=False; cap[:120]=False
cap=cv2.morphologyEx(cap.astype(np.uint8),cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
icing=icing|cap
icing=cv2.dilate(icing,np.ones((5,5),np.uint8))
# bottom rows: only the cake itself (pink sponge / cream), never the plate
bot=((Sa>30)&((H<=22)|(H>=165))|((Sa<80)&(Vi>125)&(H<=34))).astype(np.uint8)
bot=cv2.morphologyEx(bot,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
sil[800:]=sil[800:]&bot[800:]
cv2.imwrite('/workspace/r5/icing_mask.png',icing*255)
f=lambda m:cv2.GaussianBlur(m.astype(np.float32),(0,0),1.2)[...,None]
Ic=f(icing);Sil=f(sil)
Nf=N.astype(np.float32);Wf=Ws.astype(np.float32)
out=Nf.copy()
dimzone=np.zeros(V.shape,np.float32);dimzone[:,:]=0
ys=np.arange(1080);gz=np.interp(ys,[0,380,408,800,830,1080],[1,1,0,0,1,1]).astype(np.float32)  # 1 = dimmed rows
Z=gz[:,None,None]
# (1) non-icing cake pixels in the dimmed rows -> clean full colour
repl=Sil*(1-Ic)*Z
out=out*(1-repl)+Wf*repl
# (2) icing pixels in the bright rows (drips) -> dim like the rest of the icing
dim=Nf*0.21+np.array([6,4,2],np.float32)*0.0
dimm=Ic*(1-Z)
out=out*(1-dimm)+dim*dimm
cv2.imwrite('assets/n07-bridge.jpg',np.clip(out,0,255).astype(np.uint8),[cv2.IMWRITE_JPEG_QUALITY,95])
