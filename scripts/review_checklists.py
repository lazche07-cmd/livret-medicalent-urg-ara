"""Source-preserving grouping corrections identified during full-document review.
No dose or preparation value is computed or substituted here.
"""
import re

def review(f):
 s=f['sections'];p=f['page']
 if p in (62,104):
  items=s['indication']
  if items and items[0]['text'].endswith('avec :'):
   prefix=items.pop(0)['text']
   for it in items:it['text']=prefix+' '+it['text']
 if p in (49,90):
  items=s['indication']
  if items and items[0]['text']=='Antalgie de':
   items.pop(0)
   for it in items:it['text']='Antalgie de : '+it['text']
 if p==31:
  items=s['indication'];out=[]
  for it in items:
   if ': ' in it['text']:
    prefix,details=it['text'].split(': ',1)
    out.extend(dict(it,text=prefix+' : '+part.strip()) for part in details.split(','))
   else:out.append(it)
  s['indication']=out
 if p==62:
  f['title']='SÉRUM SALÉ HYPERTONIQUE 7,5%'
  f['context']='Adulte · solution à reconstituer à 7,5 % selon le livret'
 # Illustration captions are retained as information, not stand-alone actions.
 for key in ('preparation','combined','dose'):
  for it in s[key]:
   if re.fullmatch(r'(?:PURE?|À DILUER|A DILUER|À RECONSTITUER|A RECONSTITUER|FLASH|EN IVD|INTRANASALE?|AÉROSOL|en nébulisation|ADMINISTRATION|IVD EN TITRATION|Concentration|[+×=\-]|[23]X|X 2|min|= ?[\d,.]+ mg/mL)',it['text'],re.I):it['info']=True
  # Repair a PDF line break that split one sentence into two controls.
  result=[]
  for it in s[key]:
   if result and not it.get('info') and not result[-1].get('info') and it['page']==result[-1]['page']:
    prev=result[-1]['text'];newcondition=re.match(r'^(?:POIDS|Poids|AGE|ÂGE|[123](?:ère|ème|ième)? DOSE|RYTHME)',it['text'])
    if re.search(r'(?:avec du|NaCl|objectif de|en fonction du|avec une|dans une|nécessaire pour)\s*$',prev) or (prev.endswith(':') and not newcondition):
     result[-1]['text']+=' '+it['text'];continue
   result.append(it)
  s[key]=result
 def join_all(key):
  main=[i for i in s[key] if not i.get('info')];info=[i for i in s[key] if i.get('info')]
  if main:s[key]=[{'text':'\n'.join(i['text'] for i in main),'page':main[0]['page']}]+info
 def join_from(key,start):
  items=s[key];index=next((i for i,it in enumerate(items) if not it.get('info') and it['text'].startswith(start)),None)
  if index is None:return
  first=items[index];group=[i for i in items[index:] if not i.get('info')];info=[i for i in items[index:] if i.get('info')]
  s[key]=items[:index]+[{'text':'\n'.join(i['text'] for i in group),'page':first['page']}]+info
 if p in (30,34,52,56,58,95):join_all('dose')
 if p in (26,72):join_from('dose','3ème DOSE')
 if p==24:
  d=s['dose'];i=next(i for i,it in enumerate(d) if it['text'].startswith('Après 2 à 3'))
  if i+1<len(d) and d[i+1]['text'].startswith('2ème dose'):
   d[i]['text']+=' '+d.pop(i+1)['text']
 if p==66:
  out=[]
  for it in s['dose']:
   parts=re.split(r'\s+(?=POIDS > 10 kg)',it['text'])
   out.extend(dict(it,text=t) for t in parts)
  s['dose']=out
 if p==57:join_all('dose')
 # General rules remain distinguishable from alternatives; all source clauses stay visible.
 if p==72:
  for it in s['dose']:it['text']=it['text'].lstrip(': ')
 if p==77:
  f['warnings']=['Le tableau p. 78 porte le titre « 100 mg/kg/j en une fois » et une mention « En 2 prises ». Les conditions selon l’âge et les plafonds par jour/par prise sont décrites p. 77 et conservées dans la posologie. Lire ces conditions avant de retenir une ligne du tableau.']
 warnings={
  35:'La branche « Si > 75 ans » du PDF p. 35 contient la mention « DOSE IV moindre » suivie d’une dose « en SC ». Ces termes sont reproduits sans modification ; faire confirmer la voie et le schéma prescrits.',
  92:'La fiche p. 92 cite l’anxiolyse per os et l’état de mal épileptique buccal/subjugal, mais le paragraphe posologie est intitulé « BUCCAL OU SUBJUGAL ». Aucune posologie per os distincte n’a été ajoutée dans l’adaptation.',
  94:'La posologie textuelle du PDF p. 94 indique « INTRANASAL : 0,4 mg », tandis que le tableau comporte des doses différentes selon le poids. L’unité du texte n’a pas été complétée ni corrigée automatiquement ; faire confirmer le schéma avant utilisation.',
  99:'La surveillance du PDF p. 99 parle d’une FR « sous les seuils » mais écrit « 1 à 5 ans : FR > 15/min ». Le signe est conservé tel quel dans l’adaptation ; faire confirmer cette mention avant utilisation.',
  104:'Le titre du livret indique « sérum salé hypertonique 3 % » ; la préparation détaillée indique une poche de 110 mL de NaCl à 2,6 %. Les deux mentions sont conservées telles qu’elles figurent dans la source.'
 }
 if p in warnings:f['warnings'].append(warnings[p])
 f['medicine']=re.split(r'\s+[–-]\s+',f['title'])[0]
 f['category']='medicament'
 f['review']={'status':'transcription_technique_revue','clinical_validation':False,'pages':f['pages']}
