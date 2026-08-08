(() => {
  'use strict';

  const depth = Number(document.body.dataset.depth || '1');
  const dataBase = '../'.repeat(depth) + 'data/governed/';
  const derivedBase = '../'.repeat(depth) + 'data/derived/';
  const registerRoot = '../'.repeat(depth);
  const escapeHtml = value => String(value ?? '')
    .replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;').replaceAll("'", '&#039;');
  const normalize = value => String(value ?? '').normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/\s+/g, ' ').trim();

  async function load(file) {
    const response = await fetch(dataBase + file);
    if (!response.ok) throw new Error(`Unable to load ${file}: ${response.status}`);
    return response.json();
  }

  async function loadDerived(file) {
    const response = await fetch(derivedBase + file);
    if (!response.ok) throw new Error(`Unable to load ${file}: ${response.status}`);
    return response.json();
  }

  let sourceTargets = { record_pages: {}, unresolved_record_pages: {}, price_pages: {}, source_health: {} };
  const sourceTargetsReady = loadDerived('source-targets-v2.9.4.json')
    .then(data => { sourceTargets = data || sourceTargets; return sourceTargets; })
    .catch(() => sourceTargets);

  const statusLabel = status => ({
    documented: 'Documented', qualified: 'Qualified', open: 'Open research', hold: 'Evidence hold',
    ready: 'Ready', 'ready-qualified': 'Ready · qualified'
  }[String(status || '').toLowerCase()] || status || 'Recorded');
  const statusClass = status => ({
    documented: 'status-documented', qualified: 'status-qualified', open: 'status-open', hold: 'status-hold',
    ready: 'status-documented', 'ready-qualified': 'status-qualified'
  }[String(status || '').toLowerCase()] || 'status-open');

  function publicTitle(value) {
    let title = String(value ?? '').replace(/\s+/g, ' ').trim();
    const exact = title.match(/^BMXMuseum\s+(\d+)\s*[—–-]\s*(.+)$/i);
    if (exact) return `${exact[2]} · External record ${exact[1]}`;
    title = title.replace(/BMXMuseum\s+Reference\s+(\d+)/gi, 'External reference $1');
    title = title.replace(/BMXMuseum\s+reference\s+lead/gi, 'External reference lead');
    return title.replace(/BMXMuseum/gi, 'External source');
  }

  function publicSummary(value) {
    let summary = String(value ?? '').replace(/\s+/g, ' ').trim();
    summary = summary.replace(/Public\s+BMXMuseum\s+record/gi, 'Public external record');
    summary = summary.replace(/BMXMuseum\s+reference\s+lead/gi, 'external reference lead');
    return summary.replace(/BMXMuseum/gi, 'external source');
  }

  function publicSourceBadge(value) {
    const text = String(value ?? '').replace(/\s+/g, ' ').trim();
    if (/BMXMuseum/i.test(text)) return /lead/i.test(text) ? 'External reference lead' : 'External source record';
    return publicTitle(text) || 'Source record';
  }

  function pageReference(record) {
    const override = sourceTargets?.record_pages?.[record?.id]?.page;
    if (override) return String(override);
    const match = String(record?.notes || '').match(/Indexed\s+(?:supplement\s+)?page(?:s|\(s\))?\s+(\d+)(?:\s*[–—-]\s*(\d+))?/i);
    if (!match) return null;
    return match[2] ? `${match[1]}–${match[2]}` : match[1];
  }

  function routeHealthForId(id) {
    return id ? sourceTargets?.source_health?.[id] || null : null;
  }

  function sourceRouteInfo(record) {
    const rawUrl = String(record?.primary_source_url || record?.source_url || '').trim();
    const health = routeHealthForId(record?.primary_source_id);
    if (health?.status === 'unavailable' && health?.fallback_url) {
      return {
        url: health.fallback_url,
        label: health.fallback_label || 'Open current fallback ↗',
        destination: 'Original registered route unavailable — opens a current corroborating source route.',
        page: null, health
      };
    }
    if (!rawUrl) return { url: '', label: '', destination: 'No public link is registered.', page: null };
    const page = pageReference(record);
    let parsed;
    try { parsed = new URL(rawUrl); } catch (_) {
      return { url: rawUrl, label: 'Open source ↗', destination: 'Registered public source route.', page };
    }
    const host = parsed.hostname.replace(/^www\./, '').toLowerCase();
    if (host.includes('previouspage.co.uk')) {
      parsed.hash = '';
      if (page) {
        const first = page.split('–')[0];
        return {
          url: `${parsed.toString()}#page/${first}`,
          label: 'View cited page ↗',
          destination: `Cited page ${page} in the issue.`,
          page
        };
      }
      return { url: parsed.toString(), label: 'Open issue source ↗', destination: 'Issue page — exact cited page remains unresolved; opens at the cover.', page: null };
    }
    const path = parsed.pathname.replace(/^\/+|\/+$/g, '');
    const access = normalize(`${record?.access_route || ''} ${record?.source_role || ''}`);
    if (access.includes('official')) {
      return { url: rawUrl, label: 'Open official source ↗', destination: path ? 'Specific page on the official source.' : 'Official source homepage — not a specific page.', page };
    }
    if (path) return { url: rawUrl, label: 'Open source page ↗', destination: 'Specific page on the source website.', page };
    return { url: rawUrl, label: 'Open source website ↗', destination: 'Source homepage — not a specific catalog or document page.', page };
  }

  function priceSourceRouteInfo(price, records) {
    const rawUrl = String(price?.source_url || '').trim();
    if (!rawUrl) return { url: '', label: '', destination: 'No public link is registered.', page: null };
    let parsed;
    try { parsed = new URL(rawUrl); } catch (_) {
      return { url: rawUrl, label: 'Open source ↗', destination: 'Registered public source route.', page: null };
    }
    const host = parsed.hostname.replace(/^www\./, '').toLowerCase();
    if (host.includes('previouspage.co.uk')) {
      parsed.hash = '';
      let page = sourceTargets?.price_pages?.[price?.id]?.page || null;
      if (!page) {
        const target = normalizedRouteUrl(rawUrl);
        const pages = [...new Set((records || [])
          .filter(record => record?.original_id === price?.source_object_id && normalizedRouteUrl(record?.primary_source_url) === target)
          .map(pageReference).filter(Boolean))];
        if (pages.length === 1) page = pages[0];
      }
      if (page) {
        const first = String(page).split('–')[0];
        return {
          url: `${parsed.toString()}#page/${first}`,
          label: 'View cited price page ↗',
          destination: `Cited price page ${page} in the issue.`,
          page: String(page)
        };
      }
      return { url: parsed.toString(), label: 'Open issue source ↗', destination: 'Issue page — exact cited price page remains unresolved; opens at the cover.', page: null };
    }
    const path = parsed.pathname.replace(/^\/+|\/+$/g, '');
    return { url: rawUrl, label: path ? 'Open source page ↗' : 'Open source website ↗', destination: path ? 'Specific page on the source website.' : 'Source homepage — not a specific page.', page: null };
  }

  function plainBoundary(record) {
    const rawSource = record?.source_identity || record?.source_family || 'the listed source';
    const source = /BMXMuseum/i.test(rawSource) ? 'an external source record' : rawSource;
    const date = String(record?.date_text || '').trim();
    const page = pageReference(record);
    const text = String(record?.evidence_limitation || '').replace(/\s+/g, ' ').trim();
    const pendingVisual = /page[- ]image comparison|visual comparison|visual identity|exact[- ]layout/i.test(text);
    const unresolved = /unresolved|remain(?:s)? open|locate|not exposed|not recoverable|title only|indexed title/i.test(text);
    if (pendingVisual && /previouspage/i.test(String(record?.access_host || record?.source_domain || ''))) {
      let result = `This record is based on indexed text from ${source}${date ? `, ${date}` : ''}.`;
      if (page) result += ` The indexed material is associated with page ${page}.`;
      result += ' It preserves issue-specific factual details. The page image has not yet been reviewed, so exact wording, layout and visual identifications are not asserted.';
      return result;
    }
    if (unresolved) return `This record preserves the publicly indexed information and the available route to ${source}. Details not exposed by that route remain open and are not presented here as confirmed facts.`;
    if (!text) return 'This record is limited to the indexed source occurrence and the facts stated on this page. It does not reproduce the underlying source material.';
    return text.replace(/BMXMuseum/gi, 'the external source')
      .replace(/Page-image comparison remains required before exact-layout quotation or visual identity merging\.?/gi, 'The page image has not yet been reviewed, so exact wording, page layout and visual identifications are not asserted.')
      .replace(/visual comparison pending/gi, 'visual page comparison has not yet been completed');
  }

  function publicRecordStatus(record) {
    const text = String(record?.research_status || '').toLowerCase();
    if (text.includes('included') || text.includes('ready')) return 'Documented in the register';
    if (text.includes('hold')) return 'Evidence review on hold';
    if (text.includes('qualified')) return 'Documented with qualifications';
    if (text.includes('open') || text.includes('lead') || text.includes('locate')) return 'Open research';
    return publicTitle(record?.research_status || record?.public_status || 'Recorded');
  }

  function verificationNote(record) {
    const text = `${record?.research_status || ''} ${record?.evidence_limitation || ''}`.toLowerCase();
    if (text.includes('visual comparison') || text.includes('page-image comparison')) return 'Visual page comparison remains open.';
    if (text.includes('exact reference') || text.includes('reference id')) return 'Exact reference details remain open.';
    if (text.includes('unresolved') || text.includes('locate') || text.includes('not exposed')) return 'Additional source verification remains open.';
    return '';
  }

  function objectExplanation(object, count) {
    const type = String(object?.object_type || 'historical item').toLowerCase();
    if (count === 1) return `This connected object represents a distinct ${type} documented by one source record. The source record remains separately visible with its own provenance and evidence limits.`;
    return `This connected object groups ${count.toLocaleString()} source records that describe the same ${type}. Each source occurrence remains separately visible so its provenance and evidence limits are not lost.`;
  }

  function objectResearchNote(object) {
    const text = String(object?.research_status || '').toLowerCase();
    if (text.includes('visual page inspected')) return 'The supporting page has been visually reviewed.';
    if (text.includes('visual comparison')) return 'Visual page comparison remains open.';
    if (text.includes('exact reference') || text.includes('locate')) return 'Exact reference details remain open.';
    return '';
  }

  const PERIOD_PUBLICATIONS = new Set(['BMX Action Bike', 'Bicross', 'BMX Plus!', 'GO', 'BMX Weekly']);
  const TOPICS = [
    { slug: 'magazines-publications', label: 'Magazines & Publications', description: 'Issue-level records from period BMX publications.', match: r => PERIOD_PUBLICATIONS.has(r.source_identity) },
    { slug: 'catalogs-product-literature', label: 'Catalogs & Product Literature', description: 'Catalogs, model pages and manufacturer product material.', match: r => r.category === 'Catalogs and product literature' },
    { slug: 'advertisements-price-lists', label: 'Advertisements & Price Lists', description: 'Period advertising, retail offers and price-list evidence.', match: r => r.category === 'Advertisements and price lists' },
    { slug: 'mailers-information-packs', label: 'Mailers, Stickers & Information Packs', description: 'Mail-in offers, sticker offers, fulfillment pieces and information packs.', match: r => r.category === 'Mailers, stickers, and information packs' },
    { slug: 'events-promotions', label: 'Events & Promotions', description: 'Race notices, registrations, memberships, contests and promotions.', match: r => ['Events, registration, and membership', 'Contests and promotions'].includes(r.category) },
    { slug: 'teams-riders-campaigns', label: 'Teams, Riders & Campaigns', description: 'Factory teams, rider-linked records and coordinated brand campaigns.', match: r => r.category === 'Teams, riders, and brand campaigns' },
    { slug: 'dealers-distributors', label: 'Dealers & Distributors', description: 'Shop, mail-order, dealer and distributor records.', match: r => r.category === 'Dealers and distributors' },
    { slug: 'technical-material', label: 'Product & Technical Material', description: 'Product announcements, specifications, kits and technical introductions.', match: r => r.category === 'Product announcements and technical material' },
    { slug: 'historical-documentation', label: 'Historical Documentation', description: 'Editorial tests, archive collections and retrospective product history.', match: r => r.category === 'Editorial tests and historical documentation' },
    { slug: 'submitted-comparison-records', label: 'Submitted Bicycles & Comparisons', description: 'External submitted records indexed with authentication boundaries intact.', match: r => r.category === 'Submitted bicycles and comparison records' }
  ];
  const topicBySlug = slug => TOPICS.find(topic => topic.slug === slug);

  function setParams(values) {
    const params = new URLSearchParams();
    Object.entries(values).forEach(([key, value]) => {
      if (value !== '' && value !== null && value !== undefined && value !== 1 && value !== '1') params.set(key, String(value));
    });
    const query = params.toString();
    history.replaceState({}, '', `${location.pathname}${query ? `?${query}` : ''}`);
  }

  const relativeUrl = () => `${location.pathname}${location.search}`;
  const returnStateKey = url => `pkr-return-state:${url}`;

  function returnLabel(url) {
    let parsed;
    try { parsed = new URL(url, location.origin); } catch (_) { return 'Back to results'; }
    const p = parsed.pathname;
    const q = parsed.searchParams;
    if (p.includes('/chronology/')) return 'Back to chronology';
    if (p.includes('/search/')) return 'Back to search results';
    if (p.includes('/object/')) return 'Back to connected object';
    if (p.includes('/sources/')) return 'Back to source directory';
    if (p.includes('/browse/')) {
      if (q.get('object')) return 'Back to supporting records';
      if (q.get('category') || q.get('topic')) return 'Back to category results';
      return 'Back to browse results';
    }
    if (p.includes('/record/') || p.includes('/records/')) return 'Back to source record';
    return 'Back to results';
  }

  function rememberReturnState(link) {
    const from = relativeUrl();
    const card = link.closest('[data-card-id]');
    const anchor = card?.dataset.cardId || '';
    try {
      sessionStorage.setItem(returnStateKey(from), JSON.stringify({ scrollY: window.scrollY, anchor }));
      sessionStorage.setItem('pkr-return-url', from);
    } catch (_) { /* optional */ }
    try {
      const target = new URL(link.href, location.href);
      if (target.origin === location.origin) {
        target.searchParams.set('from', from);
        if (anchor) target.searchParams.set('originCard', anchor);
        link.href = `${target.pathname}${target.search}${target.hash}`;
      }
    } catch (_) { /* retain original href */ }
  }

  function restoreReturnState() {
    const current = relativeUrl();
    try {
      const raw = sessionStorage.getItem(returnStateKey(current));
      if (!raw) return;
      const state = JSON.parse(raw);
      requestAnimationFrame(() => requestAnimationFrame(() => {
        const anchor = state.anchor ? document.querySelector(`[data-card-id="${CSS.escape(state.anchor)}"]`) : null;
        if (anchor) anchor.scrollIntoView({ block: 'center' });
        else window.scrollTo(0, Number(state.scrollY || 0));
        sessionStorage.removeItem(returnStateKey(current));
      }));
    } catch (_) { /* optional */ }
  }

  function bindResultNavigation(container) {
    container.addEventListener('click', event => {
      const link = event.target.closest('a[data-result-link]');
      if (!link || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      rememberReturnState(link);
    });
  }

  function getReturnContext(fallback = '../browse/') {
    const params = new URLSearchParams(location.search);
    let url = params.get('from') || '';
    try { if (!url) url = sessionStorage.getItem('pkr-return-url') || ''; } catch (_) { /* optional */ }
    if (!url || !url.startsWith('/')) url = fallback;
    return { url, label: returnLabel(url) };
  }

  function sourceAccessType(routes) {
    const text = normalize(routes.map(route => `${route.access_route} ${route.source_roles} ${route.notes}`).join(' '));
    if (text.includes('direct official') || text.includes('official archive') || text.includes('official organization')) return 'Direct or official source';
    if (text.includes('mirror')) return 'Public mirror';
    if (text.includes('publication accessed')) return 'Publication access archive';
    if (text.includes('archive')) return 'Public archive';
    if (text.includes('discovery') || text.includes('pinterest')) return 'Discovery route';
    return 'Registered public access';
  }

  function sourceDescription(identity, routes, related) {
    if (PERIOD_PUBLICATIONS.has(identity)) return 'Issue-level BMX magazine records currently reachable through registered public issue-access routes.';
    const categories = [...new Set(related.map(r => r.category).filter(Boolean))];
    const type = sourceAccessType(routes);
    if (type === 'Direct or official source') return 'Official or source-maintained material supporting catalogs, products, teams and related historical records.';
    if (type === 'Public mirror') return 'A public mirror providing access to indexed historical material while the original source identity remains distinct.';
    if (type === 'Discovery route') return 'A public discovery route used to locate indexed reference material; provenance and evidence limits remain explicit.';
    if (categories.length) return `Registered routes supporting ${categories.slice(0, 2).join(' and ').toLowerCase()} records in the register.`;
    return 'Registered public routes supporting indexed BMX historical records.';
  }

  function normalizedRouteUrl(value) {
    try {
      const parsed = new URL(String(value || '').trim());
      parsed.hash = '';
      parsed.pathname = parsed.pathname.replace(/\/+$/, '');
      return parsed.toString();
    } catch (_) { return String(value || '').trim().replace(/#.*$/, '').replace(/\/+$/, ''); }
  }

  function recordMatchesRoute(record, route) {
    if (record.primary_source_id === route.id || record.secondary_source_id === route.id) return true;
    const target = normalizedRouteUrl(route.url);
    return [record.primary_source_url, record.source_url, record.secondary_source_url]
      .filter(Boolean).some(value => normalizedRouteUrl(value) === target);
  }

  function recordsForRoute(route, records) {
    return records.filter(record => recordMatchesRoute(record, route));
  }

  function buildSourceGroups(sourceRoutes, sourceRecords) {
    const map = new Map();
    sourceRoutes.forEach(route => {
      const identity = route.source_identity || route.source_display || route.domain || 'Unassigned source';
      if (!map.has(identity)) map.set(identity, { identity, routes: [], records: [] });
      map.get(identity).routes.push(route);
    });
    sourceRecords.forEach(record => {
      const identity = record.source_identity || record.source_family || 'Unassigned source';
      if (!map.has(identity)) map.set(identity, { identity, routes: [], records: [] });
      map.get(identity).records.push(record);
    });
    return [...map.values()].map(group => {
      const relatedById = new Map(group.records.map(record => [record.id, record]));
      group.routes.forEach(route => recordsForRoute(route, sourceRecords).forEach(record => relatedById.set(record.id, record)));
      const records = [...relatedById.values()];
      const label = publicTitle(group.identity);
      const accessType = sourceAccessType(group.routes);
      const description = sourceDescription(group.identity, group.routes, records);
      return {
        ...group, records, label, accessType, description,
        recordCount: records.length,
        routeCount: group.routes.length,
        searchText: normalize([group.identity, label, description, accessType, ...group.routes.map(r => `${r.domain} ${r.notes}`)].join(' '))
      };
    }).sort((a, b) => b.recordCount - a.recordCount || a.label.localeCompare(b.label));
  }

  function cardShell({ status = 'documented', id, type, title, statusText, source, summary, actions }) {
    return `<article class="record-card compact uniform-card" data-status="${escapeHtml(status)}" data-card-id="${escapeHtml(id)}">
      <div class="record-id-slot"><span class="record-id">${escapeHtml(id)}</span></div>
      <div class="record-type-slot"><span class="record-type">${escapeHtml(type)}</span></div>
      <div class="record-title-slot"><h3>${escapeHtml(title)}</h3></div>
      <div class="record-status-slot">${statusText ? `<span class="metadata-chip ${statusClass(status)}">${escapeHtml(statusText)}</span>` : '<span aria-hidden="true" class="slot-placeholder">—</span>'}</div>
      <div class="record-source-slot">${source ? `<span class="metadata-chip source-badge" title="${escapeHtml(source)}">${escapeHtml(source)}</span>` : '<span aria-hidden="true" class="slot-placeholder">—</span>'}</div>
      <div class="record-summary-slot"><p class="card-summary">${escapeHtml(summary || 'Indexed Public Knowledge Register entry.')}</p></div>
      <div class="record-actions">${actions}</div>
    </article>`;
  }

  function sourceRecordCard(record) {
    const route = sourceRouteInfo(record);
    const actions = `<a data-result-link href="${registerRoot}records/${encodeURIComponent(record.id)}/">Open result →</a>${route.url ? `<a class="secondary-source-action" href="${escapeHtml(route.url)}" target="_blank" rel="noopener noreferrer">${route.label}</a>` : ''}`;
    return cardShell({
      status: record.public_status, id: record.id, type: record.object_type || 'Source record',
      title: publicTitle(record.title), statusText: `Research status: ${statusLabel(record.public_status)}`,
      source: `Source: ${publicSourceBadge(record.source_identity)}`, summary: publicSummary(record.primary_subject) || plainBoundary(record), actions
    });
  }

  function objectCard(object) {
    const total = Number(object.source_occurrence_count || object.member_record_ids?.length || 0);
    const actions = `<a data-result-link href="${registerRoot}object/?id=${encodeURIComponent(object.id)}">Open result →</a><a class="secondary-source-action" data-result-link href="${registerRoot}browse/?object=${encodeURIComponent(object.id)}">View supporting records →</a>`;
    return cardShell({
      status: /open|lead/i.test(object.research_status || '') ? 'open' : 'documented', id: object.id,
      type: object.object_type || 'Connected object', title: publicTitle(object.title),
      statusText: `Supporting records: ${total.toLocaleString()}`,
      source: `Category: ${object.category || 'Connected object'}`,
      summary: objectExplanation(object, total), actions
    });
  }

  function priceCard(price, records = []) {
    const route = priceSourceRouteInfo(price, records);
    const actions = `<a data-result-link href="${registerRoot}price/?id=${encodeURIComponent(price.id)}">Open result →</a>${price.source_record_id ? `<a data-result-link class="secondary-source-action" href="${registerRoot}records/${encodeURIComponent(price.source_record_id)}/">View source record →</a>` : route.url ? `<a class="secondary-source-action" href="${escapeHtml(route.url)}" target="_blank" rel="noopener noreferrer">${route.label}</a>` : ''}`;
    return cardShell({
      status: /medium|qualified/i.test(price.confidence || '') ? 'qualified' : 'documented', id: price.id,
      type: 'Price observation', title: `${price.brand || ''} ${price.product_model || ''} — ${price.displayed_price || 'Price recorded'}`.trim(),
      statusText: `Date: ${price.issue_date || 'Undated'}`, source: `Source: ${publicSourceBadge(price.source_identity || price.source_family)}`,
      summary: price.price_basis || price.normalization_note || 'Source-specific historical price evidence.', actions
    });
  }

  function chronologyCard(entry, recordMap) {
    const record = recordMap.get(entry.source_record_id);
    const route = sourceRouteInfo(record || entry);
    const actions = `<a data-result-link href="${registerRoot}records/${encodeURIComponent(entry.source_record_id)}/">Open source record →</a>${route.url ? `<a class="secondary-source-action" href="${escapeHtml(route.url)}" target="_blank" rel="noopener noreferrer">${route.label}</a>` : ''}`;
    return `<article class="chronology-card" data-card-id="${escapeHtml(entry.id)}"><div class="chronology-date"><strong>${escapeHtml(entry.date_text || 'Undated')}</strong><span>${escapeHtml(entry.id)}</span></div><div class="chronology-content"><span class="record-type">${escapeHtml(entry.object_type || 'Chronology entry')}</span><h3>${escapeHtml(publicTitle(entry.title))}</h3><p class="chronology-subject">${escapeHtml(entry.brand_promoter || publicSourceBadge(entry.source_identity))}</p><p class="chronology-note">${escapeHtml(entry.chronology_note || 'Dated or period placement')}</p></div><div class="chronology-actions record-actions">${actions}</div></article>`;
  }

  function sourceGroupCard(group) {
    const sourceParam = encodeURIComponent(group.identity);
    const browseAction = group.recordCount > 0
      ? `<a data-result-link href="${registerRoot}browse/?source=${sourceParam}">Browse records →</a>`
      : '<span class="no-records-action">No connected records yet</span>';
    return `<article class="source-group-card" data-card-id="source-${escapeHtml(normalize(group.identity).replace(/[^a-z0-9]+/g, '-'))}">
      <div class="source-group-meta"><span class="access-type">${escapeHtml(group.accessType)}</span><span>${group.routeCount.toLocaleString()} ${group.routeCount === 1 ? 'route' : 'routes'}</span></div>
      <h2>${escapeHtml(group.label)}</h2><p>${escapeHtml(group.description)}</p>
      <dl class="source-counts"><div><dt>Related records</dt><dd>${group.recordCount.toLocaleString()}</dd></div><div><dt>Registered routes</dt><dd>${group.routeCount.toLocaleString()}</dd></div></dl>
      <div class="record-actions">${browseAction}<a data-result-link href="${registerRoot}sources/?source=${sourceParam}#routes">View source routes →</a></div>
    </article>`;
  }

  function setPagination(pagination, pageLabel, prev, next, page, pages, itemCount) {
    pageLabel.textContent = `Page ${page} of ${pages}`;
    prev.disabled = page <= 1;
    next.disabled = page >= pages;
    if (pagination) pagination.hidden = itemCount === 0 || pages <= 1;
  }

  async function initHome() {
    const metricsHolder = document.querySelector('[data-register-metrics]');
    const categoriesHolder = document.querySelector('[data-category-tiles]');
    if (!metricsHolder && !categoriesHolder) return;
    const [metrics, records, routes] = await Promise.all([
      load('register-metrics-v2.9.0.json'), load('source-records-v2.3.0.json'), load('source-register-v2.3.0.json')
    ]);
    if (metricsHolder) {
      const values = {
        source_records: Number(metrics.source_records || records.length),
        canonical_objects: Number(metrics.canonical_objects || 0),
        price_observations: Number(metrics.price_observations || 0),
        registered_sources: Number(metrics.registered_source_urls || metrics.registered_sources || routes.length)
      };
      const metricLinks = [
        ['source_records', 'Source Records', 'browse/'], ['canonical_objects', 'Connected Objects', 'search/?layer=canonical_object'],
        ['price_observations', 'Price Observations', 'search/?layer=price_observation'], ['registered_sources', 'Registered Source URLs', 'sources/']
      ];
      metricsHolder.innerHTML = metricLinks.map(([key, label, href]) => `<a class="hero-stat metric-link" href="${href}"><strong>${values[key].toLocaleString()}</strong><span>${label}</span><small>Explore this section →</small></a>`).join('');
    }
    if (categoriesHolder) {
      categoriesHolder.innerHTML = TOPICS.map((topic, index) => {
        const count = records.filter(topic.match).length;
        return `<a class="category-card" href="browse/?topic=${encodeURIComponent(topic.slug)}"><span class="category-number">${String(index + 1).padStart(2, '0')}</span><h3>${escapeHtml(topic.label)}</h3><p>${escapeHtml(topic.description)}</p><strong>Browse ${count.toLocaleString()} ${count === 1 ? 'record' : 'records'} →</strong></a>`;
      }).join('');
    }
  }

  async function initBrowse() {
    const grid = document.querySelector('#register-record-grid');
    if (!grid) return;
    await sourceTargetsReady;
    const [records, sourceRoutes] = await Promise.all([load('source-records-v2.3.0.json'), load('source-register-v2.3.0.json')]);
    const sourceGroups = buildSourceGroups(sourceRoutes, records);
    const sourceRecordIds = new Map(sourceGroups.map(group => [group.identity, new Set(group.records.map(record => record.id))]));
    const search = document.querySelector('#register-search');
    const category = document.querySelector('#register-category');
    const source = document.querySelector('#register-source');
    const status = document.querySelector('#register-status');
    const count = document.querySelector('#register-count');
    const pageLabel = document.querySelector('#register-page');
    const prev = document.querySelector('#register-prev');
    const next = document.querySelector('#register-next');
    const reset = document.querySelector('#register-reset');
    const activeTopic = document.querySelector('#active-topic');
    const activeSummary = document.querySelector('#active-filter-summary');
    const pagination = pageLabel?.closest('.pagination');
    const heroTitle = document.querySelector('.page-hero h1');
    const heroCopy = document.querySelector('.page-hero p:not(.eyebrow)');
    const pageSize = 48;
    const params = new URLSearchParams(location.search);
    const fromParam = params.get('from') || '';
    let page = Math.max(1, Number(params.get('page') || '1'));
    let topicSlug = params.get('topic') || '';
    let objectId = params.get('object') || '';
    let decade = params.get('decade') || '';

    [...new Set(records.map(r => r.category).filter(Boolean))].sort().forEach(value => category.insertAdjacentHTML('beforeend', `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`));
    sourceGroups.filter(group => group.recordCount > 0).map(group => group.identity).sort().forEach(value => source.insertAdjacentHTML('beforeend', `<option value="${escapeHtml(value)}">${escapeHtml(publicTitle(value))}</option>`));
    search.value = params.get('q') || '';
    category.value = params.get('category') || '';
    source.value = params.get('source') || '';
    status.value = params.get('status') || '';

    function updateHero(filtered, topic) {
      if (!heroTitle || !heroCopy) return;
      if (objectId) {
        heroTitle.textContent = `Supporting records for ${objectId}.`;
        heroCopy.textContent = `Review ${filtered.length.toLocaleString()} source ${filtered.length === 1 ? 'record' : 'records'} connected to this object, with provenance and evidence limits kept visible.`;
      } else if (topic) {
        heroTitle.textContent = topic.label;
        heroCopy.textContent = `Browse ${filtered.length.toLocaleString()} source ${filtered.length === 1 ? 'record' : 'records'} in this topic.`;
      } else if (category.value) {
        heroTitle.textContent = category.value;
        heroCopy.textContent = `Browse ${filtered.length.toLocaleString()} source ${filtered.length === 1 ? 'record' : 'records'} in this category.`;
      } else if (source.value) {
        heroTitle.textContent = `Records from ${publicTitle(source.value)}.`;
        heroCopy.textContent = `Browse ${filtered.length.toLocaleString()} related source ${filtered.length === 1 ? 'record' : 'records'} while the source identity and access route remain distinct.`;
      } else if (decade) {
        heroTitle.textContent = `BMX records from the ${decade}s.`;
        heroCopy.textContent = `Browse ${filtered.length.toLocaleString()} source ${filtered.length === 1 ? 'record' : 'records'} placed in this decade.`;
      } else if (search.value.trim()) {
        heroTitle.textContent = `Browse results for “${search.value.trim()}”.`;
        heroCopy.textContent = `${filtered.length.toLocaleString()} source ${filtered.length === 1 ? 'record matches' : 'records match'} this search.`;
      } else {
        heroTitle.textContent = `Explore all ${records.length.toLocaleString()} source records.`;
        heroCopy.textContent = 'Filter by topic, category, source identity or evidence status. Every result explains what it is, where it came from and what to explore next.';
      }
    }

    function render(options = {}) {
      const q = normalize(search.value);
      const topic = topicBySlug(topicSlug);
      const filtered = records.filter(r => {
        const hay = normalize([r.id, r.title, r.brand_promoter, r.primary_subject, r.category, r.source_identity, r.access_host, r.source_role, r.exact_reference_id, r.research_status, r.date_text, r.canonical_object_id].join(' '));
        const decadeMatch = !decade || (Number(r.start_year) >= Number(decade) && Number(r.start_year) <= Number(decade) + 9);
        return (!q || q.split(' ').every(term => hay.includes(term))) && (!topic || topic.match(r)) && (!objectId || r.canonical_object_id === objectId) && decadeMatch && (!category.value || r.category === category.value) && (!source.value || sourceRecordIds.get(source.value)?.has(r.id)) && (!status.value || r.public_status === status.value);
      });
      const pages = Math.max(1, Math.ceil(filtered.length / pageSize));
      page = Math.max(1, Math.min(page, pages));
      const visible = filtered.slice((page - 1) * pageSize, page * pageSize);

      if (activeTopic) {
        const label = topic ? topic.label : objectId ? `Supporting records for ${objectId}` : decade ? `Records from the ${decade}s` : '';
        if (label) {
          activeTopic.hidden = false;
          const backLink = objectId ? `<a class="button" data-result-link href="${escapeHtml(fromParam || `../object/?id=${encodeURIComponent(objectId)}`)}">Back to connected object</a>` : '';
          activeTopic.innerHTML = `<div><span>Focused result set</span><strong>${escapeHtml(label)}</strong></div><div class="focus-actions">${backLink}<button class="button" type="button" id="clear-topic">Show all records</button></div>`;
          activeTopic.querySelector('#clear-topic').onclick = () => { topicSlug = ''; objectId = ''; decade = ''; page = 1; render({ scrollTop: true }); };
        } else {
          activeTopic.hidden = true;
          activeTopic.innerHTML = '';
        }
      }

      const filters = [];
      if (search.value.trim()) filters.push(`search “${search.value.trim()}”`);
      if (category.value) filters.push(category.value);
      if (source.value) filters.push(publicTitle(source.value));
      if (status.value) filters.push(statusLabel(status.value));
      if (decade) filters.push(`${decade}s`);
      if (objectId) activeSummary.textContent = `Showing ${filtered.length.toLocaleString()} source ${filtered.length === 1 ? 'record' : 'records'} supporting ${objectId}.`;
      else if (topic) activeSummary.textContent = `Showing ${filtered.length.toLocaleString()} source ${filtered.length === 1 ? 'record' : 'records'} in ${topic.label}.`;
      else activeSummary.textContent = filters.length ? `Active filters: ${filters.join(' · ')}` : 'Showing the complete source-record collection.';

      grid.innerHTML = visible.length ? visible.map(sourceRecordCard).join('') : `<div class="notice empty-state"><h2>No records matched.</h2><p>Try fewer words, remove one filter or search a broader year.</p><button class="button" type="button" id="empty-reset">Clear filters</button></div>`;
      grid.querySelector('#empty-reset')?.addEventListener('click', () => reset.click());
      count.textContent = `${filtered.length.toLocaleString()} ${filtered.length === 1 ? 'record' : 'records'} matched`;
      setPagination(pagination, pageLabel, prev, next, page, pages, filtered.length);
      updateHero(filtered, topic);
      setParams({ q: search.value.trim(), topic: topicSlug, object: objectId, decade, category: category.value, source: source.value, status: status.value, page, from: fromParam });
      if (options.scrollTop) window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    search.oninput = () => { page = 1; render(); };
    [category, source, status].forEach(el => { el.onchange = () => { page = 1; render(); }; });
    prev.onclick = () => { page--; render({ scrollTop: true }); };
    next.onclick = () => { page++; render({ scrollTop: true }); };
    reset.onclick = () => { search.value = ''; category.value = ''; source.value = ''; status.value = ''; topicSlug = ''; objectId = ''; decade = ''; page = 1; render({ scrollTop: true }); };
    bindResultNavigation(document.querySelector('main'));
    render();
    restoreReturnState();
  }

  async function initSearch() {
    const grid = document.querySelector('#universal-search-grid');
    if (!grid) return;
    await sourceTargetsReady;
    const [raw, sourceRoutes, records, objects, prices, chronology] = await Promise.all([
      load('universal-search-index-v2.3.0.json'), load('source-register-v2.3.0.json'), load('source-records-v2.3.0.json'), load('canonical-objects-v2.3.0.json'), load('price-observations-v2.3.0.json'), load('chronology-v2.3.0.json')
    ]);
    const recordMap = new Map(records.map(r => [r.id, r]));
    const objectMap = new Map(objects.map(o => [o.id, o]));
    const priceMap = new Map(prices.map(p => [p.id, p]));
    const chronologyMap = new Map(chronology.map(c => [c.id, c]));
    const groups = buildSourceGroups(sourceRoutes, records);
    const groupEntries = groups.map(group => ({ layer: 'registered_source', id: `SOURCE-${normalize(group.identity).replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')}`, title: group.label, subtitle: `${group.recordCount} related records · ${group.routeCount} registered routes`, source_identity: group.identity, status: 'documented', group, search_text: group.searchText }));
    const entries = raw.filter(e => e.layer !== 'registered_source').concat(groupEntries);
    const search = document.querySelector('#universal-search');
    const layer = document.querySelector('#universal-layer');
    const source = document.querySelector('#universal-source');
    const count = document.querySelector('#universal-count');
    const pageLabel = document.querySelector('#universal-page');
    const prev = document.querySelector('#universal-prev');
    const next = document.querySelector('#universal-next');
    const reset = document.querySelector('#universal-reset');
    const summary = document.querySelector('#universal-filter-summary');
    const pagination = pageLabel?.closest('.pagination');
    const heroTitle = document.querySelector('.page-hero h1');
    const heroCopy = document.querySelector('.page-hero p:not(.eyebrow)');
    const params = new URLSearchParams(location.search);
    const fromParam = params.get('from') || '';
    const pageSize = 48;
    let page = Math.max(1, Number(params.get('page') || '1'));
    [...new Set(entries.map(e => e.source_identity).filter(Boolean))].sort().forEach(value => source.insertAdjacentHTML('beforeend', `<option value="${escapeHtml(value)}">${escapeHtml(publicTitle(value))}</option>`));
    search.value = params.get('q') || '';
    layer.value = params.get('layer') || '';
    source.value = params.get('source') || '';

    function entryCard(entry) {
      if (entry.layer === 'registered_source') return sourceGroupCard(entry.group);
      if (entry.layer === 'source_record') return sourceRecordCard(recordMap.get(entry.id) || entry);
      if (entry.layer === 'canonical_object') return objectCard(objectMap.get(entry.id) || entry);
      if (entry.layer === 'price_observation') return priceCard(priceMap.get(entry.id) || entry, records);
      if (entry.layer === 'chronology') return chronologyCard(chronologyMap.get(entry.id) || entry, recordMap);
      const actions = `<a data-result-link href="${registerRoot}research/?id=${encodeURIComponent(entry.id)}">Open research summary →</a>`;
      return cardShell({ status: entry.status || 'documented', id: entry.id, type: 'Detailed research page', title: publicTitle(entry.title), statusText: `Research status: ${statusLabel(entry.status)}`, source: 'Source: Lititz BMX research', summary: entry.subtitle || 'Detailed research and synthesis page.', actions });
    }

    function render(options = {}) {
      const q = normalize(search.value);
      let filtered = entries.filter(e => {
        const hay = normalize(e.search_text || [e.id, e.title, e.subtitle, e.source_identity, e.category, e.year].join(' '));
        return (!q || q.split(' ').every(t => hay.includes(t))) && (!layer.value || e.layer === layer.value) && (!source.value || e.source_identity === source.value);
      });
      const exact = search.value.trim().toUpperCase();
      if (/^[A-Z]{2,12}-\d+$/.test(exact)) {
        const direct = entries.filter(e => String(e.id || '').toUpperCase() === exact && (!layer.value || e.layer === layer.value) && (!source.value || e.source_identity === source.value));
        if (direct.length) filtered = direct;
      }
      const pages = Math.max(1, Math.ceil(filtered.length / pageSize));
      page = Math.max(1, Math.min(page, pages));
      const visible = filtered.slice((page - 1) * pageSize, page * pageSize);
      grid.innerHTML = visible.length ? visible.map(entryCard).join('') : `<div class="notice empty-state"><h2>No entries matched.</h2><p>Try fewer words, search an exact ID or remove one filter.</p><button class="button" type="button" id="empty-search-reset">Clear search</button></div>`;
      grid.querySelector('#empty-search-reset')?.addEventListener('click', () => reset.click());
      const filters = [];
      if (search.value.trim()) filters.push(`search “${search.value.trim()}”`);
      if (layer.value) filters.push(layer.options[layer.selectedIndex].text);
      if (source.value) filters.push(publicTitle(source.value));
      summary.textContent = filters.length ? `Active filters: ${filters.join(' · ')}` : 'Searching all six register layers.';
      count.textContent = `${filtered.length.toLocaleString()} ${filtered.length === 1 ? 'entry' : 'entries'} matched`;
      setPagination(pagination, pageLabel, prev, next, page, pages, filtered.length);
      if (heroTitle && heroCopy) {
        if (search.value.trim()) {
          heroTitle.textContent = /^[A-Z]{2,12}-\d+$/i.test(search.value.trim()) && filtered.length === 1 ? `Exact match for ${search.value.trim().toUpperCase()}.` : `Search results for “${search.value.trim()}”.`;
          heroCopy.textContent = `${filtered.length.toLocaleString()} ${filtered.length === 1 ? 'entry matches' : 'entries match'} across the selected register layers.`;
        } else {
          heroTitle.textContent = 'Search the complete Public Knowledge Register.';
          heroCopy.textContent = 'Search by ordinary BMX terms or exact IDs. Each layer uses a consistent card and an action that accurately describes the destination.';
        }
      }
      setParams({ q: search.value.trim(), layer: layer.value, source: source.value, page, from: fromParam });
      if (options.scrollTop) window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    search.oninput = () => { page = 1; render(); };
    [layer, source].forEach(el => { el.onchange = () => { page = 1; render(); }; });
    prev.onclick = () => { page--; render({ scrollTop: true }); };
    next.onclick = () => { page++; render({ scrollTop: true }); };
    reset.onclick = () => { search.value = ''; layer.value = ''; source.value = ''; page = 1; render({ scrollTop: true }); };
    bindResultNavigation(document.querySelector('main'));
    render();
    restoreReturnState();
  }

  async function initSourceDirectory() {
    const grid = document.querySelector('#source-directory-grid');
    if (!grid) return;
    await sourceTargetsReady;
    const [routes, records] = await Promise.all([load('source-register-v2.3.0.json'), load('source-records-v2.3.0.json')]);
    const groups = buildSourceGroups(routes, records);
    const search = document.querySelector('#source-directory-search');
    const reset = document.querySelector('#source-directory-reset');
    const count = document.querySelector('#source-directory-count');
    const detail = document.querySelector('#source-directory-detail');
    const params = new URLSearchParams(location.search);
    search.value = params.get('q') || '';

    function render() {
      const q = normalize(search.value);
      const filtered = groups.filter(g => !q || q.split(' ').every(t => g.searchText.includes(t)));
      grid.innerHTML = filtered.length ? filtered.map(sourceGroupCard).join('') : `<div class="notice empty-state"><h2>No sources matched.</h2><p>Try the publication name, organization, archive or domain with fewer words.</p><button class="button" type="button" id="empty-source-reset">Clear search</button></div>`;
      grid.querySelector('#empty-source-reset')?.addEventListener('click', () => reset.click());
      count.textContent = `${filtered.length.toLocaleString()} grouped ${filtered.length === 1 ? 'source' : 'sources'} · ${filtered.reduce((sum, group) => sum + group.routeCount, 0).toLocaleString()} registered routes`;
      setParams({ q: search.value.trim(), source: params.get('source') || '' });
    }

    function dominantIssueDate(linked) {
      const counts = new Map();
      linked.forEach(record => {
        const value = String(record.date_text || '').replace(/\s+/g, ' ').trim();
        if (!value || /undated|exact .* open|campaign$/i.test(value)) return;
        counts.set(value, (counts.get(value) || 0) + 1);
      });
      return [...counts.entries()].sort((a, b) => b[1] - a[1] || b[0].length - a[0].length)[0]?.[0] || '';
    }

    function routePublicLabel(route, linked) {
      const identity = publicTitle(route.source_identity || route.source_display || route.domain || 'Registered source');
      let host = '';
      try { host = new URL(route.url).hostname.toLowerCase(); } catch (_) { /* no-op */ }
      const notes = String(route.notes || '').replace(/\s+/g, ' ').trim();
      if (host.includes('previouspage.co.uk')) {
        const issueDate = dominantIssueDate(linked);
        const volume = notes.match(/Volume\s+\d+\s+Number\s+\d+/i)?.[0] || '';
        return [identity, issueDate, volume].filter(Boolean).join(' — ');
      }
      if (notes && !/^(Ephemera object source|Price observation source|Ephemera object source; Price observation source)$/i.test(notes)) return publicTitle(notes);
      if (linked.length === 1) return `${publicTitle(linked[0].title)} · ${linked[0].date_text || 'Undated'}`;
      return `${identity} public route`;
    }

    function routeActionInfo(route) {
      const health = routeHealthForId(route?.id);
      if (health?.status === 'unavailable' && health?.fallback_url) {
        return { url: health.fallback_url, label: health.fallback_label || 'Open current fallback ↗', note: health.note || 'Original registered route unavailable.', fallback_url: '' };
      }
      if (health?.status === 'intermittent' && health?.fallback_url) {
        return { url: route.url, label: /official|organization/i.test(route.access_route || '') ? 'Open official source ↗' : 'Open source page ↗', note: health.note || 'Source availability has been intermittent.', fallback_url: health.fallback_url, fallback_label: health.fallback_label || 'Open official fallback ↗' };
      }
      let host = '';
      try { host = new URL(route.url).hostname.toLowerCase(); } catch (_) { /* no-op */ }
      if (host.includes('previouspage.co.uk')) return { url: route.url, label: 'Open issue source ↗', note: '', fallback_url: '' };
      if (/official|organization/i.test(route.access_route || '')) return { url: route.url, label: 'Open official source ↗', note: '', fallback_url: '' };
      return { url: route.url, label: 'Open source page ↗', note: '', fallback_url: '' };
    }

    function citedPageUrl(route, page) {
      const first = String(page).split('–')[0].trim();
      return `${String(route.url || '').replace(/#.*$/, '')}#page/${first}`;
    }

    function renderDetail() {
      const identity = params.get('source');
      if (!identity) { detail.innerHTML = ''; return; }
      const group = groups.find(g => g.identity === identity);
      if (!group) {
        detail.innerHTML = '<div class="notice"><h2>Source not found.</h2><p>The requested source identity is not available in this directory.</p><p><a class="button" href="./">Back to source directory</a></p></div>';
        return;
      }
      const routeRows = group.routes.map(route => {
        const linked = recordsForRoute(route, records);
        const pages = [...new Set(linked.map(pageReference).filter(Boolean))]
          .sort((a, b) => Number(String(a).match(/\d+/)?.[0] || 9999) - Number(String(b).match(/\d+/)?.[0] || 9999));
        const pageLinks = pages.length
          ? `<div class="cited-page-list"><span>Cited ${pages.length === 1 ? 'page' : 'pages'}:</span>${pages.map(page => `<a href="${escapeHtml(citedPageUrl(route, page))}" target="_blank" rel="noopener noreferrer">${escapeHtml(page)} ↗</a>`).join('')}</div>`
          : '<p class="route-page-note">No cited pages are currently connected to this route.</p>';
        const routeKind = /previouspage\.co\.uk/i.test(route.domain || route.url || '') ? 'Issue access through PreviousPage' : (route.access_route || 'Registered public access route');
        const action = routeActionInfo(route);
        const healthNote = action.note ? `<p class="route-page-note">${escapeHtml(action.note)}</p>` : '';
        const fallbackAction = action.fallback_url ? `<a class="secondary-source-action route-primary-action" href="${escapeHtml(action.fallback_url)}" target="_blank" rel="noopener noreferrer">${action.fallback_label}</a>` : '';
        return `<article data-card-id="${escapeHtml(route.id)}"><div class="source-route-main"><h3>${escapeHtml(routePublicLabel(route, linked))}</h3><span class="route-id">Registered route ${escapeHtml(route.id)}</span><p>${linked.length.toLocaleString()} linked ${linked.length === 1 ? 'record' : 'records'} · ${escapeHtml(routeKind)}</p>${pageLinks}${healthNote}</div><div class="record-actions"><a class="secondary-source-action route-primary-action" href="${escapeHtml(action.url)}" target="_blank" rel="noopener noreferrer">${action.label}</a>${fallbackAction}</div></article>`;
      }).join('');
      const browseAction = group.recordCount > 0
        ? `<a class="button primary" data-result-link href="../browse/?source=${encodeURIComponent(group.identity)}">Browse ${group.recordCount.toLocaleString()} related records →</a>`
        : '<span class="no-records-action detail-no-records">No connected records yet</span>';
      detail.innerHTML = `<section class="source-detail" id="routes"><p class="eyebrow">Source route detail</p><h2>${escapeHtml(group.label)}</h2><p>${escapeHtml(group.description)}</p><div class="source-detail-actions">${browseAction}<a class="button" href="./">Back to source directory</a></div><div class="source-route-list">${routeRows}</div></section>`;
      detail.scrollIntoView({ block: 'start' });
    }

    search.oninput = render;
    reset.onclick = () => { search.value = ''; history.replaceState({}, '', location.pathname); render(); detail.innerHTML = ''; };
    bindResultNavigation(document.querySelector('main'));
    render();
    renderDetail();
    restoreReturnState();
  }

  async function initChronology() {
    const holder = document.querySelector('#chronology-results');
    if (!holder) return;
    await sourceTargetsReady;
    const [entries, records] = await Promise.all([load('chronology-v2.3.0.json'), load('source-records-v2.3.0.json')]);
    const recordMap = new Map(records.map(r => [r.id, r]));
    const search = document.querySelector('#chronology-search');
    const decade = document.querySelector('#chronology-decade');
    const certainty = document.querySelector('#chronology-certainty');
    const reset = document.querySelector('#chronology-reset');
    const count = document.querySelector('#chronology-count');
    const pageLabel = document.querySelector('#chronology-page');
    const prev = document.querySelector('#chronology-prev');
    const next = document.querySelector('#chronology-next');
    const summary = document.querySelector('#chronology-filter-summary');
    const pagination = pageLabel?.closest('.pagination');
    const heroTitle = document.querySelector('.page-hero h1');
    const heroCopy = document.querySelector('.page-hero p:not(.eyebrow)');
    const params = new URLSearchParams(location.search);
    const fromParam = params.get('from') || '';
    const pageSize = 48;
    let page = Math.max(1, Number(params.get('page') || '1'));
    const decades = [...new Set(entries.map(e => e.start_year ? Math.floor(Number(e.start_year) / 10) * 10 : null).filter(Boolean))].sort((a, b) => a - b);
    decades.forEach(value => decade.insertAdjacentHTML('beforeend', `<option value="${value}">${value}s</option>`));
    search.value = params.get('q') || '';
    decade.value = params.get('decade') || '';
    certainty.value = params.get('certainty') || '';
    const certaintyOf = entry => {
      if (!entry.start_year) return 'undated';
      return /provisional|open|pending|approx|circa|unknown/i.test(`${entry.date_text} ${entry.chronology_note}`) ? 'provisional' : 'exact';
    };

    function render(options = {}) {
      const q = normalize(search.value);
      const filtered = entries.filter(entry => {
        const hay = normalize([entry.id, entry.title, entry.brand_promoter, entry.date_text, entry.object_type, entry.source_identity, entry.source_record_id, entry.chronology_note].join(' '));
        const entryDecade = entry.start_year ? Math.floor(Number(entry.start_year) / 10) * 10 : '';
        return (!q || q.split(' ').every(term => hay.includes(term))) && (!decade.value || String(entryDecade) === decade.value) && (!certainty.value || certaintyOf(entry) === certainty.value);
      });
      const pages = Math.max(1, Math.ceil(filtered.length / pageSize));
      page = Math.max(1, Math.min(page, pages));
      const visible = filtered.slice((page - 1) * pageSize, page * pageSize);
      const groups = new Map();
      visible.forEach(entry => {
        const key = entry.start_year ? `${Math.floor(Number(entry.start_year) / 10) * 10}s` : 'Undated';
        if (!groups.has(key)) groups.set(key, []);
        groups.get(key).push(entry);
      });
      holder.innerHTML = visible.length ? [...groups.entries()].map(([label, items]) => `<section class="chronology-decade"><div class="chronology-decade-heading"><h2>${label}</h2><span>${items.length} shown on this page</span></div><div class="chronology-list">${items.map(entry => chronologyCard(entry, recordMap)).join('')}</div></section>`).join('') : `<div class="notice empty-state"><h2>No chronology entries matched.</h2><p>Try a broader date, fewer words or reset the filters.</p><button class="button" type="button" id="empty-chronology-reset">Clear filters</button></div>`;
      holder.querySelector('#empty-chronology-reset')?.addEventListener('click', () => reset.click());
      const filters = [];
      if (search.value.trim()) filters.push(`search “${search.value.trim()}”`);
      if (decade.value) filters.push(`${decade.value}s`);
      if (certainty.value) filters.push(certainty.options[certainty.selectedIndex].text);
      summary.textContent = filters.length ? `Active filters: ${filters.join(' · ')}` : 'All chronology rows are shown with provisional placements clearly labeled.';
      count.textContent = `${filtered.length.toLocaleString()} of ${entries.length.toLocaleString()} chronology entries matched`;
      setPagination(pagination, pageLabel, prev, next, page, pages, filtered.length);
      if (heroTitle && heroCopy) {
        if (decade.value) {
          heroTitle.textContent = `Follow the register through the ${decade.value}s.`;
          heroCopy.textContent = `${filtered.length.toLocaleString()} chronology ${filtered.length === 1 ? 'entry is' : 'entries are'} placed in this decade, with uncertainty labeled rather than converted into false precision.`;
        } else {
          heroTitle.textContent = 'Follow the register through time.';
          heroCopy.textContent = `All ${entries.length.toLocaleString()} Source Records have one chronology entry. Exact, approximate and provisional placements remain labeled rather than being converted into false precision.`;
        }
      }
      setParams({ q: search.value.trim(), decade: decade.value, certainty: certainty.value, page, from: fromParam });
      if (options.scrollTop) window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    search.oninput = () => { page = 1; render(); };
    [decade, certainty].forEach(el => { el.onchange = () => { page = 1; render(); }; });
    reset.onclick = () => { search.value = ''; decade.value = ''; certainty.value = ''; page = 1; render({ scrollTop: true }); };
    prev.onclick = () => { page--; render({ scrollTop: true }); };
    next.onclick = () => { page++; render({ scrollTop: true }); };
    bindResultNavigation(document.querySelector('main'));
    render();
    restoreReturnState();
  }

  async function initRecord() {
    const holder = document.querySelector('#register-record-detail');
    if (!holder) return;
    await sourceTargetsReady;
    const id = new URLSearchParams(location.search).get('id');
    if (!id) {
      holder.innerHTML = '<div class="wrap missing-destination"><div class="notice"><h2>No record was selected.</h2><p>Choose a record from Browse Records or Universal Search.</p><div class="missing-actions"><a class="button primary" href="../search/">Search the register</a><a class="button" href="../browse/">Browse all records</a></div></div></div>';
      return;
    }
    const [records, objects, prices] = await Promise.all([load('source-records-v2.3.0.json'), load('canonical-objects-v2.3.0.json'), load('price-observations-v2.3.0.json')]);
    const record = records.find(item => item.id === id);
    if (!record) {
      holder.innerHTML = `<div class="wrap missing-destination"><div class="notice"><h2>Record not found.</h2><p>No record matched <strong>${escapeHtml(id)}</strong>.</p><div class="missing-actions"><a class="button primary" href="../search/?q=${encodeURIComponent(id)}">Search the register</a><a class="button" href="../browse/">Browse all records</a></div></div></div>`;
      return;
    }
    const object = objects.find(item => item.id === record.canonical_object_id);
    const price = prices.find(item => item.id === record.price_observation_id || item.source_record_id === record.id);
    const title = publicTitle(record.title);
    const context = getReturnContext('../browse/');
    const route = sourceRouteInfo(record);
    const related = [];
    if (record.source_identity) related.push(['More from this source', `../browse/?source=${encodeURIComponent(record.source_identity)}`]);
    if (record.start_year) {
      const decade = Math.floor(Number(record.start_year) / 10) * 10;
      related.push([`More from the ${decade}s`, `../browse/?decade=${decade}`]);
    }
    if (record.brand_promoter) related.push([`More about ${record.brand_promoter.split(';')[0].trim()}`, `../browse/?q=${encodeURIComponent(record.brand_promoter.split(';')[0].trim())}`]);
    related.push(['View this period in chronology', `../chronology/?q=${encodeURIComponent(record.id)}`]);
    const note = verificationNote(record);
    const boundaryBoxes = `<dl class="boundary-status"><div><dt>Documentation status</dt><dd>${escapeHtml(publicRecordStatus(record))}</dd></div>${note ? `<div><dt>Verification note</dt><dd>${escapeHtml(note)}</dd></div>` : ''}</dl>`;
    const objectCount = object ? Number(object.source_occurrence_count || object.member_record_ids?.length || 0) : 0;
    document.title = `${title} | Lititz BMX Public Knowledge Register`;
    holder.innerHTML = `<nav aria-label="Breadcrumb" class="breadcrumb wrap"><ol><li><a href="../">Register</a></li><li><a href="${escapeHtml(context.url)}">Results</a></li><li aria-current="page">${escapeHtml(record.id)}</li></ol></nav><section class="page-hero"><div class="wrap"><p class="eyebrow">Public Knowledge Register · Source record</p><h1>${escapeHtml(title)}</h1><p class="record-summary">${escapeHtml(publicSummary(record.primary_subject) || 'Indexed source occurrence with provenance and evidence limits.')}</p><div class="detail-meta"><span class="metadata-chip source-badge">Source: ${escapeHtml(publicSourceBadge(record.source_identity))}</span><span class="metadata-chip">Record: ${escapeHtml(record.id)}</span><span class="metadata-chip ${statusClass(record.public_status)}">Research status: ${escapeHtml(statusLabel(record.public_status))}</span></div><div class="hero-actions"><a class="button return-button" data-back-to-results="true" href="${escapeHtml(context.url)}">← ${escapeHtml(context.label)}</a></div></div></section><div class="wrap content-layout"><article><section id="identity"><h2>What is this?</h2><dl class="facts"><dt>Register ID</dt><dd>${escapeHtml(record.id)}</dd><dt>Record type</dt><dd>${escapeHtml(record.object_type || 'Source record')}</dd><dt>Date or period</dt><dd>${escapeHtml(record.date_text || 'Undated')}</dd><dt>Brand / promoter</dt><dd>${escapeHtml(record.brand_promoter || 'Not assigned')}</dd><dt>Category</dt><dd>${escapeHtml(record.category || 'Not assigned')}</dd><dt>Confidence</dt><dd>${escapeHtml(record.confidence || 'Not assigned')}</dd></dl></section><section id="supports"><h2>Why does it matter?</h2><p>${escapeHtml(publicSummary(record.primary_subject) || 'The public source occurrence and its indexed metadata.')}</p></section><section id="boundary"><h2>Evidence boundary</h2><div class="boundary"><p>${escapeHtml(plainBoundary(record))}</p>${boundaryBoxes}</div></section><section id="provenance"><h2>Source identity and access</h2><p><strong>Source identity:</strong> ${escapeHtml(record.source_identity)}</p><p><strong>Access host:</strong> ${escapeHtml(record.access_host || 'Not assigned')}</p><p><strong>Access route:</strong> ${escapeHtml(record.access_route || 'Not assigned')}</p><p><strong>Link destination:</strong> ${escapeHtml(route.destination)}</p><p>${escapeHtml(record.source_provenance_note || '')}</p>${route.url ? `<p><a class="button secondary-source-action" href="${escapeHtml(route.url)}" target="_blank" rel="noopener noreferrer">${route.label}</a></p>` : ''}</section>${object ? `<section id="object"><h2>Connected object</h2><p><strong>${escapeHtml(object.id)}</strong> · ${escapeHtml(publicTitle(object.title))}</p><p>${escapeHtml(objectExplanation(object, objectCount))}</p><div class="record-actions"><a data-result-link href="../object/?id=${encodeURIComponent(object.id)}">Open connected object →</a><a data-result-link href="../browse/?object=${encodeURIComponent(object.id)}">View ${objectCount.toLocaleString()} supporting ${objectCount === 1 ? 'record' : 'records'} →</a></div></section>` : ''}${price ? `<section id="price"><h2>Related price evidence</h2><p><strong>${escapeHtml(price.displayed_price || '')}</strong> · ${escapeHtml(price.brand || '')} ${escapeHtml(price.product_model || '')}</p><p>${escapeHtml(price.price_basis || '')}</p><p><a data-result-link href="../price/?id=${encodeURIComponent(price.id)}">Open price observation →</a></p></section>` : ''}<section id="related-exploration"><h2>What should I explore next?</h2><div class="related-link-grid">${related.slice(0, 4).map(([label, href]) => `<a class="related-link" data-result-link href="${href}">${escapeHtml(label)} →</a>`).join('')}</div></section></article><aside><nav class="toc" aria-label="Record navigation"><h2>On this record</h2><a href="#identity">What is this?</a><a href="#supports">Why it matters</a><a href="#boundary">Evidence boundary</a><a href="#provenance">Source and access</a>${object ? '<a href="#object">Connected object</a>' : ''}<a href="#related-exploration">Explore next</a><a class="toc-return" data-back-to-results="true" href="${escapeHtml(context.url)}">${escapeHtml(context.label)}</a></nav></aside></div>`;
    bindResultNavigation(holder);
  }

  async function initObject() {
    const holder = document.querySelector('#register-object-detail');
    if (!holder) return;
    await sourceTargetsReady;
    const id = new URLSearchParams(location.search).get('id');
    const [objects, records] = await Promise.all([load('canonical-objects-v2.3.0.json'), load('source-records-v2.3.0.json')]);
    const object = objects.find(item => item.id === id);
    if (!object) {
      holder.innerHTML = '<div class="wrap missing-destination"><div class="notice"><h2>Connected object not found.</h2><p><a class="button primary" href="../search/?layer=canonical_object">Browse connected objects</a></p></div></div>';
      return;
    }
    const supporting = records.filter(record => (object.member_record_ids || []).includes(record.id) || record.canonical_object_id === object.id);
    const context = getReturnContext('../search/?layer=canonical_object');
    const explanation = objectExplanation(object, supporting.length);
    const note = objectResearchNote(object);
    document.title = `${publicTitle(object.title)} | Connected Object`;
    const focusedLink = supporting.length > 1 ? `<a data-result-link href="../browse/?object=${encodeURIComponent(object.id)}">View focused supporting-record list</a>` : '';
    holder.innerHTML = `<nav class="breadcrumb wrap"><ol><li><a href="../">Register</a></li><li><a href="../search/?layer=canonical_object">Connected Objects</a></li><li aria-current="page">${escapeHtml(object.id)}</li></ol></nav><section class="page-hero"><div class="wrap"><p class="eyebrow">Public Knowledge Register · Connected object</p><h1>${escapeHtml(publicTitle(object.title))}</h1><p>${escapeHtml(explanation)}</p><div class="hero-actions"><a class="button return-button" href="${escapeHtml(context.url)}">← ${escapeHtml(context.label)}</a></div></div></section><div class="wrap content-layout"><article><section><h2>Object identity</h2><dl class="facts"><dt>Object ID</dt><dd>${escapeHtml(object.id)}</dd><dt>Type</dt><dd>${escapeHtml(object.object_type || 'Connected object')}</dd><dt>Date</dt><dd>${escapeHtml(object.date_text || 'Not assigned')}</dd><dt>Brand / promoter</dt><dd>${escapeHtml(object.brand_promoter || 'Not assigned')}</dd><dt>Category</dt><dd>${escapeHtml(object.category || 'Not assigned')}</dd><dt>Confidence</dt><dd>${escapeHtml(object.confidence || 'Not assigned')}</dd></dl></section><section><h2>What the connection means</h2><p>${escapeHtml(explanation)}</p>${note ? `<p>${escapeHtml(note)}</p>` : ''}</section><section><h2>Supporting source records</h2><p>${supporting.length.toLocaleString()} ${supporting.length === 1 ? 'source record supports' : 'source records support'} this object.</p><div class="record-grid object-support-grid">${supporting.slice(0, 6).map(sourceRecordCard).join('')}</div>${supporting.length > 6 ? `<p><a class="button" data-result-link href="../browse/?object=${encodeURIComponent(object.id)}">View all ${supporting.length.toLocaleString()} supporting records →</a></p>` : ''}</section></article><aside><nav class="toc"><h2>Explore</h2><a href="${escapeHtml(context.url)}">${escapeHtml(context.label)}</a>${focusedLink}<a href="../search/?layer=canonical_object">Browse connected objects</a></nav></aside></div>`;
    bindResultNavigation(holder);
  }

  async function initPrice() {
    const holder = document.querySelector('#register-price-detail');
    if (!holder) return;
    await sourceTargetsReady;
    const id = new URLSearchParams(location.search).get('id');
    const [prices, records, objects] = await Promise.all([load('price-observations-v2.3.0.json'), load('source-records-v2.3.0.json'), load('canonical-objects-v2.3.0.json')]);
    const price = prices.find(item => item.id === id);
    if (!price) {
      holder.innerHTML = '<div class="wrap missing-destination"><div class="notice"><h2>Price observation not found.</h2><p><a class="button primary" href="../search/?layer=price_observation">Browse price observations</a></p></div></div>';
      return;
    }
    const record = records.find(item => item.id === price.source_record_id);
    const object = objects.find(item => item.id === price.canonical_object_id);
    const sourceRoute = priceSourceRouteInfo(price, records);
    const context = getReturnContext('../search/?layer=price_observation');
    document.title = `${price.brand || ''} ${price.product_model || ''} | Price Observation`;
    holder.innerHTML = `<nav class="breadcrumb wrap"><ol><li><a href="../">Register</a></li><li><a href="../search/?layer=price_observation">Price Observations</a></li><li aria-current="page">${escapeHtml(price.id)}</li></ol></nav><section class="page-hero"><div class="wrap"><p class="eyebrow">Public Knowledge Register · Price observation</p><h1>${escapeHtml(`${price.brand || ''} ${price.product_model || ''}`.trim())}</h1><p>${escapeHtml(price.displayed_price || 'Price not exposed')} · ${escapeHtml(price.issue_date || 'Undated')}</p><div class="hero-actions"><a class="button return-button" href="${escapeHtml(context.url)}">← ${escapeHtml(context.label)}</a></div></div></section><div class="wrap content-layout"><article><section><h2>What was observed?</h2><dl class="facts"><dt>Observation ID</dt><dd>${escapeHtml(price.id)}</dd><dt>Displayed price</dt><dd>${escapeHtml(price.displayed_price || 'Not exposed')}</dd><dt>Price basis</dt><dd>${escapeHtml(price.price_basis || 'Not assigned')}</dd><dt>Currency</dt><dd>${escapeHtml(price.currency || 'Unconfirmed')}</dd><dt>Geography</dt><dd>${escapeHtml(price.geography_context || 'Unresolved')}</dd><dt>Confidence</dt><dd>${escapeHtml(price.confidence || 'Not assigned')}</dd></dl></section><section><h2>Evidence boundary</h2><p>${escapeHtml(price.normalization_note || 'This is a source-specific observation and is not automatically treated as MSRP, dealer cost or a completed transaction price.')}</p></section><section><h2>Source and related records</h2><p><strong>Source identity:</strong> ${escapeHtml(price.source_identity || price.source_family || 'Not assigned')}</p>${record ? `<p><a data-result-link href="../record/?id=${encodeURIComponent(record.id)}">Open source record ${escapeHtml(record.id)} →</a></p>` : ''}${object ? `<p><a data-result-link href="../object/?id=${encodeURIComponent(object.id)}">Open connected object ${escapeHtml(object.id)} →</a></p>` : ''}${sourceRoute.url ? `<p><strong>Link destination:</strong> ${escapeHtml(sourceRoute.destination)}</p><p><a class="button" href="${escapeHtml(sourceRoute.url)}" target="_blank" rel="noopener noreferrer">${sourceRoute.label}</a></p>` : ''}</section></article><aside><nav class="toc"><h2>Explore</h2><a href="${escapeHtml(context.url)}">${escapeHtml(context.label)}</a></nav></aside></div>`;
    bindResultNavigation(holder);
  }

  async function initResearch() {
    const holder = document.querySelector('#register-research-detail');
    if (!holder) return;
    const id = new URLSearchParams(location.search).get('id');
    const entries = await load('universal-search-index-v2.3.0.json');
    const entry = entries.find(item => item.layer === 'research_page' && item.id === id);
    if (!entry) {
      holder.innerHTML = '<div class="wrap missing-destination"><div class="notice"><h2>Research page not found.</h2><p><a class="button primary" href="../search/?layer=research_page">Browse research pages</a></p></div></div>';
      return;
    }
    const context = getReturnContext('../search/?layer=research_page');
    document.title = `${publicTitle(entry.title)} | Detailed Research`;
    holder.innerHTML = `<nav class="breadcrumb wrap"><ol><li><a href="../">Register</a></li><li><a href="../search/?layer=research_page">Detailed Research Pages</a></li><li aria-current="page">${escapeHtml(entry.id)}</li></ol></nav><section class="page-hero"><div class="wrap"><p class="eyebrow">Lititz BMX · Detailed research page</p><h1>${escapeHtml(publicTitle(entry.title))}</h1><p>${escapeHtml(entry.subtitle || 'Detailed Lititz BMX research and synthesis page.')}</p><div class="hero-actions"><a class="button return-button" href="${escapeHtml(context.url)}">← ${escapeHtml(context.label)}</a></div></div></section><section class="section"><div class="wrap"><div class="notice"><h2>About this destination</h2><p>This is a hand-built Lititz BMX research page rather than a separately countable Source Record. Open the current page when you are ready to continue to the full research destination.</p>${entry.target_url ? `<p><a class="button primary" data-live-exit="true" href="${escapeHtml(entry.target_url)}">Open current research page →</a></p>` : ''}</div></div></section>`;
  }

  const fail = (selector, error) => {
    const holder = document.querySelector(selector);
    if (holder) holder.innerHTML = `<div class="notice">${escapeHtml(error.message)}. Start the included local server and reload this page.</div>`;
  };

  initHome().catch(error => document.querySelectorAll('[data-register-metrics],[data-category-tiles]').forEach(holder => { holder.innerHTML = `<div class="notice">${escapeHtml(error.message)}. Start the included local server and reload this page.</div>`; }));
  initBrowse().catch(error => fail('#register-record-grid', error));
  initSearch().catch(error => fail('#universal-search-grid', error));
  initSourceDirectory().catch(error => fail('#source-directory-grid', error));
  initChronology().catch(error => fail('#chronology-results', error));
  initRecord().catch(error => fail('#register-record-detail', error));
  initObject().catch(error => fail('#register-object-detail', error));
  initPrice().catch(error => fail('#register-price-detail', error));
  initResearch().catch(error => fail('#register-research-detail', error));
})();
