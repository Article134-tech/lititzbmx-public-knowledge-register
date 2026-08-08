(() => {
  'use strict';

  const publicTitle = value => {
    let title = String(value ?? '').replace(/\s+/g, ' ').trim();
    const exact = title.match(/^BMXMuseum\s+(\d+)\s*[—–-]\s*(.+)$/i);
    if (exact) return `${exact[2]} · External record ${exact[1]}`;
    title = title.replace(/BMXMuseum\s+Reference\s+(\d+)/gi, 'External reference $1');
    title = title.replace(/BMXMuseum\s+reference\s+lead/gi, 'External reference lead');
    return title.replace(/BMXMuseum/gi, 'External source');
  };
  const publicSourceBadge = value => /BMXMuseum/i.test(String(value || ''))
    ? (/lead/i.test(String(value || '')) ? 'External reference lead' : 'External source record')
    : publicTitle(value);

  const menuButton = document.querySelector('.menu-button');
  const primaryNav = document.querySelector('.primary-nav');
  if (menuButton && primaryNav) {
    const setOpen = open => {
      primaryNav.classList.toggle('open', open);
      menuButton.setAttribute('aria-expanded', String(open));
      menuButton.querySelector('[aria-hidden="true"]')?.replaceChildren(document.createTextNode(open ? '×' : '☰'));
    };
    menuButton.addEventListener('click', () => setOpen(!primaryNav.classList.contains('open')));
    document.addEventListener('keydown', event => { if (event.key === 'Escape') setOpen(false); });
    primaryNav.addEventListener('click', event => { if (event.target.closest('a')) setOpen(false); });
  }

  // Preserve exact source identity in provenance sections, but avoid giving an
  // external aggregation platform headline or badge prominence elsewhere.
  document.querySelectorAll('h1, h2, h3').forEach(heading => {
    if (/BMXMuseum/i.test(heading.textContent)) heading.textContent = publicTitle(heading.textContent);
  });
  document.querySelectorAll('.source-badge').forEach(badge => {
    if (badge.closest('#source, #provenance')) return;
    if (/BMXMuseum/i.test(badge.textContent)) badge.textContent = publicSourceBadge(badge.textContent);
    badge.classList.add('metadata-chip');
    if (badge.closest('.page-hero') && !/^Source:/i.test(badge.textContent.trim())) badge.textContent = `Source: ${badge.textContent.trim()}`;
  });
  document.querySelectorAll('.page-hero .status').forEach(status => {
    status.classList.add('metadata-chip');
    if (!/^Research status:/i.test(status.textContent.trim())) status.textContent = `Research status: ${status.textContent.trim()}`;
  });
  if (/BMXMuseum/i.test(document.title)) document.title = publicTitle(document.title);

  const returnLabel = url => {
    let parsed;
    try { parsed = new URL(url, location.origin); } catch (_) { return 'Back to results'; }
    const path = parsed.pathname;
    const params = parsed.searchParams;
    if (path.includes('/chronology/')) return 'Back to chronology';
    if (path.includes('/search/')) return 'Back to search results';
    if (path.includes('/object/')) return 'Back to connected object';
    if (path.includes('/sources/')) return 'Back to source directory';
    if (path.includes('/browse/')) {
      if (params.get('object')) return 'Back to supporting records';
      if (params.get('category') || params.get('topic')) return 'Back to category results';
      return 'Back to browse results';
    }
    if (path.includes('/record/') || path.includes('/records/')) return 'Back to source record';
    return 'Back to results';
  };

  let returnUrl = new URLSearchParams(location.search).get('from') || '';
  try { if (!returnUrl) returnUrl = sessionStorage.getItem('pkr-return-url') || ''; } catch (_) { /* optional */ }
  document.querySelectorAll('[data-back-to-results]').forEach(link => {
    if (returnUrl) link.href = returnUrl;
    const label = returnLabel(returnUrl || link.href);
    link.textContent = link.textContent.trim().startsWith('←') ? `← ${label}` : label;
    link.classList.add('return-link');
  });

  document.addEventListener('click', event => {
    const link = event.target.closest('a[data-result-link], .record-actions a[href], .related-link[href], #object a[href], #price a[href]');
    if (!link || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const from = `${location.pathname}${location.search}`;
    try {
      sessionStorage.setItem('pkr-return-url', from);
      sessionStorage.setItem(`pkr-return-state:${from}`, JSON.stringify({ scrollY: window.scrollY, anchor: link.closest('[data-card-id]')?.dataset.cardId || '' }));
      const target = new URL(link.href, location.href);
      if (target.origin === location.origin) {
        target.searchParams.set('from', from);
        link.href = `${target.pathname}${target.search}${target.hash}`;
      }
    } catch (_) { /* retain original route */ }
  });

  const cards = [...document.querySelectorAll('[data-register-card]')];
  if (cards.length) {
    const search = document.querySelector('#register-search');
    const status = document.querySelector('#register-status');
    const group = document.querySelector('#register-group');
    const count = document.querySelector('#result-count');
    const reset = document.querySelector('#reset-filters');
    const params = new URLSearchParams(window.location.search);
    if (search && params.get('q')) search.value = params.get('q');
    if (status && params.get('status')) status.value = params.get('status');
    if (group && params.get('group')) group.value = params.get('group');
    const apply = () => {
      const q = (search?.value || '').trim().toLowerCase();
      const selectedStatus = status?.value || '';
      const selectedGroup = group?.value || '';
      let shown = 0;
      cards.forEach(card => {
        const statusMatch = !selectedStatus || card.dataset.status === selectedStatus || (selectedStatus === 'public' && ['documented', 'qualified'].includes(card.dataset.status));
        const matches = (!q || String(card.dataset.search || '').includes(q)) && statusMatch && (!selectedGroup || card.dataset.group === selectedGroup);
        card.hidden = !matches;
        if (matches) shown += 1;
      });
      if (count) count.textContent = `${shown} ${shown === 1 ? 'record' : 'records'} shown`;
      const next = new URLSearchParams();
      if (search?.value.trim()) next.set('q', search.value.trim());
      if (selectedStatus) next.set('status', selectedStatus);
      if (selectedGroup) next.set('group', selectedGroup);
      history.replaceState({}, '', `${location.pathname}${next.toString() ? `?${next}` : ''}`);
    };
    [search, status, group].forEach(control => control?.addEventListener(control.tagName === 'INPUT' ? 'input' : 'change', apply));
    reset?.addEventListener('click', () => { if (search) search.value = ''; if (status) status.value = ''; if (group) group.value = ''; apply(); });
    apply();
  }
})();
