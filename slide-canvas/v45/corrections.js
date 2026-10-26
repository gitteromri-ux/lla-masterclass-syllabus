/* V45-only corrections. Original comment keys remain attached to original slots. */
const courseUrl='https://www.longevitylifeacademy.com/store/longevity-blueprint/';
const slot=n=>document.getElementById('s'+n);
function change(n,src,title,note){
  const s=slot(n);
  if(src)s.querySelector('.main').src=src;
  if(title){s.querySelector('h2').textContent=title;s.querySelector('textarea').dataset.t=title;}
  if(note)s.querySelector('.why').textContent=note;
}
function noOptions(n){slot(n).querySelector('.opts')?.remove();}
change(1,'assets/title.jpg',null,'Say: “This is not medical advice. Please talk to your doctor.” Then move to the next slide.');
change(8,'assets/sleep.jpg',"I'll sleep when I die.",'Said the person aging at twice the normal speed. Sleep is the repair shift, followed by the night timeline.');
noOptions(8);
slot(9).remove();
slot(12).remove();
change(10,'assets/food-plate.jpg',null,'The plate illustrates Julie’s script: protein is the floor, fiber is the lever, whole food is the default. Her five personal rules stay on screen.');
const food=slot(10).cloneNode(true);
food.id='s10-food';
food.querySelector('.num').textContent='10A';
food.querySelector('.main').src='../images/claude-b-09.jpg';
food.querySelector('.why').textContent='Food foundations. Claude B, Protocol, slide 9. Followed by Julie’s plate.';
food.querySelector('.opts')?.remove();
food.querySelector('label').htmlFor='c10-food';
food.querySelector('textarea').id='c10-food';
food.querySelector('textarea').dataset.n='10-food';
food.querySelector('.saved').id='v10-food';
slot(10).before(food);
noOptions(10);
change(13,'../images/claude-a-11.jpg',null,'Selected option 2: the two people, side by side.');
noOptions(13);
change(14,'assets/movement.jpg');
change(15,'../images/claude-b-15.jpg',null,'Main: The protocol. Julie to update the V2 movement-week alternative below.');
slot(15).querySelector('.opts').innerHTML='<figure class="v2"><span>V2 · Julie to update</span><img src="../images/claude-b-13.jpg" alt="V2: Movement week. Julie to update."></figure>';
change(16,'assets/stress.jpg');
slot(16).dataset.link=courseUrl;
const lp=document.createElement('a');
lp.href=courseUrl;lp.target='_blank';lp.rel='noopener';lp.className='lp-link';
lp.textContent='Longevity Life Academy · View the course';
slot(16).querySelector('.why').after(lp);
change(17,'../images/claude-b-15.jpg',null,'Selected Claude B, Protocol, slide 15.');
noOptions(17);
change(18,'assets/notebook.jpg');
change(19,'assets/testing.jpg',null,'Selected option 2, with a testing-related background, three distinctly colored cards and DunedinPACE in the baseline-testing list.');
noOptions(19);
const allSlots=[...document.querySelectorAll('.slot')];
allSlots.forEach((s,i)=>{
  s.dataset.originalSlide=s.id.slice(1);
  s.querySelector('.num').textContent=String(i+1).padStart(2,'0');
  s.querySelector('label').textContent='Your comment on slide '+(i+1);
  s.querySelector('textarea').dataset.displayN=String(i+1);
});
document.querySelector('.lead').textContent='Twenty slides in presentation order. Press Play for the selected slides only. The full-color V2 movement-week alternative is marked “Julie to update” and is not included in Play. Click any image to open it full screen. Original comment keys are preserved.';
const deckLinks=allSlots.map(s=>s.dataset.link||'');
const link=document.createElement('a');
link.id='play-link';link.href=courseUrl;link.target='_blank';link.rel='noopener';link.textContent='View the Longevity Life Academy course';
link.addEventListener('click',e=>e.stopPropagation());
document.getElementById('play').append(link);
const lbLink=link.cloneNode(true);lbLink.id='lb-link';lbLink.addEventListener('click',e=>e.stopPropagation());document.getElementById('lb').append(lbLink);
