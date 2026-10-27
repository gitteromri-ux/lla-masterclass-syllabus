# Builds The-Longevity-Masterclass-V46.pptx: the 25 final V46 slides, same order, each as a full-bleed 1920x1080 picture (exact design) with the slide number and title in the notes.
from pptx import Presentation
from pptx.util import Emu
import cv2,os
ORDER=[('n01-title.jpg','The Longevity Masterclass'),('n02-why.jpg','Why I went down this path'),('n03-dunedin.jpg','Ten years pass. By this test, I age about six. The speed towards death.'),
('n22-risks.jpg','The four risks.'),('n04-cake.jpg','Longevity is like a cake.'),('n05-icing.jpg','Not wrong. Not first.'),('n23-bluezones.jpg','The Blue Zones.'),
('n06-menopause.jpg','Menopause therapy is a layer, not icing.'),('n07-bridge.jpg','Four layers hold up the cake.'),('n08-sleep.jpg',"I'll sleep when I die."),
('n26-religion.jpg','Take the religion out of your diet.'),('n09-food.jpg','Food.'),('n10-plate.jpg','What does it look like in real life?'),('n11-sugar.jpg','The one thing every diet agrees on.'),('n24-brulee.jpg','Crème brûlée and wrinkles.'),
('n12-sameage.jpg','Same age.'),('n13-movement.jpg','Four types of movement, four parts of you.'),('n14-movement-week.jpg','Julie Gibson Clark’s Movement Week. (V2, Julie to update)'),
('n15-stress.jpg','The layer people skip.'),('n16-protocol.jpg',"Julie Gibson Clark's Longevity Protocol."),('n17-notebook.jpg',"You don't need a lab. You need a notebook."),
('n18-testing.jpg','Test. Then buy.'),('n19-cake.jpg',"That's the cake."),('n20-why.jpg','Why. Intention. Resources.'),('n25-fork.png','One takeaway. Take action. (closing, Julie slide 22 unchanged)')]
import docx,re
DOC='/cursor/stores/store-f39abc32-0760-4b19-bf30-568e546a4efa/grok-bot/agents/c61b0413-74f6-4b70-b321-85860153aec2/attachments/01M5XN1NF1BZ71TXPB6J5JQ1PP.docx'
PS=[p.text for p in docx.Document(DOC).paragraphs]
# paragraph ranges (inclusive) of the final script for each V46 slide; markers (NEW SLIDE, Slide n | ... headers) are not spoken and are dropped
RANGES=[[(1,7)],[(9,16)],[(18,28)],[(30,33)],[(35,42)],[(44,55)],[(57,62)],[(64,76)],[(78,78)],[(80,97)],[(99,104)],[(106,125)],[(127,134)],[(136,148)],[(150,155),(157,164)],[(166,180)],[(182,203)],[(214,228)],[(230,245)],[(247,272)],[(274,279)],[(281,288)],[(290,292)],[(294,308)],[(310,316)]]
def script(i):
    out=[]
    for a,z in RANGES[i]:
        for t in PS[a:z+1]:
            if t.strip():out.append(t.strip())
    return '\n\n'.join(out)
prs=Presentation();prs.slide_width=Emu(12192000);prs.slide_height=Emu(6858000)
os.makedirs('/tmp/pp',exist_ok=True)
for i,(f,t) in enumerate(ORDER,1):
    p='assets/'+f
    if f.endswith('png') and f!='n25-fork.png':
        cv2.imwrite('/tmp/pp/%s.jpg'%f,cv2.imread(p),[cv2.IMWRITE_JPEG_QUALITY,93]);p='/tmp/pp/%s.jpg'%f
    s=prs.slides.add_slide(prs.slide_layouts[6])
    s.shapes.add_picture(p,0,0,prs.slide_width,prs.slide_height)
    s.notes_slide.notes_text_frame.text=script(i-1)
prs.save('The-Longevity-Masterclass-V46.pptx');print(len(ORDER))
