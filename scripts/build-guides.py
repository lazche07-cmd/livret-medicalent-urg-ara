import fitz,json,re
from pathlib import Path
R=Path(__file__).resolve().parent.parent;D=R/'dist';doc=fitz.open(D/'livret-source.pdf')
KEYS=['presentation','indication','contra','preparation','combined','dose','surveillance','effects','notes']
def text(s):return re.sub(r'\s+',' ',s).strip()
def guide(page,title,context):return {'page':page,'pages':[page],'title':title,'medicine':title,'population':'reperes','category':'guide','context':context,'text':doc[page-1].get_text(),'sections':{k:[] for k in KEYS},'tables':[],'warnings':[],'sectionConfig':{},'review':{'status':'transcription_technique_revue','clinical_validation':False,'pages':[page]}}
def add(f,key,lines,**extra):
 for line in lines:f['sections'][key].append({'text':line,'page':f['page'],**extra})
def cfg(f,key,title,hint='',action='Repère relu / vérifié'):f['sectionConfig'][key]={'title':title,'hint':hint,'action':action}
a=[]
f=guide(13,'Sécuriser l’administration · 5B et 10B','Recommandations HAS');a.append(f)
cfg(f,'presentation','Les 5B','Les étapes à sécuriser et à retenir, selon le livret.','Vérification effectuée')
add(f,'presentation',['BON PATIENT','BON MÉDICAMENT injectable et soluté de perfusion','BONNE DOSE','BONNE VOIE','BON MOMENT'])
cfg(f,'preparation','Les 10B · compléments pour la perfusion','Les cinq vérifications complémentaires s’ajoutent aux 5B.','Vérification effectuée')
add(f,'preparation',['BON CALCUL de dilution pour la bonne concentration, le respect des protocoles de dilution du service','BONNE MANIÈRE avec le choix du solvant de dilution, la préparation qui doit rester stérile, le respect du système clos, sans bulles (sans embolie gazeuse), sans particules, sans précipité, sans trouble, sans changement de couleur…','BON DÉBIT avec le réglage et maintien du débit et la bonne programmation de la pompe ou du PSE','BON MONTAGE (sécurisé, optimisé) des dispositifs médicaux utilisés, prévention des bolus de médicaments, minimisation des volumes résiduels et du volume du tronc commun','BONNE COMPATIBILITÉ entre les produits perfusés, prévention des incompatibilités physico chimiques et des interactions'])
cfg(f,'surveillance','En cas d’évènement indésirable grave',action='Action effectuée si la situation est présente')
add(f,'surveillance',['En cas de survenue d’un évènement indésirable grave : prévenir le médecin et déclarer l’évènement'])
add(f,'notes',['Le livret répond aux recommandations de l’HAS et ses préconisations sur la sécurité d’administration des médicaments'],info=True)
f=guide(14,'Glossaire · pictogrammes et diluants','18 pictogrammes et mentions générales');a.append(f)
cfg(f,'presentation','Signification des pictogrammes','Pictogrammes extraits de la page originale.','Signification relue')
t=doc[13].find_tables().tables[0]
for i,row in enumerate(t.extract()):
 label=text(row[1]);filename=f'assets/glossaire-{i}.png';doc[13].get_pixmap(matrix=fitz.Matrix(2,2),clip=fitz.Rect(t.rows[i].cells[0])).save(str(D/filename));add(f,'presentation',[label],image=filename)
cfg(f,'preparation','Mentions générales de dilution et conservation','Appliquer les spécificités de chaque fiche.','Mention relue / vérifiée')
add(f,'preparation',['Toute dilution non spécifiquement désignée s’effectue avec du NaCl 0,9 %','Le G5 % est utilisé préférentiellement pour les amines (meilleure stabilité du médicament)','Le NaCl 0,9 % peut également être utilisé pour les amines','La conservation au froid concerne essentiellement les curares'])
f=guide(15,'Étiquetage · classes, couleurs et trames','Codes de la légende du livret');a.append(f)
cfg(f,'presentation','Classe pharmacologique et étiquette','Les couleurs et trames affichées sont des extraits de la source, associés aux substances citées.','Classe / étiquette relue')
t=doc[14].find_tables().tables[0]
for i,row in enumerate(t.extract()[1:],1):
 filename=f'assets/etiquette-{i}.png';doc[14].get_pixmap(matrix=fitz.Matrix(2,2),clip=fitz.Rect(t.rows[i].cells[0])).save(str(D/filename));add(f,'presentation',[text(row[0])+' : '+text(row[1])],image=filename)
