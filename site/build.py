from __future__ import annotations

from collections import defaultdict, Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
import csv
import hashlib
import html
import json
import os
import re
import shutil
import unicodedata
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '_site'
DATA = ROOT / 'data'
DOCS = ROOT / 'docs'
DOWNLOADS = ROOT / 'downloads'
SITE = ROOT / 'site'
ASSETS = SITE / 'assets'
REVIEW = ROOT / 'review'
BASE_PATH = '/lititzbmx-public-knowledge-register/'
BASE_URL = 'https://article134-tech.github.io/lititzbmx-public-knowledge-register/'
REPO_URL = 'https://github.com/Article134-tech/lititzbmx-public-knowledge-register'
ARCHIVE_URL = 'https://www.lititzbmx.com'
YOUTUBE_URL = 'https://www.youtube.com/@LititzBMX17543'
SPOTIFY_URL = 'https://open.spotify.com/show/50iXYKiNPlsvM47ZPZL1Fi'
FACEBOOK_URL = 'https://www.facebook.com/profile.php?id=61573071505099'
NETWORK_GITHUB_URL = 'https://github.com/Article134-tech/lititzbmx-docs'
DONATE_URL = 'https://www.paypal.me/kyto1138'
CORRECTIONS_URL = REPO_URL + '/issues/new?template=record-correction.yml'
LOGO = 'Lititz-BMX-Logo-White-Tire-White-Lettering.png'
WORKBOOK = 'Lititz_BMX_Public_Knowledge_Register_Ephemera_v2.0.0_1010_RECORDS.xlsx'
DATA_LOCK = 'August 2, 2026'
RELEASE_VERSION = 'v2.0.0'


def esc(value):
    return html.escape('' if value is None else str(value), quote=True)


