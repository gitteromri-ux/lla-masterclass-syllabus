# V45-only polish pass. Run after build-numbers.py (it rewrites the n*.jpg files that this script edits).
import sys,os,cv2,numpy as np
H=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,H+'/assets/src')
from editlib import *
from counterlib import replace,OUTFIT
A=H+'/assets/';S=os.path.dirname(H)+'/'
def rd(n):return cv2.imread(A+n)
def wr(img,n):cv2.imwrite(A+n,img,[cv2.IMWRITE_JPEG_QUALITY,95] if n.endswith('jpg') else []);print('fixed',n)
only=sys.argv[1:]
def want(k):return not only or k in only
if want('1'):
    im=rd('n01-title.jpg');im=erase_color(im,(995,728,1366,762),d=8);im=erase_color(im,(995,728,1366,762),d=6);wr(std_counter(im,1),'n01-title.jpg')
if want('3'):
    im=rd('n03-dunedin.jpg')
    p,a=extract(im,(984,666,1086,694),d=24);im=erase_color(im,(984,666,1086,694),d=12)
    q,b=extract(im,(76,690,365,716),d=24);im=erase_color(im,(76,690,365,716),d=12)
    shift=100
    im=paste(im,q,b,(76+shift,690));im=paste(im,p,a,(984-(988-79),666+24));wr(im,'n03-dunedin.jpg')
if want('4'):
    im=rd('n04-cake.jpg');im=erase_color(im,(1120,818,1530,852),d=8);im=erase_color(im,(1120,818,1530,852),d=6);wr(std_counter(im,4),'n04-cake.jpg')
if want('5'):
    im=rd('n05-icing.jpg');im=erase(im,(1446,1012,1786,1044),d=22);im=erase(im,(112,1048,192,1080),d=22);wr(im,'n05-icing.jpg')
if want('8'):
    im=rd('n08-sleep.jpg');im=erase_color(im,(1288,730,1364,760),d=10)
    im=move(im,(104,690,262,772),0,22,d=16);wr(std_counter(im,8),'n08-sleep.jpg')
if want('14'):
    im=rd('n14-movement-week.jpg');wr(std_counter(im,14),'n14-movement-week.jpg')
if want('15'):
    im=rd('n15-stress.jpg');im=move(im,(74,931,140,1034),0,26,d=16);im=move(im,(140,946,292,1034),0,26,d=16);im=erase_color(im,(108,939,300,960),d=5,grow=5)
    x0,y0,x1,y1=150,944,340,962;L=im[y0:y1,x0-3:x0].astype(float).mean(1);R=im[y0:y1,x1:x1+3].astype(float).mean(1);t=np.linspace(0,1,x1-x0)[None,:,None]
    patch=L[:,None]*(1-t)+R[:,None]*t;w=np.minimum(1,np.minimum(np.arange(y1-y0),np.arange(y1-y0)[::-1])/3)[:,None,None]
    im[y0:y1,x0:x1]=(patch*w+im[y0:y1,x0:x1]*(1-w)).astype(np.uint8);wr(std_counter(im,15,bottom=1062),'n15-stress.jpg')
if want('16'):
    im=rd('n16-protocol.jpg')
    bx=(517,707,643,732);im=erase(im,(512,703,648,736),d=30)
    f=font(PF,40,500);# fit size to bbox height of '9:00 AM'
    for s in np.arange(20,60,0.25):
        f=font(PF,s,500);bb=f.getbbox('AM',anchor='ls')
        if bb[3]-bb[1]>=26:break
    col=(242,236,226)
    im=text(im,((bx[0]+bx[2])/2,733),'10:00 AM',f,col,anchor='ms')
    wr(std_counter(im,16),'n16-protocol.jpg')
if want('21'):
    im=rd('n21-takeaway.png');im=erase_color(im,(1740,1018,1832,1056),d=8);im=erase_color(im,(1740,1018,1832,1056),d=5);wr(std_counter(im,21),'n21-takeaway.png')
if want('20'):
    im=rd('n20-why.jpg');x0,y0,x1,y1=1360,978,1830,1012
    g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(int);sub=g[y0:y1,x0:x1]
    bright=cv2.dilate((sub>200).astype(np.uint8),np.ones((3,3),np.uint8))
    faint=cv2.dilate(((sub>26)&(bright==0)).astype(np.uint8),np.ones((2,2),np.uint8))*(1-bright)
    bgc=np.median(im[y0:y1,x0:x1][sub<40],axis=0)
    reg=im[y0:y1,x0:x1];reg[faint>0]=bgc;im[y0:y1,x0:x1]=reg
    im=erase_color(im,(1772,980,1826,1010),d=10)
    wr(std_counter(im,20,bottom=1066),'n20-why.jpg')