add(f,'notes',['Le système d’étiquetage s’appuie sur les codes internationaux de couleurs et de trames correspondant aux différentes classes pharmacologiques recommandées par la SFAR. Ce code permet une meilleure identification des drogues et assure la sécurité du patient.','Recommandation ANSM : « Harmonisation de l’étiquetage des ampoules et autres petits conditionnements de solutions injectables de médicaments ». Code couleur à appliquer selon la classe pharmacologique de la spécialité.'],info=True)
f=guide(16,'Lire une fiche · voies et limites du livret','Préparation, administration, grossesse et interactions');a.append(f)
cfg(f,'preparation','Préparation et modes d’administration',action='Repère relu')
add(f,'preparation',['Pour chaque médicament, le mode de préparation est détaillé dans la fiche : PURE, À DILUER, À RECONSTITUER','Pour la préparation d’une seringue : prélever les ampoules du médicament puis compléter jusqu’à un volume défini dans la fiche','IVD : Intra Veineuse Directe','IVDL : Intra Veineuse Directe Lente (en seringue, temps précisé dans la fiche)','IVL : Intra Veineuse Lente (en poche). Temps précisé dans la fiche','IVSE : Intra Veineuse par Seringue Électrique','PSE : administration au Pousse Seringue Électrique'])
cfg(f,'surveillance','Informations à compléter auprès des références','Limites explicitement décrites dans le livret.','Limite relue / référence vérifiée si nécessaire')
add(f,'surveillance',['GROSSESSE ET ALLAITEMENT : Les données ne sont pas toujours mentionnées. Se référer à la monographie du médicament et au Centre de Référence sur les Agents Tératogènes (CRAT)','INTERACTION PHYSICO-CHIMIQUE : Les IPC (Interactions Physiques Chimiques) ne sont pas mentionnées dans ce document : se référer à la monographie du médicament'])
add(f,'notes',['Toutes les fiches ont été construites selon la même trame : DCI – NOM COMMERCIAL®, présentation(s), concentration, classe pharmaceutique, spécificité du médicament et indication du médicament.','PLUSIEURS INDICATIONS : UNE FICHE PAR INDICATION. Signifie qu’une fiche correspond à une seule indication médicale ; un médicament peut avoir jusqu’à 6 fiches.','INDICATIONS : Principales indications en situation d’urgence. Selon les indications, un médicament peut avoir plusieurs fiches spécifiées : tourner les pages !','CONTRE-INDICATIONS : Les principales contre-indications sont mentionnées. La liste n’est pas exhaustive et concerne essentiellement la médecine d’urgence.','INSTALLATION ET SURVEILLANCE : Préparation du patient avant l’administration du médicament. Surveillance particulière par rapport au médicament ou la pathologie en cause.','POSOLOGIE : Posologie selon les recommandations des référentiels Urg’Ara, ou des dernières recommandations des sociétés savantes.','EFFETS SECONDAIRES : La liste des effets secondaires n’est pas exhaustive mais concerne essentiellement le domaine de l’urgence. Pour plus d’informations, se référer à la monographie du médicament.'],info=True)
f=guide(17,'Abréviations · lexique du livret','Abréviations et développements de la page 17');a.append(f)
cfg(f,'presentation','Abréviations','Développements conservés tels qu’ils figurent dans le livret.','Abréviation consultée')
t=doc[16].find_tables().tables[0];pairs={}
for row in t.extract():
 for i in range(0,len(row),2):
  if row[i] and row[i+1]:pairs.setdefault(text(row[i]),text(row[i+1]))
