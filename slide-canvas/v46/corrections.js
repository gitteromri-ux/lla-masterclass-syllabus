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
change(2,'assets/n02-why.jpg?v=v46j');
change(3,'assets/n03-dunedin.jpg?v=v46j');
change(4,'assets/n04-cake.jpg?v=v46j');
change(5,'assets/n05-icing.jpg?v=v46j');
change(6,'assets/n06-menopause.jpg?v=v46j');
change(7,'assets/n07-bridge.jpg?v=v46j');
change(11,'assets/n11-sugar.jpg?v=v46j');
change(20,'assets/n19-cake.jpg?v=v46j');
change(21,'assets/n20-why.jpg?v=v46j');
change(1,'assets/n01-title.jpg?v=v46j',null,'Say: “This is not medical advice. Please talk to your doctor.” Then move to the next slide.');
change(8,'assets/n08-sleep.jpg?v=v46j',"I'll sleep when I die.",'Said the person aging at twice the normal speed. Sleep is the repair shift, followed by the night timeline.');
noOptions(8);
slot(9).remove();
slot(12).remove();
change(10,'assets/n10-plate.jpg?v=v46j',null,'The plate illustrates Julie’s script: protein is the floor, fiber is the lever, whole food is the default. Her five personal rules stay on screen.');
const food=slot(10).cloneNode(true);
food.id='s10-food';
food.querySelector('.num').textContent='10A';
food.querySelector('.main').src='assets/n09-food.jpg?v=v46j';food.querySelector('h2').textContent='Food.';food.querySelector('textarea').dataset.t='Food.';
food.querySelector('.why').textContent='Food foundations. Claude B, Protocol, slide 9. Followed by Julie’s plate.';
food.querySelector('.opts')?.remove();
food.querySelector('label').htmlFor='c10-food';
food.querySelector('textarea').id='c10-food';
food.querySelector('textarea').dataset.n='10-food';
food.querySelector('.saved').id='v10-food';
slot(10).before(food);
noOptions(10);
change(13,'assets/n12-sameage.jpg?v=v46j',null,'Selected option 2: the two people, side by side.');
noOptions(13);
change(14,'assets/n13-movement.jpg?v=v46j',null,'Weights, VO2 max, Zone 2 (two people walking and talking), mobility and balance.');
change(15,'assets/n14-movement-week.jpg?v=v46j',"Julie Gibson Clark’s Movement Week.",'Movement week (option 2), Claude B, Protocol, slide 13. Marked V2. Julie to update. The full protocol follows after the stress slide.');
noOptions(15);

change(16,'assets/n15-stress.jpg?v=v46j',null,'Layer four. Stress, your cortisol story, and the physiological sigh.');
slot(16).querySelector('.why').innerHTML='Layer four. Stress, your cortisol story, and the physiological sigh. The link to our landing page replaces “Let’s do three together”: <a href="'+courseUrl+'" target="_blank" rel="noopener" style="color:#8AD2FF">'+courseUrl+'</a>';

change(17,'assets/n16-protocol.jpg?v=v46j',null,'Selected Claude B, Protocol, slide 15.');
noOptions(17);
change(18,'assets/n17-notebook.jpg?v=v46j');
change(19,'assets/n18-testing.jpg?v=v46j',null,'Selected option 2, with a testing-related background, three distinctly colored cards and DunedinPACE in the baseline-testing list.');
noOptions(19);
const closing=slot(21).cloneNode(true);
closing.id='s22';
closing.querySelector('h2').textContent='One takeaway. Take action.';
closing.querySelector('.main').src='assets/n21-takeaway.png?v=v46j';
closing.querySelector('.main').alt='One takeaway. Take action.';
closing.querySelector('.why').textContent='Closing slide. Exact original image.';
closing.querySelector('.opts')?.remove();
closing.querySelector('label').htmlFor='c22';
closing.querySelector('textarea').id='c22';
closing.querySelector('textarea').dataset.n='22';
closing.querySelector('textarea').dataset.t='One takeaway. Take action.';
closing.querySelector('.saved').id='v22';
slot(21).after(closing);
// The user's original slide references define the order, not inferred numbering.
const orderedIds=['s1','s2','s3','s4','s5','s6','s7','s8','s10-food','s10','s11','s13','s14','s15','s16','s17','s18','s19','s20','s21','s22'];
const allSlots=orderedIds.map(id=>document.getElementById(id));
const endMarker=document.querySelector('.coming');
allSlots.forEach(s=>endMarker.before(s));
const slideRefs=orderedIds.map(id=>id==='s10-food'?'10A':id==='s10'?'10B':id==='s15-v2'?'15 · V2':id.slice(1));
allSlots.forEach((s,i)=>{
  s.dataset.originalSlide=s.id.slice(1);
  s.querySelector('.num').textContent=slideRefs[i];
  s.querySelector('label').textContent='Your comment on slide '+slideRefs[i];
  s.querySelector('textarea').dataset.displayN=slideRefs[i];
});
document.querySelector('.lead').textContent='Original slide references are retained. Slides 9 and 12 are removed. Slide 10 is split: 10A Food foundations, then 10B the plate. Slide 15 is Movement week (V2, Julie to update) and the full protocol is slide 17. Play presents the 21 main slides only, ending with One takeaway. Take action.';
const deckLinks=allSlots.map(s=>s.dataset.link||'');
const variantTag=document.createElement('div');
variantTag.id='play-variant';
variantTag.style.cssText='display:none;position:absolute;top:20px;left:24px;padding:10px 16px;background:#08152D;color:#8AD2FF;font-size:22px;z-index:70;pointer-events:none';
document.getElementById('play').append(variantTag);