if want('18'):
    im=rd('n18-testing.jpg')
    def dotfix(im,gap,ymid,yr,col,dot=True):
        x0,x1=gap;m=np.zeros(im.shape[:2],np.uint8);m[yr[0]:yr[1],x0:x1]=255
        im=cv2.inpaint(im,m,3,cv2.INPAINT_TELEA)
        if dot:cv2.circle(im,(int((x0+x1)/2),ymid),2,tuple(int(c) for c in col),-1,cv2.LINE_AA)
        return im
    def colat(im,box):
        sub=im[box[1]:box[3],box[0]:box[2]].reshape(-1,3);l=sub.sum(1);return sub[l>=np.percentile(l,92)].mean(0)
    im=dotfix(im,(137,157),62,(51,72),colat(im,(112,55,134,70)))
    im=dotfix(im,(142,163),354,(340,364),colat(im,(121,347,140,361)))
    im=dotfix(im,(576,597),354,(340,364),colat(im,(552,347,574,361)))
    im=dotfix(im,(1009,1028),354,(340,364),colat(im,(983,347,1007,361)))
    im=dotfix(im,(1136,1145),354,(342,357),None,dot=False)
    # logo: remove dark box behind it, keep logo
    bx=(84,716,206,786);sub=im[bx[1]:bx[3],bx[0]:bx[2]].astype(float)
    boxbg=np.median(sub.reshape(-1,3),axis=0);diff=np.abs(sub-boxbg).max(2)
    a=np.clip((diff-10)*255/30,0,255).astype(np.uint8)
    fg=sub.copy()
    pad=8;X0,Y0,X1,Y1=bx[0]-pad,bx[1]-pad,bx[2]+pad,bx[3]+pad
    L=im[Y0:Y1,X0-4:X0].astype(float).mean(1);R=im[Y0:Y1,X1:X1+4].astype(float).mean(1)
    t=np.linspace(0,1,X1-X0)[None,:,None];T=im[Y0-4:Y0,X0:X1].astype(float).mean(0);B=im[Y1:Y1+4,X0:X1].astype(float).mean(0)
    u=np.linspace(0,1,Y1-Y0)[:,None,None];bgp=((L[:,None]*(1-t)+R[:,None]*t)+(T[None]*(1-u)+B[None]*u))/2
    im[Y0:Y1,X0:X1]=bgp.astype(np.uint8)
    # logo pixels: lighten relative to new bg, keep original logo tone
    reg=im[bx[1]:bx[3],bx[0]:bx[2]].astype(float);al=(a.astype(float)/255)[...,None]
    im[bx[1]:bx[3],bx[0]:bx[2]]=np.clip(fg*al+reg*(1-al),0,255).astype(np.uint8)
    # subtitle off the photo: deepen the dark fade behind the subtitle line ends
    g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY);x0,y0,x1,y1=900,196,1330,292
    txt=cv2.dilate((g[y0:y1,x0:x1]>165).astype(np.uint8),np.ones((3,3),np.uint8)).astype(float)
    xs=np.clip((np.arange(x1-x0)-0)/120,0,1);xs=np.minimum(xs,np.clip((x1-x0-np.arange(x1-x0))/110,0,1))
    ys=np.minimum(np.clip(np.arange(y1-y0)/18,0,1),np.clip((y1-y0-np.arange(y1-y0))/18,0,1))
    al=(ys[:,None]*xs[None,:]*0.82*(1-txt))[...,None];navy=np.array([60,22,10],float)
    im[y0:y1,x0:x1]=np.clip(im[y0:y1,x0:x1]*(1-al)+navy*al,0,255).astype(np.uint8)
    wr(std_counter(im,18),'n18-testing.jpg')
