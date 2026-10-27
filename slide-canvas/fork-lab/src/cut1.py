import sys
from rembg import remove,new_session
from PIL import Image
se=new_session('birefnet-general')
n=sys.argv[1];b=tuple(map(int,sys.argv[2:6]))
remove(Image.open('o.png').convert('RGB').crop(b),session=se).save('c_%s.png'%n)
