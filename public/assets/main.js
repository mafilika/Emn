(function(){
document.getElementById('y').textContent=new Date().getFullYear();
var mb=document.querySelector('.menu'),ul=document.querySelector('nav ul');
mb.addEventListener('click',function(){var o=ul.classList.toggle('open');mb.setAttribute('aria-expanded',o)});
ul.addEventListener('click',function(){ul.classList.remove('open')});
document.querySelectorAll('[data-more]').forEach(function(b){b.addEventListener('click',function(){var m=b.parentNode.querySelector('.more');var s=m.classList.toggle('show');b.textContent=s?'Show Less':'Read More'})});
var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{threshold:.12});
document.querySelectorAll('.rv').forEach(function(el){io.observe(el)});
var so=new IntersectionObserver(function(es){es.forEach(function(e){if(!e.isIntersecting)return;so.unobserve(e.target);
e.target.querySelectorAll('[data-n]').forEach(function(c){var t=+c.dataset.n,s=c.dataset.s||'',i=0,st=Math.max(1,Math.ceil(t/40));var iv=setInterval(function(){i=Math.min(t,i+st);c.textContent=i+s;if(i>=t)clearInterval(iv)},30)})})},{threshold:.3});
var st=document.querySelector('.stats');if(st)so.observe(st);
var qf=document.getElementById('qf');if(qf)qf.addEventListener('submit',function(e){e.preventDefault();
var t='Hi EMN Projects, I would like a free quote.%0AName: '+encodeURIComponent(n.value)+'%0APhone: '+encodeURIComponent(p.value)+'%0AService: '+encodeURIComponent(s.value)+'%0AMessage: '+encodeURIComponent(m.value);
window.open('https://wa.me/27000000000?text='+t,'_blank','noopener')});
})();
