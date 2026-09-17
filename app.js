
function filterApps(){const q=(document.getElementById('app-search')?.value||'').toLowerCase();const cat=document.querySelector('.chip.active')?.dataset.cat||'all';document.querySelectorAll('.app-card').forEach(c=>{c.style.display=((cat==='all'||c.dataset.category===cat)&&c.dataset.search.includes(q))?'block':'none'})}
document.addEventListener('click',e=>{const chip=e.target.closest('.chip');if(chip&&chip.dataset.cat){document.querySelectorAll('.chip').forEach(x=>x.classList.remove('active'));chip.classList.add('active');filterApps()}const tab=e.target.closest('.tab');if(tab&&tab.dataset.tab){const box=tab.closest('[data-tabs]');box.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));box.querySelectorAll('.tab-pane').forEach(x=>x.classList.remove('active'));tab.classList.add('active');box.querySelector('#'+tab.dataset.tab).classList.add('active')}const open=e.target.closest('[data-open]');if(open)document.getElementById(open.dataset.open)?.classList.add('open');const close=e.target.closest('[data-close]');if(close)document.getElementById(close.dataset.close)?.classList.remove('open')});
document.addEventListener('input',e=>{if(e.target.id==='app-search')filterApps()});
document.addEventListener('change',e=>{if(e.target.id==='app-logo-file'){const file=e.target.files?.[0];if(!file)return;if(!file.type.startsWith('image/')){alert('Please select an image file.');e.target.value='';return}if(file.size>300000){alert('Logo must be smaller than 300 KB.');e.target.value='';return}const reader=new FileReader();reader.onload=()=>{const value=document.getElementById('app-logo-value');const preview=document.getElementById('app-logo-preview');if(value)value.value=reader.result;if(preview){preview.src=reader.result;preview.hidden=false}};reader.readAsDataURL(file)}});
document.addEventListener('input',e=>{if(e.target.id==='app-logo-value'){const preview=document.getElementById('app-logo-preview');if(preview){preview.src=e.target.value;preview.hidden=!e.target.value}}if(e.target.id==='brand-color-picker'){const code=document.getElementById('brand-color-code');const swatch=document.getElementById('brand-color-swatch');if(code)code.value=e.target.value.toUpperCase();if(swatch)swatch.style.background=e.target.value}if(e.target.id==='brand-color-code'){const value=e.target.value.trim();if(/^#[0-9a-f]{6}$/i.test(value)){const picker=document.getElementById('brand-color-picker');const swatch=document.getElementById('brand-color-swatch');if(picker)picker.value=value;if(swatch)swatch.style.background=value}}});
document.addEventListener('change',e=>{if(e.target.matches('.quick-choice input')){const checked=document.querySelectorAll('.quick-choice input:checked');if(checked.length>6){e.target.checked=false;alert('Choose up to 6 applications for Quick Access.')}}});
document.addEventListener('DOMContentLoaded',()=>{const wanted=new URLSearchParams(location.search).get('tab')||location.hash.slice(1);const tab=wanted&&document.querySelector(`.tab[data-tab="${wanted}"]`);if(tab)tab.click()});
setTimeout(()=>document.querySelectorAll('.flash').forEach(x=>x.style.display='none'),5000);

// More-details button — use capture phase to run BEFORE the card-launch-link intercepts
document.addEventListener('click', function(e) {
    const btn = e.target.closest('.more-details-btn');
    if (!btn) return;
    e.preventDefault();
    e.stopImmediatePropagation();
    e.stopPropagation();

    const modal = document.getElementById('app-details-modal');
    if (!modal) return;

    // Populate text fields from data attributes on the button
    document.getElementById('modal-app-name').textContent = btn.dataset.appName || '';
    document.getElementById('modal-app-desc').textContent = btn.dataset.appDesc || '';
    document.getElementById('modal-app-cat').textContent = btn.dataset.appCat || '';
    document.getElementById('modal-app-version').textContent = btn.dataset.appVersion || '';
    document.getElementById('modal-app-pub').textContent = btn.dataset.appPub || '';

    // Populate Icon HTML from nearest icon-wrap
    const iconWrap = btn.closest('.app-top') && btn.closest('.app-top').querySelector('.app-icon-wrap');
    if (iconWrap && iconWrap.dataset.html) {
        document.getElementById('modal-app-icon').innerHTML = iconWrap.dataset.html;
    }

    // Set launch link href
    const card = btn.closest('.app-card');
    const launchLink = card && card.querySelector('.card-launch-link');
    const launchBtn = document.getElementById('modal-launch-btn');
    if (launchBtn && launchLink) {
        launchBtn.href = launchLink.href || '#';
        if (launchLink.target) {
            launchBtn.setAttribute('target', launchLink.target);
            launchBtn.setAttribute('rel', 'noopener');
        } else {
            launchBtn.removeAttribute('target');
            launchBtn.removeAttribute('rel');
        }
    }

    modal.classList.add('open');
}, true); // capture=true: runs before any bubbling handlers

// Close modal when clicking backdrop
document.addEventListener('click', function(e) {
    const modal = document.getElementById('app-details-modal');
    if (modal && modal.classList.contains('open') && e.target === modal) {
        modal.classList.remove('open');
    }
});

window.openAppModal = function(e, btn) { /* legacy shim - handled by delegation above */ };
