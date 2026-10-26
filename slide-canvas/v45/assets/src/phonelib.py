from PIL import Image,ImageDraw,ImageFilter,ImageChops
def brand(pil):
    im=pil.copy()
    mask=Image.new('L',im.size,0);ImageDraw.Draw(mask).polygon([(1114,181),(1246,187),(1245,233),(1113,228)],fill=255)
    mask=mask.filter(ImageFilter.GaussianBlur(1.5))
    im=Image.composite(Image.new('RGB',im.size,(17,62,105)),im,mask)
    logo=pil.crop((1104,23,1250,74))
    # make logo transparent: alpha from luminance over its dark bg
    L=logo.convert('L');bgv=min(L.getdata())
    a=L.point(lambda v:max(0,min(255,int((v-bgv-22)*2.6))))
    rgba=logo.copy();rgba.putalpha(a)
    s=124/rgba.width;rgba=rgba.resize((124,round(rgba.height*s)),Image.LANCZOS).rotate(-2.5,resample=Image.BICUBIC,expand=True)
    im.paste(rgba,(1117,184),rgba)
    return im
