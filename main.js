document.addEventListener("DOMContentLoaded",()=>{
 const lang=localStorage.getItem("tripmate_lang")||"English";
 const select=document.querySelector("#language");
 if(select){select.value=lang;select.addEventListener("change",()=>{localStorage.setItem("tripmate_lang",select.value);location.reload()})}
 document.querySelectorAll("[data-demo-book]").forEach(btn=>btn.addEventListener("click",async()=>{
   const r=await fetch("/book",{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded"},body:new URLSearchParams({type:btn.dataset.type||"Hotel",destination:btn.dataset.destination||"Goa",amount:btn.dataset.amount||"2500"})});
   const d=await r.json(); alert(d.ok?"Booking confirmed: "+d.booking_id:d.message); if(d.ok) location.href="/bookings";
 }));
});