def read_csv(path: Path):
    with path.open('r', encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def copy_file(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def internal(path=''):
    return BASE_PATH + path.lstrip('/')


def slugify(value: str):
    value = re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')
    return value or 'item'


def normalize_search_text(value: str):
    value = unicodedata.normalize('NFD', str(value or ''))
    value = ''.join(char for char in value if not unicodedata.combining(char))
    return re.sub(r'[^a-z0-9]+', ' ', value.lower()).strip()


def status_tone(value: str):
    key = (value or '').lower()
    if any(x in key for x in ('ready', 'verified', 'included', 'match', 'pass', 'high')):
        return 'ready'
    if any(x in key for x in ('open', 'lead', 'review', 'estimate', 'pending', 'provisional', 'unresolved', 'medium')):
        return 'review'
    if any(x in key for x in ('low', 'fail', 'caution')):
        return 'caution'
    return 'neutral'


def friendly_status(research_status: str, confidence: str):
    key = (research_status or '').lower()
    if 'page-image' in key or 'visual comparison' in key:
        return 'Page image still needed'
    if any(x in key for x in ('open', 'lead', 'unresolved')):
        return 'Open research question'
    if 'recurring' in key or 'candidate' in key:
        return 'Campaign under comparison'
    if any(x in key for x in ('review', 'provisional', 'estimate', 'pending')):
        return 'Evidence reviewed; identity provisional'
    if confidence and confidence.upper().startswith('HIGH'):
        return 'Strong indexed evidence'
    return 'Evidence documented'


def badge(value: str, label: str | None = None):
    return f'<span class="badge badge-{status_tone(value)}">{esc(label or value or "Not stated")}</span>'


def external_link(url: str, label: str, cls='button'):
    if not url:
        return ''
    return f'<a class="{cls}" href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(label)}</a>'


def action_link(path: str, label: str, secondary=False):
    cls = 'button button-secondary' if secondary else 'button'
    return f'<a class="{cls}" href="{esc(path)}">{esc(label)}</a>'


def nav_link(path: str, label: str, section: str, key: str):
    current = section == key
    return f'<a class="simple-nav-link{" is-current" if current else ""}" href="{esc(path)}"{" aria-current=\"page\"" if current else ""}>{esc(label)}</a>'


def breadcrumbs(items):
    if not items:
        return ''
    parts = ['<nav class="breadcrumbs" aria-label="Breadcrumb"><ol>']
    for i, (label, url) in enumerate(items):
        if i == len(items) - 1:
            parts.append(f'<li><span aria-current="page">{esc(label)}</span></li>')
        else:
            parts.append(f'<li><a href="{esc(url)}">{esc(label)}</a></li>')
    parts.append('</ol></nav>')
    return ''.join(parts)


def layout(title: str, body: str, description='', section='home', crumbs=None, page_class='', extra_head=''):
    main_class = 'preview-shell' if 'home-page' in page_class.split() else ''
    more_href = internal('#more-lititz') if section == 'home' else internal('#more-lititz')
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light">
<title>{esc(title)} · Lititz BMX</title>
<meta name="description" content="{esc(description or title)}">
<link rel="stylesheet" href="{internal('assets/site.css')}">
<script>window.LBMX_BASE_PATH={json.dumps(BASE_PATH)};</script>
<script defer src="{internal('assets/site.js')}"></script>
{extra_head}
</head>
<body class="{esc(page_class)}" data-section="{esc(section)}">
<a class="skip-link" href="#main-content">Skip to main content</a>
<div class="release-banner"><strong>Lititz BMX Public Knowledge Register</strong><span>1,010 source records · evidence-linked BMX history</span></div>
<div class="global-dock" aria-label="Lititz BMX destinations">
  <div class="global-dock-inner">
    <span class="global-dock-label">Lititz BMX network</span>
    <nav class="global-dock-nav" aria-label="Other Lititz BMX sites">
      <a href="{ARCHIVE_URL}" target="_blank" rel="noopener">Archive <span aria-hidden="true">↗</span></a>
      <a href="{YOUTUBE_URL}" target="_blank" rel="noopener">YouTube <span aria-hidden="true">↗</span></a>
      <a href="{SPOTIFY_URL}" target="_blank" rel="noopener">Spotify <span aria-hidden="true">↗</span></a>
      <a href="{FACEBOOK_URL}" target="_blank" rel="noopener">Facebook <span aria-hidden="true">↗</span></a>
      <a href="{NETWORK_GITHUB_URL}" target="_blank" rel="noopener">GitHub <span aria-hidden="true">↗</span></a>
      <a class="global-dock-support" href="{DONATE_URL}" target="_blank" rel="noopener">Donate <span aria-hidden="true">↗</span></a>
    </nav>
  </div>
</div>
<header class="site-header">
  <div class="header-inner">
    <a class="brand" href="{internal()}" aria-label="Lititz BMX Public Knowledge Register home">
      <span class="brand-logo"><img src="{internal('assets/'+LOGO)}" width="446" height="532" alt="Lititz BMX"></span>
      <span class="brand-copy"><strong>Public Knowledge Register</strong><small>Simple on the surface. Rigorous underneath.</small></span>
    </a>
    <nav class="simple-nav" aria-label="Register navigation">
      {nav_link(internal('search/'),'Search',section,'search')}
      {nav_link(internal('explore/'),'Explore',section,'explore')}
      {nav_link(internal('methodology/'),'Method',section,'methodology')}
      <a class="simple-nav-link" href="{more_href}">More Lititz BMX</a>
    </nav>
  </div>
</header>
<main id="main-content" class="{main_class}" tabindex="-1">
{breadcrumbs(crumbs or [])}
{body}
</main>
<footer class="site-footer">
  <div class="footer-inner footer-revised">
    <div class="footer-brand"><strong>Lititz BMX Public Knowledge Register</strong><p>Metadata, evidence routes, limitations, and corrections—without reproducing protected historical scans.</p></div>
    <nav class="footer-links" aria-label="Register information"><a href="{internal('methodology/')}">Methodology</a><a href="{internal('data/')}">Public data</a><a href="{internal('methodology/#rights-boundary')}">Rights boundary</a><a href="{CORRECTIONS_URL}" target="_blank" rel="noopener">Corrections ↗</a></nav>
  </div>
</footer>
</body>
</html>'''


# Build from the governed files committed in the repository.
# No external working directory or prior package is required.
if OUT.exists():
    shutil.rmtree(OUT)
required = [
    DATA / 'ephemera-register-v2.0.0.csv',
    DATA / 'canonical-objects-v2.0.0.csv',
    DATA / 'price-observations-v2.0.0.csv',
    DATA / 'public-claims-v2.0.0.csv',
    DATA / 'claim-items-v2.0.0.csv',
    DATA / 'source-register-v2.0.0.csv',
    DATA / 'source-usage-v2.0.0.csv',
    DATA / 'chronology-v2.0.0.csv',
    DATA / 'category-register-v2.0.0.csv',
    DATA / 'universal-search-index-v2.0.0-rc1.json',
    DATA / 'source-page-routing-v2.0.0.csv',
    DOCS / 'V2.0.0-FINAL-PREDEPLOYMENT-QA.json',
    DOCS / 'V2.0.0-RELEASE-AUTHORIZATION.json',
    DOCS / 'V2.0.0-DOCUMENTATION-CLEANUP-QA.json',
    DOWNLOADS / WORKBOOK,
    ASSETS / LOGO,
]
missing_required = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
if missing_required:
    raise FileNotFoundError('Missing governed build inputs: ' + ', '.join(missing_required))

# Load governed data.
records = read_csv(DATA / 'ephemera-register-v2.0.0.csv')
objects = read_csv(DATA / 'canonical-objects-v2.0.0.csv')
prices = read_csv(DATA / 'price-observations-v2.0.0.csv')
claims = read_csv(DATA / 'public-claims-v2.0.0.csv')
claim_items = read_csv(DATA / 'claim-items-v2.0.0.csv')
sources = read_csv(DATA / 'source-register-v2.0.0.csv')
source_usage = read_csv(DATA / 'source-usage-v2.0.0.csv')
chronology = read_csv(DATA / 'chronology-v2.0.0.csv')
categories = read_csv(DATA / 'category-register-v2.0.0.csv')
source_page_routing = read_csv(DATA / 'source-page-routing-v2.0.0.csv')
search_payload = json.loads((DATA / 'universal-search-index-v2.0.0-rc1.json').read_text(encoding='utf-8'))

# Publish a stable frontend name while preserving RC1 source index.
search_payload['release'] = 'v2.0.0'
search_payload['public_release_unchanged'] = False
record_search_text = {row['Master ID']: normalize_search_text(' '.join(str(value or '') for value in row.values())) for row in records}
for entry in search_payload.get('entries', []):
    url = str(entry.get('url') or '')
    if url.startswith(BASE_URL):
        entry['url'] = '/' + url[len(BASE_URL):].lstrip('/')
    if entry.get('layer') == 'source_record':
        entry['register_text'] = record_search_text.get(entry.get('id'), '')
write(DATA / 'universal-search-index-v2.0.0.json', json.dumps(search_payload, ensure_ascii=False, separators=(',', ':')))

records_by_id = {r['Master ID']: r for r in records}
objects_by_id = {o['Canonical Object ID']: o for o in objects}
prices_by_id = {p['Price Observation ID']: p for p in prices}
sources_by_id = {s['Source ID']: s for s in sources}
source_by_url = {s['URL']: s for s in sources}
category_by_id = {c['Category ID']: c for c in categories}
source_page_route_by_id = {row['Master ID']: row for row in source_page_routing}
usage_by_id = {u['Source ID']: u for u in source_usage}
claim_items_by_claim = defaultdict(list)
for item in claim_items:
    claim_items_by_claim[item['Claim ID']].append(item)
objects_by_record = defaultdict(list)
for obj in objects:
    for rid in [x.strip() for x in obj.get('Member Record IDs', '').split('|') if x.strip()]:
        objects_by_record[rid].append(obj)
prices_by_object = defaultdict(list)
for price in prices:
    prices_by_object[price.get('Source Object ID', '')].append(price)
records_by_source_url = defaultdict(list)
for record in records:
    if record.get('Primary Source URL'):
        records_by_source_url[record['Primary Source URL']].append(record)
chronology_by_master = defaultdict(list)
for row in chronology:
    chronology_by_master[row.get('Master ID', '')].append(row)

# Natural issue order is governed by Master ID within each registered source.
for group in records_by_source_url.values():
    group.sort(key=lambda r: r['Master ID'])


def source_for_record(record):
    return source_by_url.get(record.get('Primary Source URL', ''))


def category_for_record(record):
    return category_by_id.get(record.get('Category ID', ''), {})


def record_route(rid):
    return internal(f'records/{rid}/')


def source_route(sid):
    return internal(f'sources/{sid}/')


def record_summary(record):
    return record.get('Primary Subject') or record.get('Evidence / Limitation') or 'A documented BMX source occurrence.'


def record_plain_facts(record):
    facts = []
    for label, key in [('Date', 'Date Text'), ('Brand / people', 'Brand / Promoter'), ('Type', 'Object Type'), ('Place', 'Geography')]:
        if record.get(key):
            facts.append(f'<div><dt>{esc(label)}</dt><dd>{esc(record[key])}</dd></div>')
    return '<dl class="facts">' + ''.join(facts) + '</dl>'


def primary_source_button(record):
    url = record.get('Primary Source URL', '')
    if not url:
        return ''
    route = source_page_route_by_id.get(record.get('Master ID',''))
    if route:
        if route.get('Routing Status') == 'KNOWN' and route.get('Start Page'):
            url = url.split('#',1)[0] + '#page/' + route['Start Page']
        attrs = f' title="{esc(route.get("Button Title",""))}"' if route.get('Button Title') else ''
        return f'<a class="button" href="{esc(url)}" target="_blank" rel="noopener noreferrer"{attrs}>{esc(route.get("Button Label") or "Open original source")}</a>'
    return external_link(url, 'Open original source')


def source_location_note(record):
    route = source_page_route_by_id.get(record.get('Master ID',''))
    if not route:
        return ''
    return f'<p class="source-location-note">{esc(route.get("Location Note"))}</p>'


def source_buttons(record):
    out = []
    if record.get('Primary Source URL'):
        out.append(primary_source_button(record))
    if record.get('Secondary Source URL'):
        out.append(external_link(record['Secondary Source URL'], 'Open supporting source', 'button button-secondary'))
    src = source_for_record(record)
    if src:
        out.append(action_link(source_route(src['Source ID']), 'View this publication / source', True))
    return ''.join(out)


def record_issue_navigation(record):
    group = records_by_source_url.get(record.get('Primary Source URL', ''), [])
    if len(group) < 2:
        return ''
    idx = next((i for i, item in enumerate(group) if item['Master ID'] == record['Master ID']), 0)
    prev_item = group[idx - 1] if idx > 0 else None
    next_item = group[idx + 1] if idx + 1 < len(group) else None
    parts = ['<nav class="sequence-nav" aria-label="Publication sequence">']
    if prev_item:
        parts.append(f'<a href="{record_route(prev_item["Master ID"])}"><span>Previous in source</span><strong>{esc(prev_item["Master ID"])} · {esc(prev_item["Title"])}</strong></a>')
    else:
        parts.append('<span class="sequence-empty"></span>')
    if next_item:
        parts.append(f'<a class="sequence-next" href="{record_route(next_item["Master ID"])}"><span>Next in source</span><strong>{esc(next_item["Master ID"])} · {esc(next_item["Title"])}</strong></a>')
    parts.append('</nav>')
    return ''.join(parts)


def related_records(record, limit=6):
    scored = []
    brand = record.get('Brand / Promoter', '')
    category = record.get('Category ID', '')
    subject_tokens = set(re.findall(r'[a-z0-9]{4,}', (record.get('Primary Subject') or '').lower()))
    for other in records:
        if other['Master ID'] == record['Master ID']:
            continue
        score = 0
        if brand and other.get('Brand / Promoter') == brand:
            score += 5
        if category and other.get('Category ID') == category:
            score += 1
        if record.get('Primary Source URL') and other.get('Primary Source URL') == record.get('Primary Source URL'):
            score += 3
        other_tokens = set(re.findall(r'[a-z0-9]{4,}', (other.get('Primary Subject') or '').lower()))
        score += min(3, len(subject_tokens & other_tokens))
        if score:
            scored.append((score, other['Master ID'], other))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [x[2] for x in scored[:limit]]


def small_record_card(record, context=''):
    cat = category_for_record(record)
    label = friendly_status(record.get('Research Status', ''), record.get('Confidence', ''))
    return f'''<article class="result-card record-mini">
<div class="result-top"><span class="eyebrow">Source record</span>{badge(record.get('Research Status',''), label)}</div>
<h3><a href="{record_route(record['Master ID'])}">{esc(record['Title'])}</a></h3>
<p class="result-id">{esc(record['Master ID'])} · {esc(record.get('Date Text'))} · {esc(record.get('Object Type'))}</p>
<p>{esc(context or record_summary(record))}</p>
<div class="chip-row"><span class="chip">{esc(cat.get('Category Label', record.get('Primary Category','Record')))}</span>{f'<span class="chip">{esc(record.get("Brand / Promoter"))}</span>' if record.get('Brand / Promoter') else ''}</div>
</article>'''


def list_page_intro(kicker, title, text, actions=''):
    return f'<section class="page-intro"><p class="eyebrow">{esc(kicker)}</p><h1>{esc(title)}</h1><p>{esc(text)}</p>{f"<div class=\"actions\">{actions}</div>" if actions else ""}</section>'


def progressive_collection(items_html: list[str], collection_id: str, page_size=24):
    return f'<div class="card-collection" id="{esc(collection_id)}" data-progressive data-page-size="{page_size}">{"".join(items_html)}</div><div class="load-more-wrap"><button class="button button-secondary" type="button" data-load-more data-target="{esc(collection_id)}">Load more</button></div>'


# New streamlined assets.
css = r'''
:root{--ink:#132630;--muted:#5c6d76;--black:#0b151b;--blue:#15556f;--blue-dark:#0d3e52;--link:#086f99;--cream:#fbf7ed;--paper:#fff;--line:#d8e1e5;--gold:#f1d38a;--green:#e1f1e9;--green-ink:#205d45;--amber:#fff3d5;--amber-ink:#705100;--red:#f7dfdb;--red-ink:#842e2e;--gray:#edf2f4;--focus:#ffbf47;--max:1120px;--shadow:0 8px 24px rgba(11,21,27,.07)}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--cream);color:var(--ink);font-family:Arial,Helvetica,sans-serif;line-height:1.58;text-rendering:optimizeLegibility}img{max-width:100%;height:auto}a{color:var(--link);text-underline-offset:.17em}a:hover{color:var(--blue-dark)}button,input,select{font:inherit}a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible,.result-card:focus-visible{outline:4px solid var(--focus);outline-offset:3px}.skip-link{position:fixed;left:1rem;top:1rem;z-index:1000;transform:translateY(-180%);padding:.7rem 1rem;background:#fff;color:#000;border:3px solid var(--focus);font-weight:800}.skip-link:focus{transform:none}.sr-only{position:absolute!important;width:1px!important;height:1px!important;padding:0!important;margin:-1px!important;overflow:hidden!important;clip:rect(0,0,0,0)!important;white-space:nowrap!important;border:0!important}
.site-header{background:var(--black);color:#fff;border-bottom:5px solid var(--blue)}.header-inner{max-width:var(--max);margin:auto;padding:.75rem 1rem;display:grid;grid-template-columns:minmax(250px,1fr) auto minmax(260px,340px);gap:1rem;align-items:center}.brand{display:flex;align-items:center;gap:.8rem;color:#fff;text-decoration:none;min-width:0}.brand-logo{display:grid;place-items:center;width:52px;height:52px;flex:0 0 52px}.brand-logo img{width:46px;max-height:52px;object-fit:contain}.brand-copy{display:grid;min-width:0}.brand-copy strong{font-size:1.05rem;line-height:1.15}.brand-copy small{color:#cbdbe2;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.simple-nav{display:flex;gap:.2rem}.simple-nav-link{display:inline-flex;align-items:center;min-height:44px;padding:.5rem .7rem;color:#fff;text-decoration:none;font-weight:800;border-radius:4px}.simple-nav-link:hover,.simple-nav-link:focus-visible{background:rgba(255,255,255,.12);color:#fff}.simple-nav-link.is-current{background:#fff;color:var(--blue-dark)}.header-search{display:grid;grid-template-columns:minmax(0,1fr) auto}.header-search input{min-width:0;border:0;border-radius:5px 0 0 5px;padding:.62rem .7rem}.header-search button{border:0;border-radius:0 5px 5px 0;background:var(--gold);color:var(--black);padding:.62rem .8rem;font-weight:900;cursor:pointer}
main{max-width:var(--max);margin:auto;padding:1rem 1rem 4rem;min-height:70vh}.breadcrumbs{margin:.2rem 0 1rem}.breadcrumbs ol{display:flex;flex-wrap:wrap;gap:.4rem;margin:0;padding:0;list-style:none;font-size:.9rem}.breadcrumbs li:not(:last-child)::after{content:'›';margin-left:.4rem;color:#788890}.breadcrumbs span[aria-current=page]{font-weight:800;color:var(--black)}h1,h2,h3{color:var(--black);line-height:1.16}h1{font-size:clamp(2rem,5vw,3.6rem);margin:.2rem 0 .8rem}h2{font-size:clamp(1.45rem,3vw,2.1rem);margin:.2rem 0 .65rem}h3{font-size:1.18rem;margin:.2rem 0 .55rem}p{overflow-wrap:anywhere}.eyebrow{display:inline-block;margin:0 0 .25rem;color:var(--blue);font-size:.76rem;font-weight:900;letter-spacing:.12em;text-transform:uppercase}.lede{max-width:760px;font-size:1.12rem;color:#314851}.page-intro,.panel,.record-hero,.search-shell,.journey-card,.result-card,.metric-strip,.trust-note{background:var(--paper);border:1px solid var(--line);border-radius:8px;box-shadow:var(--shadow)}.page-intro{padding:clamp(1.25rem,4vw,2rem);margin-bottom:1rem;border-left:7px solid var(--blue)}.page-intro>p{max-width:800px}.panel{padding:1.15rem;margin:0 0 1rem}.section-head{display:flex;justify-content:space-between;align-items:end;gap:1rem;margin:2rem 0 .8rem}.section-head p{max-width:550px;margin:0;color:var(--muted)}
.home-hero{padding:clamp(1.4rem,5vw,3rem) 0 2rem;text-align:center}.home-hero h1{max-width:900px;margin-left:auto;margin-right:auto}.home-hero .lede{margin-left:auto;margin-right:auto}.hero-search,.search-form{max-width:780px;margin:1.4rem auto 0;display:grid;grid-template-columns:minmax(0,1fr) auto;background:#fff;border:3px solid var(--blue);border-radius:8px;box-shadow:0 12px 34px rgba(11,21,27,.12)}.hero-search input,.search-form input{min-width:0;border:0;padding:1rem;font-size:1.12rem;border-radius:6px 0 0 6px}.hero-search button,.search-form button{border:0;background:var(--blue);color:#fff;padding:.8rem 1.1rem;font-weight:900;cursor:pointer}.search-examples{display:flex;flex-wrap:wrap;justify-content:center;gap:.45rem;margin:.8rem 0 0}.search-examples a,.chip-link{display:inline-flex;min-height:36px;align-items:center;padding:.35rem .65rem;background:#fff;border:1px solid var(--line);border-radius:999px;text-decoration:none;font-weight:800;font-size:.9rem}.journey-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.8rem}.journey-card{padding:1rem;display:flex;flex-direction:column}.journey-card p{color:var(--muted)}.journey-card a{margin-top:auto;font-weight:900}.metric-strip{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));margin:1rem 0;overflow:hidden}.metric-strip a{padding:1rem;text-decoration:none;border-right:1px solid var(--line)}.metric-strip a:last-child{border-right:0}.metric-strip strong{display:block;font-size:1.7rem;color:var(--black)}.metric-strip span{color:var(--muted);font-weight:800}.trust-note{padding:1rem;border-left:6px solid var(--gold);margin:1rem 0}.trust-note p{margin:.35rem 0}.recent-list{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.7rem}.recent-list a{display:block;background:#fff;border:1px solid var(--line);border-radius:7px;padding:.8rem;text-decoration:none}.recent-list span{display:block;color:var(--muted);font-size:.86rem}
.button{display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:.62rem .9rem;border:2px solid var(--blue);border-radius:5px;background:var(--blue);color:#fff;text-decoration:none;font-weight:900;cursor:pointer}.button:hover{background:var(--black);border-color:var(--black);color:#fff}.button-secondary{background:#fff;color:var(--blue-dark)}.button-secondary:hover{background:var(--blue-dark);color:#fff}.button-quiet{background:transparent;color:var(--blue-dark);border-color:var(--line)}.actions{display:flex;flex-wrap:wrap;gap:.55rem;margin:1rem 0}.badge{display:inline-flex;align-items:center;min-height:28px;padding:.2rem .5rem;border:1px solid transparent;border-radius:999px;font-size:.77rem;font-weight:900}.badge-ready{background:var(--green);color:var(--green-ink);border-color:#acd3bf}.badge-review{background:var(--amber);color:var(--amber-ink);border-color:#e2c271}.badge-caution{background:var(--red);color:var(--red-ink);border-color:#e4b5ae}.badge-neutral{background:var(--gray);color:var(--ink);border-color:#ccd7dc}.chip-row{display:flex;flex-wrap:wrap;gap:.35rem}.chip{display:inline-flex;padding:.2rem .5rem;border-radius:999px;background:var(--gray);font-size:.78rem;font-weight:800;color:#40535c}
.search-shell{padding:1rem;margin-bottom:1rem}.search-form{max-width:none;margin:0}.search-meta{display:flex;justify-content:space-between;gap:1rem;align-items:center;margin:.8rem 0 0}.layer-filters{display:flex;flex-wrap:wrap;gap:.35rem;margin:1rem 0}.layer-filter{min-height:40px;border:1px solid var(--line);border-radius:999px;background:#fff;color:var(--ink);padding:.35rem .7rem;font-weight:900;cursor:pointer}.layer-filter[aria-pressed=true]{background:var(--blue);color:#fff;border-color:var(--blue)}.search-results{display:grid;gap:.7rem}.result-card{padding:1rem}.result-card h2,.result-card h3{margin:.2rem 0 .45rem}.result-card p{margin:.35rem 0}.result-top{display:flex;justify-content:space-between;align-items:start;gap:.7rem}.result-id{color:var(--muted);font-weight:800;font-size:.9rem}.match-note{font-size:.84rem;color:var(--muted);border-top:1px solid var(--line);padding-top:.45rem;margin-top:.6rem}.empty-state{padding:1rem;background:var(--amber);border-left:6px solid var(--amber-ink);border-radius:5px}.load-more-wrap{display:flex;justify-content:center;margin:1rem 0}.loading-state{padding:1rem;color:var(--muted)}mark{background:#ffe28a;color:var(--black);padding:0 .05em}
.record-hero{padding:clamp(1.2rem,4vw,2rem);margin-bottom:1rem;border-top:7px solid var(--blue)}.record-hero h1{font-size:clamp(1.75rem,4vw,3rem)}.record-kicker{display:flex;flex-wrap:wrap;gap:.45rem;align-items:center;margin-bottom:.55rem}.record-id{font-weight:900;color:var(--blue);letter-spacing:.05em}.facts{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.7rem;margin:1rem 0 0}.facts div{padding:.7rem;background:var(--cream);border-left:4px solid var(--gold)}.facts dt{font-size:.76rem;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);font-weight:900}.facts dd{margin:.15rem 0 0;font-weight:800}.human-layout{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(270px,.8fr);gap:1rem;align-items:start}.side-stack{position:sticky;top:1rem}.plain-list{margin:.5rem 0 0;padding-left:1.15rem}.plain-list li{margin:.4rem 0}.detail-list{display:grid;grid-template-columns:minmax(150px,220px) 1fr;gap:.35rem .8rem}.detail-list dt{font-weight:900;color:var(--blue-dark)}.detail-list dd{margin:0 0 .45rem;overflow-wrap:anywhere}.sequence-nav{display:grid;grid-template-columns:1fr 1fr;gap:.7rem;margin:1rem 0}.sequence-nav a{display:flex;flex-direction:column;padding:.8rem;background:#fff;border:1px solid var(--line);border-radius:7px;text-decoration:none}.sequence-nav span{color:var(--muted);font-size:.8rem;font-weight:900;text-transform:uppercase;letter-spacing:.07em}.sequence-nav .sequence-next{text-align:right}.sequence-empty{display:block}.related-grid,.card-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.75rem}.record-mini{box-shadow:none}.record-mini h3{font-size:1.05rem}.copy-feedback{font-size:.86rem;color:var(--green-ink);font-weight:800}.return-search[hidden]{display:none!important}
.card-collection{display:grid;gap:.75rem}.card-collection>[hidden]{display:none!important}.browse-tools{display:grid;grid-template-columns:minmax(0,1fr) repeat(2,minmax(170px,220px));gap:.6rem;margin-bottom:1rem}.browse-tools label{display:grid;gap:.25rem;font-weight:900;color:var(--blue-dark)}.browse-tools input,.browse-tools select{min-height:44px;padding:.55rem .65rem;border:1px solid #97aab3;border-radius:5px;background:#fff}.issue-summary{display:flex;flex-wrap:wrap;gap:.4rem;margin:.8rem 0}.issue-summary span{background:var(--gray);padding:.3rem .55rem;border-radius:999px;font-weight:800}.price-card strong{font-size:1.4rem;color:var(--black)}.timeline-list{border-left:4px solid var(--blue);margin-left:.5rem;padding-left:1rem}.timeline-item{position:relative;padding:.2rem 0 1rem}.timeline-item::before{content:'';position:absolute;left:-1.42rem;top:.55rem;width:.75rem;height:.75rem;border-radius:50%;background:var(--gold);border:3px solid var(--blue)}
.site-footer{background:var(--black);color:#d7e4e9;border-top:5px solid var(--blue)}.footer-inner{max-width:var(--max);margin:auto;padding:1.3rem 1rem;display:grid;grid-template-columns:1.4fr 1fr;gap:1rem}.footer-inner p{margin:.35rem 0}.footer-inner nav{display:flex;flex-wrap:wrap;gap:.8rem;align-content:center;justify-content:flex-end}.footer-inner a{color:#fff;font-weight:800}
@media(max-width:940px){.header-inner{grid-template-columns:1fr auto}.header-search{grid-column:1/-1}.journey-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.metric-strip{grid-template-columns:repeat(2,minmax(0,1fr))}.metric-strip a:nth-child(2){border-right:0}.metric-strip a:nth-child(-n+2){border-bottom:1px solid var(--line)}.human-layout{grid-template-columns:1fr}.side-stack{position:static}.facts{grid-template-columns:repeat(2,minmax(0,1fr))}.related-grid,.card-grid,.recent-list{grid-template-columns:repeat(2,minmax(0,1fr))}.browse-tools{grid-template-columns:1fr 1fr}.browse-tools label:first-child{grid-column:1/-1}}
@media(max-width:620px){.header-inner{display:flex;flex-wrap:wrap}.brand{flex:1 1 230px}.simple-nav{order:3;width:100%;justify-content:center;border-top:1px solid rgba(255,255,255,.15);padding-top:.45rem}.header-search{order:2;flex:1 1 100%}.brand-copy small{white-space:normal}.journey-grid,.related-grid,.card-grid,.recent-list,.browse-tools{grid-template-columns:1fr}.metric-strip{display:grid;grid-template-columns:1fr}.metric-strip a{border-right:0;border-bottom:1px solid var(--line)}.metric-strip a:last-child{border-bottom:0}.hero-search,.search-form{grid-template-columns:1fr}.hero-search input,.search-form input{border-radius:5px 5px 0 0}.hero-search button,.search-form button{min-height:48px}.search-meta,.section-head,.result-top{align-items:flex-start;flex-direction:column}.facts{grid-template-columns:1fr}.sequence-nav{grid-template-columns:1fr}.sequence-nav .sequence-next{text-align:left}.detail-list{grid-template-columns:1fr}.detail-list dd{padding-bottom:.45rem;border-bottom:1px solid var(--line)}.actions .button{width:100%}.footer-inner{grid-template-columns:1fr}.footer-inner nav{justify-content:flex-start}.home-hero{padding-top:1.2rem}h1{font-size:2.15rem}}
@media(max-width:360px){main{padding-left:.7rem;padding-right:.7rem}.header-inner{padding-left:.7rem;padding-right:.7rem}.brand-logo{width:42px;height:48px;flex-basis:42px}.brand-logo img{width:40px}.simple-nav-link{padding:.45rem .55rem}.page-intro,.panel,.record-hero,.search-shell,.journey-card,.result-card{padding:.85rem}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important}}
[hidden]{display:none!important}
'''

css += r'''
/* Homepage Example 2 — offline review additions */
:root{--lbmx-gold:#f1bf52;--lbmx-gold-soft:#f8df9e;--lbmx-ink:#071015;--lbmx-deep:#0d1a22;--lbmx-blue:#1f69a7;--lbmx-paper:#f5f1e7;--lbmx-white:#fff;--lbmx-muted:#5b666d}
html{scroll-behavior:smooth}body{background:linear-gradient(180deg,#f8f5ed 0,#f5f1e7 42%,#ede8dc 100%)}
.release-banner{min-height:34px;display:flex;justify-content:center;gap:.65rem;align-items:center;padding:.4rem 1rem;background:#f1bf52;color:#071015;font-size:.78rem;letter-spacing:.02em}.release-banner strong{text-transform:uppercase;letter-spacing:.11em;font-size:.7rem}.release-banner span{opacity:.8}
.global-dock{background:#071015;border-bottom:1px solid rgba(255,255,255,.12);color:white}.global-dock-inner{width:min(1120px,calc(100% - 2rem));margin:auto;display:flex;align-items:center;justify-content:space-between;gap:1rem;min-height:54px}.global-dock-label{color:#f1bf52;font-size:.69rem;font-weight:800;letter-spacing:.13em;text-transform:uppercase;white-space:nowrap}.global-dock-nav{display:flex;align-items:center;justify-content:flex-end;gap:.35rem}.global-dock-nav a{display:inline-flex;align-items:center;gap:.25rem;color:#edf3f7;text-decoration:none;padding:.55rem .75rem;border:1px solid rgba(255,255,255,.14);border-radius:999px;font-size:.78rem;font-weight:750;line-height:1;white-space:nowrap;transition:.18s ease}.global-dock-nav a:hover,.global-dock-nav a:focus-visible{background:#fff;color:#071015;border-color:#fff;transform:translateY(-1px)}.global-dock-nav .global-dock-support{background:#f1bf52;color:#071015;border-color:#f1bf52}.global-dock-nav .global-dock-support:hover,.global-dock-nav .global-dock-support:focus-visible{background:#f8df9e;border-color:#f8df9e}
.site-header{position:sticky;top:0;z-index:30;box-shadow:0 8px 24px rgba(7,16,21,.12)}.header-inner{min-height:82px;grid-template-columns:minmax(250px,1fr) auto}.simple-nav{flex-wrap:wrap;justify-content:flex-end}.simple-nav-link{font-size:.82rem}.preview-shell{width:min(1120px,calc(100% - 2rem));padding-top:2.25rem;padding-bottom:5rem}
.home-hero{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(260px,.55fr);gap:2rem;align-items:stretch;padding:clamp(2rem,5vw,4.25rem);border-radius:30px;background:radial-gradient(circle at 18% 12%,rgba(31,105,167,.34),transparent 34%),linear-gradient(135deg,#071015 0%,#0d1a22 60%,#102838 100%);color:#fff;box-shadow:0 30px 70px rgba(7,16,21,.18);overflow:hidden;position:relative}.home-hero:after{content:"";position:absolute;width:350px;height:350px;border:1px solid rgba(241,191,82,.14);border-radius:50%;right:-160px;bottom:-190px;box-shadow:0 0 0 34px rgba(241,191,82,.04),0 0 0 68px rgba(241,191,82,.025)}.hero-copy{position:relative;z-index:1}.home-hero .eyebrow{color:#f1bf52}.home-hero h1{font-size:clamp(2.8rem,7vw,5.8rem);max-width:790px;line-height:.92;letter-spacing:-.055em;margin:.35rem 0 1.1rem;color:#fff}.home-hero .lede{font-size:clamp(1rem,2vw,1.25rem);line-height:1.65;max-width:760px;color:#d9e1e5}.hero-search{display:grid;grid-template-columns:minmax(0,1fr) auto;background:#fff;border:4px solid rgba(255,255,255,.14);border-radius:16px;overflow:hidden;margin-top:2rem;max-width:800px;box-shadow:0 18px 44px rgba(0,0,0,.24)}.hero-search input{border:0;min-height:62px;padding:0 1.15rem;font-size:1rem;color:#071015;background:#fff;min-width:0}.hero-search input:focus{outline:3px solid #f1bf52;outline-offset:-3px}.hero-search button{border:0;border-left:1px solid #d9e0e4;background:#f1bf52;color:#071015;padding:0 1.35rem;font-weight:850;font-size:.9rem;cursor:pointer}.hero-search button:hover,.hero-search button:focus-visible{background:#f8df9e}.search-examples{display:flex;flex-wrap:wrap;align-items:center;gap:.48rem;margin-top:1rem}.search-examples>span{font-size:.76rem;color:#aebbc2;font-weight:700;text-transform:uppercase;letter-spacing:.08em;margin-right:.2rem}.home-hero .chip-link{background:rgba(255,255,255,.06);color:#fff;border:1px solid rgba(255,255,255,.22);font-size:.76rem;padding:.5rem .7rem}.home-hero .chip-link:hover,.home-hero .chip-link:focus-visible{background:#fff;color:#071015;border-color:#fff}.hero-scope{position:relative;z-index:1;align-self:stretch;background:rgba(255,255,255,.075);border:1px solid rgba(255,255,255,.16);border-radius:22px;padding:1.6rem;display:flex;flex-direction:column;justify-content:center;backdrop-filter:blur(8px)}.hero-scope-number{font-size:clamp(3.5rem,7vw,5.6rem);line-height:.9;letter-spacing:-.06em;color:#f1bf52}.hero-scope-label{text-transform:uppercase;letter-spacing:.1em;font-size:.72rem;font-weight:800;margin-top:.55rem}.hero-scope-rule{height:1px;background:rgba(255,255,255,.2);margin:1.35rem 0}.hero-scope p{color:#d3dde2;line-height:1.55;font-size:.92rem}.hero-scope a{color:#fff;font-weight:800;text-decoration:none;margin-top:.8rem}.hero-scope a:hover{text-decoration:underline;text-decoration-color:#f1bf52;text-underline-offset:4px}
.curated-section,.broad-paths,.more-lititz{margin-top:4.5rem}.section-head{align-items:end;gap:2rem}.section-head>p{max-width:590px;color:#5b666d;line-height:1.6}.section-head h2{font-size:clamp(1.9rem,4vw,3.15rem);letter-spacing:-.035em;line-height:1.02}.cluster-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:1rem;margin-top:1.55rem}.cluster-card{appearance:none;text-decoration:none;text-align:left;display:flex;flex-direction:column;min-height:260px;padding:1.4rem;border-radius:18px;border:1px solid #d8d4c9;background:rgba(255,255,255,.86);color:#071015;cursor:pointer;box-shadow:0 10px 28px rgba(7,16,21,.055);transition:.2s ease}.cluster-card:hover,.cluster-card:focus-visible{transform:translateY(-4px);border-color:#1f69a7;box-shadow:0 18px 36px rgba(7,16,21,.12);outline:none}.cluster-card strong{font-size:1.45rem;letter-spacing:-.03em;margin:.5rem 0 .65rem}.cluster-card>span:not(.cluster-type){color:#5b666d;line-height:1.55;font-size:.9rem}.cluster-card b{margin-top:auto;padding-top:1.25rem;color:#155b91;font-size:.78rem;text-transform:uppercase;letter-spacing:.065em}.cluster-card i,.journey-card i,.more-card i{font-style:normal}.cluster-type{font-size:.65rem;text-transform:uppercase;letter-spacing:.12em;font-weight:850;color:#7a5a13}.cluster-feature{background:linear-gradient(145deg,#0b1d28,#123d59);color:#fff;border-color:#123d59}.cluster-feature .cluster-type,.cluster-feature b{color:#f1bf52}.cluster-feature>span:not(.cluster-type){color:#d7e1e6}.publication-card{border-top:5px solid #f1bf52;padding-top:1.15rem}
.broad-paths{padding-top:1rem}.journey-grid{gap:1rem}.journey-button{appearance:none;text-decoration:none;text-align:left;color:inherit;cursor:pointer;position:relative;overflow:hidden;min-height:270px}.journey-button:hover,.journey-button:focus-visible{transform:translateY(-3px);border-color:#1f69a7;outline:none}.journey-index{position:absolute;right:1rem;top:.6rem;font-size:4.5rem;font-weight:900;color:rgba(31,105,167,.07);letter-spacing:-.08em}.journey-card b{display:block;margin-top:1rem;color:#155b91;font-size:.77rem;text-transform:uppercase;letter-spacing:.06em}.metric-strip{margin:2rem 0 0;border-radius:18px;overflow:hidden;box-shadow:0 10px 28px rgba(7,16,21,.06)}.metric-strip a{background:#fff;border-color:#e1ddd2}.metric-strip a:hover{background:#f8df9e;color:#071015}
.trust-note{margin-top:4.5rem;display:grid;grid-template-columns:1.15fr .85fr;gap:2.5rem;padding:clamp(1.8rem,4vw,3.4rem);border-radius:24px;background:#fff;border:1px solid #d8d4c9;box-shadow:0 18px 44px rgba(7,16,21,.07)}.trust-copy h2{font-size:clamp(1.8rem,4vw,3rem);line-height:1.05;letter-spacing:-.035em}.trust-copy>p:last-child{font-size:1rem;line-height:1.7;color:#4e5a61}.trust-principles{display:grid;gap:.75rem}.trust-principles div{display:flex;flex-direction:column;gap:.25rem;padding:1rem 1.05rem;background:#f5f1e7;border-left:4px solid #f1bf52;border-radius:4px 12px 12px 4px}.trust-principles strong{font-size:.92rem}.trust-principles span{font-size:.82rem;color:#5b666d;line-height:1.45}
.more-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:1rem;margin-top:1.5rem}.more-card{display:flex;flex-direction:column;min-height:250px;padding:1.35rem;border-radius:18px;background:#0d1a22;color:#fff;text-decoration:none;border:1px solid #1c3442;box-shadow:0 12px 30px rgba(7,16,21,.12);transition:.2s ease}.more-card:hover,.more-card:focus-visible{transform:translateY(-4px);border-color:#f1bf52;outline:none}.more-card>span{color:#f1bf52;font-size:.65rem;text-transform:uppercase;letter-spacing:.12em;font-weight:850}.more-card strong{font-size:1.35rem;margin:.55rem 0 .65rem;letter-spacing:-.025em}.more-card p{color:#c9d4da;line-height:1.5;font-size:.88rem}.more-card b{margin-top:auto;padding-top:1rem;color:#f1bf52;font-size:.76rem;text-transform:uppercase;letter-spacing:.06em}.radical-card{background:linear-gradient(145deg,#1a1624,#34204b)}
.home-page .search-shell{margin-top:4.5rem;border-radius:24px;padding:clamp(1.35rem,3vw,2.4rem);background:rgba(255,255,255,.72);border:1px solid #d8d4c9;box-shadow:0 16px 40px rgba(7,16,21,.07)}.home-page .search-heading{margin-bottom:1.5rem}.search-heading h2{font-size:clamp(1.7rem,3.5vw,2.65rem)}.home-page .search-shell .layer-filters{padding-top:1rem;border-top:1px solid #ddd8cc}
.site-footer{background:#071015;border-top:4px solid #f1bf52}.footer-revised{display:flex;justify-content:space-between;align-items:center;gap:2rem}.footer-brand p{color:#aebbc2}.footer-links{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:.5rem}.footer-links a{color:#e9eff2;text-decoration:none;font-size:.8rem;font-weight:750;padding:.55rem .7rem;border:1px solid rgba(255,255,255,.14);border-radius:999px}.footer-links a:hover,.footer-links a:focus-visible{background:#fff;color:#071015}
@media (max-width:980px){.cluster-grid,.more-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.home-hero{grid-template-columns:1fr}.hero-scope{display:grid;grid-template-columns:auto 1fr;column-gap:1rem;align-items:end}.hero-scope .eyebrow,.hero-scope-rule,.hero-scope p,.hero-scope a{grid-column:1/-1}.hero-scope-label{align-self:center}.trust-note{grid-template-columns:1fr}}
@media (max-width:760px){.global-dock-inner{display:block;width:100%;padding:.6rem 0}.global-dock-label{display:block;padding:0 1rem .5rem}.global-dock-nav{justify-content:flex-start;overflow-x:auto;padding:0 1rem .35rem;scrollbar-width:thin;scroll-snap-type:x proximity}.global-dock-nav a{scroll-snap-align:start;min-height:40px}.site-header{top:0}.header-inner{align-items:flex-start;gap:.7rem;padding-top:.8rem;padding-bottom:.8rem}.simple-nav{justify-content:flex-start}.home-hero{padding:1.5rem;border-radius:22px}.home-hero h1{font-size:clamp(2.6rem,14vw,4.4rem)}.hero-search{grid-template-columns:1fr}.hero-search button{border-left:0;border-top:1px solid #d9e0e4;min-height:50px}.cluster-grid,.more-grid{grid-template-columns:1fr}.cluster-card,.more-card{min-height:220px}.journey-grid{grid-template-columns:1fr}.trust-note{padding:1.4rem}.section-head{display:block}.section-head>p{margin-top:.8rem}.footer-revised{display:block}.footer-links{justify-content:flex-start;margin-top:1rem}.release-banner{align-items:flex-start;text-align:left;flex-direction:column;gap:.12rem;padding:.45rem 1rem}.hero-scope{display:block}.hero-scope-number{display:block}.metric-strip{grid-template-columns:repeat(2,1fr)}}
@media (max-width:440px){.preview-shell{width:min(100% - 1rem,1120px)}.global-dock-nav a{font-size:.74rem;padding:.5rem .65rem}.simple-nav-link{font-size:.74rem;padding:.4rem .48rem}.home-hero{padding:1.2rem}.cluster-card,.journey-card,.more-card{padding:1.1rem}.search-shell{padding:1rem}.footer-links a{font-size:.72rem}}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}.cluster-card,.journey-button,.more-card,.global-dock-nav a{transition:none}.cluster-card:hover,.journey-button:hover,.more-card:hover,.global-dock-nav a:hover{transform:none}}
'''
css += r'''
.source-location-note{margin:1rem 0;padding:.75rem .9rem;background:var(--amber);border-left:4px solid var(--gold);border-radius:5px;color:var(--black)}.source-location-note strong{color:var(--blue-dark)}
'''
write(ASSETS / 'site.css', css)

js = r'''
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
'''
write(ASSETS / 'site.js', js)

# Build static output.
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)
shutil.copytree(ASSETS, OUT / 'assets')
shutil.copytree(DATA, OUT / 'data')
shutil.copytree(DOCS, OUT / 'docs')
shutil.copytree(DOWNLOADS, OUT / 'downloads')
(OUT / '.nojekyll').write_text('', encoding='utf-8')

# Homepage.
def record_token_set(row):
    return set(normalize_search_text(' '.join(str(value or '') for value in row.values())).split())

record_tokens = {row['Master ID']: record_token_set(row) for row in records}
harry_count = sum({'harry','leary'}.issubset(record_tokens[row['Master ID']]) for row in records)
brand_family_terms = {'gt','dyno','auburn','robinson'}
brand_family_count = sum(bool(brand_family_terms & record_tokens[row['Master ID']]) for row in records)
diamond_back_count = sum({'diamond','back'}.issubset(record_tokens[row['Master ID']]) for row in records)
category_by_id = {row['Category ID']: row for row in categories}
catalog_count = int(category_by_id['PKR-CAT-001']['Record Count'])
ad_count = int(category_by_id['PKR-CAT-002']['Record Count'])

def home_search_url(query='', layer='source_record', match='', id_start='', id_end='', label=''):
    params=[]
    if query: params.append('q='+quote(query))
    if layer: params.append('layer='+quote(layer))
    if match: params.append('match='+quote(match))
    if id_start: params.append('id_start='+quote(str(id_start)))
    if id_end: params.append('id_end='+quote(str(id_end)))
    if label: params.append('label='+quote(label))
    return internal() + ('?' + '&'.join(params) if params else '') + '#search'

hero_examples = [
    ('Harry Leary',home_search_url('Harry Leary')),
    ('GT, Dyno, Auburn, Robinson',home_search_url('GT Dyno Auburn Robinson',match='any')),
    ('Diamond Back',home_search_url('Diamond Back')),
    ('BMX Action Bike',home_search_url(layer='source_record',id_start=62,id_end=760,label='BMX Action Bike')),
    ('Bicross',home_search_url(layer='source_record',id_start=761,id_end=1010,label='Bicross')),
]
hero_links=''.join(f'<a class="chip-link" href="{esc(url)}">{esc(label)}</a>' for label,url in hero_examples)
clusters = [
    ('Rider','Harry Leary',f'{harry_count:,} source records connecting riders, brands, interviews, advertisements, and period coverage.','Explore records',home_search_url('Harry Leary'),'cluster-feature'),
    ('Brand family','GT, Dyno, Auburn, Robinson',f'{brand_family_count:,} source records spanning catalogs, product lines, team identity, and advertising.','Explore records',home_search_url('GT Dyno Auburn Robinson',match='any'),''),
    ('Brand','Diamond Back',f'{diamond_back_count:,} source records including product literature, advertising, riders, and model-year evidence.','Explore records',home_search_url('Diamond Back'),''),
    ('Source type','Catalogs',f'{catalog_count:,} records classified as catalogs and product literature.','Browse catalogs',home_search_url('Catalogs and product literature'),''),
    ('Source type','Advertisements',f'{ad_count:,} records classified as advertisements and price lists.','Browse advertising',home_search_url('Advertisements and price lists'),''),
    ('Market evidence','Historical prices',f'{len(prices):,} source-specific observations—evidence of period pricing, not modern value guides.','Browse prices',home_search_url('',layer='price_observation'),''),
    ('Publication run','BMX Action Bike','699 source records from the register’s largest publication sequence.','Open the run',home_search_url(layer='source_record',id_start=62,id_end=760,label='BMX Action Bike'),'publication-card'),
    ('Publication run','Bicross','250 source records forming the second major publication sequence.','Open the run',home_search_url(layer='source_record',id_start=761,id_end=1010,label='Bicross'),'publication-card'),
]
cluster_html=''.join(f'<a class="cluster-card {esc(extra)}" href="{esc(url)}"><span class="cluster-type">{esc(kind)}</span><strong>{esc(title)}</strong><span>{esc(text)}</span><b>{esc(action)} <i aria-hidden="true">→</i></b></a>' for kind,title,text,action,url,extra in clusters)
journeys = [
    ('01','People and brands','Find riders, teams, manufacturers, dealers, and promoters.','Start with Harry Leary',home_search_url('Harry Leary')),
    ('02','Publications','Open issue groups and trace records back to the sources that preserve them.','Start with BMX Action Bike',home_search_url(layer='source_record',id_start=62,id_end=760,label='BMX Action Bike')),
    ('03','Eras','Move through the 1970s, 1980s, 1990s, and later historical records.','Start with 1982',home_search_url('1982',layer='all')),
    ('04','Prices and products',f'Compare period product language and {len(prices):,} source-specific price observations.','Browse historical prices',home_search_url('',layer='price_observation')),
]
journey_html=''.join(f'<a class="journey-card journey-button" href="{esc(url)}"><span class="journey-index">{idx}</span><p class="eyebrow">Explore</p><h3>{esc(title)}</h3><p>{esc(text)}</p><b>{esc(action)} <i aria-hidden="true">→</i></b></a>' for idx,title,text,action,url in journeys)
metric_html=''.join([
    f'<a href="{internal("records/")}"><strong>{len(records):,}</strong><span>source records</span></a>',
    f'<a href="{internal("objects/")}"><strong>{len(objects):,}</strong><span>provisional objects</span></a>',
    f'<a href="{internal("prices/")}"><strong>{len(prices):,}</strong><span>price observations</span></a>',
    f'<a href="{internal("sources/")}"><strong>{len(sources):,}</strong><span>registered sources</span></a>',
])
layer_buttons=[('all','Everything'),('source_record','Records'),('canonical_object','Objects'),('price_observation','Prices'),('chronology','Timeline'),('source','Sources'),('public_claim','Claims')]
home_filters=''.join(f'<button class="layer-filter" type="button" data-layer-filter="{key}" aria-pressed="{str(key=="all").lower()}">{label}</button>' for key,label in layer_buttons)
home=f'''<section class="home-hero" aria-labelledby="hero-title"><div class="hero-copy"><p class="eyebrow">Lititz BMX · Public Knowledge Register</p><h1 id="hero-title">Search BMX history.</h1><p class="lede">Explore {len(records):,} documented appearances from magazines, catalogs, advertisements, price lists, product literature, and other BMX ephemera—then inspect the evidence behind each record.</p><form class="hero-search" action="{internal()}#search" role="search"><label class="sr-only" for="home-search">Search BMX history</label><input id="home-search" name="q" type="search" placeholder="Search a rider, brand, publication, year, product, or exact ID" autocomplete="off"><button type="submit">Search the register</button></form><div class="search-examples" aria-label="Suggested searches"><span>Try:</span>{hero_links}</div></div><aside class="hero-scope" aria-label="Register scope"><p class="eyebrow">Inside this register</p><strong class="hero-scope-number">{len(records):,}</strong><span class="hero-scope-label">source records</span><div class="hero-scope-rule"></div><p>Built from {len(sources):,} registered sources, with {len(prices):,} historical price observations and {len(objects):,} provisional object identities.</p><a href="#about">How the records work <span aria-hidden="true">→</span></a></aside></section>
<section class="curated-section" id="curated"><div class="section-head curated-head"><div><p class="eyebrow">Explore what’s here</p><h2>A Lititz BMX starting point</h2></div><p>These are not simply the most common words. They are useful, data-backed entrances into the history represented by this register.</p></div><div class="cluster-grid">{cluster_html}</div></section>
<section class="broad-paths" id="paths"><div class="section-head"><div><p class="eyebrow">Or browse broadly</p><h2>Four ways through the register</h2></div><p>Start with a familiar name, follow a publication, move through time, or inspect the products and prices preserved in period sources.</p></div><div class="journey-grid">{journey_html}</div></section>
<div class="metric-strip" aria-label="Register totals">{metric_html}</div>
<section class="trust-note" id="about"><div class="trust-copy"><p class="eyebrow">How to read the register</p><h2>Occurrences are preserved. Identities are reviewed separately.</h2><p>A repeated advertisement, catalog appearance, edition, or publication mention remains visible as its own source record. Those {len(records):,} documented occurrences currently point toward {len(objects):,} provisional objects; identity is merged only when the evidence supports it.</p><p><a href="{internal('methodology/#source-records-vs-objects')}">Read the full plain-language method →</a></p></div><div class="trust-principles" aria-label="Register principles"><div><strong>Index broadly</strong><span>Make documented appearances discoverable.</span></div><div><strong>Republish narrowly</strong><span>Respect source access and rights boundaries.</span></div><div><strong>Preserve provenance</strong><span>Keep the route back to the evidence visible.</span></div></div></section>
<section class="more-lititz" id="more-lititz"><div class="section-head"><div><p class="eyebrow">More from Lititz BMX</p><h2>The register is one part of a larger archive</h2></div><p>These destinations sit outside the {len(records):,}-record ephemera register. They are presented separately so the scope remains honest.</p></div><div class="more-grid"><a class="more-card radical-card" href="https://sites.google.com/view/lititzbmxinventorylist/campaigns/rebuild-radical-rick-campaigns" target="_blank" rel="noopener"><span>Campaign</span><strong>Rebuild Radical Rick</strong><p>Follow the preservation campaign and the broader Radical Rick story.</p><b>Open the campaign <i aria-hidden="true">↗</i></b></a><a class="more-card" href="https://sitemap.lititzbmx.com/artifact-inventory/" target="_blank" rel="noopener"><span>Collection</span><strong>Artifact Archive</strong><p>Explore documented BMX objects, provenance, images, and related stories.</p><b>Browse artifacts <i aria-hidden="true">↗</i></b></a><a class="more-card" href="https://sitemap.lititzbmx.com/record-collection/" target="_blank" rel="noopener"><span>Media preservation</span><strong>Record Collection</strong><p>Open preserved interview, podcast, unboxing, and production dossiers.</p><b>Browse dossiers <i aria-hidden="true">↗</i></b></a><a class="more-card" href="https://sitemap.lititzbmx.com/campaigns/" target="_blank" rel="noopener"><span>Wider archive</span><strong>Campaigns and stories</strong><p>Discover preservation projects, community work, and connected BMX narratives.</p><b>Explore more <i aria-hidden="true">↗</i></b></a></div></section>
<section class="search-shell" id="search" data-universal-search><div class="section-head search-heading"><div><p class="eyebrow">Search the full register</p><h2>Inspect the records behind the entry points</h2></div><p>Search across {len(search_payload.get('entries',[])):,} indexed entries, then narrow to records, provisional objects, prices, chronology, sources, or public claims.</p></div><form class="search-form" role="search" data-search-form><label class="sr-only" for="home-universal-search">Search the register</label><input id="home-universal-search" data-search-input type="search" placeholder="Type a name, brand, year, publication, product, or exact ID" autocomplete="off"><button type="submit">Search</button></form><div class="layer-filters" aria-label="Filter search results by type">{home_filters}</div><div class="search-meta"><p data-search-summary aria-live="polite">Type a name, brand, year, publication, product, or exact ID.</p><p><strong data-search-count>0</strong> results</p></div><p class="loading-state" data-search-loading>Loading the search index…</p><p class="empty-state" data-search-empty hidden>No matching result. Check the spelling, use fewer words, or browse the exploration paths.</p><div class="search-results" data-search-results></div><div class="load-more-wrap"><button class="button button-secondary" type="button" data-search-more hidden>Load more results</button></div></section>
<section data-recent-section hidden><div class="section-head"><div><p class="eyebrow">Continue exploring</p><h2>Recently viewed</h2></div></div><div class="recent-list" data-recent-viewed></div></section>'''
write(OUT / 'index.html', layout('Public Knowledge Register', home, 'Search and explore the Lititz BMX Public Knowledge Register.', 'home', page_class='home-page'))

# Universal search.
filters=''.join(f'<button class="layer-filter" type="button" data-layer-filter="{key}" aria-pressed="{str(key=="all").lower()}">{label}</button>' for key,label in layer_buttons)
search_body=f'''{list_page_intro('Search','Search the entire register','One search across records, reviewed objects, prices, timeline entries, sources, and public claims.')}
<section class="search-shell" data-universal-search><form class="search-form" role="search" data-search-form><label class="sr-only" for="universal-search-input">Search the register</label><input id="universal-search-input" data-search-input type="search" placeholder="Type a name, brand, year, publication, product, or exact ID" autocomplete="off"><button type="submit">Search</button></form><div class="layer-filters" aria-label="Filter search results by type">{filters}</div><div class="search-meta"><p data-search-summary aria-live="polite">Type a name, brand, year, publication, product, or exact ID.</p><p><strong data-search-count>0</strong> results</p></div><p class="loading-state" data-search-loading>Loading the search index…</p><p class="empty-state" data-search-empty hidden>No matching result. Check the spelling, use fewer words, or browse the exploration paths.</p><div class="search-results" data-search-results></div><div class="load-more-wrap"><button class="button button-secondary" type="button" data-search-more hidden>Load more results</button></div></section>'''
write(OUT / 'search' / 'index.html', layout('Search', search_body, 'Universal search across six governed register layers.', 'search', [('Home',internal()),('Search',internal('search/'))]))

# Explore page.
brand_counts=Counter()
for r in records:
    for term in [x.strip() for x in re.split(r'[;|]', r.get('Brand / Promoter','')) if x.strip()]:
        brand_counts[term]+=1
popular_brands=[x for x in brand_counts.most_common(16) if len(x[0])<45]
brand_links=''.join(f'<a class="chip-link" href="{internal("search/?q="+quote(name))}">{esc(name)} <span aria-hidden="true">·</span> {count}</a>' for name,count in popular_brands)
era_counts=Counter()
for r in records:
    y=r.get('Start Year','')
    era=(y[:3]+'0s') if len(y)==4 and y.isdigit() else 'Undated'
    era_counts[era]+=1
era_links=''.join(f'<a class="chip-link" href="{internal("search/?q="+quote(era[:4]))}">{esc(era)} <span aria-hidden="true">·</span> {count}</a>' for era,count in sorted(era_counts.items()))
category_cards=''.join(f'<article class="journey-card"><p class="eyebrow">{esc(c["Category ID"])}</p><h3>{esc(c["Category Label"])}</h3><p>{esc(c["Definition"])}</p><a href="{internal("categories/"+c["Slug"]+"/")}">Browse {esc(c["Record Count"])} records →</a></article>' for c in categories if int(c.get('Record Count') or 0)>0)
explore=f'''{list_page_intro('Explore','Choose a path','Browse without learning the internal database structure first.')}
<section id="eras" class="panel"><p class="eyebrow">By era</p><h2>Move through time</h2><div class="chip-row">{era_links}</div></section>
<section id="people-brands" class="panel"><p class="eyebrow">People and brands</p><h2>Frequently represented names</h2><div class="chip-row">{brand_links}</div><p><a href="{internal('search/')}">Search any person, team, company, or promoter →</a></p></section>
<section><div class="section-head"><div><p class="eyebrow">By subject</p><h2>Browse the controlled categories</h2></div></div><div class="journey-grid">{category_cards}</div></section>
<section class="panel"><p class="eyebrow">Publication journeys</p><h2>Explore complete source groups</h2><p>Open a registered source to move through every retained record from the same issue, catalog, archive, or evidence route.</p><div class="actions">{action_link(internal('sources/'),'Browse sources')}{action_link(internal('chronology/'),'Browse the timeline',True)}</div></section>'''
write(OUT/'explore'/'index.html',layout('Explore',explore,'Simple exploration paths into the register.','explore',[('Home',internal()),('Explore',internal('explore/'))]))

# Records index.
category_options=''.join(f'<option value="{esc(c["Category ID"])}">{esc(c["Category Label"])}</option>' for c in categories if int(c.get('Record Count') or 0)>0)
decades=sorted(era_counts.keys())
decade_options=''.join(f'<option value="{esc(x)}">{esc(x)}</option>' for x in decades)
record_items=[]
for r in records:
    y=r.get('Start Year',''); dec=(y[:3]+'0s') if len(y)==4 and y.isdigit() else 'Undated'
    card=small_record_card(r)
    record_items.append(card.replace('<article class="result-card record-mini"',f'<article class="result-card record-mini" data-browse-item data-category="{esc(r.get("Category ID"))}" data-decade="{esc(dec)}"'))
record_body=f'''{list_page_intro('Browse','Source records',f'All {len(records):,} retained source occurrences. Use Universal Search for cross-register results, or narrow this list.')}
<section class="browse-tools"><label>Search records<input type="search" data-browse-search placeholder="ID, title, brand, subject, or status"></label><label>Category<select data-browse-category><option value="">All categories</option>{category_options}</select></label><label>Era<select data-browse-decade><option value="">All eras</option>{decade_options}</select></label></section><p><strong data-browse-count>{len(records)}</strong> records shown.</p><p class="empty-state" data-browse-empty hidden>No records match these filters.</p><div data-browse-root>{progressive_collection(record_items,'records-collection',24)}</div>'''
write(OUT/'records'/'index.html',layout('Source records',record_body,'Browse all source records.','explore',[('Home',internal()),('Records',internal('records/'))]))

# Record detail pages.
for r in records:
    rid=r['Master ID']; src=source_for_record(r); prices_for=prices_by_object.get(r.get('Original ID',''),[]); objs=objects_by_record.get(rid,[]); related=related_records(r)
    friendly=friendly_status(r.get('Research Status',''),r.get('Confidence',''))
    status_html=badge(r.get('Research Status',''),friendly)+badge(r.get('Confidence',''),r.get('Confidence','Evidence status'))
    evidence_note=r.get('Evidence / Limitation') or 'No separate evidence limitation was stated.'
    uncertainty_parts=[x for x in [r.get('Research Status'),r.get('Canonical Action'),r.get('Notes')] if x]
    uncertainty='<ul class="plain-list">'+''.join(f'<li>{esc(x)}</li>' for x in uncertainty_parts)+'</ul>' if uncertainty_parts else '<p>No additional unresolved note is recorded.</p>'
    price_html=''
    if prices_for:
        price_html='<section class="panel"><p class="eyebrow">Price evidence</p><h2>Source-specific prices</h2><div class="card-grid">'+''.join(f'<article class="result-card price-card"><p class="result-id">{esc(p["Price Observation ID"])}</p><h3>{esc(p["Product / Model"])}</h3><p><strong>{esc(p["Displayed Price"])}</strong></p><p>{esc(p["Price Basis"])}</p></article>' for p in prices_for[:12])+'</div>'+ (f'<p><a href="{internal("prices/?q="+quote(rid))}">View all {len(prices_for)} linked observations →</a></p>' if len(prices_for)>12 else '')+'</section>'
    object_html=''
    if objs:
        object_html='<section class="panel"><p class="eyebrow">Identity review</p><h2>Canonical object relationship</h2>'+''.join(f'<p><a href="{internal("objects/")}#{esc(o["Canonical Object ID"])}"><strong>{esc(o["Canonical Object ID"])}</strong> · {esc(o["Title"])}</a><br>{esc(o["Canonical Decision"])}</p>' for o in objs)+'</section>'
    related_html=''.join(small_record_card(x) for x in related)
    detail_pairs=[]
    for key in ['Source Stage','Original ID','Object Type','Start Year','End Year','Date Text','Brand / Promoter','Geography','BMXMuseum Status','Exact Reference ID','Source Role','Confidence','Rights Code','Research Status','Accessed','Category ID','Primary Category']:
        if r.get(key): detail_pairs.append(f'<dt>{esc(key)}</dt><dd>{esc(r[key])}</dd>')
    citation=f'{r["Master ID"]}. {r["Title"]}. Lititz BMX Public Knowledge Register, {RELEASE_VERSION}, data lock {DATA_LOCK}.'
    body=f'''<article data-record-meta data-id="{esc(rid)}" data-title="{esc(r['Title'])}"><section class="record-hero"><div class="record-kicker"><span class="record-id">{esc(rid)}</span>{status_html}</div><h1>{esc(r['Title'])}</h1></section>
<div class="actions"><a class="button button-secondary return-search" data-return-search hidden>Return to search results</a>{source_buttons(r)}{action_link(internal('records/'),'Browse all records',True)}</div>
{record_issue_navigation(r)}
<div class="human-layout"><div>
<section class="panel"><p class="eyebrow">What this is</p><h2>Plain-language summary</h2><p>{esc(record_summary(r))}</p></section>
<section class="panel"><p class="eyebrow">What we currently know</p><h2>Documented facts</h2>{record_plain_facts(r)}<p>{esc(r.get('Primary Subject'))}</p></section>
<section class="panel"><p class="eyebrow">Evidence and source</p><h2>Where this information came from</h2><p>{esc(evidence_note)}</p>{source_location_note(r)}<div class="actions">{source_buttons(r)}</div></section>
<section class="panel"><p class="eyebrow">Uncertainty and limitations</p><h2>What remains qualified</h2>{uncertainty}</section>
{price_html}{object_html}
<section><div class="section-head"><div><p class="eyebrow">Keep exploring</p><h2>Related records</h2></div></div><div class="related-grid">{related_html}</div></section>
</div><aside class="side-stack">
<section class="panel"><p class="eyebrow">Use this record</p><h2>Share or correct</h2><div class="actions"><button class="button button-secondary" type="button" data-copy="{esc(rid)}">Copy ID</button><button class="button button-secondary" type="button" data-copy="{esc(citation)}">Copy citation</button></div><p class="copy-feedback" data-copy-feedback aria-live="polite"></p><a href="{REPO_URL}/issues/new?template=record-correction.yml&title={quote('Record correction: '+rid)}">Suggest a correction →</a></section>
<section class="panel"><p class="eyebrow">Technical details</p><details><summary>Show complete register fields</summary><dl class="detail-list">{''.join(detail_pairs)}</dl></details></section>
</aside></div></article>'''
    extra=f'<link rel="canonical" href="{BASE_URL}records/{rid}/">'
    write(OUT/'records'/rid/'index.html',layout(f'{rid} — {r["Title"]}',body,record_summary(r),'explore',[('Home',internal()),('Records',internal('records/')),(rid,record_route(rid))],'record-page',extra))

# Categories.
cat_cards=[]
for c in categories:
    if int(c.get('Record Count') or 0)==0: continue
    cat_cards.append(f'<article class="journey-card"><p class="eyebrow">{esc(c["Category ID"])}</p><h3>{esc(c["Category Label"])}</h3><p>{esc(c["Definition"])}</p><a href="{internal("categories/"+c["Slug"]+"/")}">Browse {esc(c["Record Count"])} records →</a></article>')
cat_body=list_page_intro('Explore','Categories','Controlled navigation paths that do not replace each record’s exact historical type.')+f'<div class="journey-grid">{"".join(cat_cards)}</div>'
write(OUT/'categories'/'index.html',layout('Categories',cat_body,'Browse controlled categories.','explore',[('Home',internal()),('Categories',internal('categories/'))]))
for c in categories:
    subset=[r for r in records if r.get('Category ID')==c['Category ID']]
    cards=[small_record_card(r) for r in subset]
    body=list_page_intro('Category',c['Category Label'],c['Definition'],action_link(internal('categories/'),'All categories',True))+progressive_collection(cards,'category-'+c['Slug'],24)
    if not subset: body+='<p class="empty-state">No current record requires this holding category.</p>'
    write(OUT/'categories'/c['Slug']/'index.html',layout(c['Category Label'],body,c['Definition'],'explore',[('Home',internal()),('Categories',internal('categories/')),(c['Category Label'],internal('categories/'+c['Slug']+'/'))]))

# Sources / publication issue views.
source_cards=[]
for s in sources:
    usage=usage_by_id.get(s['Source ID'],{})
    title=(s.get('Notes') or s.get('Domain') or s['Source ID']).split(';')[0]
    source_cards.append(f'<article class="result-card"><div class="result-top"><span class="eyebrow">Registered source</span>{badge(usage.get("Count Reconciliation","MATCH"))}</div><h2><a href="{source_route(s["Source ID"])}">{esc(title)}</a></h2><p class="result-id">{esc(s["Source ID"])} · {esc(s["Domain"])}</p><p>{esc(usage.get("Register Record Count") or s.get("Record References") or 0)} records · {esc(usage.get("Price Observation Count") or 0)} prices</p></article>')
source_body=list_page_intro('Evidence','Publications and sources',f'{len(sources)} registered evidence routes. Open one to explore every associated record.')+progressive_collection(source_cards,'sources-collection',24)
write(OUT/'sources'/'index.html',layout('Sources',source_body,'Browse registered sources and publication issue groups.','explore',[('Home',internal()),('Sources',internal('sources/'))]))
for s in sources:
    sid=s['Source ID']; usage=usage_by_id.get(sid,{}); subset=records_by_source_url.get(s.get('URL',''),[]); title=(s.get('Notes') or s.get('Domain') or sid).split(';')[0]
    cards=[small_record_card(r) for r in subset]
    issue_summary=f'<div class="issue-summary"><span>{len(subset)} records</span><span>{esc(usage.get("Price Observation Count") or 0)} prices</span><span>{esc(s.get("Default Rights Treatment") or "Rights stated per record")}</span></div>'
    body=f'''{list_page_intro('Publication / source',title,f'{sid} · {s.get("Domain","")}',external_link(s.get('URL',''),'Open original source')+action_link(internal('sources/'),'All sources',True))}{issue_summary}<section class="panel"><p class="eyebrow">Source treatment</p><h2>Use and limitations</h2><p>{esc(s.get('Notes'))}</p><p><strong>Access route:</strong> {esc(s.get('Access Route'))}</p></section><section><div class="section-head"><div><p class="eyebrow">Records from this source</p><h2>{len(subset)} retained occurrences</h2></div><p>Move through these records as one publication or evidence journey.</p></div>{progressive_collection(cards,'source-'+sid,24) if cards else '<p class="empty-state">No source-record route was associated with this URL.</p>'}</section>'''
    write(OUT/'sources'/sid/'index.html',layout(title,body,f'Registered source {sid}.','explore',[('Home',internal()),('Sources',internal('sources/')),(sid,source_route(sid))]))

# Prices.
price_cards=[]
for p in prices:
    record_match=next((r for r in records if r.get('Original ID')==p.get('Source Object ID')),None)
    action=record_route(record_match['Master ID']) if record_match else p.get('Source URL','')
    price_cards.append(f'<article class="result-card price-card"><div class="result-top"><span class="eyebrow">Price observation</span>{badge(p.get("Confidence",""))}</div><h2 id="{esc(p["Price Observation ID"])}">{esc(p["Product / Model"])}</h2><p><strong>{esc(p["Displayed Price"])}</strong></p><p class="result-id">{esc(p["Price Observation ID"])} · {esc(p["Issue / Date"])} · {esc(p["Brand"])}</p><p>{esc(p["Price Basis"])}</p><a href="{esc(action)}">Inspect the supporting record →</a></article>')
price_body=list_page_intro('Explore','Prices and products',f'{len(prices):,} source-specific observations. These are evidence from their original context, not a modern value guide.')+progressive_collection(price_cards,'prices-collection',24)
write(OUT/'prices'/'index.html',layout('Prices and products',price_body,'Browse source-specific period prices.','explore',[('Home',internal()),('Prices',internal('prices/'))]))

# Objects.
object_cards=[]
for o in objects:
    member_links=' · '.join(f'<a href="{record_route(rid)}">{esc(rid)}</a>' for rid in [x.strip() for x in o.get('Member Record IDs','').split('|') if x.strip()])
    object_cards.append(f'<article class="result-card" id="{esc(o["Canonical Object ID"])}"><div class="result-top"><span class="eyebrow">Canonical object</span>{badge(o.get("Canonical Decision",""))}</div><h2>{esc(o["Title"])}</h2><p class="result-id">{esc(o["Canonical Object ID"])} · {esc(o["Date Text"])} · {esc(o["Object Type"])}</p><p>{esc(o["Canonical Decision"])}</p><p><strong>Source records:</strong> {member_links}</p></article>')
object_body=list_page_intro('Identity layer','Provisional objects',f'{len(objects):,} reviewed identities while every source occurrence stays visible.')+progressive_collection(object_cards,'objects-collection',24)
write(OUT/'objects'/'index.html',layout('Provisional objects',object_body,'Browse provisional canonical objects.','explore',[('Home',internal()),('Objects',internal('objects/'))]))

# Chronology.
chron_sorted=sorted(chronology,key=lambda x:((x.get('Start Year') or '9999'),x.get('Chronology ID','')))
timeline=''.join(f'<article class="timeline-item"><p class="eyebrow">{esc(row.get("Date Text") or row.get("Start Year") or "Undated")}</p><h3><a href="{record_route(row["Master ID"])}">{esc(row["Title"])}</a></h3><p class="result-id">{esc(row["Chronology ID"])} · {esc(row["Master ID"])} · {esc(row["Brand / Promoter"])}</p><p>{esc(row["Chronology Note"])}</p></article>' for row in chron_sorted)
chron_body=list_page_intro('Explore','Timeline',f'{len(chronology):,} dated or provisionally placed entries.')+f'<div class="timeline-list">{timeline}</div>'
write(OUT/'chronology'/'index.html',layout('Timeline',chron_body,'Chronological view of the register.','explore',[('Home',internal()),('Timeline',internal('chronology/'))]))

# Claims.
claim_cards=[]
for c in claims:
    claim_cards.append(f'<article class="result-card"><div class="result-top"><span class="eyebrow">Public claim</span>{badge(c.get("Publication Status",""))}</div><h2><a href="{internal("claims/"+c["Claim ID"]+"/")}">{esc(c["Claim Label"])}</a></h2><p><strong>{esc(c["Displayed Value"])} {esc(c["Unit"])}</strong></p><p class="result-id">{esc(c["Claim ID"])} · {esc(c["Reconciliation"])}</p></article>')
claim_body=list_page_intro('Trust layer','Public claims',f'{len(claims)} aggregate statements with itemized support and correction paths.')+progressive_collection(claim_cards,'claims-collection',24)
write(OUT/'claims'/'index.html',layout('Public claims',claim_body,'Browse public claims.','methodology',[('Home',internal()),('Claims',internal('claims/'))]))
for c in claims:
    cid=c['Claim ID']; items=claim_items_by_claim[cid]
    item_cards=[]
    for item in items:
        href=item.get('Item URL') or ''
        if href.startswith(BASE_URL): href=internal(href[len(BASE_URL):])
        elif href.startswith('/'): href=internal(href.lstrip('/'))
        title=f'<a href="{esc(href)}">{esc(item["Item Label"])}</a>' if href else esc(item['Item Label'])
        item_cards.append(f'<article class="result-card"><p class="eyebrow">{esc(item["Item Type"])}</p><h3>{title}</h3><p class="result-id">{esc(item["Item ID"])}</p><p>{esc(item["Item Note"])}</p>{badge(item.get("Item Status",""))}</article>')
    body=f'''<section class="record-hero"><div class="record-kicker"><span class="record-id">{esc(cid)}</span>{badge(c.get('Publication Status',''))}{badge(c.get('Reconciliation',''))}</div><h1>{esc(c['Claim Label'])}</h1><p class="lede"><strong>{esc(c['Displayed Value'])}</strong> {esc(c['Unit'])}</p></section><section class="panel"><p class="eyebrow">How it is counted</p><h2>Rule and boundary</h2><p>{esc(c['Counting Rule'])}</p><p>{esc(c['Limitations / Boundary'])}</p><p><strong>Recomputed support:</strong> {esc(c['Recomputed Item Count'])} · {esc(c['Reconciliation'])}</p></section><section><div class="section-head"><div><p class="eyebrow">Itemized support</p><h2>{len(items):,} supporting relationships</h2></div></div>{progressive_collection(item_cards,'claim-'+cid,24)}</section>'''
    write(OUT/'claims'/cid/'index.html',layout(f'{cid} — {c["Claim Label"]}',body,c['Claim Label'],'methodology',[('Home',internal()),('Claims',internal('claims/')),(cid,internal('claims/'+cid+'/'))]))

# Methodology / About.
method=f'''{list_page_intro('About','How the register works','The public experience is intentionally simple. The evidence model remains available whenever a user chooses to inspect it.')}
<section class="panel"><p class="eyebrow">The basic path</p><h2>Search → record → source → limitation → correction</h2><p>A visitor can explore without learning the database. A researcher can still reconstruct every public count and inspect every source route.</p></section>
<section class="panel" id="source-records-vs-objects"><p class="eyebrow">Source records and objects</p><h2>Why 1,010 records become 1,000 provisional objects</h2><p>A source record documents an occurrence: an advertisement in one issue, a catalog page, an event notice, or another evidence appearance. A provisional object is an identity decision. Ten reviewed duplicate groups account for the difference while all original occurrences remain visible.</p></section>
<div class="card-grid"><section class="panel"><h2>Evidence status</h2><p>Plain labels explain whether the source is strong, image-dependent, provisional, or still open.</p></section><section class="panel"><h2>Price treatment</h2><p>Prices stay attached to their source, date, currency, and stated basis. They are not averaged or converted into modern market values.</p></section><section class="panel" id="rights-boundary"><h2>Rights boundary</h2><p>The public site publishes metadata and source routes. It does not reproduce protected historical scans, pages, advertisements, or artwork.</p></section><section class="panel"><h2>Corrections</h2><p>Every record and claim exposes a direct correction path so the register can improve without hiding its revision history.</p></section></div>
<section class="panel"><p class="eyebrow">Data and validation</p><h2>Inspect the machinery</h2><div class="actions">{action_link(internal('data/'),'Public data')}{action_link(internal('validation/'),'Validation',True)}{action_link(internal('downloads/'),'Downloads',True)}</div></section>'''
write(OUT/'methodology'/'index.html',layout('About the register',method,'How the public register works.','methodology',[('Home',internal()),('About',internal('methodology/'))]))

# Data, downloads, validation. Keep the current release simple; prior files remain available inside disclosures.
current_data_names = [
    'ephemera-register-v2.0.0.csv', 'canonical-objects-v2.0.0.csv',
    'price-observations-v2.0.0.csv', 'source-register-v2.0.0.csv',
    'source-usage-v2.0.0.csv', 'chronology-v2.0.0.csv',
    'public-claims-v2.0.0.csv', 'claim-items-v2.0.0.csv',
    'category-register-v2.0.0.csv'
]
data_cards=[]
for name in current_data_names:
    f=DATA/name
    data_cards.append(f'<article class="result-card"><p class="eyebrow">Current v2.0.0 CSV</p><h2>{esc(f.name)}</h2><p>{f.stat().st_size:,} bytes</p><a href="{internal("data/"+f.name)}">Download CSV →</a></article>')
search_file=DATA/'universal-search-index-v2.0.0.json'
data_cards.append(f'<article class="result-card"><p class="eyebrow">Current search index</p><h2>{esc(search_file.name)}</h2><p>{search_file.stat().st_size:,} bytes</p><a href="{internal("data/"+search_file.name)}">Download JSON →</a></article>')
prior_data=[f for f in sorted(DATA.glob('*')) if f.is_file() and f.name not in set(current_data_names+[search_file.name]) and f.suffix.lower() in {'.csv','.json'}]
prior_links=''.join(f'<li><a href="{internal("data/"+f.name)}">{esc(f.name)}</a> · {f.stat().st_size:,} bytes</li>' for f in prior_data)
data_body=list_page_intro('Resources','Public data','The current v2.0.0 machine-readable exports are shown first.')+f'<div class="card-grid">{"".join(data_cards)}</div><section class="panel"><details><summary>Prior-release and build-control datasets</summary><p>These remain available for reproducibility and release history, but they are not the current public data layer.</p><ul class="plain-list">{prior_links}</ul></details></section>'
write(OUT/'data'/'index.html',layout('Public data',data_body,'Current v2.0.0 public datasets.','methodology',[('Home',internal()),('Data',internal('data/'))]))

current_download=DOWNLOADS/WORKBOOK
current_card=f'<article class="result-card"><p class="eyebrow">Current governed workbook</p><h2>{esc(current_download.name)}</h2><p>{current_download.stat().st_size:,} bytes</p><a href="{internal("downloads/"+current_download.name)}">Download workbook →</a></article>'
prior_downloads=[f for f in sorted(DOWNLOADS.iterdir()) if f.is_file() and f.name!=WORKBOOK]
prior_download_links=''.join(f'<li><a href="{internal("downloads/"+f.name)}">{esc(f.name)}</a> · {f.stat().st_size:,} bytes</li>' for f in prior_downloads)
download_body=list_page_intro('Resources','Downloads','The current governed workbook is presented first.')+f'<div class="card-grid">{current_card}</div><section class="panel"><details><summary>Prior release workbooks and packages</summary><p>Retained for continuity, audit, and rollback—not as the current v2.0.0 data source.</p><ul class="plain-list">{prior_download_links}</ul></details></section>'
write(OUT/'downloads'/'index.html',layout('Downloads',download_body,'Current workbook and prior release downloads.','methodology',[('Home',internal()),('Downloads',internal('downloads/'))]))
validation_data=json.loads((DOCS/'V2.0.0-FINAL-PREDEPLOYMENT-QA.json').read_text(encoding='utf-8'))
authorization_data=json.loads((DOCS/'V2.0.0-RELEASE-AUTHORIZATION.json').read_text(encoding='utf-8'))
cleanup_qa=json.loads((DOCS/'V2.0.0-DOCUMENTATION-CLEANUP-QA.json').read_text(encoding='utf-8'))
claim_map={c['Claim ID']:c for c in claims}
checks=[
 ('Source records',1010,len(records)),('Canonical objects',1000,len(objects)),('Price observations',717,len(prices)),('Registered sources',73,len(sources)),('Public claims',69,len(claims)),('Search entries',3879,len(search_payload.get('entries',[]))),('Chronology rows',1010,len(chronology))]
check_cards=''.join(f'<article class="result-card"><p class="eyebrow">Parity check</p><h2>{esc(label)}</h2><p><strong>{actual:,}</strong> generated · <strong>{expected:,}</strong> governed</p>{badge("PASS" if actual==expected else "FAIL")}</article>' for label,expected,actual in checks)
open_count=claim_map.get('PKR-CLM-006',{}).get('Displayed Value','28')
image_backlog=claim_map.get('PKR-CLM-016',{}).get('Displayed Value','949')
recurring_backlog=claim_map.get('PKR-CLM-017',{}).get('Displayed Value','235')
validation_body=list_page_intro('Trust layer','Validation','The current authority is the final v2.0.0 QA and project-owner release authorization. Earlier RC1 and RC2 documents remain available only as historical supporting records.')+f'''<div class="card-grid">{check_cards}</div>
<section class="panel"><p class="eyebrow">Current release authority</p><h2>Final QA: {esc(validation_data.get('result'))} · Cleanup QA: {esc(cleanup_qa.get('result'))} · Deployment: {esc(authorization_data.get('status'))}</h2><p>The final technical checks passed and the exact public-facing candidate completed project-owner ordinary-browser review. The public site remains unchanged until the controlled push.</p><div class="actions"><a class="button" href="{internal('docs/V2.0.0-FINAL-PREDEPLOYMENT-QA.md')}">Read final QA</a><a class="button button-secondary" href="{internal('docs/V2.0.0-RELEASE-AUTHORIZATION.md')}">Read release authorization</a><a class="button button-secondary" href="{internal('docs/V2.0.0-DOCUMENTATION-CLEANUP-QA.md')}">Read cleanup QA</a></div></section>
<section class="panel"><p class="eyebrow">Disclosed research status</p><h2>Uncertainty is published, not hidden</h2><p><strong>{esc(open_count)}</strong> open or unresolved records, <strong>{esc(image_backlog)}</strong> indexed-text records awaiting page-image comparison, and <strong>{esc(recurring_backlog)}</strong> recurring candidates remain visible as governed research queues. In addition, <strong>87</strong> source routes explicitly state that the exact page remains unresolved.</p><p>These are content-status disclosures—not broken pages, failed parity, or missing routes.</p><div class="actions"><a class="button button-secondary" href="{internal('claims/PKR-CLM-006/')}">Open-record claim</a><a class="button button-secondary" href="{internal('claims/PKR-CLM-016/')}">Page-image backlog</a><a class="button button-secondary" href="{internal('claims/PKR-CLM-017/')}">Recurring candidates</a></div></section>
<section class="panel"><details><summary>Historical QA and release checkpoints</summary><p>RC1, RC2, v1.2.0, and earlier QA files are retained for audit history. Their pre-release language is superseded by the current authority above.</p><a href="{internal('docs/README.md')}">Read the documentation status guide →</a></details></section>'''
write(OUT/'validation'/'index.html',layout('Validation',validation_body,'Final v2.0.0 validation, release authorization, and disclosed research status.','methodology',[('Home',internal()),('Validation',internal('validation/'))]))

# 404 and machine files.
write(OUT/'404.html',layout('Page not found',list_page_intro('Navigation','Page not found','This route is not part of the public register.',action_link(internal(),'Return home')+action_link(internal('search/'),'Search the register',True)),'Page not found.','home'))
write(OUT/'robots.txt',f'User-agent: *\nAllow: /\nSitemap: {BASE_URL}sitemap.xml\n')
urls=[]
for p in OUT.rglob('index.html'):
    rel=p.relative_to(OUT).as_posix()
    urls.append(BASE_URL+rel[:-10])
write(OUT/'sitemap.xml','<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'  <url><loc>{esc(url)}</loc></url>\n' for url in sorted(set(urls)))+'</urlset>\n')

# Basic build report before QA.
report={
    'status':'BUILT — V2.0.0 AUTHORIZED DEPLOYMENT RELEASE',
    'public_deployment_changed':False,
    'deployment_authorization':'CLEARED FOR CONTROLLED DEPLOYMENT',
    'source_records':len(records),
    'canonical_objects':len(objects),
    'price_observations':len(prices),
    'registered_sources':len(sources),
    'public_claims':len(claims),
    'claim_items':len(claim_items),
    'chronology_rows':len(chronology),
    'search_entries':len(search_payload.get('entries',[])),
    'generated_html_pages':len(list(OUT.rglob('*.html'))),
    'sitemap_urls':len(set(urls)),
    'record_routes':len(list((OUT/'records').glob('EPH-* /index.html'))) if False else len(list((OUT/'records').glob('EPH-*/index.html'))),
    'brand_asset':LOGO,
    'experience_principle':'Simple on the surface. Rigorous underneath.',
    'build_time_utc':datetime.now(timezone.utc).isoformat(),
}
write(OUT/'build-report.json',json.dumps(report,indent=2)+'\n')
write(ROOT/'RC2-BUILD-REPORT.json',json.dumps(report,indent=2)+'\n')

# The portable builder already lives at site/build.py in the repository package.

print(json.dumps(report,indent=2))
