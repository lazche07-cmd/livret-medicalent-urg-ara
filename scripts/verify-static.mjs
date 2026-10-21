import { readFileSync, existsSync, statSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..'),dist=resolve(root,'dist');
const html=readFileSync(resolve(dist,'index.html'),'utf8');
assert(html.includes('<title>Livret médicament Urg ara — Urgentistes et Médecins correspondants SAMU (MCS)</title>'));
assert(/id="source-open"[^>]*target="_blank"/.test(html));
for(const [,raw] of html.matchAll(/(?:src|href)="([^"#]+)"/g)){
 if(/^(?:https?:|mailto:|data:)/.test(raw))continue;
 const path=raw.split(/[?#]/)[0];if(path)assert(existsSync(resolve(dist,path)),`Fichier absent : ${path}`);
}
for(const file of ['livret-source.pdf','livret-adulte.pdf','livret-pediatrique.pdf']){
 const path=resolve(dist,file),data=readFileSync(path);assert(data.subarray(0,5).toString()==='%PDF-');assert(statSync(path).size>1000);
}
const context=vm.createContext({window:{}});
for(const file of ['checklists.js','guides.js','document.js'])vm.runInContext(readFileSync(resolve(dist,file),'utf8'),context);
const {CHECKLISTS:meds,GUIDES:guides,DOCUMENT:document}=context.window;
assert.equal(meds.length,73);assert.equal(guides.length,8);assert.equal(document.page_count,106);
for(const f of [...meds,...guides])for(const n of f.pages)assert(existsSync(resolve(dist,`assets/page-${n}.jpg`)));
console.log('Build statique vérifié : 73 checklists, 8 repères, 106 pages sources et trois PDF.');
