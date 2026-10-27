# Builds The-Longevity-Masterclass-V46.pptx: the 25 final V46 slides, same order, each as a full-bleed 1920x1080 picture (exact design) with the slide number and title in the notes.
from pptx import Presentation
from pptx.util import Emu
import cv2,os
ORDER=[('n01-title.jpg','The Longevity Masterclass'),('n02-why.jpg','Why I went down this path'),('n03-dunedin.jpg','Ten years pass. By this test, I age about six. The speed towards death.'),
('n22-risks.jpg','The four risks.'),('n04-cake.jpg','Longevity is like a cake.'),('n05-icing.jpg','Not wrong. Not first.'),('n23-bluezones.jpg','The Blue Zones.'),
('n06-menopause.jpg','Menopause therapy is a layer, not icing.'),('n07-bridge.jpg','Four layers hold up the cake.'),('n08-sleep.jpg',"I'll sleep when I die."),
('n09-food.jpg','Food.'),('n10-plate.jpg','Take the religion out of your diet.'),('n11-sugar.jpg','The one thing every diet agrees on.'),('n24-brulee.jpg','Crème brûlée and wrinkles.'),
('n12-sameage.jpg','Same age.'),('n13-movement.jpg','Four types of movement, four parts of you.'),('n14-movement-week.jpg','Julie Gibson Clark’s Movement Week. (V2, Julie to update)'),
('n15-stress.jpg','The layer people skip.'),('n16-protocol.jpg',"Julie Gibson Clark's Longevity Protocol."),('n17-notebook.jpg',"You don't need a lab. You need a notebook."),
('n18-testing.jpg','Test. Then buy.'),('n19-cake.jpg',"That's the cake."),('n20-why.jpg','Why. Intention. Resources.'),('n21-takeaway.png','One takeaway. Take action.'),('n25-fork.jpg','The fork in the road.')]
prs=Presentation();prs.slide_width=Emu(12192000);prs.slide_height=Emu(6858000)
os.makedirs('/tmp/pp',exist_ok=True)
for i,(f,t) in enumerate(ORDER,1):
    p='assets/'+f
    if f.endswith('png'):
        cv2.imwrite('/tmp/pp/%s.jpg'%f,cv2.imread(p),[cv2.IMWRITE_JPEG_QUALITY,93]);p='/tmp/pp/%s.jpg'%f
    s=prs.slides.add_slide(prs.slide_layouts[6])
    s.shapes.add_picture(p,0,0,prs.slide_width,prs.slide_height)
    s.notes_slide.notes_text_frame.text='Slide %d of %d: %s'%(i,len(ORDER),t)
prs.save('The-Longevity-Masterclass-V46.pptx');print(len(ORDER))
