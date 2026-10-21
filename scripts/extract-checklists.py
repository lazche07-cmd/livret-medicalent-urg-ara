import fitz,json,re,unicodedata
from review_checklists import review
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
D=ROOT/'dist';doc=fitz.open(D/'livret-source.pdf');old=json.loads((D/'data.js').read_text()[14:-1]);oldmap={f['page']:f for f in old}
PAGES=list(range(22,65))+list(range(66,105))
CONT={64:63,68:67,71:70,76:75,78:77,80:79,89:88,97:96,102:101}

def norm(s):return ''.join(c for c in unicodedata.normalize('NFD',s) if not unicodedata.combining(c)).upper()
def heading(s):
 n=norm(s).strip()
 for pattern,key in [(r'^CONTRE[ -]?INDICATIONS?\s*:', 'contra'),(r'^INDICATIONS?\s*:','indication'),(r'^INSTALLATION\s+ET\s+SURVEILLANCE\s*:','surveillance'),(r'^EFFETS SECONDAIRES\s*:','effects'),(r'^PREPARATION\s+ET\s+POSOLOGIE\s*:','combined'),(r'^PREPARATION\s*:','preparation'),(r'^POSOLOGIE\s*:','dose')]:
  m=re.match(pattern,n)
  if m:return key,s[m.end():].strip()
 return None

def clean(s):return re.sub(r'\s+',' ',s).strip()
def overlap(b,t):
 r=fitz.Rect(b); inter=r&fitz.Rect(t)
 return not inter.is_empty and inter.get_area()/max(1,r.get_area())>.6

def extract(number):
 p=doc[number-1];tables=[]
 for t in p.find_tables().tables:
  if t.bbox[1]>55 and t.bbox[3]-t.bbox[1]>25:
   rows=[[clean(v or '') for v in row] for row in t.extract()]
   if any(any(re.search(r'\d',c) for c in row) for row in rows):
    # Ignore page-sized outer cells mistaken for part of a table. The true grid
    # starts at the following cell row; surrounding paragraphs are extracted normally.
    kept=[i for i,row in enumerate(rows) if not(len([c for c in row if c])==1 and len(' '.join(row))>200)]
    if not kept:continue
    bbox=list(t.bbox)
    if len(kept)!=len(rows):
     cells=[cell for i in kept for cell in t.rows[i].cells if cell]
     bbox=[min(c[0] for c in cells),min(c[1] for c in cells),max(c[2] for c in cells),max(c[3] for c in cells)]
     rows=[rows[i] for i in kept]
    context=[]
    # Remove empty phantom columns introduced by the discarded outer cell.
    keep=[i for i in range(len(rows[0])) if any(row[i] for row in rows)]
    rows=[[row[i] for i in keep] for row in rows]
    tables.append({'bbox':bbox,'rows':rows,'page':number,'context':context,'cells':[list(cell) for i in kept for cell in t.rows[i].cells if cell], 'annotations':[]})
 if number==63:
  # These two source tables have no drawn cell borders. Reconstruct their four
  # original columns directly from the source row blocks, without calculation.
  for top,bottom,label in [(282,374,'ÂGE < 75 ans'),(424,515,'ÂGE ≥ 75 ans')]:
   existing=next((t for t in tables if t['bbox'][1]<top+20 and t['bbox'][3]>bottom-15),None)
   if existing:
    existing['caption']=label;continue
   rows=[['Poids (kg)','Volume reconstitué (mL)','METALYSE (UI)','METALYSE (mg)']]
   for b in sorted(p.get_text('blocks'),key=lambda b:b[1]):
    if top<b[1]<bottom:
     cells=[clean(v) for v in b[4].strip().splitlines()]
     if len(cells)==4 and re.match(r'^[<≥0-9P]',cells[0]):rows.append(cells)
   tables.append({'bbox':[28,top,400,bottom],'rows':rows,'page':number,'caption':label})
 units=[];headers=[]
 for block in p.get_text('dict')['blocks']:
  if 'lines' not in block:continue
  lines=[]
  for line in block['lines']:
   text=''.join(s['text'] for s in line['spans']).strip()
   if not text:continue
   bbox=line['bbox']
   if bbox[1]<62 or bbox[1]>575:continue
   if text==str(number) and bbox[0]>375 and bbox[1]>555:continue
   if 'PLUSIEURS INDICATIONS' in text:continue
   in_table=False
   for table in tables:
    regions=table.get('cells',[table['bbox']])
    if any(overlap(bbox,r) for r in regions):
     tokens=lambda s:set(re.findall(r'\w+',clean(s).lower()))
     tabletext=' '.join(c for row in table['rows'] for c in row)
     if tokens(text)<=tokens(tabletext):in_table=True
     else:table.setdefault('annotations',[]).append(text)
   if in_table:continue
   lines.append({'text':text,'bbox':list(bbox),'size':max(s['size'] for s in line['spans'])})
  chunks=[]
  for line in lines:
   h=heading(line['text'])
   if h:
    headers.append({'key':h[0],'bbox':line['bbox'],'size':line['size']})
    chunks.append({'text':h[1],'bbox':line['bbox'],'heading':h[0],'size':line['size']})
   elif chunks and not chunks[-1].get('heading') and abs(chunks[-1]['size']-line['size'])<.5:
    chunks[-1]['text']+='\n'+line['text']; chunks[-1]['bbox'][2]=max(chunks[-1]['bbox'][2],line['bbox'][2]);chunks[-1]['bbox'][3]=line['bbox'][3]
   else:chunks.append({'text':line['text'],'bbox':line['bbox'],'size':line['size']})
  units.extend(chunks)
 # Assign the two top columns independently; full-width sections form the remaining flow.
 def classify(b):
  x,y,_,_=b
  preceding=[h for h in headers if h['bbox'][1]<=y+.1]
  if not preceding:return 'notes'
  last_y=max(h['bbox'][1] for h in preceding)
  band=[h for h in preceding if abs(h['bbox'][1]-last_y)<5]
  if len(band)>1:
   # Right-column contraindications and left-column indications share a baseline.
   chosen=min(band,key=lambda h:abs(h['bbox'][0]-x))
  else:chosen=band[0]
  return chosen['key']
 sections={k:[] for k in ['indication','contra','preparation','combined','dose','surveillance','effects','notes','presentation']}
 for b in p.get_text('blocks'):
  if b[1]<62 and re.search(r'Ampoule|Flacon|Concentration|Seringue|Solution|solution|Unidose|Kit|mg|UI|mL',b[4]):
   sections['presentation'].append({'text':clean(b[4]),'page':number})
 for u in sorted(units,key=lambda u:(u['bbox'][1],u['bbox'][0])):
  if not u['text']:continue
  key=u.get('heading') or classify(u['bbox'])
  sections[key].append({'text':u['text'],'page':number,'y':u['bbox'][1], 'x':u['bbox'][0], 'x2':u['bbox'][2], 'size':u['size']})
 for t in tables:t['section']=classify(t['bbox'])
 if number==64:
  sections['contra']=sections['notes'];sections['notes']=[]
 return sections,tables

