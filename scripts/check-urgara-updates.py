"""Read-only publication check. Never modifies clinical content or production assets."""
import argparse,hashlib,json,urllib.request,urllib.parse
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  if tag=='a':
   href=dict(attrs).get('href','')
   if '.pdf' in href.lower():self.links.append(href)
def fetch(url):
 req=urllib.request.Request(url,headers={'User-Agent':'LivretUrgAra-publication-watch/1.0 (personal clinical reference watch)'})
 with urllib.request.urlopen(req,timeout=45) as response:
  data=response.read(35*1024*1024)
  if response.read(1):raise ValueError('Document exceeds 35 MiB')
  return data,response.geturl(),response.headers.get('Content-Type','')
def check(config,fetcher=fetch):
 reports=[]
 for source in config['official_sources']:
  try:
   data,url,kind=fetcher(source['url'])
   if source['kind']=='index':
    parser=Links();parser.feed(data.decode('utf-8',errors='replace'))
    links=sorted({urllib.parse.urljoin(url,x) for x in parser.links})
    links=[x for x in links if urllib.parse.urlparse(x).hostname in ('www.urgences-ara.fr','urgences-ara.fr')]
    reports.append({'id':source['id'],'url':url,'pdf_links':links})
   else:
    if not data.startswith(b'%PDF-'):raise ValueError('Response is not a PDF')
    sha=hashlib.sha256(data).hexdigest();prior=source.get('sha256')
    reports.append({'id':source['id'],'series':source['series'],'url':url,'sha256':sha,'bytes':len(data),'status':'unchanged' if prior==sha else 'changed' if prior else 'first_check'})
  except Exception as exc:reports.append({'id':source['id'],'status':'error','error':str(exc)})
 return {'clinical_content_modified':False,'reports':reports,'review_note':'Compare each series separately. A changed hash can reflect layout only. Validate clinical differences before updating the application.'}
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);args=parser.parse_args()
 result=check(json.loads((ROOT/'veille/sources.json').read_text()))
 output=json.dumps(result,ensure_ascii=False,indent=2)
 if args.output:
  destination=args.output.resolve()
  if destination.is_relative_to((ROOT/'dist').resolve()):raise SystemExit('Refusing to write into production dist')
  destination.parent.mkdir(parents=True,exist_ok=True);destination.write_text(output)
 else:print(output)
 if any(r.get('status')=='error' for r in result['reports']):raise SystemExit(1)
