/* V46 corrections (from V45). Original comment keys remain attached to original slots. */
const courseUrl='https://www.longevitylifeacademy.com/store/longevity-blueprint/';
const slot=n=>document.getElementById('s'+n);
function change(n,src,title,note){
  const s=slot(n);
  if(src)s.querySelector('.main').src=src;
  if(title){s.querySelector('h2').textContent=title;s.querySelector('textarea').dataset.t=title;}
  if(note)s.querySelector('.why').textContent=note;
}
function noOptions(n){slot(n).querySelector('.opts')?.remove();}

// V45 renumbered copies of the original images (only the baked-in counter changed).
change(2,'assets/n02-why.jpg?v=v46y13');
change(3,'assets/n03-dunedin.jpg?v=v46y13');
change(4,'assets/n04-cake.jpg?v=v46y13');
change(5,'assets/n05-icing.jpg?v=v46y13');
change(6,'assets/n06-menopause.jpg?v=v46y13');
change(7,'assets/n07-bridge.jpg?v=v46y13');
change(11,'assets/n11-sugar.jpg?v=v46y13');
change(20,'assets/n19-cake.jpg?v=v46y13');
change(21,'assets/n20-why.jpg?v=v46y13');
change(1,'assets/n01-title.jpg?v=v46y13',null,'Say: “This is not medical advice. Please talk to your doctor.” Then move to the next slide.');
change(8,'assets/n08-sleep.jpg?v=v46y13',"I'll sleep when I die.",'Said the person aging at twice the normal speed. Sleep is the repair shift, followed by the night timeline.');
noOptions(8);
slot(9).remove();
slot(12).remove();
change(10,'assets/n10-plate.jpg?v=v46y13','What does it look like in real life?','The plate illustrates Julie’s script: protein is the floor, fiber is the lever, whole food is the default. Her five personal rules stay on screen.');
const food=slot(10).cloneNode(true);
food.id='s10-food';
food.querySelector('.num').textContent='10A';
food.querySelector('.main').src='assets/n09-food.jpg?v=v46y13';food.querySelector('h2').textContent='Food.';food.querySelector('textarea').dataset.t='Food.';
food.querySelector('.why').textContent='Food foundations. Claude B, Protocol, slide 9. Follows the religion statement slide; Julie’s plate comes next.';
food.querySelector('.opts')?.remove();
food.querySelector('label').htmlFor='c10-food';
food.querySelector('textarea').id='c10-food';
food.querySelector('textarea').dataset.n='10-food';
food.querySelector('.saved').id='v10-food';
slot(10).before(food);
noOptions(10);
change(13,'assets/n12-sameage.jpg?v=v46y13',null,'Selected option 2: the two people, side by side.');
noOptions(13);
change(14,'assets/n13-movement.jpg?v=v46y13',null,'Weights, VO2 max, Zone 2 (two people walking and talking), mobility and balance.');
change(15,'assets/n14-movement-week.jpg?v=v46y13',"Julie Gibson Clark’s Movement Week.",'Movement week (option 2), Claude B, Protocol, slide 13. Marked V2. Julie to update. The full protocol follows after the stress slide.');
noOptions(15);

change(16,'assets/n15-stress.jpg?v=v46y13',null,'Layer four. Stress, your cortisol story, and the physiological sigh.');
slot(16).querySelector('.why').innerHTML='Layer four. Stress, your cortisol story, and the physiological sigh.';

