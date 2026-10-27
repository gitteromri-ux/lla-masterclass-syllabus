# slide 15 round 7: remove the faint cyan glow patch left of 'Heart and lungs' (leftover of the old diagonal's glow).
# Only x1548-1584, y503-556 is touched: the background there is rebuilt per column by vertical interpolation between the clean rows above and below; the white glyph pixels are kept.
import cv2,numpy as np
im=cv2.imread('/workspace/r5/n12_before7.jpg')
x0,y0,x1,y1=1548,503,1584,556
f=im.astype(np.float32);sub=f[y0:y1,x0:x1]
top=f[y0:y0+4,x0:x1].mean(0);bot=f[y1-4:y1,x0:x1].mean(0)           # clean rows above / below, per column
t=np.linspace(0,1,y1-y0)[:,None,None]
bg=top[None]*(1-t)+bot[None]*t
B,G,R=sub[...,0],sub[...,1],sub[...,2]
tint=np.clip(((G-R)-6)/14,0,1)                 # 0 = neutral background, 1 = cyan glow
core=np.clip((R-90)/50,0,1)                    # white glyph body
a=np.clip(tint*(1-core),0,1);a=cv2.GaussianBlur(a,(0,0),0.8)[...,None]
a=np.maximum(a,0)*(1-core[...,None])
out=f.copy();out[y0:y1,x0:x1]=sub*(1-a)+bg*a
# neutralise the cyan fringe on the glyph's own left edge (glow added to G/B only): R follows G, B capped
o=out[y0:y1,x0:x1];Rr,Gg,Bb=o[...,2].copy(),o[...,1].copy(),o[...,0].copy()
fr=(core>0)&((Gg-Rr)>6)&(np.arange(x0,x1)[None,:]<1578)
o[...,2]=np.where(fr,np.maximum(Rr,Gg),Rr);o[...,0]=np.where(fr,np.minimum(Bb,np.maximum(Gg,Rr)+8),Bb)
out=np.clip(out,0,255).astype(np.uint8)
cv2.imwrite('assets/n12-sameage.jpg',out,[cv2.IMWRITE_JPEG_QUALITY,95])
cv2.imwrite('/workspace/r5/p_new2.png',cv2.resize(out[495:565,1520:1620],None,fx=9,fy=9,interpolation=cv2.INTER_NEAREST))
# pass 2: remove the remaining 4-px light halo strip left of the 'H' stem (x1556-1565); the H's own top/bottom serifs (rows 520-522, 529-532) are kept
out=cv2.imread('assets/n12-sameage.jpg').astype(np.float32)
xa,xb,ya,yb=1554,1566,505,556
top=out[ya:ya+3,xa:xb].mean(0);bot=out[yb-3:yb,xa:xb].mean(0)
t=np.linspace(0,1,yb-ya)[:,None,None];bg=top[None]*(1-t)+bot[None]*t
m=np.ones((yb-ya,xb-xa),np.float32)
for r0,r1,xmin in [(520,523,1561),(529,533,1563)]:
    m[r0-ya:r1-ya,xmin-xa:]=0
Lc=out[ya:yb,xa:xb].max(2);m[Lc>=200]=0
m=cv2.GaussianBlur(m,(0,0),0.7)
# keep a soft hold on whatever is bright
m*=np.clip((220-Lc)/40,0,1)
out[ya:yb,xa:xb]=out[ya:yb,xa:xb]*(1-m[...,None])+bg*m[...,None]
cv2.imwrite('assets/n12-sameage.jpg',np.clip(out,0,255).astype(np.uint8),[cv2.IMWRITE_JPEG_QUALITY,95])
# pass 3: faint light speck just above the H's top serif (rows 511-519, x1562-1580)
out=cv2.imread('assets/n12-sameage.jpg').astype(np.float32)
xa,xb,ya,yb=1562,1582,504,522
top=out[ya:ya+4,xa:xb].mean(0);bg=np.repeat(top[None],yb-ya,0)
m=np.zeros((yb-ya,xb-xa),np.float32);m[7:15,:]=1;m=cv2.GaussianBlur(m,(0,0),1.5)*0.9
Lc=out[ya:yb,xa:xb].max(2);m*=np.clip((200-Lc)/40,0,1)
out[ya:yb,xa:xb]=out[ya:yb,xa:xb]*(1-m[...,None])+bg*m[...,None]
cv2.imwrite('assets/n12-sameage.jpg',np.clip(out,0,255).astype(np.uint8),[cv2.IMWRITE_JPEG_QUALITY,95])
