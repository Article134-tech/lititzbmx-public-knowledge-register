
(() => {
  const BASE = window.LBMX_BASE_PATH || '/';
  const normalize = (value) => (value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
  const escapeHTML = (value) => String(value ?? '').replace(/[&<>'"]/g, (char) => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
  const layerLabels = {source_record:'Records',canonical_object:'Objects',price_observation:'Prices',public_claim:'Claims',source:'Sources',chronology:'Timeline'};
  const layerSingular = {source_record:'Source record',canonical_object:'Canonical object',price_observation:'Price observation',public_claim:'Public claim',source:'Registered source',chronology:'Timeline entry'};
  const highlight = (text, terms) => {
    let output = escapeHTML(text || '');
    [...terms].sort((a,b)=>b.length-a.length).forEach((term) => {
      if (!term) return;
      const safe = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      output = output.replace(new RegExp(`(${safe})`, 'ig'), '<mark>$1</mark>');
    });
    return output;
  };
  const resolveURL = (url) => {
    if (!url) return BASE;
    if (/^https?:/.test(url)) return url;
    return BASE + url.replace(/^\//,'');
  };

  document.querySelectorAll('[data-copy]').forEach((button) => {
    button.addEventListener('click', async () => {
      const value = button.dataset.copy || '';
      try { await navigator.clipboard.writeText(value); }
      catch { const area=document.createElement('textarea'); area.value=value; document.body.append(area); area.select(); document.execCommand('copy'); area.remove(); }
      const feedback = button.parentElement.querySelector('[data-copy-feedback]');
      if (feedback) { feedback.textContent = 'Copied.'; setTimeout(()=>feedback.textContent='',1800); }
    });
  });

  const recordMeta = document.querySelector('[data-record-meta]');
  if (recordMeta) {
    const entry = {id:recordMeta.dataset.id,title:recordMeta.dataset.title,url:location.pathname,viewed_at:new Date().toISOString()};
    let recent=[]; try { recent=JSON.parse(localStorage.getItem('lbmx:recent')||'[]'); } catch {}
    recent=[entry,...recent.filter((x)=>x.id!==entry.id)].slice(0,8);
    localStorage.setItem('lbmx:recent',JSON.stringify(recent));
    const back = document.querySelector('[data-return-search]');
    const last = sessionStorage.getItem('lbmx:lastSearch');
    if (back && last) { back.href=last; back.hidden=false; }
  }

  const recentRoot = document.querySelector('[data-recent-viewed]');
  if (recentRoot) {
    let recent=[]; try { recent=JSON.parse(localStorage.getItem('lbmx:recent')||'[]'); } catch {}
    if (recent.length) {
      recentRoot.innerHTML=recent.slice(0,6).map((item)=>`<a href="${escapeHTML(item.url)}"><strong>${escapeHTML(item.title)}</strong><span>${escapeHTML(item.id)}</span></a>`).join('');
      recentRoot.closest('[data-recent-section]').hidden=false;
    }
  }

  document.querySelectorAll('[data-progressive]').forEach((root) => {
    const size = Number(root.dataset.pageSize || 24);
    const children=[...root.children];
    let visible=size;
    const button=document.querySelector(`[data-load-more][data-target="${root.id}"]`);
    const update=()=>{ children.forEach((item,i)=>item.hidden=i>=visible); if(button) button.hidden=visible>=children.length; };
    if(button) button.addEventListener('click',()=>{visible+=size;update();});
    update();
  });

  const browse = document.querySelector('[data-browse-root]');
  if (browse) {
    const items=[...browse.querySelectorAll('[data-browse-item]')];
    const input=document.querySelector('[data-browse-search]');
    const category=document.querySelector('[data-browse-category]');
    const decade=document.querySelector('[data-browse-decade]');
    const count=document.querySelector('[data-browse-count]');
    const empty=document.querySelector('[data-browse-empty]');
    const update=()=>{
      const q=normalize(input?.value||''); const cat=category?.value||''; const dec=decade?.value||'';
      let shown=0;
      items.forEach((item)=>{ const ok=(!q||normalize(item.textContent).includes(q))&&(!cat||item.dataset.category===cat)&&(!dec||item.dataset.decade===dec); item.hidden=!ok; if(ok)shown++; });
      if(count)count.textContent=String(shown); if(empty)empty.hidden=shown!==0;
    };
    [input,category,decade].filter(Boolean).forEach((control)=>control.addEventListener(control.tagName==='INPUT'?'input':'change',update));
    update();
  }

  const searchRoot = document.querySelector('[data-universal-search]');
  if (!searchRoot) return;
  const input=searchRoot.querySelector('[data-search-input]');
  const results=searchRoot.querySelector('[data-search-results]');
  const count=searchRoot.querySelector('[data-search-count]');
  const summary=searchRoot.querySelector('[data-search-summary]');
  const empty=searchRoot.querySelector('[data-search-empty]');
  const loading=searchRoot.querySelector('[data-search-loading]');
  const loadMore=searchRoot.querySelector('[data-search-more]');
  const filters=[...searchRoot.querySelectorAll('[data-layer-filter]')];
  let entries=[]; let layer='all'; let visible=20; let current=[];

  const params=new URLSearchParams(location.search);
  input.value=params.get('label')||params.get('q')||'';
  layer=params.get('layer')||'all';
  let matchMode=params.get('match')==='any'?'any':'all';
  let rangeStart=Number(params.get('id_start')||0);
  let rangeEnd=Number(params.get('id_end')||0);
  let rangeLabel=params.get('label')||'';
  filters.forEach((b)=>b.setAttribute('aria-pressed',String(b.dataset.layerFilter===layer)));

  const termMatches=(text,term)=>term.length<=2?new Set(text.split(/\s+/)).has(term):text.includes(term);
  const scoreEntry=(entry,terms,raw)=>{
    const id=normalize(entry.id); const title=normalize(entry.title); const brand=normalize(entry.brand); const year=normalize(entry.year);
    const text=(entry.search_text||normalize([entry.id,entry.title,entry.summary,entry.brand,entry.year,entry.date,entry.object_type,entry.category,entry.geography,entry.status].join(' ')))+' '+(entry.register_text||'');
    const matched=matchMode==='any'?terms.some((term)=>termMatches(text,term)):terms.every((term)=>termMatches(text,term));
    if(!matched)return -1;
    let score=0;
    if(id===normalize(raw))score+=10000;
    if(title===normalize(raw))score+=5000;
    if(title.includes(normalize(raw)))score+=1500;
    terms.forEach((term)=>{ if(id.includes(term))score+=900; if(title.includes(term))score+=450; if(brand.includes(term))score+=260; if(year===term)score+=220; });
    if(entry.layer==='source_record')score+=25;
    return score;
  };
  const matchedFields=(entry,terms)=>{
    const fields=[['ID',entry.id],['title',entry.title],['brand / people',entry.brand],['date',entry.date||entry.year],['category',entry.category],['summary',entry.summary]];
    return fields.filter(([,value])=>terms.some((term)=>termMatches(normalize(value),term))).map(([label])=>label).slice(0,3);
  };
  const recordNumber=(entry)=>Number(((entry.id||'').match(/\d+/)||['0'])[0]);
  const clearCurated=()=>{rangeStart=0;rangeEnd=0;rangeLabel='';matchMode='all';};
  const render=()=>{
    const raw=input.value.trim(); const terms=normalize(raw).split(/\s+/).filter(Boolean); const hasRange=rangeStart>0&&rangeEnd>=rangeStart;
    const url=new URL(location.href);
    if(raw)url.searchParams.set('q',raw);else url.searchParams.delete('q');
    if(layer!=='all')url.searchParams.set('layer',layer);else url.searchParams.delete('layer');
    if(matchMode==='any')url.searchParams.set('match','any');else url.searchParams.delete('match');
    if(hasRange){url.searchParams.set('id_start',String(rangeStart));url.searchParams.set('id_end',String(rangeEnd));if(rangeLabel)url.searchParams.set('label',rangeLabel);}else{url.searchParams.delete('id_start');url.searchParams.delete('id_end');url.searchParams.delete('label');}
    history.replaceState({},'',url);
    if(terms.length===0&&!hasRange&&layer==='all'){current=[];results.innerHTML='';count.textContent='0';summary.textContent='Type a name, brand, year, publication, product, or exact ID.';empty.hidden=true;loadMore.hidden=true;return;}
    const scored=[];
    entries.forEach((entry)=>{
      if(layer!=='all'&&entry.layer!==layer)return;
      if(hasRange){const num=recordNumber(entry);if(entry.layer!=='source_record'||num<rangeStart||num>rangeEnd)return;scored.push({entry,score:0});return;}
      if(terms.length===0){scored.push({entry,score:0});return;}
      const score=scoreEntry(entry,terms,raw);if(score>=0)scored.push({entry,score});
    });
    scored.sort((a,b)=>b.score-a.score||a.entry.id.localeCompare(b.entry.id)); current=scored.map((x)=>x.entry);
    const visibleEntries=current.slice(0,visible);
    results.innerHTML=visibleEntries.map((entry)=>{
      const matches=matchedFields(entry,terms); const status=entry.status||entry.confidence||'';
      return `<article class="result-card" data-search-result tabindex="-1"><div class="result-top"><span class="eyebrow">${escapeHTML(layerSingular[entry.layer]||entry.layer)}</span>${status?`<span class="badge badge-${/open|lead|review|pending|provisional|estimate|medium/i.test(status)?'review':'ready'}">${escapeHTML(status.length>60?status.slice(0,57)+'…':status)}</span>`:''}</div><h2><a href="${escapeHTML(resolveURL(entry.url))}" data-result-link>${highlight(entry.title,terms)}</a></h2><p class="result-id">${highlight(entry.id,terms)}${entry.date?` · ${highlight(entry.date,terms)}`:''}${entry.brand?` · ${highlight(entry.brand,terms)}`:''}</p>${entry.summary?`<p>${highlight(entry.summary,terms)}</p>`:''}<p class="match-note">${hasRange?'Included in the curated '+escapeHTML(rangeLabel||'publication')+' sequence.':'Matched '+(matches.length?matches.join(', '):'indexed public fields')+'.'}</p></article>`;
    }).join('');
    count.textContent=String(current.length);
    summary.textContent=hasRange?`${current.length.toLocaleString()} records in ${rangeLabel||'this curated publication run'}.`:`${current.length.toLocaleString()} result${current.length===1?'':'s'}${layer==='all'?'':` in ${layerLabels[layer]||layer}`}.`;
    empty.hidden=current.length!==0; loadMore.hidden=visibleEntries.length>=current.length;
    results.querySelectorAll('[data-result-link]').forEach((link)=>link.addEventListener('click',()=>{sessionStorage.setItem('lbmx:lastSearch',location.href);sessionStorage.setItem('lbmx:lastSearchScroll',String(scrollY));}));
  };
  const searchForm=searchRoot.querySelector('[data-search-form]');
  searchForm?.addEventListener('submit',(event)=>{event.preventDefault();clearCurated();visible=20;render();input.focus();});
  input.addEventListener('input',()=>{clearCurated();visible=20;render();});
  filters.forEach((button)=>button.addEventListener('click',()=>{clearCurated();layer=button.dataset.layerFilter;visible=20;filters.forEach((b)=>b.setAttribute('aria-pressed',String(b===button)));render();}));
  loadMore.addEventListener('click',()=>{visible+=20;render();});
  document.addEventListener('keydown',(event)=>{
    if(!searchRoot.contains(document.activeElement))return;
    const cards=[...results.querySelectorAll('[data-search-result]')]; const currentIndex=cards.indexOf(document.activeElement);
    if(event.key==='ArrowDown'&&cards.length){event.preventDefault();(cards[Math.min(cards.length-1,currentIndex+1)]||cards[0]).focus();}
    if(event.key==='ArrowUp'&&cards.length){event.preventDefault();(cards[Math.max(0,currentIndex-1)]||cards[0]).focus();}
    if(event.key==='Enter'&&currentIndex>=0){cards[currentIndex].querySelector('a')?.click();}
    if(event.key==='Escape'){input.value='';clearCurated();input.focus();visible=20;render();}
  });
  fetch(BASE+'data/universal-search-index-v2.0.0.json').then((r)=>{if(!r.ok)throw new Error('Search index failed');return r.json();}).then((payload)=>{entries=payload.entries||[];loading.hidden=true;render();const scroll=Number(sessionStorage.getItem('lbmx:lastSearchScroll')||0);if(scroll&&location.href===sessionStorage.getItem('lbmx:lastSearch'))requestAnimationFrame(()=>scrollTo(0,scroll));}).catch(()=>{loading.textContent='Search could not load. The browse pages remain available.';});
})();
