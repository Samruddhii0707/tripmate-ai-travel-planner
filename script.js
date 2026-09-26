const pages=['home','plan','explore','hotels','trips','assistant'];
function go(id){
  if(!document.getElementById('app').classList.contains('hidden')===false) return;
  pages.forEach(p=>document.getElementById(p).classList.toggle('active',p===id));
  window.scrollTo({top:0,behavior:'smooth'});
  if(id==='trips') updateDashboard();
}
function toggleMenu(){
  document.querySelector('.navlinks').style.display =
    document.querySelector('.navlinks').style.display==='flex'?'none':'flex';
}
function showSignup(){document.getElementById('loginBox').classList.add('hidden');document.getElementById('signupBox').classList.remove('hidden')}
function showLogin(){document.getElementById('signupBox').classList.add('hidden');document.getElementById('loginBox').classList.remove('hidden')}
function login(){
  const e=document.getElementById('loginEmail').value.trim(),p=document.getElementById('loginPassword').value.trim();
  if(!e||!p){toast('Please enter email and password');return}
  localStorage.setItem('tripmateUser',e); openApp(); toast('Welcome back ✨');
}
function signup(){
  const n=document.getElementById('signupName').value.trim(),e=document.getElementById('signupEmail').value.trim(),p=document.getElementById('signupPassword').value.trim();
  if(!n||!e||!p){toast('Please fill all fields');return}
  localStorage.setItem('tripmateUser',e); openApp(); toast('Account created successfully ✨');
}
function openApp(){document.getElementById('authPage').classList.add('hidden');document.getElementById('app').classList.remove('hidden');go('home')}
function logout(){localStorage.removeItem('tripmateUser');location.reload()}
function toast(t){const x=document.getElementById('toast');x.textContent=t;x.classList.remove('hidden');setTimeout(()=>x.classList.add('hidden'),2500)}
function generateTrip(){
  const d=document.getElementById('dest').value.trim()||'Goa',days=Math.max(1,+document.getElementById('days').value||3),people=Math.max(1,+document.getElementById('people').value||2),budget=Math.max(0,+document.getElementById('budget').value||25000),interest=document.getElementById('interest').value;
  const per=Math.round(budget/days),names=['Arrival & local exploration','Signature sightseeing','Local food experience','Scenic evening','Shopping & culture','Relax & departure'];
  let out=`<div class="result glass reveal"><h3>✨ AI Itinerary — ${d}</h3><p class="muted">Personalized for ${people} traveler(s) • ${days} day(s) • ₹${budget.toLocaleString('en-IN')} budget • ${interest}</p><div class="itinerary" style="margin-top:16px">`;
  for(let i=1;i<=days;i++) out+=`<div class="day glass"><div class="day-top"><strong>Day ${i}</strong><span class="tag">₹${per.toLocaleString('en-IN')} target</span></div><div class="activity"><strong>🌅 ${names[(i-1)%names.length]}</strong><span class="muted">Explore ${d} with a balanced plan, local highlights and flexible time.</span></div><div class="activity"><strong>🍽 ${interest}</strong><span class="muted">Recommended experience • Cab / local transport • 45–60 min</span></div></div>`;
  out+=`</div></div>`;document.getElementById('tripResult').innerHTML=out;
  localStorage.setItem('tripmateTrip',JSON.stringify({d,days,people,budget,interest}));updateDashboard();toast('Your AI itinerary is ready ✨');
}
function updateDashboard(){
  const t=JSON.parse(localStorage.getItem('tripmateTrip')||'null');
  if(!t){return}
  document.getElementById('tripCount').textContent='1';document.getElementById('dashBudget').textContent='₹'+t.budget.toLocaleString('en-IN');document.getElementById('dashPeople').textContent=t.people;
  document.getElementById('recentTrip').innerHTML=`<strong>${t.d}</strong> • ${t.days} days • ${t.people} travelers • ${t.interest}`;
}
function sendMsg(){
  const i=document.getElementById('chatInput'),v=i.value.trim();if(!v)return;
  const box=document.getElementById('messages');box.innerHTML+=`<div class="msg me">${v}</div>`;
  let r='I can help with destinations, hotels, budgets, food and transport. ✈️';
  if(/hotel|stay/i.test(v))r='For hotels, compare location, rating, facilities and price before booking. 🏨';
  else if(/cheap|budget|cost|price/i.test(v))r='For a budget trip, keep a daily target and reserve a small emergency buffer. 💰';
  else if(/food|eat/i.test(v))r='Try local specialties and popular local cafés; keep a food budget per day. 🍽️';
  else if(/transport|cab|bus|train/i.test(v))r='Cab, local transport and public transit can be compared based on distance and time. 🚌';
  setTimeout(()=>{box.innerHTML+=`<div class="msg bot">${r}</div>`;box.scrollTop=box.scrollHeight},350);i.value='';
}
if(localStorage.getItem('tripmateUser'))openApp();