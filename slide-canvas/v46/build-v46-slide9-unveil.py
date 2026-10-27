# builds the UN-VEILED photo base for slide 9 (x<1000): bg + sponge/stripe layers in true brightness, icing cap stays dark
import cv2,numpy as np
def build_U(N,R='/workspace/lla-masterclass-syllabus/slide-canvas/',MM='/workspace/r5/M.npy',ICE='/workspace/r5/icing_mask.png'):
    A=cv2.imread(R+'images/github-round-9-12.jpg');M=np.load(MM)*1.5
    W=cv2.warpAffine(A,M,(1920,1080),flags=cv2.INTER_CUBIC)
    Ws=cv2.addWeighted(W,1.6,cv2.GaussianBlur(W,(0,0),2.2),-0.6,0)
    hsv=cv2.cvtColor(W,cv2.COLOR_BGR2HSV);V=hsv[...,2]
    box=np.zeros(V.shape,bool);box[130:870,185:900]=True
    H=hsv[...,0].astype(int);Sa=hsv[...,1].astype(int);Vi=V.astype(int)
    navy=(H>=92)&(H<=118)&(Sa>85)&(Vi<80)
    sil=((~navy)&box).astype(np.uint8)
    sil=cv2.morphologyEx(sil,cv2.MORPH_OPEN,np.ones((7,7),np.uint8))
    sil=cv2.morphologyEx(sil,cv2.MORPH_CLOSE,np.ones((21,21),np.uint8))
    ff=sil.copy();h,w=ff.shape;msk=np.zeros((h+2,w+2),np.uint8);cv2.floodFill(ff,msk,(0,0),2)
    sil=((ff!=2)).astype(np.uint8);sil=cv2.bitwise_and(sil,box.astype(np.uint8))
    icing=(cv2.imread(ICE,0)>0).astype(np.uint8)
    # only real cap pixels of the dimmed photo count as icing (drops the veiled-background ring the mask picked up around the cap)
    Ns=N.astype(int).sum(2);capm=((icing>0)&(Ns>78)).astype(np.uint8);capm[420:]=icing[420:]
    capm[:100]=0;cl=cv2.morphologyEx(capm,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))
    ff2=cl.copy();m2=np.zeros((ff2.shape[0]+2,ff2.shape[1]+2),np.uint8);cv2.floodFill(ff2,m2,(0,0),2);cl=((ff2!=2)).astype(np.uint8)
    cl=cv2.morphologyEx(cl,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    icing=(icing&cl).astype(np.uint8);icing[420:]=(cv2.imread(ICE,0)[420:]>0)
    f=lambda m:cv2.GaussianBlur(m.astype(np.float32),(0,0),1.2)[...,None]
    Ic=f(icing);Sil=f(sil)
    ys=np.arange(1080)
    gz=np.interp(ys,[0,386,414,800,830,1080],[1,1,0,0,1,1]).astype(np.float32)
    # keep the bottom veil exactly as it was (only the top veil is removed)
    gz[500:]=0
    Zc=gz[:,None,None]
    zb=np.clip((420-ys)/34.0,0,1)*(lambda t:t*t*(3-2*t))(np.clip((ys-58)/80.0,0,1));zb[500:]=0
    Zb=zb[:,None,None].astype(np.float32)
    Nf=N.astype(np.float32);Wf=Ws.astype(np.float32);Wf[:500,:24]=Wf[:500,24:25]
    # cake (non-icing) pixels and background both come from the clean photo in the top rows
    wgt=Sil*(1-Ic)*Zc+(1-Sil)*Zb*1.0
    wgt=np.clip(wgt,0,1)
    U=Nf*(1-wgt)+Wf*wgt
    # bottom: stretch the abrupt bottom veil step into a long smooth fade (clean photo -> original dark base)
    wbv=np.interp(ys,[800,815,975],[0,1,0]).astype(np.float32)[:,None,None]*np.clip((1000-np.arange(1920))/60.0,0,1)[None,:,None]
    U=U*(1-wbv)+Wf*wbv
    # cap rim: smooth, feathered outer edge (cap tone over clean background); the interior keeps its real texture
    capb=(cl>0).astype(np.uint8);capb[420:]=0
    sil_d=cv2.dilate(sil,np.ones((7,7),np.uint8));sil_d[:100]=0
    ff3=(1-sil_d).astype(np.uint8);m3=np.zeros((ff3.shape[0]+2,ff3.shape[1]+2),np.uint8)
    out3=ff3.copy();cv2.floodFill(out3,m3,(0,0),2);outside=(out3==2).astype(np.uint8)
    near=(cv2.dilate(outside,np.ones((25,25),np.uint8))>0)&(outside==0)
    near&=(cv2.dilate(icing,np.ones((13,13),np.uint8))>0)
    near[:100]=False;near[400:]=False
    ell=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9))
    capsm=cv2.morphologyEx(cv2.morphologyEx(capb,cv2.MORPH_OPEN,ell),cv2.MORPH_CLOSE,ell).astype(np.float32)
    capsm=cv2.GaussianBlur(capsm,(0,0),2.2)[...,None]
    inside_core=(cv2.erode(capb,np.ones((15,15),np.uint8))>0).astype(np.float32)
    # local cap tone (normalised blur of the real cap pixels)
    w_=cv2.GaussianBlur(inside_core,(0,0),14);num=cv2.GaussianBlur(Nf*inside_core[...,None],(0,0),14)
    captone=num/np.maximum(w_[...,None],1e-3)
    ow=cv2.dilate(outside,np.ones((3,3),np.uint8)).astype(np.float32);num2=cv2.GaussianBlur(Wf*ow[...,None],(0,0),18);den2=cv2.GaussianBlur(ow,(0,0),18)
    Wbg=num2/np.maximum(den2[...,None],1e-3)
    rim=capsm*captone+(1-capsm)*Wbg
    nm=cv2.GaussianBlur(near.astype(np.float32),(0,0),1.5)[...,None]
    U=U*(1-nm)+rim*nm
    # right edge of the photo block: fade into the slide background so there is no vertical seam at x~1000
    tgt=cv2.GaussianBlur(Nf[:,1002:1022].mean(1)[:,None,:].astype(np.float32),(0,0),sigmaX=0.1,sigmaY=5)
    tx=np.arange(1920);tt=np.clip((tx-880)/120.0,0,1);tt=(tt*tt*(3-2*tt))[None,:,None]
    U=U*(1-tt)+tgt*tt
    return np.clip(U,0,255).astype(np.uint8)
if __name__=='__main__':
    N=cv2.imread('/workspace/A9.jpg');U=build_U(N);cv2.imwrite('/workspace/U9_e.png',U[:, :1000])
