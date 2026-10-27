# V46 round 17 (Julie): slide 10 (n08-sleep.jpg): add '8 hour opportunity' directly under the 9 PM-5 AM bar, in the slide's small label style (Outfit, light blue-white). Nothing else changes.
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
OUT='assets/n08-sleep.jpg'
im=cv2.imread(OUT)
F='/usr/share/fonts/truetype/sand-box/google/Outfit/Outfit-VariableFont_wght.ttf'
S=4;size=24
f=ImageFont.truetype(F,size*S);f.set_variation_by_axes([400])
s='8 hour opportunity'
cx,top=1350,656          # centred under the pill (x 985-1718); text top ~24px below the pill glow
w=int(f.getlength(s))+8*S;h=40*S
lay=Image.new('L',(w,h),0);ImageDraw.Draw(lay).text((4*S,8*S),s,font=f,fill=255,anchor='ls' if False else 'la')
a=np.array(lay.resize((w//S,h//S),Image.LANCZOS)).astype(np.float32)/255
ys,xs=np.where(a>0.3);print('glyph bbox',xs.min(),ys.min(),xs.max(),ys.max(),'width',xs.max()-xs.min())
x0=int(cx-(xs.min()+xs.max())/2);y0=top-ys.min()
col=np.array([250,238,226],np.float32)  # BGR, matches the label colour (p95 of 'Wash · floss')
reg=im[y0:y0+a.shape[0],x0:x0+a.shape[1]].astype(np.float32)
im[y0:y0+a.shape[0],x0:x0+a.shape[1]]=np.clip(reg*(1-a[...,None])+col*a[...,None],0,255).astype(np.uint8)
cv2.imwrite(OUT,im,[cv2.IMWRITE_JPEG_QUALITY,95])
