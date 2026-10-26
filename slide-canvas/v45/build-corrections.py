from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=Path(__file__).parent/'assets'
OUT.mkdir(exist_ok=True)
FONTS=ROOT.parent/'backup-deck/fonts'
def font(n,italic=False):
    return ImageFont.truetype(str(FONTS/('PlayfairDisplay-Italic.ttf' if italic else 'Inter.ttf')),n)

im=Image.open(ROOT/'images-logo/github-deck2-dark-01.jpg').convert('RGB').resize((1430,804),Image.Resampling.LANCZOS)
d=ImageDraw.Draw(im)
text='This is not medical advice. Please talk to your doctor.'
d.text((im.width/2,665),text,font=font(27),fill='#F3EBDD',anchor='mt')
im.save(OUT/'title.jpg',quality=96)

src=Image.open(ROOT/'images-logo/claude-b-07.jpg').convert('RGB').resize((1430,804),Image.Resampling.LANCZOS)
im=Image.new('RGB',src.size)
d=ImageDraw.Draw(im)
for y in range(im.height):
    t=y/im.height
    d.line((0,y,im.width,y),fill=(int(7+5*t),int(18+7*t),int(43+10*t)))
lower=src.crop((0,285,src.width,src.height))
lower=lower.resize((1315,477),Image.Resampling.LANCZOS)
im.paste(lower,(57,320))
d.text((82,30),"I'll sleep when I die.",font=font(83,True),fill='#F3EBDD')
d.text((88,144),'Said the person aging at twice the normal speed.',font=font(36),fill='#9AD8EF')
d.text((88,230),'Sleep is the repair shift.',font=font(46,True),fill='#F3EBDD')
im.save(OUT/'sleep.jpg',quality=96)

im=Image.open(ROOT/'images-logo/claude-b-14.jpg').convert('RGB').resize((1430,804),Image.Resampling.LANCZOS)
d=ImageDraw.Draw(im)
d.rounded_rectangle((821,668,1382,727),radius=10,fill='#08152D')
d.text((844,680),'longevitylifeacademy.com',font=font(32),fill='#8AD2FF')
d.line((844,719,1282,719),fill='#8AD2FF',width=1)
im.save(OUT/'stress.jpg',quality=96)
