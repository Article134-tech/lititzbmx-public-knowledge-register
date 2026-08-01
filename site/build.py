from pathlib import Path
from collections import defaultdict
import csv, html, json, shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"
DATA = ROOT / "data"
DOWNLOADS = ROOT / "downloads"
DOCS = ROOT / "docs"
ASSETS = ROOT / "site" / "assets"
BASE_PATH = "/lititzbmx-public-knowledge-register/"
BASE_URL = "https://article134-tech.github.io/lititzbmx-public-knowledge-register/"
REPO_URL = "https://github.com/Article134-tech/lititzbmx-public-knowledge-register"
ARCHIVE_URL = "https://lititzbmx.com"
LOGO = "Lititz-BMX-Logo-White-Tire-White-Lettering.png"
WORKBOOK = "Lititz_BMX_Public_Knowledge_Register_Ephemera_v1.1.0_RELEASE_CANDIDATE.xlsx"


def esc(v): return html.escape("" if v is None else str(v))
class SafeHTML(str): pass

def read_csv(name):
    with (DATA / name).open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def internal(path=""): return BASE_PATH + path.lstrip("/")

def status_badge(value):
    text = str(value or "Not stated")
    key = text.lower(); cls = "neutral"
    if any(x in key for x in ("pass", "match", "ready", "verified", "included")): cls = "pass"
    elif any(x in key for x in ("open", "lead", "review", "estimate", "medium", "unconfirmed", "provisional", "pending")): cls = "review"
    elif any(x in key for x in ("low", "fail")): cls = "low"
    return f'<span class="status status-{cls}">{esc(text)}</span>'

def link_value(value):
    text = str(value or "")
    if text.startswith(("http://", "https://")): return f'<a href="{esc(text)}">{esc(text)}</a>'
    return esc(text)

def field_list(row, order=None):
    keys = order or list(row.keys()); out = ['<dl class="field-list">']
    status_keys = {"status","publication status","reconciliation","count reconciliation","confidence","research status","canonical decision","duplicate decision"}
    for key in keys:
        value = row.get(key)
        if value in (None, ""): continue
        rendered = status_badge(value) if key.lower() in status_keys else link_value(value)
        out.append(f'<dt>{esc(key)}</dt><dd>{rendered}</dd>')
    out.append('</dl>'); return "".join(out)

def table(rows, columns, table_id=None, caption=None):
    ident = f' id="{esc(table_id)}"' if table_id else ""
    out = [f'<div class="table-wrap"><table class="responsive-table"{ident}>']
    if caption: out.append(f'<caption class="sr-only">{esc(caption)}</caption>')
    out.append('<thead><tr>'); out += [f'<th scope="col">{esc(c)}</th>' for c in columns]; out.append('</tr></thead><tbody>')
    status_cols = {"status","publication status","reconciliation","count reconciliation","confidence","research status","priority","rights treatment"}
    for row in rows:
        out.append('<tr data-filter-item>')
        for c in columns:
            v = row.get(c, "")
            rendered = str(v) if isinstance(v, SafeHTML) else link_value(v)
            if c.lower() in status_cols: rendered = status_badge(v)
            out.append(f'<td data-label="{esc(c)}">{rendered}</td>')
        out.append('</tr>')
    out.append('</tbody></table></div>'); return "".join(out)

def filter_controls(target_id, noun, total, placeholder):
    iid = f'filter-{target_id}'
    return f'''<div class="filter-tools" data-filter-tools data-target="{esc(target_id)}" data-noun="{esc(noun)}">
<label for="{iid}">Search {esc(noun)}</label><div class="filter-row"><input id="{iid}" class="search" type="search" data-filter-input placeholder="{esc(placeholder)}" autocomplete="off"><button class="button button-secondary" type="button" data-filter-reset>Reset</button></div>
<p class="filter-summary" aria-live="polite"><strong data-filter-count>{total}</strong> of {total} {esc(noun)} shown</p><p class="empty-state" data-filter-empty hidden>No matching {esc(noun)}. Clear the search and try again.</p></div>'''