fiches=[];audit=[]
for number in PAGES:
 sections,tables=extract(number)
 if number in CONT:
  parent=next(f for f in fiches if f['page']==CONT[number]);parent['pages'].append(number);parent['text']+='\n'+oldmap[number]['text']
  for k,v in sections.items():parent['sections'][k].extend(v)
  parent['tables'].extend(tables)
 else:
  f={k:v for k,v in oldmap[number].items() if k!='context'};f['context']=oldmap[number]['context'];f['pages']=[number];f['sections']=sections;f['tables']=tables;f['warnings']=[];fiches.append(f)

# Keep clauses and limits together. A leading bullet starts a new checkable item;
# continuation lines belong to that item. Dose sections stay grouped by branch.
for f in fiches:
 for key,blocks in f['sections'].items():
  items=[]
  diagrams=[]
  if key in ('preparation','dose','combined'):
   diagrams=[b for b in blocks if b.get('size',10)<8.5]
   blocks=[b for b in blocks if b.get('size',10)>=8.5]
  # Indications/contraindications/effects use hanging-indent bullets across PDF blocks.
  # Joining by section/page before splitting keeps wrapped clinical clauses intact.
  if key in ('indication','contra','effects'):
   bypage={}
   for b in blocks:bypage.setdefault(b['page'],[]).append(b['text'])
   blocks=[{'page':p,'text':'\n'.join(v)} for p,v in bypage.items()]
  for b in blocks:
   parts=re.split(r'\n(?=\s*[–‒−•-]\s|\s*[–‒−][A-ZÀÂÉÈÊÎÔÛ])',b['text'])
   if key=='surveillance':
    parts=[]
    for line in b['text'].splitlines():
     if parts and (not re.match(r'^[A-ZÀÂÉÈÊÎÔÛ]',line) or parts[-1].endswith(':')):parts[-1]+=' '+line
     else:parts.append(line)
   for part in parts:
    text=clean(part).lstrip('-–‒−• ').strip()
    if not text:continue
    if re.fullmatch(r'[+×X-]+',text):items.append({'text':text,'page':b['page'],'info':True});continue
    pieces=[text]
    if key=='effects' and not re.search(r'si |sauf|après|en cas|dépend|liée|dose|hémorragie',text,re.I):
     pieces=[];start=0;depth=0
     for i,c in enumerate(text):
      if c=='(':depth+=1
      if c==')':depth=max(0,depth-1)
      if c==',' and depth==0:pieces.append(text[start:i].strip());start=i+1
     pieces.append(text[start:].strip());pieces=[s for s in pieces if s]
     prefix=re.match(r'^([^:]+:)\s*',text)
     if prefix:pieces=[pieces[0]]+[prefix.group(1)+' '+piece for piece in pieces[1:]]
    for piece in pieces:items.append({'text':piece,'page':b['page']})
  for b in diagrams:items.append({'text':clean(b['text']),'page':b['page'],'info':True})
  f['sections'][key]=items
 # Join an isolated condition heading with its immediate dose paragraph, without
 # merging separate rhythm, age or dose branches.
 dose=f['sections']['dose'];merged=[]
 for item in dose:
  if item.get('info'):merged.append(item);continue
  newbranch=bool(re.match(r'^(RYTHME|[123](?:ère|ème|ième)? DOSE|Poids|POIDS|AGE|ÂGE|Si [<>]|SCA|NSTEMI|Anaphylaxie|Laryngite)',item['text']))
  if merged and merged[-1]['text'].rstrip().endswith(':') and '\n' not in merged[-1]['text'] and not newbranch and merged[-1]['page']==item['page']:
   merged[-1]['text']+='\n'+item['text']
  else:merged.append(item)
 f['sections']['dose']=merged
 for k in ('preparation','combined','dose'):
  joined=[]
  for it in f['sections'][k]:
   if joined and not it.get('info') and not joined[-1].get('info') and it['page']==joined[-1]['page'] and re.match(r'^[a-zàâéèêîôû(]',it['text']) and not it['text'].startswith(('puis ','soit ')):
    joined[-1]['text']+=' '+it['text']
   else:joined.append(it)
  f['sections'][k]=joined
 # Page 24 presents dosing within the preparation layout without a POSOLOGIE heading.
 if f['page']==24:
  src=f['sections']['preparation'];cut=next(i for i,it in enumerate(src) if it['text'].startswith('1ère dose'))
  f['sections']['dose']=src[cut:];f['sections']['preparation']=src[:cut]
 if f['page']==63:
  ci=f['sections']['contra'];fixed=[];qualifier=''
  for it in ci:
   text=it['text']
   if it['page']==64:
    if '1. Contre-indications absolues' in text:
     qualifier='Contre-indication absolue';continue
    change='2. Contre-indications relatives' in text
    text=text.replace('2. Contre-indications relatives','').strip()
    if text:fixed.append({'text':qualifier+' : '+text,'page':64})
    if change:qualifier='Contre-indication relative'
   else:fixed.append(it)
  f['sections']['contra']=fixed
 # The first adult anaphylaxis dose has two consecutive source lines.
 if f['page']==26:
  dose=f['sections']['dose']
  if len(dose)>1 and dose[1]['text'].startswith('soit '):dose[0]['text']+=' '+dose.pop(1)['text']
 if f['page']==77:f['warnings'].append('La page 78 comporte à la fois le titre « POSOLOGIE A 100 mg/kg/j en une fois » et une mention « En 2 prises ». Les deux mentions sont conservées ; faire confirmer le schéma applicable avant utilisation.')
 if f['page']==26:f['warnings'].append('Incohérence dans le PDF source, p. 26 : le texte de préparation du PSE mentionne « Concentration : 0,01mg/kg », alors que le schéma indique « 0,01 mg/mL ». Ces mentions sont conservées telles quelles ; faire confirmer la concentration avant utilisation.')
 review(f)
 for k,items in f['sections'].items():
  for i,it in enumerate(items):it['id']=f"{f['page']}-{k}-{i}"
 for i,t in enumerate(f['tables']):
  t['id']=f"{f['page']}-table-{i}"
  t.pop('cells',None)
 audit.append({'page':f['page'],'pages':f['pages'],'counts':{k:len(v) for k,v in f['sections'].items()},'tables':len(f['tables'])})
(D/'checklists.js').write_text('window.CHECKLISTS='+json.dumps(fiches,ensure_ascii=False)+';',encoding='utf8')
(ROOT/'scripts/extraction-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
print(len(fiches),'fiches,',sum(len(f['pages']) for f in fiches),'pages,',sum(sum(len(v) for v in f['sections'].values()) for f in fiches),'items,',sum(len(f['tables']) for f in fiches),'tableaux')
for f in fiches:
 if f['page'] in [24,25,26,44,67,70]:
  print('\nPAGE',f['page'])
  for k,v in f['sections'].items():print(k, [it['text'] for it in v])
