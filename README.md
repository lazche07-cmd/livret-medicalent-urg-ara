# Livret médicament Urg ara

Application statique interactive issue du livret MCS Urg’Ara V2.0 de juillet 2026 fourni par l’utilisateur : 31 médicaments, 73 checklists (42 adultes et 31 pédiatriques), huit repères généraux et 106 pages sources. Les deux PDF adulte et pédiatrique de l’application sont des **extraits du livret MCS**, avec les pages générales communes. Ils ne sont pas les livrets généraux Urg’Ara.

## Déployer sur Vercel

Importer ce dépôt depuis le compte Vercel autorisé à le lire. La configuration est dans `vercel.json` :

- Framework : Other.
- Répertoire racine : racine du dépôt.
- Installation : `npm ci --ignore-scripts`.
- Build : `npm run build`.
- Répertoire publié : `dist`.
- Aucune variable d’environnement nécessaire.

Les fichiers PDF sont servis avec le type `application/pdf` et une disposition `inline`. Les liens natifs ouvrent un nouvel onglet à la page correspondante. L’aperçu des pages est un contrôle séparé.

Vercel publie généralement une adresse accessible sur Internet. Vérifier le public visé et les conditions de reproduction du livret avant de diffuser cette adresse ; la copie source demeure protégée par les droits d’Urg’Ara. Le dépôt est destiné à rester privé.

## Vérifier et ouvrir en local

Node 22 ou supérieur suffit pour les contrôles statiques :

```sh
npm ci --ignore-scripts
npm run build
npm test
```

Ouvrir ensuite `dist/index.html` dans un navigateur, ou servir `dist` avec un serveur HTTP local. Il n’y a aucun serveur applicatif ni base de données. Les coches restent dans l’onglet ouvert ; les favoris sont locaux au navigateur. Aucune donnée patient n’est enregistrée.

Les scripts d’extraction et de relecture Python nécessitent PyMuPDF. Ils ne doivent pas être réutilisés automatiquement sur un livret d’une autre série ou d’une autre pagination. La relecture identifie explicitement les ambiguïtés du document sans remplacer automatiquement une dose ou une unité.

## Veille des publications

Une veille quotidienne « Veille livrets Urg’Ara » a été activée dans ChatGPT dans la conversation de création de l’application. Elle est indépendante de Vercel et reste administrée dans ChatGPT ; le dépôt ne crée pas une seconde tâche planifiée.

Elle surveille les éditions adulte générale, pédiatrique générale et MCS séparément. Une publication détectée donne lieu à une proposition d’actualisation et à une comparaison, avec validation médicale avant modification des données cliniques en production. `veille/sources.json` documente les sources connues et les empreintes des PDF de l’application. `scripts/check-urgara-updates.py` permet un contrôle ponctuel des liens et empreintes officiels ; il n’écrit jamais dans `dist`.

## Limites et droits

Prototype indépendant, sans affiliation officielle avec Urg’Ara ou le SMUR de Marseille. Les contrôles techniques et la relecture de transcription ne constituent pas une validation clinique. Les listes de contre-indications et d’effets secondaires sont celles du livret et ne sont pas exhaustives. La version officielle à jour prévaut.

Les contenus médicaux et PDF restent © Urg’Ara ; aucune licence open source n’est accordée sur ces contenus. Usage personnel selon la préface du PDF. Les pages source et leurs mentions sont conservées.