if want('9'):
    im=cv2.imread(S+'images/claude-b-09.jpg')
    g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    col=g[150:280,105:150]>150;ys=np.nonzero(col.any(1))[0];top=150+ys.min();base=150+ys.max()+1  # 'T' top & baseline
    for s in np.arange(40,140,0.5):
        f=font(PF,s,500);bb=f.getbbox('T',anchor='ls')
        if -bb[1]>=base-top:break
    im=erase(im,(100,150,1720,282),d=30,r=6)
    im=text(im,(105-f.getbbox('F',anchor='ls')[0],base),'Food.',f,(244,239,230),anchor='ls')
    # pill 4 wording to match the script: per pound of goal bodyweight
    old='1 g protein / lb lean mass';new='1 g protein / lb goal weight'
    px=(1076,845,1486,920);tb=(1110,869,1452,901)
    for s in np.arange(14,50,0.25):
        pf=font(PF,s,500);b=pf.getbbox(old)
        if b[2]-b[0]>=tb[2]-tb[0]:break
    sub=im[tb[1]:tb[3],tb[0]:tb[2]].reshape(-1,3);l=sub.sum(1);pcol=tuple(int(c) for c in sub[l>=np.percentile(l,90)].mean(0)[::-1])
    gg=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)[tb[1]:tb[3],tb[0]:tb[2]]
    rows=np.nonzero((gg>150).any(1))[0]
    im=erase(im,(tb[0]-4,tb[1]-4,tb[2]+4,tb[3]+4),d=30)
    while pf.getlength(new)>(px[2]-px[0])-66:pf=font(PF,pf.size-0.25,500)
    bl=tb[1]+(rows.max()+1 if False else 0)
    # baseline: bottom of 'n'/'m' letters ~ original baseline = bbox bottom minus descender of 'p'
    ob=font(PF,s,500).getbbox(old,anchor='ls');baseline=tb[3]-ob[3]
    im=text(im,((px[0]+px[2])/2,baseline),new,pf,pcol[::-1] if False else pcol,anchor='ms')
    wr(std_counter(im,9),'n09-food.jpg')
def colat(im,box,p=90):
    x0,y0,x1,y1=box;sub=im[y0:y1,x0:x1];g=cv2.cvtColor(sub,cv2.COLOR_BGR2GRAY).astype(int)
    bg=cv2.medianBlur(cv2.copyMakeBorder(g.astype(np.uint8),20,20,20,20,cv2.BORDER_REFLECT),31)[20:-20,20:-20].astype(int)
    m=(g-bg)>45;px=sub[m].astype(float);ch=px.max(1)-px.min(1)+px.sum(1)/6;c=np.median(px[ch>=np.percentile(ch,80)],axis=0);return (int(c[2]),int(c[1]),int(c[0]))
def para(im,lines,x,y,f,col,lh,anchor='la'):
    for i,l in enumerate(lines):im=text(im,(x,y+i*lh),l,f,col,anchor=anchor)
    return im
if want('12'):
    im=rd('n12-sameage.jpg')
    pc=(236,238,242)
    im=erase(im,(760,830,1262,958),d=30,r=5)
    f=font(ARIAL,21.5);t="years: the gap between how long Americans live and how long they live in good health. The widest in the world. Worldwide, 9.6. Mayo Clinic, 183 countries, December 2024"
    im=para(im,wrap(t,f,350),1005,838,f,pc,29.5,anchor='ma')
    labels=[((1555,424,1905,454),["Weights, mobility and balance"],428),((1555,555,1905,607),["VO2 max intervals","and Zone 2 walks"],556),((1555,684,1905,712),["Weights: squats,","push-ups, lunges"],688),((1555,814,1905,844),["Balance: thirty seconds","on one leg"],818)]
    fl=font(ARIAL,24)
    cols=[(233,166,90),(110,178,242),(137,224,255),(113,174,191)]  # measured from the original label glyphs
    for (bx,s,y),c in zip(labels,cols):
        im=erase(im,bx,d=22,r=4);im=erase(im,bx,d=10,r=4);im=para(im,s,1560,y,fl,c,29)
    # redraw the Heart-and-lungs connector (dot + diagonal) that crosses the Brain label, as in the original
    orig=cv2.imread(S+'images/claude-a-11.jpg');lc=tuple(int(v) for v in orig[441,1599]);
    cv2.line(im,(1599,441),(1583,477),lc,2,cv2.LINE_AA);cv2.circle(im,(1599,441),8,lc,-1,cv2.LINE_AA)
    im=erase(im,(1760,988,1852,1018),d=15)
    wr(std_counter(im,12),'n12-sameage.jpg')
if want('13'):
    im=rd('n13-movement.jpg')
    caps=[(0,"Muscles, bones and, increasingly, your brain. Compound lifts: squats, push-ups, lunges"),(480,"Heart and lungs. Hard intervals, then recovery. The sprint through the airport to make the connection"),(960,"Metabolic health and heart. Walking or hiking at a pace where you can still chat with a friend"),(1440,"Brain, joints and staying steady on your feet. The one most people forget, and the one that keeps you safe for the other three")]
    f=font(ARIAL,23)
    cols=[(222,168,104),(234,174,192),(140,223,255),(170,204,122)]  # measured from the original captions
    for (x0,s),c in zip(caps,cols):
        im=erase(im,(x0+14,749,x0+470,836),d=25,r=5)
        im=para(im,wrap(s,f,428),x0+22,752,f,c,31)
    im=erase(im,(1758,88,1856,116),d=12)
    wr(std_counter(im,13,bottom=1040),'n13-movement.jpg')