for k,v in sorted(pairs.items()):add(f,'presentation',[k+' : '+v])
f=guide(18,'PSE MICREL MP mlh+ · utilisation et alarmes','Mode d’emploi simplifié du dispositif illustré');a.append(f)
cfg(f,'presentation','Volume et installation','Se reporter au manuel du dispositif pour plus d’informations.','Installation / volume vérifié')
add(f,'presentation',['La seringue de 50 mL ne peut être installée sur le PSE qu’avec un volume de 40 mL dans la seringue. Ajuster le volume final de la seringue à 40 mL.'])
cfg(f,'preparation','Programmation du pousse-seringue','Transcription du mode d’emploi illustré p. 18. La touche de validation est celle représentée dans le schéma original.','Étape effectuée / vérifiée')
add(f,'preparation',['Mise en marche : maintenir les touches ↑ et ↓ appuyées 3 secondes.','Appuyer sur la flèche ↑ pour régler la marque de la seringue.','Appuyer sur la flèche ↑ pour régler le volume de la seringue.','Programmation du débit.','Démarrage de la perfusion : maintenir la touche de validation représentée sur le schéma appuyée jusqu’à l’apparition du symbole CAL.','Arrêt de la perfusion et extinction de l’appareil (OFF) : maintenir les touches ↑ et ↓ appuyées 3 secondes.','Pour changer le débit en cours de perfusion, programmer le nouveau débit et valider dans les trois secondes. Appuyer sur la touche de validation représentée sur le schéma jusqu’à l’apparition du message CAL.'])
cfg(f,'effects','Signaux d’avertissement et alarmes','Cocher uniquement un signal effectivement observé. Les consignes sont celles de la notice reproduite dans le livret.','Signal / alarme observé')
add(f,'effects',['Pompe en attente : affichage clignotant, démarrer la perfusion.','Piles faibles.','Fin prochaine de la perfusion.','En cas d’alarme, la perfusion est arrêtée. Éteindre le pousse-seringue pour annuler l’alarme.','Occlusion ou fin de perfusion.','Piles déchargées : éteindre le pousse-seringue et changer les piles.','Alarmes techniques : noter le code de l’alarme, éteindre et remettre en marche l’appareil ; si l’alarme persiste, ne plus utiliser l’appareil.','Déplacement de seringue : s’assurer que les ailettes du tube de la seringue sont bien en place dans les encoches, que le bout arrondi du piston est dans la fente du poussoir et que la lanière autour du tube de la seringue est bien serrée.','Aucune marque et/ou volume de seringue n’a été sélectionné.'])
add(f,'notes',['La notice simplifiée est une image dans le PDF : ses libellés ont été transcrits à partir de la page rendue et relus visuellement. Les symboles exacts des touches et des alarmes restent consultables dans l’annexe. Se reporter au manuel d’utilisation pour plus d’informations.'],info=True)
f=guide(19,'Voie intranasale · préparation et surveillance','Dispositif MAD, volumes, contre-indications');a.append(f)
add(f,'indication',['Analgésie sédation en absence de VVP'])
cfg(f,'presentation','Dispositif et installation',action='Matériel / installation vérifié')
add(f,'presentation',['Dispositif spécifique : embout dispositif MAD® nasal + seringue luer lock 1 mL','Installation du patient : désobstruction nasale si besoin ; en semi-assis à 45° ou en position couchée'])
add(f,'preparation',['Médicament : utilisation PURE. VIGILANCE sur la concentration du médicament et l’ampoule à utiliser. Utiliser les formes les plus concentrées.','Avec la seringue de 1 mL, prélever dans l’ampoule PURE le volume à administrer du tableau des posologies des fiches médicaments. Le volume à administrer de la 1re dose du tableau correspond au volume de la dose prescrite auquel est ajouté 0,1 mL pour purger l’embout nasal (0,1 mL non administré et qui reste dans l’espace mort de l’embout nasal).','Le volume de l’espace mort peut varier selon le type de dispositif MAD (de 0,06 à 0,15 mL) : choix du réseau d’un arrondi à 0,1 mL pour tous les dispositifs.','Prélever le 2e volume avec la même seringue et le même embout nasal. Le volume de la 2e dose correspond au volume de la dose prescrite sans le volume de la purge de l’embout puisqu’il a déjà été purgé.','En résumé, il faut prélever et administrer les volumes indiqués dans les tableaux des fiches (tous les calculs sont déjà faits).','Double contrôle du dosage par 2 soignants.'])
cfg(f,'dose','Administration et volumes',action='Modalité d’administration vérifiée')
add(f,'dose',['Connecter l’embout nasal (MAD®) puis insérer l’embout dans la narine en direction du septum et presser le piston en 1 à 2 secondes.','Volume maximal par narine : 1 mL (la dose peut être divisée entre les 2 narines). Préférer 0,5 mL par narine pour une meilleure absorption.'])
add(f,'surveillance',['Score de sédation','FR, SpO2, PA, FC, efficacité','Scope selon la molécule et la situation clinique','ANTIDOTE et matériel de réanimation disponible'])
add(f,'contra',['Allergie au médicament utilisé','Traumatisme cranio facial','Altération de la conscience','Détresse respiratoire, instabilité hémodynamique','Traumatisme nasal, épistaxis, obstruction nasale complète'])
add(f,'effects',['Inconfort à l’instillation','Secondaires au médicament : sédation profonde, détresse respiratoire, nausées, vomissements'])
f=guide(20,'Surveillance · Glasgow et Ramsay','Sélection des critères observés · sans interprétation automatique');a.append(f)
cfg(f,'surveillance','Glasgow · critères observés','Sélectionner une réponse par domaine Y, V et M. Les valeurs sont celles du livret. Aucun diagnostic ni calcul de dose n’est déduit.','Critère observé')
groups=[('glasgow-y','Y · Ouverture des yeux',[('Spontanée',4),('À la demande',3),('À la douleur',2),('Aucune',1)]),('glasgow-v','V · Réponse verbale',[('Orientée',5),('Confuse',4),('Incohérente',3),('Incompréhensible',2),('Aucune',1)]),('glasgow-m','M · Réponse motrice',[('Obéit à la demande verbale',6),('Orientée à la douleur',5),('Évitement non adapté',4),('Décortication (flexion à la douleur)',3),('Décérébration (extension à la douleur)',2),('Aucune',1)])]
for group,title,rows in groups:
 for label,value in rows:add(f,'surveillance',[title+' : '+label+' — '+str(value)],group=group,groupLabel=title,value=value)