def nav_link(href, label, current, key, external=False):
    active = current == key
    return f'<a class="nav-link{" is-current" if active else ""}" href="{esc(href)}"{" aria-current=\"page\"" if active else ""}{" target=\"_blank\" rel=\"noopener\"" if external else ""}>{esc(label)}</a>'

def breadcrumbs(items):
    if not items: return ""
    out = ['<nav class="breadcrumbs" aria-label="Breadcrumb"><ol>']
    for i, (label, url) in enumerate(items):
        out.append(f'<li><span aria-current="page">{esc(label)}</span></li>' if i == len(items)-1 else f'<li><a href="{esc(url)}">{esc(label)}</a></li>')
    out.append('</ol></nav>'); return "".join(out)

def layout(title, body, description="", section="home", crumbs=None):
    nav = f'''<nav class="site-nav" aria-label="Primary navigation"><div class="nav-shell"><button class="nav-toggle" type="button" aria-expanded="false" aria-controls="primary-nav"><span aria-hidden="true">☰</span><span>Menu</span></button><div class="nav-panel" id="primary-nav">
<div class="nav-home">{nav_link(internal(), "Overview", section, "home")}</div>
<div class="nav-group"><span class="nav-group-label">Explore</span><div class="nav-links">{nav_link(internal("claims/"),"Claims",section,"claims")}{nav_link(internal("records/"),"Records",section,"records")}{nav_link(internal("objects/"),"Objects",section,"objects")}{nav_link(internal("prices/"),"Prices",section,"prices")}</div></div>
<div class="nav-group"><span class="nav-group-label">Evidence</span><div class="nav-links">{nav_link(internal("sources/"),"Sources",section,"sources")}{nav_link(internal("chronology/"),"Chronology",section,"chronology")}{nav_link(internal("validation/"),"Validation",section,"validation")}</div></div>
<div class="nav-group"><span class="nav-group-label">Resources</span><div class="nav-links">{nav_link(internal("data/"),"Data",section,"data")}{nav_link(internal("downloads/"),"Downloads",section,"downloads")}{nav_link(internal("methodology/"),"Methodology",section,"methodology")}</div></div>
<div class="nav-external">{nav_link(ARCHIVE_URL,"View Archive",section,"archive",True)}{nav_link(REPO_URL,"View on GitHub",section,"github",True)}</div></div></div></nav>'''
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>{esc(title)} · Lititz BMX</title><meta name="description" content="{esc(description or title)}"><link rel="stylesheet" href="{internal('assets/site.css')}"><script defer src="{internal('assets/site.js')}"></script></head><body data-section="{esc(section)}"><a class="skip-link" href="#main-content">Skip to main content</a>
<header class="site-header"><div class="masthead"><a class="brand-mark" href="{internal()}" aria-label="Lititz BMX Public BMX Knowledge Register home"><img src="{internal('assets/'+LOGO)}" width="446" height="532" alt="Lititz BMX"></a><div class="masthead-copy"><p class="brand-eyebrow">Lititz BMX</p><p class="product-title">Public BMX Knowledge Register</p><p class="release-line">Ephemera v1.1.0 · Claim-visible public register · Data locked August 1, 2026</p></div></div></header>{nav}<main id="main-content" tabindex="-1">{breadcrumbs(crumbs or [])}{body}</main>
<footer class="site-footer"><div class="footer-inner"><div class="footer-brand"><img src="{internal('assets/'+LOGO)}" width="446" height="532" alt=""><div><strong>Lititz BMX</strong><br><span>Public BMX Knowledge Register</span></div></div><div class="footer-copy"><p><strong>Evidence chain:</strong> Claim → Item → Evidence / Source → Limitation / Status → Correction</p><p>No protected historical source scans are reproduced. Maintained by Lititz BMX.</p><p><a href="{internal('methodology/')}">Methodology</a> · <a href="{internal('validation/')}">Validation</a> · <a href="{REPO_URL}/issues/new?template=record-correction.yml">Submit a correction</a></p></div></div></footer></body></html>'''

claims = read_csv("public-claims-v1.1.csv"); claim_items = read_csv("claim-items-v1.1.csv"); objects = read_csv("canonical-objects-v1.1.csv"); records = read_csv("ephemera-register-v1.1.csv"); prices = read_csv("price-observations-v1.1.csv"); source_register = read_csv("source-register-v1.1.csv"); source_usage = read_csv("source-usage-v1.1.csv"); chronology = read_csv("chronology-v1.1.csv"); validation = read_csv("validation-v1.1.csv")
claim_items_by_claim = defaultdict(list)
for x in claim_items: claim_items_by_claim[x["Claim ID"]].append(x)
usage_by_source = {x["Source ID"]:x for x in source_usage}; source_by_url = {x["URL"]:x for x in source_register}
records_by_url = defaultdict(list); prices_by_url = defaultdict(list); objects_by_record = defaultdict(list); records_by_original = defaultdict(list); prices_by_object = defaultdict(list)
for r in records:
    for k in ("Primary Source URL","Secondary Source URL"):
        if r.get(k): records_by_url[r[k]].append(r)
    if r.get("Original ID"): records_by_original[r["Original ID"]].append(r)
for p in prices:
    if p.get("Source URL"): prices_by_url[p["Source URL"]].append(p)
    if p.get("Source Object ID"): prices_by_object[p["Source Object ID"]].append(p)
for o in objects:
    for rid in [x.strip() for x in o.get("Member Record IDs","").split("|") if x.strip()]: objects_by_record[rid].append(o)

if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir(parents=True); shutil.copytree(ASSETS,OUT/"assets"); shutil.copytree(DATA,OUT/"data"); shutil.copytree(DOWNLOADS,OUT/"downloads"); shutil.copytree(DOCS,OUT/"docs"); (OUT/".nojekyll").write_text(""); shutil.copy2(ROOT/"release-manifest.json",OUT/"release-manifest.json")
claim_ids = {x["Claim ID"] for x in claims}
metrics=[("Source records",len(records),"PKR-CLM-001","Inspect all source records"),("Canonical objects",len(objects),"PKR-CLM-002","Inspect the canonical-object count"),("Price observations",len(prices),"PKR-CLM-003","Inspect all price observations"),("Registered sources",len(source_register),"PKR-CLM-004","Inspect the source count"),("Public claims",len(claims),None,"Inspect all public claims"),("Claim-item relationships",len(claim_items),None,"Inspect relationship validation"),("Chronology rows",len(chronology),"PKR-CLM-009","Inspect chronology support"),("Validation checks passing",sum(1 for x in validation if x.get("Status")=="PASS"),None,"Inspect validation results")]
cards=[]
for label,value,cid,action in metrics:
    href=internal(f"claims/{cid}/") if cid in claim_ids else internal("claims/" if label=="Public claims" else "validation/")
    cards.append(f'<a class="metric-card" href="{href}"><span class="metric-value">{value}</span><span class="metric-label">{esc(label)}</span><span class="metric-action">{esc(action)} <span aria-hidden="true">→</span></span></a>')
home=f'''<section class="hero home-hero"><p class="kicker">Public research product</p><h1>Every claim can be inspected. Every number opens.</h1><p class="lede">A claim-visible BMX ephemera register connecting aggregate statements to records, evidence routes, limitations, status, and correction pathways.</p><div class="actions"><a class="button" href="{internal('claims/')}">Browse public claims</a><a class="button button-secondary" href="{internal('downloads/'+WORKBOOK)}">Download the v1.1.0 workbook</a></div></section>
<section><div class="section-heading"><div><p class="kicker">Current release candidate</p><h2>Register totals</h2></div><p>Each total links to its definition, itemized support, or release-gate evidence.</p></div><div class="metrics">{''.join(cards)}</div></section>
<section><div class="section-heading"><div><p class="kicker">Product navigation</p><h2>Choose a route into the register</h2></div></div><div class="product-grid"><article class="product-card"><h3>Explore</h3><p>Browse claims, source occurrences, reviewed identities, and price evidence.</p><ul class="link-list"><li><a href="{internal('claims/')}">Claims</a></li><li><a href="{internal('records/')}">Records</a></li><li><a href="{internal('objects/')}">Objects</a></li><li><a href="{internal('prices/')}">Prices</a></li></ul></article><article class="product-card"><h3>Evidence</h3><p>Trace sources, chronology, rights treatment, and validation.</p><ul class="link-list"><li><a href="{internal('sources/')}">Sources</a></li><li><a href="{internal('chronology/')}">Chronology</a></li><li><a href="{internal('validation/')}">Validation</a></li></ul></article><article class="product-card"><h3>Resources</h3><p>Download datasets, release files, and methodology.</p><ul class="link-list"><li><a href="{internal('data/')}">Data</a></li><li><a href="{internal('downloads/')}">Downloads</a></li><li><a href="{internal('methodology/')}">Methodology</a></li></ul></article></div></section>
<section class="panel evidence-panel"><p class="kicker">Governing principle</p><h2>Claim visibility and traceability</h2><p>If the register makes a claim, the public user must be able to inspect the details supporting that claim.</p><p class="evidence-chain"><code>CLAIM → ITEM → EVIDENCE / SOURCE → LIMITATION / STATUS → CORRECTION</code></p></section><section class="panel"><p class="kicker">Rights boundary</p><h2>Metadata and evidence routes—not copied historical scans</h2><p>No historical catalog, flyer, advertisement, publication, or BMXMuseum source scan is reproduced.</p></section>'''
write(OUT/"index.html",layout("Public BMX Knowledge Register",home,"Claim-visible public register of BMX ephemera and supporting evidence.","home"))

claim_rows=[]
for r in claims:
    cid=r["Claim ID"]; claim_rows.append({"Claim ID":SafeHTML(f'<a class="id-link" href="{internal(f"claims/{cid}/")}">{cid}</a>'),"Claim Label":r["Claim Label"],"Displayed Value":r["Displayed Value"],"Unit":r["Unit"],"Category":r["Category"],"Publication Status":r["Publication Status"],"Reconciliation":r["Reconciliation"],"Action":SafeHTML(f'<a href="{internal(f"claims/{cid}/")}">Inspect claim</a>')})
body=f'<section class="hero"><p class="kicker">Explore</p><h1>Public Claims</h1><p>All {len(claims)} aggregate claims, counting rules, limitations, correction routes, and reconciliation results.</p></section>{filter_controls("claims-table","claims",len(claims),"Search by claim ID, label, category, or status")}{table(claim_rows,list(claim_rows[0]),"claims-table","Public claims")}'
write(OUT/"claims"/"index.html",layout("Public Claims",body,section="claims",crumbs=[("Overview",internal()),("Claims",internal("claims/"))]))
for c in claims:
    cid=c["Claim ID"]; items=claim_items_by_claim[cid]; rows=[]
    for i in items: rows.append({"Item Type":i["Item Type"],"Item ID":i["Item ID"],"Item Label":i["Item Label"],"Item Status":i["Item Status"],"Item Note":i["Item Note"],"Open":SafeHTML(f'<a href="{esc(i.get("Item URL",""))}">Open item</a>') if i.get("Item URL") else ""})
    body=f'<section class="claim-identity"><p class="kicker">Public claim</p><h1>{cid} <span>— {esc(c["Claim Label"])}</span></h1><p class="claim-total"><strong>{esc(c["Displayed Value"])}</strong> {esc(c["Unit"])}</p><div class="status-row">{status_badge(c["Publication Status"])}{status_badge(c["Reconciliation"])}</div></section><div class="reconciliation-bar"><strong>Reconciliation:</strong> displayed value {esc(c["Displayed Value"])}; recomputed support {esc(c["Recomputed Item Count"])}; status {esc(c["Reconciliation"])}.</div><div class="actions"><a class="button" href="{esc(c.get("Correction URL",""))}">Submit a claim correction</a><a class="button button-secondary" href="{internal("claims/")}">Back to all claims</a></div><section class="panel"><p class="kicker">Definition</p><h2>Counting rule and boundary</h2>{field_list(c)}</section><section class="panel"><p class="kicker">Itemized evidence</p><h2>Supporting items ({len(items)})</h2>{filter_controls("items-"+cid,"supporting items",len(items),"Search IDs, labels, notes, or status")}{table(rows,["Item Type","Item ID","Item Label","Item Status","Item Note","Open"],"items-"+cid,"Supporting items")}</section>'
    write(OUT/"claims"/cid/"index.html",layout(f'{cid} — {c["Claim Label"]}',body,section="claims",crumbs=[("Overview",internal()),("Claims",internal("claims/")),(cid,internal(f"claims/{cid}/"))]))

record_rows=[]
for r in records:
    rid=r["Master ID"]; record_rows.append({"Record ID":SafeHTML(f'<a class="id-link" href="{internal(f"records/{rid}/")}">{rid}</a>'),"Title":r["Title"],"Date":r["Date Text"],"Brand / Promoter":r["Brand / Promoter"],"Object Type":r["Object Type"],"Confidence":r["Confidence"],"Research Status":r["Research Status"],"Action":SafeHTML(f'<a href="{internal(f"records/{rid}/")}">Open record</a>')})
body=f'<section class="hero"><p class="kicker">Explore</p><h1>Source Records</h1><p>All {len(records)} source occurrences and provenance records.</p></section>{filter_controls("records-table","records",len(records),"Search record ID, title, brand, type, status, or date")}{table(record_rows,list(record_rows[0]),"records-table","Source records")}'
write(OUT/"records"/"index.html",layout("Source Records",body,section="records",crumbs=[("Overview",internal()),("Records",internal("records/"))]))
for r in records:
    rid=r["Master ID"]; rel=[]
    for o in objects_by_record.get(rid,[]): rel.append(f'<div><h3>Canonical object</h3><p><a class="relation-link" href="{internal("objects/")}#{o["Canonical Object ID"]}">{o["Canonical Object ID"]} — {esc(o["Title"])}</a></p></div>')
    for p in prices_by_object.get(r.get("Original ID",""),[]): rel.append(f'<div><h3>Price evidence</h3><p><a class="relation-link" href="{internal("prices/")}#{p["Price Observation ID"]}">{p["Price Observation ID"]} — {esc(p["Displayed Price"])}</a></p></div>')
    s=source_by_url.get(r.get("Primary Source URL",""))
    if s: rel.append(f'<div><h3>Registered source</h3><p><a class="relation-link" href="{internal(f"sources/{s["Source ID"]}/")}">{s["Source ID"]} — {esc(s["Domain"])}</a></p></div>')
    body=f'<section class="record-identity"><p class="kicker">Source record</p><h1>{rid} <span>— {esc(r["Title"])}</span></h1><div class="status-row">{status_badge(r["Confidence"])}{status_badge(r["Research Status"])}</div></section><div class="actions"><a class="button" href="{REPO_URL}/issues/new?template=record-correction.yml&title=Record%20correction%3A%20{rid}">Submit a record correction</a><a class="button button-secondary" href="{internal("records/")}">Back to all records</a></div><section class="panel"><p class="kicker">Record metadata</p><h2>Evidence, provenance, and limitations</h2>{field_list(r)}</section><section class="panel relationship-panel"><p class="kicker">Relationship navigation</p><h2>Connected register entries</h2>{"".join(rel) if rel else "<p>No related register entry was resolved for this release.</p>"}</section>'
    write(OUT/"records"/rid/"index.html",layout(f'{rid} — {r["Title"]}',body,section="records",crumbs=[("Overview",internal()),("Records",internal("records/")),(rid,internal(f"records/{rid}/"))]))

obj_cards=[]
for o in objects:
    oid=o["Canonical Object ID"]; members=' · '.join(f'<a href="{internal(f"records/{rid}/")}">{rid}</a>' for rid in [x.strip() for x in o.get("Member Record IDs","").split("|") if x.strip()]) or 'None listed'
    obj_cards.append(f'<article class="record-card anchor-offset" id="{oid}" data-filter-item><div class="record-card-heading"><div><p class="record-id">{oid}</p><h2>{esc(o["Title"])}</h2></div>{status_badge(o["Confidence"])}</div>{field_list(o)}<p class="related-line"><strong>Open member records:</strong> {members}</p></article>')
body=f'<section class="hero"><p class="kicker">Explore</p><h1>Canonical Objects</h1><p>{len(objects)} reviewed object identities while preserving all {len(records)} source occurrences.</p></section>{filter_controls("objects-collection","objects",len(objects),"Search object ID, title, brand, type, decision, or status")}<div class="record-collection" id="objects-collection">{"".join(obj_cards)}</div>'
write(OUT/"objects"/"index.html",layout("Canonical Objects",body,section="objects",crumbs=[("Overview",internal()),("Objects",internal("objects/"))]))

price_cards=[]
for p in prices:
    pid=p["Price Observation ID"]; rr=' · '.join(f'<a href="{internal(f"records/{r["Master ID"]}/")}">{r["Master ID"]}</a>' for r in records_by_original.get(p.get("Source Object ID",""),[])) or 'Not resolved'
    price_cards.append(f'<article class="record-card anchor-offset" id="{pid}" data-filter-item><div class="record-card-heading"><div><p class="record-id">{pid}</p><h2>{esc(p["Brand"])} — {esc(p["Product / Model"])}</h2></div>{status_badge(p["Confidence"])}</div><p class="price-callout">{esc(p["Displayed Price"])}</p>{field_list(p)}<p class="related-line"><strong>Related source record:</strong> {rr}</p></article>')
body=f'<section class="hero"><p class="kicker">Explore</p><h1>Price Observations</h1><p>{len(prices)} source-specific observations preserved without averaging, inflation adjustment, or unsupported MSRP conversion.</p></section>{filter_controls("prices-collection","price observations",len(prices),"Search price ID, brand, product, amount, date, basis, or confidence")}<div class="record-collection" id="prices-collection">{"".join(price_cards)}</div>'
write(OUT/"prices"/"index.html",layout("Price Observations",body,section="prices",crumbs=[("Overview",internal()),("Prices",internal("prices/"))]))

src_rows=[]
for s in source_register:
    sid=s["Source ID"]; src_rows.append({"Source ID":SafeHTML(f'<a class="id-link" href="{internal(f"sources/{sid}/")}">{sid}</a>'),"Domain":s["Domain"],"Stages Used":s["Stages Used"],"Source Roles":s["Source Roles"],"Record References":s["Record References"],"Rights Treatment":s["Default Rights Treatment"],"Priority":s["Preservation Priority"],"Action":SafeHTML(f'<a href="{internal(f"sources/{sid}/")}">Inspect source</a>')})
body=f'<section class="hero"><p class="kicker">Evidence</p><h1>Source Register</h1><p>{len(source_register)} registered public source routes, rights treatment, usage counts, and preservation priorities.</p></section>{filter_controls("sources-table","sources",len(source_register),"Search source ID, domain, role, rights treatment, or priority")}{table(src_rows,list(src_rows[0]),"sources-table","Registered sources")}'
write(OUT/"sources"/"index.html",layout("Source Register",body,section="sources",crumbs=[("Overview",internal()),("Sources",internal("sources/"))]))
for s in source_register:
    sid=s["Source ID"]; url=s["URL"]; usage=usage_by_source.get(sid,{}); rr=records_by_url.get(url,[]); pp=prices_by_url.get(url,[])
    rrrows=[{"Record ID":SafeHTML(f'<a href="{internal(f"records/{r["Master ID"]}/")}">{r["Master ID"]}</a>'),"Title":r["Title"],"Research Status":r["Research Status"],"Action":SafeHTML(f'<a href="{internal(f"records/{r["Master ID"]}/")}">Open record</a>')} for r in rr]
    prows=[{"Price ID":SafeHTML(f'<a href="{internal("prices/")}#{p["Price Observation ID"]}">{p["Price Observation ID"]}</a>'),"Brand":p["Brand"],"Product / Model":p["Product / Model"],"Displayed Price":p["Displayed Price"],"Confidence":p["Confidence"]} for p in pp]
    body=f'<section class="record-identity"><p class="kicker">Registered source</p><h1>{sid} <span>— {esc(s["Domain"])}</span></h1><p><a class="source-url" href="{esc(url)}">Open the public source route</a></p></section><div class="actions"><a class="button" href="{REPO_URL}/issues/new?template=record-correction.yml&title=Source%20correction%3A%20{sid}">Submit a source correction</a><a class="button button-secondary" href="{internal("sources/")}">Back to all sources</a></div><section class="panel"><p class="kicker">Registration</p><h2>Rights, access, and preservation treatment</h2>{field_list(s)}</section><section class="panel"><p class="kicker">Reconciliation</p><h2>Published usage</h2>{field_list(usage) if usage else "<p>No usage row.</p>"}</section><section class="panel"><p class="kicker">Connected records</p><h2>Related source records ({len(rr)})</h2>{table(rrrows,["Record ID","Title","Research Status","Action"],caption="Related source records") if rrrows else "<p>No directly matched record URL.</p>"}</section><section class="panel"><p class="kicker">Connected prices</p><h2>Related price observations ({len(pp)})</h2>{table(prows,["Price ID","Brand","Product / Model","Displayed Price","Confidence"],caption="Related price observations") if prows else "<p>No directly matched price observation URL.</p>"}</section>'
    write(OUT/"sources"/sid/"index.html",layout(f'{sid} — {s["Domain"]}',body,section="sources",crumbs=[("Overview",internal()),("Sources",internal("sources/")),(sid,internal(f"sources/{sid}/"))]))

chron_cards=[]
for c in chronology:
    cid=c["Chronology ID"]; rid=c.get("Master ID",""); rl=f'<a href="{internal(f"records/{rid}/")}">{rid}</a>' if rid else 'Not linked'
    chron_cards.append(f'<article class="record-card timeline-card anchor-offset" id="{cid}" data-filter-item><div class="timeline-date"><span>{esc(c["Date Text"])}</span></div><div class="timeline-content"><p class="record-id">{cid}</p><h2>{esc(c["Title"])}</h2>{field_list(c)}<p class="related-line"><strong>Open record:</strong> {rl}</p></div></article>')
body=f'<section class="hero"><p class="kicker">Evidence</p><h1>Chronology</h1><p>{len(chronology)} date-ordered records with source identity, confidence, and chronology notes.</p></section>{filter_controls("chronology-collection","chronology rows",len(chronology),"Search date, title, brand, type, record ID, or confidence")}<div class="record-collection timeline" id="chronology-collection">{"".join(chron_cards)}</div>'
write(OUT/"chronology"/"index.html",layout("Chronology",body,section="chronology",crumbs=[("Overview",internal()),("Chronology",internal("chronology/"))]))

vrows=[]
for v in validation:
    ev=v.get("Claim / evidence",""); evh=SafeHTML(f'<a href="{internal(f"claims/{ev}/")}">{ev}</a>') if ev in claim_ids else ev
    vrows.append({"Check":v["Check"],"Expected":v["Expected"],"Method":v["Method"],"Result":v["Result"],"Status":v["Status"],"Claim / evidence":evh})
pass_count=sum(1 for v in validation if v["Status"]=="PASS")
body=f'<section class="hero"><p class="kicker">Evidence</p><h1>Validation</h1><div class="success"><strong>{pass_count} of {len(validation)} release-gate checks pass.</strong><span>Validation supports structural integrity; it does not replace historical review.</span></div></section>{filter_controls("validation-table","validation checks",len(validation),"Search check, method, result, status, or claim")}{table(vrows,["Check","Expected","Method","Result","Status","Claim / evidence"],"validation-table","Validation checks")}<div class="actions"><a class="button button-secondary" href="{internal("docs/VALIDATION-REPORT.md")}">Download validation report</a><a class="button button-secondary" href="{internal("docs/BRAND-COMPLIANCE-RECORD.md")}">Read brand compliance record</a></div>'
write(OUT/"validation"/"index.html",layout("Validation",body,section="validation",crumbs=[("Overview",internal()),("Validation",internal("validation/"))]))

data_files=sorted((OUT/"data").glob("*.csv")); drows=[{"Dataset":f.name,"Version":"v1.1" if "v1.1" in f.name else "v1.0 frozen baseline","Bytes":f.stat().st_size,"Download":SafeHTML(f'<a href="{internal(f"data/{f.name}")}">Download CSV</a>')} for f in data_files]
body=f'<section class="hero"><p class="kicker">Resources</p><h1>Public Data</h1><p>Versioned CSV exports used to generate the public register.</p></section>{filter_controls("data-table","datasets",len(drows),"Search dataset name or version")}{table(drows,["Dataset","Version","Bytes","Download"],"data-table","Public datasets")}'
write(OUT/"data"/"index.html",layout("Public Data",body,section="data",crumbs=[("Overview",internal()),("Data",internal("data/"))]))
files=sorted(f for f in (OUT/"downloads").iterdir() if f.is_file()); frows=[{"File":f.name,"Type":f.suffix.lstrip('.').upper() or "File","Bytes":f.stat().st_size,"Download":SafeHTML(f'<a href="{internal(f"downloads/{f.name}")}">Download file</a>')} for f in files]
body=f'<section class="hero"><p class="kicker">Resources</p><h1>Downloads</h1><p>Release workbooks, authoritative sequence package, and checksums.</p></section>{filter_controls("downloads-table","downloads",len(frows),"Search file name or type")}{table(frows,["File","Type","Bytes","Download"],"downloads-table","Downloads")}'
write(OUT/"downloads"/"index.html",layout("Downloads",body,section="downloads",crumbs=[("Overview",internal()),("Downloads",internal("downloads/"))]))
method=f'<section class="hero"><p class="kicker">Resources</p><h1>Methodology</h1><p>The register is designed as a public research product: stable identifiers, visible evidence routes, explicit limitations, and correction pathways.</p></section><div class="method-grid"><section class="panel"><h2>Claim visibility</h2><p>Aggregate statements link to stable Claim IDs and normalized supporting items.</p></section><section class="panel"><h2>Canonical identity</h2><p>Source occurrences remain preserved even when multiple records are reviewed as one object.</p></section><section class="panel"><h2>Price evidence</h2><p>Prices remain source-specific and are not automatically averaged or converted into MSRP.</p></section><section class="panel"><h2>Rights treatment</h2><p>Historical source scans are not reproduced; metadata and evidence routes are retained.</p></section><section class="panel"><h2>Status language</h2><dl class="status-key"><dt>{status_badge("READY / MATCH / PASS")}</dt><dd>Release-ready under the stated rule.</dd><dt>{status_badge("OPEN / REVIEW / PROVISIONAL")}</dt><dd>A limitation or review task remains visible.</dd><dt>{status_badge("LOW / FAIL")}</dt><dd>Caution or corrective work is required.</dd></dl></section><section class="panel"><h2>Corrections</h2><p>Claim, record, and source pages include direct correction actions.</p><p><a class="button" href="{REPO_URL}/issues/new?template=record-correction.yml">Open correction form</a></p></section></div>'
write(OUT/"methodology"/"index.html",layout("Methodology",method,section="methodology",crumbs=[("Overview",internal()),("Methodology",internal("methodology/"))]))
notfound=f'<section class="hero"><p class="kicker">Navigation</p><h1>Page not found</h1><p>The requested route is not present in this release.</p><div class="actions"><a class="button" href="{internal()}">Return to register</a><a class="button button-secondary" href="{REPO_URL}/issues/new?template=record-correction.yml">Report broken route</a></div></section>'
write(OUT/"404.html",layout("Page not found",notfound,section="none"))
(OUT/"robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: "+BASE_URL+"sitemap.xml\n",encoding="utf-8")
urls=[]
for p in OUT.rglob("index.html"):
    rel=p.relative_to(OUT).as_posix(); urls.append(BASE_URL+rel[:-10])
sm=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']+[f'  <url><loc>{html.escape(u)}</loc></url>' for u in sorted(set(urls))]+['</urlset>']
(OUT/"sitemap.xml").write_text("\n".join(sm)+"\n",encoding="utf-8")
report={"generated_pages":len(list(OUT.rglob("*.html"))),"sitemap_urls":len(set(urls)),"claims":len(claims),"records":len(records),"objects":len(objects),"prices":len(prices),"sources":len(source_register),"chronology":len(chronology),"validation":len(validation),"claim_items":len(claim_items),"brand_asset":LOGO}
(OUT/"build-report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8"); print(json.dumps(report,indent=2))
