# V46 round 16 (Omri): 'I'll sleep when I die' slide (n08-sleep.jpg): remove ONLY the blue text line 'TARGET WINDOW · 9 PM – 5 AM' under the sleep window; fill with the original background.
import cv2,numpy as np,subprocess
G='/workspace/lla-masterclass-syllabus'
src=cv2.imdecode(np.frombuffer(subprocess.check_output(['git','-C',G,'show','24511ff:slide-canvas/v46/assets/n08-sleep.jpg']),np.uint8),1)
H,W=src.shape[:2]
x0,y0,x1,y1=1090,650,1620,712                       # box around the blue line (measured: x~1119-1588, y~668-690)
pad=cv2.copyMakeBorder(src,60,60,60,60,cv2.BORDER_REFLECT)
sub=pad[y0:y1+120,x0:x1+120]
bg=cv2.medianBlur(sub,41).astype(int);d=np.abs(sub.astype(int)-bg).max(2)[60:-60,60:-60]
m=np.zeros((H,W),np.uint8);txt=(sub[60:-60,60:-60].max(2)>110)&(d>14)    # the line is bright cyan; the dark eye-mask edges behind it stay
m[y0:y1,x0:x1]=txt.astype(np.uint8)*255
m=cv2.dilate(m,np.ones((9,9),np.uint8))
print('masked px',int((m>0).sum()))
# fill: low-res inpaint (smooth, no streaks) + original fine grain, feathered into the untouched pixels
s4=3;sm=cv2.resize(src,(W//s4,H//s4),interpolation=cv2.INTER_AREA);mm=cv2.resize(m,(W//s4,H//s4),interpolation=cv2.INTER_NEAREST)
fill=cv2.inpaint(sm,mm,5,cv2.INPAINT_TELEA);fill=cv2.GaussianBlur(fill,(0,0),1.2);fill=cv2.resize(fill,(W,H),interpolation=cv2.INTER_CUBIC).astype(np.float32)
rng=np.random.RandomState(5);fill+=rng.randn(H,W,1).astype(np.float32)*1.5
a=cv2.GaussianBlur(m.astype(np.float32)/255,(0,0),2.0)[...,None]
out=(src.astype(np.float32)*(1-a)+fill*a)
cv2.imwrite('assets/n08-sleep.jpg',np.clip(out,0,255).astype(np.uint8),[cv2.IMWRITE_JPEG_QUALITY,95])
cv2.imwrite('/workspace/sl_new.png',np.clip(out,0,255).astype(np.uint8))
