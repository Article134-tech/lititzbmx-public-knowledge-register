# Lititz BMX Public Knowledge Register — Link Integrity Audit

**Release:** v1.1.0 current live data set  
**Audit scope:** Generated public site, claim-item evidence actions, entity-to-source navigation, self-links, internal links, anchors, and source-dataset routes  
**Result:** PASS

## Root cause corrected

The prior generator treated `Item URL` as the only action for a Claim Item. In most cases that URL was the item's own internal register route, not the underlying evidence source. Several metadata fields also displayed self-referential routes such as `Object URL` and `Detail URL`. Ten duplicate-group Claim Items pointed to anchors that did not exist.

The corrected generator now keeps two routes separate:

1. **Open register item** — the stable Lititz BMX record, object, price, chronology, or source-registration route.
2. **Open evidence source** — the external source URL supporting that item.

Release assets retain a **Download asset** action because they are release files rather than historical evidence sources.

## Corrections

- Added external source actions to all evidence-bearing Claim Item cards.
- Added prominent primary and secondary source actions to every Source Record page.
- Added source actions to Canonical Object, Price Observation, Chronology, and Registered Source views.
- Added external source links to the Records and Sources index action cells without adding another table column.
- Added direct source-dataset links to every Claim page.
- Removed raw self-referential `Object URL` and `Detail URL` fields from public detail displays.
- Added 10 real duplicate-group anchors with canonical-object, member-record, and original-source navigation.
- Kept correction routes separate from evidence-source routes.

## Automated QA

- Generated HTML pages: **380**
- Internal links and anchors checked: **11,086**
- Internal link or anchor errors: **0**
- Content self-links: **0**
- Claim Item cards: **1,910**
- Claim Item cards with external evidence source: **1,904**
- Release asset cards with download action: **6**
- Source Record pages missing source action: **0 of 250**
- Canonical Object cards missing source action: **0 of 240**
- Price Observation cards missing source action: **0 of 101**
- Chronology cards missing source action: **0 of 250**
- Registered Source pages missing original-source action: **0 of 60**
- Reviewed duplicate-group anchors present: **10 of 10**
- Raw public `Object URL` self-fields remaining: **0**
- Raw public `Detail URL` self-fields remaining: **0**
- Claim pages missing source-dataset link: **0 of 58**

The audit validates route construction and source mapping in the generated site. It does not guarantee that every independent third-party website will remain online indefinitely.
