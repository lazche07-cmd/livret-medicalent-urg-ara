import json,re,unicodedata,fitz
from pathlib import Path
R=Path(__file__).resolve().parent.parent;D=R/'dist'
read=lambda name,prefix:json.loads((D/name).read_text()[len(prefix):-1])
a=read('checklists.js','window.CHECKLISTS=');g=read('guides.js','window.GUIDES=');meta=read('document.js','window.DOCUMENT=');pdf=fitz.open(D/'livret-source.pdf')
assert len(a)==73 and len(g)==8 and len(pdf)==106
assert len({f['medicine'] for f in a})==31
assert sum(f['population']=='adulte' for f in a)==42 and sum(f['population']=='pediatrie' for f in a)==31
expected=set(range(22,65))|set(range(66,105));actual=[n for f in a for n in f['pages']]
assert len(actual)==len(set(actual)) and set(actual)==expected
assert {f['page'] for f in g}==set(range(13,21))
assert {p['page'] for p in meta['pages']}==set(range(1,107))
assert all((D/f'assets/page-{n}.jpg').is_file() for n in range(1,107))
seen=set();counts={}
for f in a+g:
 for key,items in f['sections'].items():
  counts[key]=counts.get(key,0)+len(items)
  for it in items:
   assert it['text'].strip() and it['page'] in f['pages']
   assert it['id'] not in seen;seen.add(it['id'])
   if it.get('image'):assert (D/it['image']).is_file()
 for t in f['tables']:
  assert t['page'] in f['pages']
  assert t['rows'] and len(t['rows'])>1
  assert all(len(row)==len(t['rows'][0]) for row in t['rows'])
  assert t['id'] not in seen;seen.add(t['id'])
  # No merged page-sized cell masquerading as a dose row.
  assert not any(len([c for c in row if c])==1 and len(' '.join(row))>200 for row in t['rows'])
# Coverage of the full words and numeric tokens in each original medicine page body.
# This is an omission check, not a medical validation or a proof of cell alignment.
missing=[]
tok=lambda s:set(re.findall(r'[\wÀ-ÿ]+',unicodedata.normalize('NFKC',s).lower()))
headings={'indications','indication','contre','installation','et','surveillance','préparation','posologie','effets','secondaires','plusieurs','une','fiche','par'}
for f in a:
 for n in f['pages']:
  src=' '.join(b[4] for b in pdf[n-1].get_text('blocks') if 62<=b[1]<575 and not(b[4].strip()==str(n) and b[0]>375 and b[1]>555))
  dest=' '.join(it['text'] for v in f['sections'].values() for it in v if it['page']==n)+' '+' '.join(c for t in f['tables'] if t['page']==n for row in t['rows'] for c in row)+' '+' '.join(c for t in f['tables'] if t['page']==n for c in t.get('annotations',[]))
  absent=tok(src)-tok(dest)-headings
  if n==64:absent-={'2','absolues','dans','fibrinolyse','le','relatives','thrombolytique'}
  if absent:missing.append({'page':n,'missing':sorted(absent)})
assert not missing,missing
by={f['page']:f for f in a}
assert by[62]['title']=='SÉRUM SALÉ HYPERTONIQUE 7,5%'
assert by[104]['title']=='SÉRUM SALÉ HYPERTONIQUE 3%'
for n in [92,93]:
 assert any(it['text']=='Myasthénie' for it in by[n]['sections']['contra'])
 assert not any('Myasthénie' in it['text'] for it in by[n]['sections']['surveillance'])
assert len(by[33]['sections']['contra'])==4
assert 'Maximum 5 mg' in by[25]['sections']['dose'][0]['text']
assert '3ième CEE' in by[25]['sections']['dose'][1]['text']
assert len(by[63]['tables'])==2
assert sum('Contre-indication absolue :' in it['text'] for it in by[63]['sections']['contra'])==8
assert sum('Contre-indication relative :' in it['text'] for it in by[63]['sections']['contra'])==8
assert all(by[n]['warnings'] for n in [26,35,77,92,94,99,104])
byguide={f['page']:f for f in g}
assert len(byguide[13]['sections']['presentation'])==5 and len(byguide[13]['sections']['preparation'])==5
assert len(byguide[14]['sections']['presentation'])==18
assert len(byguide[15]['sections']['presentation'])==13
assert len(byguide[17]['sections']['presentation'])>90
assert len(byguide[18]['sections']['effects'])==9
assert len(byguide[20]['sections']['surveillance'])==15 and len(byguide[20]['sections']['presentation'])==6
report={'technical_checks':'passed','clinical_validation':False,'source_pages':106,'medicine_pages':82,'medicines':31,'medicine_checklists':73,'adult_checklists':42,'pediatric_checklists':31,'general_guides':8,'reference_pages':16,'tables':sum(len(f['tables']) for f in a),'items':counts,'source_body_word_omissions':missing,'limitations':['Contrôles techniques et relecture de transcription ; aucune validation clinique.','Les contrôles de couverture des mots ne prouvent pas à eux seuls la bonne association des colonnes.','Les symboles de la notice PSE ont été relus sur la page rendue ; la notice originale reste accessible.','Interface non vérifiée dans un navigateur dans cet environnement.']}
(R/'scripts/validation-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
