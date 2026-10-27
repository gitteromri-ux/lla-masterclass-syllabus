# V45-only: renumber baked-in slide counters/tags to the V45 Play order (21 slides) and apply approved fixes.
import sys,os,cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
H=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,H+'/assets/src')
from counterlib import replace,INTER,OUTFIT,textmask,draw_tracked,tw
from phonelib import brand
from zone2lib import build as zone2
S=os.path.dirname(H)+'/';A=H+'/assets/'
def rd(p):return cv2.imread(S+p)
def save(img,name):
    p=A+name;cv2.imwrite(p,img,[cv2.IMWRITE_JPEG_QUALITY,95] if name.endswith('jpg') else []);print('wrote',name)
log={}
def C(img,box,old,new,**k):
    img,info=replace(img,box,old,new,**k);log.setdefault('last',[]).append(info);return img,info
T='21'
from counterlib import ink_bbox
_b=ink_bbox(rd('images-logo/github-r4-v1-05.jpg'),(1722,986,1828,1014));B5=(_b[0],_b[1],_b[2],_b[1]+25);print('B5',B5)
# 1 title
im,i1=C(rd('v46/assets/title.jpg'),(1290,733,1362,758),'00 / 16','01 / 21');save(im,'n01-title.jpg')
im,_=C(rd('images-logo/added-why-light.jpg'),(1733,988,1828,1023),'02 / 17','02 / 21');save(im,'n02-why.jpg')
im,_=C(rd('images-logo/github-r7-last-06.jpg'),(1150,658,1221,685),'03 / 17','03 / 21');save(im,'n03-dunedin.jpg')
im,_=C(rd('images-logo/github-deck2-dark-04.jpg'),(1445,821,1523,848),'03 / 16','04 / 21');save(im,'n04-cake.jpg')
im,_=C(rd('images-logo/github-r4-v1-05.jpg'),(1722,988,1828,1018),'05 / 17','05 / 21',bbox=B5);save(im,'n05-icing.jpg')
im,_=C(rd('images-logo/github-round-9-11.jpg'),(1151,658,1221,685),'06 / 17','06 / 21');save(im,'n06-menopause.jpg')
im,_=C(rd('images-logo/github-round-10-12.jpg'),(1151,657,1221,684),'06 / 17','07 / 21');save(im,'n07-bridge.jpg')
# 8 sleep: add counter in slide-1 style/position (same canvas size)
pil=Image.open(A+'sleep.jpg').convert('RGB');d=ImageDraw.Draw(pil);f=ImageFont.truetype(INTER,i1['size'])
txt='08 / 21';bx=i1['bbox'];w=tw(txt,f,i1['track'])-f.getbbox(txt[0])[0]-(f.getlength(txt[-1])-f.getbbox(txt[-1])[2])
draw_tracked(d,(bx[2]-w-f.getbbox(txt[0])[0],bx[3]-f.getbbox('01 / 21')[3]),txt,f,i1['color'],i1['track'])
save(cv2.cvtColor(np.array(pil),cv2.COLOR_RGB2BGR),'n08-sleep.jpg')
# 9 = claude-b-09 tag already '09' (unchanged)
im,_=C(rd('v46/assets/food-plate.jpg'),(1150,658,1222,686),'09 / 17','10 / 21');save(im,'n10-plate.jpg')
im,_=C(rd('images-logo/github-r6-v2-10.jpg'),(1736,988,1828,1023),'10 / 17','11 / 21');save(im,'n11-sugar.jpg')
im,_=C(rd('images/claude-a-11.jpg'),(1762,991,1853,1017),'11 / 17','12 / 21');save(im,'n12-sameage.jpg')
im=zone2(A+'movement.jpg');im,_=C(im,(1761,91,1853,112),'12 / 17','13 / 21');save(im,'n13-movement.jpg')
im,_=C(rd('images/claude-b-13.jpg'),(148,72,185,97),'13','14',fontpath=OUTFIT,align='right',wght=500);save(im,'n14-movement-week.jpg')
# 15 stress from original source: remove "Let's do three together." (no link), renumber tag
im=rd('images-logo/claude-b-14.jpg');m=textmask(im,(1108,915,1498,962),d=20);im=cv2.inpaint(im,m,5,cv2.INPAINT_TELEA)
im,_=C(im,(147,70,187,98),'14','15',fontpath=OUTFIT,align='right',wght=500);save(im,'n15-stress.jpg')
im,_=C(rd('images/claude-b-15.jpg'),(148,72,185,97),'15','16',fontpath=OUTFIT,align='right',wght=500);save(im,'n16-protocol.jpg')
# 17 notebook: LLA phone branding, remove counter from phone reflection, redraw left of the phone
pil=brand(Image.open(A+'src/notebook-phone-base.jpg').convert('RGB'));im=cv2.cvtColor(np.array(pil),cv2.COLOR_RGB2BGR)
ref=rd('images-logo/github-round-9-11.jpg');_,r=replace(ref,(1151,658,1221,685),'06 / 17','06 / 21')
m=textmask(im,(1156,656,1221,687),d=18);im=cv2.inpaint(im,m,4,cv2.INPAINT_TELEA)
pil=Image.fromarray(cv2.cvtColor(im,cv2.COLOR_BGR2RGB));d=ImageDraw.Draw(pil);f=ImageFont.truetype(INTER,r['size']);txt='17 / 21'
w=tw(txt,f,r['track'])-f.getbbox(txt[0])[0]-(f.getlength(txt[-1])-f.getbbox(txt[-1])[2]);right=1060
draw_tracked(d,(right-w-f.getbbox(txt[0])[0],r['bbox'][3]-f.getbbox(txt)[3]),txt,f,r['color'],r['track'])
save(cv2.cvtColor(np.array(pil),cv2.COLOR_RGB2BGR),'n17-notebook.jpg')
im,_=C(rd('v46/assets/testing.jpg'),(106,50,139,74),'16','18',fontpath=OUTFIT,align='right',wght=500);save(im,'n18-testing.jpg')
im,_=C(rd('images-logo/github-round-9-27.jpg'),(1155,657,1221,684),'16 / 17','19 / 21');save(im,'n19-cake.jpg')
im,_=C(rd('images-logo/github-deck1-dark-17.jpg'),(1743,981,1826,1011),'17 / 17','20 / 21');save(im,'n20-why.jpg')
im=rd('julie/additional-take-action-20261026.png')
im,_=C(im,(105,60,151,89),'26','21',align='right');im,_=C(im,(1744,1022,1827,1052),'26 / 27','21 / 21');save(im,'n21-takeaway.png')
for x in log['last']:print(x)