change(17,'assets/n16-protocol.jpg?v=v46y13',null,'Selected Claude B, Protocol, slide 15.');
noOptions(17);
change(18,'assets/n17-notebook.jpg?v=v46y13');
change(19,'assets/n18-testing.jpg?v=v46y13',null,'Selected option 2, with a testing-related background, three distinctly colored cards and DunedinPACE in the baseline-testing list.');
noOptions(19);
const closing=slot(21).cloneNode(true);
closing.id='s22';
closing.querySelector('h2').textContent='One takeaway. Take action.';
closing.querySelector('.main').src='assets/n21-takeaway.png?v=v46y13';
closing.querySelector('.main').alt='One takeaway. Take action.';
closing.querySelector('.why').textContent='Closing slide. Exact original image.';
closing.querySelector('.opts')?.remove();
closing.querySelector('label').htmlFor='c22';
closing.querySelector('textarea').id='c22';
closing.querySelector('textarea').dataset.n='22';
closing.querySelector('textarea').dataset.t='One takeaway. Take action.';
closing.querySelector('.saved').id='v22';
slot(21).after(closing);closing.remove();   // V46 slide 24 (own 'One takeaway') dropped: the closing slide is the latest Claude one (sx-fork)
// New slides from the Round 13 page (risks, Blue Zones, creme brulee) and the closing fork in the road.
function newSlot(id,img,title,note,key){
  const c=slot(21).cloneNode(true);c.id=id;
  c.querySelector('h2').textContent=title;c.querySelector('.main').src=img;c.querySelector('.main').alt=title;
  c.querySelector('.why').textContent=note;c.querySelector('.opts')?.remove();
  c.querySelector('label').htmlFor='c'+key;
  const t=c.querySelector('textarea');t.id='c'+key;t.dataset.n=key;t.dataset.t=title;t.value='';
  c.querySelector('.saved').id='v'+key;c.querySelector('.saved').textContent='';
  return c;
}
const sxRisks=newSlot('sx-risks','assets/n22-risks.jpg?v=v46y13','The four risks.','Added from the Round 13 page (slide 04, The four risks). Placed after the Dunedin slide, before the cake.','x1');
const sxBz=newSlot('sx-bz','assets/n23-bluezones.jpg?v=v46y13','The Blue Zones.','Added from the Round 13 page (slide 07, The Blue Zones). Placed before the menopause slide.','x2');
const sxBr=newSlot('sx-brulee','assets/n24-brulee.jpg?v=v46y13','Crème brûlée and wrinkles.','Added from the Round 13 page (slide 13, Crème brûlée and wrinkles). Placed after the sugar slide, before Same age.','x3');
const sxReligion=newSlot('sx-religion','assets/n26-religion.jpg?v=v46y13','Take the religion out of your diet.','New statement slide: only the sentence, large. Carries the religion part of the old plate-slide script; the pillars follow, then the plate.','x5');
const sxFork=newSlot('sx-fork','assets/n25-fork.png?v=v46z10','One takeaway. Take action. (closing)','Closing slide: exactly the Julie deck slide 22 at commit f220cbd, unchanged (image file additional-take-action-20261026.png). It ends the deck.','x4');
const sxSugar=newSlot('sx-sugar','assets/n28-sugar-limit.jpg?v=v46y13','Six teaspoons: the daily limit for added sugar.','New slide after the crème brûlée. Script it covers (quoted): “Here’s where the data points to a hard ceiling: keep your added sugar to under twenty-five grams a day. That’s roughly six teaspoons.” Then: “birthday cake is too precious of a tradition to scrap for watermelon cake. Sorry not gonna happen. But in it’s rightful place - once in a blue moon - it’s ok.” Then the CGM: “every student in the Longevity Life Academy will wear a CGM for two weeks.” Time 0:30, taken from the brûlée slide (now 0:30).','x6');
const sxMwB=newSlot('sx-mw-julie','assets/n27-movement-week-julie.jpg?v=v46y13','Slide 19, Julie’s version (option B)','Alternative to slide 19 (Movement Week), shown as slide 20, time 0:00. Julie’s comment, quoted: “Can you add a mobility & balance block every day. Make it first and if possible title it “mobility & balance” while tea brews”. Play either slide 19 or slide 20, not both. Same script as slide 19.','x7');
// The user's original slide references define the order, not inferred numbering.
const orderedIds=['s1','s2','s3','sx-risks','s4','s5','sx-bz','s6','s7','s8','sx-religion','s10-food','s10','s11','sx-brulee','sx-sugar','s13','s14','s15','sx-mw-julie','s16','s17','s18','s19','s20','s21','sx-fork'];
document.body.append(sxRisks,sxBz,sxBr,sxFork,sxReligion,sxSugar,sxMwB);
const allSlots=orderedIds.map(id=>document.getElementById(id));
const endMarker=document.querySelector('.coming');
allSlots.forEach(s=>endMarker.before(s));
const slideRefs=orderedIds.map((id,i)=>String(i+1));
allSlots.forEach((s,i)=>{
  s.dataset.originalSlide=s.id.slice(1);
  s.querySelector('.num').textContent=slideRefs[i];
  s.querySelector('label').textContent='Your comment on slide '+slideRefs[i];
  s.querySelector('textarea').dataset.displayN=slideRefs[i];
});
const TIMES=[0.5,2.5,2,1.5,3.5,2,1,1.5,1,2.75,2/3,2.75,4/3,2.75,0.5,0.5,0.5,3,1.5,0,2.75,4,1.5,2,1,3,4];   // minutes per slide, in order; sum = 50
const fmt=m=>{const t=Math.round(m*60);return Math.floor(t/60)+':'+String(t%60).padStart(2,'0');};
let run=0;
allSlots.forEach((s,i)=>{
  run+=TIMES[i];
  const n=s.querySelector('.num');
  n.innerHTML=slideRefs[i]+' <span style="display:inline-block;vertical-align:middle;margin-left:14px;padding:5px 14px;border-radius:999px;background:#F6DC8C;color:#06142a;font:700 22px Inter,Arial,sans-serif;font-style:normal">'+fmt(TIMES[i])+' min</span> <span style="vertical-align:middle;margin-left:10px;color:#8DBCFF;font:500 16px Inter,Arial,sans-serif;font-style:normal">running total '+fmt(run)+' of 50:00</span>';
});
document.querySelector('.lead').innerHTML='<b style="color:#F6DC8C;font-size:22px">Total talk time: 50:00 net, 27 slides (slide 20 is an alternative at 0:00).</b> The number and timing sit beside each slide (never on it); the yellow label is that slide’s time, followed by the running total. Slides are numbered 1 to 27 in presentation order. New: 4 The four risks, 7 The Blue Zones, 14 Crème brûlée and wrinkles, 16 Six teaspoons, the daily sugar limit (new). Slide 20 is Julie’s version (option B) of slide 19, the Movement Week; play slide 19 or slide 20. Slide 27 is the closing slide, exactly Julie slide 22 (f220cbd), unchanged.';
const deckLinks=allSlots.map(s=>s.dataset.link||'');
const variantTag=document.createElement('div');
variantTag.id='play-variant';
variantTag.style.cssText='display:none;position:absolute;top:20px;left:24px;padding:10px 16px;background:#08152D;color:#8AD2FF;font-size:22px;z-index:70;pointer-events:none';
document.getElementById('play').append(variantTag);

