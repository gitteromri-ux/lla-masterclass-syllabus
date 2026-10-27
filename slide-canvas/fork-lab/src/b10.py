import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
R=cv2.imread('new.png').astype(np.float32);H,W=R.shape[:2]
B=cv2.imread('base.png').astype(np.float32);hf=B[560:700,1300:1460];hf=hf-cv2.GaussianBlur(hf,(0,0),3)
hf2=np.concatenate([hf,hf[::-1]],0);hf2=np.concatenate([hf2,hf2[:,::-1]],1);tile=np.tile(hf2,(H//280+1,W//320+1,1))[:H,:W]
sub=R[838:965,1380:1905];m=((sub.max(2)-sub.min(2)>40)|(sub.mean(2)>130)).astype(np.uint8)*255
M=np.zeros((H,W),np.uint8);M[838:965,1380:1905]=cv2.dilate(m,np.ones((7,7),np.uint8))
inp=cv2.inpaint(np.clip(R,0,255).astype(np.uint8),M,9,cv2.INPAINT_TELEA).astype(np.float32)+tile*0.8
mf=cv2.GaussianBlur(M.astype(np.float32)/255,(0,0),1.5)[...,None];R=R*(1-mf)+inp*mf
F='/usr/share/fonts/truetype/sand-box/google/Inter/Inter-VariableFont_opsz,wght.ttf'
l1='Building your guided protocol in 18 weeks';a='with ';b='Longevity Life Academy.'
def f(s):
  ft=ImageFont.truetype(F,s);
  try: ft.set_variation_by_axes([32,400])
  except Exception: pass
  return ft
s=32
while f(s).getlength(l1)>1860-1387: s-=0.5
ft=f(s);print('size',s,f(32).getlength(l1))
im=Image.fromarray(cv2.cvtColor(np.clip(R,0,255).astype(np.uint8),cv2.COLOR_BGR2RGB));d=ImageDraw.Draw(im)
asc=ft.getbbox('B')[1];y1=847-asc;y2=y1+41
d.text((1387,y1),l1,font=ft,fill=(242,242,242));d.text((1387,y2),a,font=ft,fill=(242,242,242))
d.text((1387+ft.getlength(a),y2),b,font=ft,fill=(158,230,255))
o=cv2.cvtColor(np.array(im),cv2.COLOR_RGB2BGR);cv2.imwrite('new.png',o);cv2.imwrite('z34.png',o[720:1080,820:1920])
