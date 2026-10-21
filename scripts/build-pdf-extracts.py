"""Build faithful adult/paediatric extracts with shared introductory pages."""
import fitz,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent.parent;D=R/'dist';src=fitz.open(D/'livret-source.pdf');report={}
for name,indices in [('adulte',list(range(64))),('pediatrique',list(range(20))+list(range(64,104)))]:
 target=D/f'livret-{name}.pdf';out=fitz.open(D/'livret-source.pdf');out.select(indices);mapping={n:i for i,n in enumerate(indices)}
 # Rebuild internal links using original page numbers, retaining only valid destinations.
 for i,n in enumerate(indices):
  page=out[i]
  for link in page.get_links():page.delete_link(link)
  for link in src[n].get_links():
   if link['kind']==fitz.LINK_GOTO and link['page'] in mapping:
    page.insert_link({'kind':fitz.LINK_GOTO,'from':link['from'],'page':mapping[link['page']],'to':link.get('to',fitz.Point(0,0))})
   elif link['kind']==fitz.LINK_URI:
    page.insert_link({'kind':fitz.LINK_URI,'from':link['from'],'uri':link['uri']})
 out.set_toc([]);meta=src.metadata.copy();meta['title']='Livret médicament Urg ara — '+('Adulte' if name=='adulte' else 'Pédiatrique')+' (extrait)';meta['subject']='Extrait du livret MCS Urg’Ara V2.0, juillet 2026. Pages communes 1–20 et partie '+name+'.';out.set_metadata(meta);out.save(target,garbage=4,deflate=True);out.close()
 check=fitz.open(target)
 assert len(check)==len(indices)
 for i,n in enumerate(indices):
  assert check[i].get_text()==src[n].get_text(),(name,i,n,'text changed')
  # Compare original decoded drawing instructions and embedded images without
  # relying on renderer caches or antialiasing at a particular zoom level.
  streams=lambda doc,page:[hashlib.sha256(doc.xref_stream(x)).hexdigest() for x in page.get_contents()]
  images=lambda doc,page:sorted(hashlib.sha256(doc.xref_stream(x[0])).hexdigest() for x in page.get_images(full=True))
  assert streams(check,check[i])==streams(src,src[n]),(name,i,n,'drawing changed')
  assert images(check,check[i])==images(src,src[n]),(name,i,n,'image changed')
  for link in check[i].get_links():
   if link['kind']==fitz.LINK_GOTO:assert 0<=link['page']<len(check)
 report[name]={'file':target.name,'pages':len(check),'source_pages':[n+1 for n in indices],'text_matches':True,'drawing_streams_match':True,'images_match':True,'internal_links_in_bounds':True}
(R/'scripts/pdf-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:{x:y for x,y in v.items() if x!='source_pages'} for k,v in report.items()},ensure_ascii=False,indent=2))