cfg(f,'presentation','Ramsay · niveau observé','Sélectionner un seul niveau observé. Les repères d’interprétation du livret figurent dans les précisions.','Niveau observé')
for value,label in enumerate(['Patient anxieux, agité','Patient coopérant, orienté, calme','Patient répondant seulement aux ordres','Patient endormi mais avec une réponse nette à la stimulation de la glabelle ou à un bruit intense','Patient endormi avec une faible réponse aux stimulations nociceptives','Aucune réponse aux stimulations nociceptives'],1):add(f,'presentation',['Ramsay '+str(value)+' : '+label],group='ramsay',groupLabel='Ramsay',value=value)
add(f,'notes',['L’échelle ou score de Glasgow est une méthode utilisée pour évaluer l’état de conscience du patient et son évolution. Le résultat à lui seul ne permet d’apprécier la profondeur du coma. Il convient d’étudier la variabilité des 3 critères cliniques (Y + V + M), déterminant un score compris entre 15 et 3.','La méthode de stimulation nociceptive recommandée est la pression appuyée au niveau sus-orbitaire ou la pression du lit unguéal avec un stylo. Le frottement ou le pincement de la peau doivent être évités.','Le score de Ramsay est une échelle simplifiée évaluant la profondeur de sédation chez un patient, en réponse à un stimuli. À l’aide de différents indicateurs, il déterminera l’adaptation des posologies aux besoins du patient, par une évaluation régulière de la surveillance neurologique.','Le niveau s’interprète par : un score à 2-3 : sédation optimale légère ; un score à 4-5 : sédation profonde ; un score à 6 : surdosage du sédatif.'],info=True)
for f in a:
 if f['page']==20:f['sectionOrder']=['surveillance','presentation','notes']
 for key,items in f['sections'].items():
  for i,it in enumerate(items):it['id']=f"{f['page']}-{key}-{i}"
(D/'guides.js').write_text('window.GUIDES='+json.dumps(a,ensure_ascii=False)+';',encoding='utf8')
meds=json.loads((D/'checklists.js').read_text()[18:-1]);pages=[]
for n in range(1,len(doc)+1):
 med=next((f for f in meds if n in f['pages']),None);g=next((f for f in a if n in f['pages']),None)
 if med:kind='medicament';title=med['title'];target=med['page']
 elif g:kind='guide';title=g['title'];target=g['page']
 else:
  kind='reference';target=None
  title={1:'Couverture',2:'Page blanche',3:'Préface · conditions d’usage',4:'Rédaction et validation du livret',5:'Sommaire',6:'Sommaire adulte',7:'Sommaire adulte',8:'Sommaire adulte',9:'Sommaire adulte',10:'Sommaire adulte',11:'Sommaire pédiatrique',12:'Sommaire pédiatrique',21:'Intercalaire adulte',65:'Intercalaire pédiatrique',105:'Page blanche',106:'Contacts et références'}.get(n,'Référence du document')
 pages.append({'page':n,'title':title,'kind':kind,'target':target})
meta={'page_count':len(doc),'medicine_count':len({f['medicine'] for f in meds}),'checklist_count':len(meds),'adult_count':sum(f['population']=='adulte' for f in meds),'pediatric_count':sum(f['population']=='pediatrie' for f in meds),'guide_count':len(a),'table_count':sum(len(f['tables']) for f in meds),'pages':pages,'source':'Livret du médicament du MCS · Urg’Ara V2.0 · juillet 2026','clinical_validation':False}
(D/'document.js').write_text('window.DOCUMENT='+json.dumps(meta,ensure_ascii=False)+';',encoding='utf8')
(R/'scripts/document-coverage.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf8')
print('Repères',len(a),'Pages',len(pages),'Médicaments',meta['medicine_count'])
