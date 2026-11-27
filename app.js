
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

// Demo / Pilot Mode Modal Handlers
window.openDemoModal = function(e, appName) {
    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }
    const detailsModal = document.getElementById('app-details-modal');
    if (detailsModal) detailsModal.classList.remove('open');
    const demoModal = document.getElementById('demo-version-modal');
    if (!demoModal) return;
    const target = document.getElementById('demo-modal-app-name');
    if (target && appName) target.textContent = appName;
    demoModal.classList.add('open');
};

window.closeDemoModal = function() {
    const demoModal = document.getElementById('demo-version-modal');
    if (demoModal) demoModal.classList.remove('open');
};

document.addEventListener('click', function(e) {
    const modal = document.getElementById('demo-version-modal');
    if (modal && modal.classList.contains('open') && e.target === modal) {
        modal.classList.remove('open');
    }
});

// Seamless client-side SPA navigation (swaps <main class="content"> without full page reload)
(function() {
    let activeNavController = null;
    const prefetched = new Map();

    function activateTabFromUrl(urlObj) {
        const wanted = urlObj.searchParams.get('tab') || urlObj.hash.slice(1);
        const tab = wanted && document.querySelector(`.tab[data-tab="${wanted}"]`);
        if (tab) tab.click();
    }

    function syncSidebarActive(targetUrl) {
        const targetPath = targetUrl.pathname + targetUrl.search;
        document.querySelectorAll('.sidebar .nav a[href]').forEach(a => {
            const href = a.getAttribute('href');
            if (!href || href.startsWith('javascript:')) return;
            const linkUrl = new URL(href, location.origin);
            const isMatch = (linkUrl.pathname + linkUrl.search) === targetPath;
            a.classList.toggle('active', isMatch);
        });
    }

    async function navigateTo(url, push = true) {
        const mainEl = document.querySelector('main.content');
        if (!mainEl) {
            location.href = url;
            return;
        }
        if (activeNavController) activeNavController.abort();
        activeNavController = new AbortController();

        mainEl.style.transition = 'opacity 0.12s ease';
        mainEl.style.opacity = '0.6';

        try {
            const targetUrl = new URL(url, location.origin);
            let htmlText = prefetched.get(targetUrl.href);
            if (!htmlText) {
                const res = await fetch(targetUrl.href, {
                    credentials: 'same-origin',
                    signal: activeNavController.signal
                });
                if (res.redirected && new URL(res.url).pathname === '/login') {
                    location.href = res.url;
                    return;
                }
                if (!res.ok && res.status !== 403 && res.status !== 404) {
                    location.href = targetUrl.href;
                    return;
                }
                htmlText = await res.text();
            } else {
                prefetched.delete(targetUrl.href);
            }

            const doc = new DOMParser().parseFromString(htmlText, 'text/html');
            const nextMain = doc.querySelector('main.content');
            if (!nextMain) {
                location.href = targetUrl.href;
                return;
            }

            mainEl.innerHTML = nextMain.innerHTML;
            mainEl.style.opacity = '1';
            document.title = doc.title || document.title;

            const nextActions = doc.querySelector('.topbar .actions');
            const curActions = document.querySelector('.topbar .actions');
            if (nextActions && curActions) {
                curActions.innerHTML = nextActions.innerHTML;
            }

            if (push) {
                history.pushState({ url: targetUrl.href }, '', targetUrl.href);
            }
            syncSidebarActive(targetUrl);
            activateTabFromUrl(targetUrl);
            filterApps();

            if (targetUrl.hash) {
                const anchor = document.getElementById(targetUrl.hash.slice(1));
                if (anchor) anchor.scrollIntoView({ behavior: 'smooth' });
            } else {
                window.scrollTo({ top: 0, behavior: 'instant' });
            }
            setTimeout(() => document.querySelectorAll('.flash').forEach(x => x.style.display = 'none'), 5000);
        } catch (err) {
            if (err.name !== 'AbortError') {
                location.href = url;
            }
        }
    }

    document.addEventListener('click', function(e) {
        if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
        const link = e.target.closest('a[href]');
        if (!link) return;
        const href = link.getAttribute('href');
        if (!href || href.startsWith('#') || href.startsWith('javascript:') || link.target === '_blank' || link.hasAttribute('download')) return;

        const targetUrl = new URL(href, location.origin);
        if (targetUrl.origin !== location.origin) return;
        if (targetUrl.pathname.startsWith('/api/') || targetUrl.pathname === '/payroll/download' || targetUrl.pathname === '/logout') return;
        if (!document.querySelector('main.content')) return;

        e.preventDefault();
        navigateTo(targetUrl.href, true);
    });

    document.addEventListener('pointerenter', function(e) {
        const link = e.target.closest('.sidebar .nav a[href], .section-link[href], .page-home[href]');
        if (!link) return;
        const href = link.getAttribute('href');
        if (!href || href.startsWith('#') || href.startsWith('javascript:')) return;
        const targetUrl = new URL(href, location.origin);
        if (targetUrl.origin !== location.origin || prefetched.has(targetUrl.href)) return;
        fetch(targetUrl.href, { credentials: 'same-origin' })
            .then(r => (r.ok && !r.redirected) ? r.text() : null)
            .then(text => { if (text) prefetched.set(targetUrl.href, text); })
            .catch(() => {});
    }, true);

    window.addEventListener('popstate', function() {
        navigateTo(location.href, false);
    });
})();
