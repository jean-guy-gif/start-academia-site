# Site Start Academia

Site vitrine de Start Academia (anciennement Start Academy), organisme de formation immobilier et IA certifié Qualiopi.
Objectif unique de conversion : réserver un appel découverte.

- Production : https://start-academia.vercel.app (domaine final prévu : https://www.start-academia.fr)
- Hébergement : Vercel, projet `start-academia`
- Technique : HTML, CSS et JavaScript simples, sans framework. Les pages sont générées par les scripts Python de `outils/` (bibliothèque standard uniquement) et commitées : Vercel ne fait aucun build

## Arborescence

| Chemin | Rôle |
|---|---|
| `index.html` | Accueil (vidéo défilante, paperboard, A en 3D, outils, résultats, FAQ) |
| `formations/` | Catalogue des formations (généré depuis QualiOF, voir plus bas) |
| `formation-ia-immobilier/`, `formation-chatgpt-immobilier/`, `formation-ia-nice/` | Pages SEO (générées) |
| `financement-formation-immobilier/` | Page financement + simulateur AGEFICE / OPCO EP (générée) |
| `formation-loi-alur/`, `coaching-pour-directeur-dagence-immobiliere-dans-le-06/`, `mentions-legales/`, `404.html` | Pages secondaires (générées) |
| `styles.css` | Feuille de style unique (charte : #2F44CE, #6988EE, #B9CDFF, #FE5500) |
| `voyage.js` | Vidéo du bateau pilotée par le défilement (choix 1080 carré / 1920 / 2560 selon l'écran) |
| `simulateur.js` | Simulateur de financement. **Barèmes, taux et années dans `CONFIG` en tête de fichier**, à mettre à jour chaque année (rien n'est reconduit automatiquement) |
| `paperboard.js`, `logo3d.js`, `logo3d-geo.js`, `logo.js`, `fin.js`, `demo.js`, `mur.js` | Animations de l'accueil (`mur.js` : défilement du mur de logos) |
| `img/`, `documents/` | Images, vidéos, PDF (CGV, règlement intérieur, charte handicap, certificat Qualiopi valable jusqu'au 23/07/2029) |
| `vercel.json` | Redirections 301 de l'ancien site WordPress, redirection des autres domaines vers www.start-academia.fr, `noindex` sur *.vercel.app |
| `outils/` | Générateurs Python des pages (non déployés, voir `.vercelignore`) |
| `data/qualiof.json` | Catalogue et indicateurs récupérés de QualiOF (écrit par `outils/sync_qualiof.py`, non déployé) |
| `data/qualiof.exemple.json` | Fixture pour tester la synchro hors ligne |
| `.github/workflows/sync-qualiof.yml` | Synchro automatique avec QualiOF |

## Régénérer les pages

Depuis la racine du dépôt (ou de n'importe où) :

```bash
python3 outils/build.py
```

Le script enchaîne `pages.py` (sous-pages, en-tête et pied repris de `index.html`), `formations.py` (catalogue), `seo_pages.py`, `jsonld_pages.py` (données structurées) et `chiffres.py` (chiffres de l'accueil). Les chemins sont relatifs au dépôt. Relancer après toute modification de l'en-tête, du pied de page ou du contenu des pages.

## Synchronisation avec QualiOF

Le catalogue `/formations/` et les chiffres de l'accueil (apprenants formés, taux de recommandation) viennent de l'API publique de QualiOF, notre outil Qualiopi : `https://qualiof.vercel.app/api/public/v1/programmes` et `/indicateurs`.

**Déclencheurs** (workflow `.github/workflows/sync-qualiof.yml`) :

- QualiOF prévient le site après une modification (`repository_dispatch`, type `qualiof-sync`) ;
- chaque nuit à 3 h 40 UTC, en filet ;
- à la main : onglet Actions → sync-qualiof → Run workflow.

Le workflow lance `python3 outils/sync_qualiof.py` puis `python3 outils/build.py`, et commite sur `main` seulement si une page a changé. Vercel déploie ce commit tout seul.

**Ce qui est affiché** : seuls les programmes QualiOF qui ont au moins un apprenant formé, avec une ligne d'indicateurs (apprenants formés, note sur 5, taux de recommandation). Les tarifs restent « Sur devis » même si QualiOF a un prix, et le bloc « Valable pour toutes les formations » ne vient pas de QualiOF. Les catégories et les ancres des anciennes fiches se règlent dans `outils/qualiof_mapping.py`. Les avis Google ne viennent pas de l'API et ne bougent pas.

**Coordonnées** : `sync_qualiof.py` retire toute ligne contenant un téléphone ou un e-mail avant d'écrire `data/qualiof.json`, et le signale dans le journal. Corriger le texte dans QualiOF.

**Repli** : si l'API est injoignable ou répond mal, `data/qualiof.json` est conservé tel quel et le site ne change pas (le script sort quand même en succès). Sans `data/qualiof.json`, le catalogue reprend la liste intégrée à `outils/formations.py` et `index.html` garde ses chiffres.

**Tester hors ligne** :

```bash
python3 outils/sync_qualiof.py --fixture data/qualiof.exemple.json && python3 outils/build.py
```

Variable d'environnement `QUALIOF_API_BASE` pour viser une autre instance de QualiOF (défaut `https://qualiof.vercel.app`).

**Le site n'a pas changé après une modification dans QualiOF ?** Onglet Actions → sync-qualiof : vérifier que le run a eu lieu, lire l'avertissement « sync-qualiof » s'il y en a un (API injoignable, réponse invalide), et regarder si l'étape de commit dit « Aucun changement » (programme sans apprenant formé, par exemple). Puis vérifier le déploiement dans Vercel.

**Réglages à faire une fois** :

- GitHub : Settings → Actions → General → Workflow permissions → « Read and write permissions », sinon le workflow ne peut pas pousser.
- QualiOF : un token GitHub à accès fin, limité au dépôt `jean-guy-gif/start-academia-site`, permission Contents en lecture et écriture. QualiOF l'utilise pour appeler :

```bash
curl -X POST https://api.github.com/repos/jean-guy-gif/start-academia-site/dispatches \
  -H "Authorization: Bearer $GITHUB_TOKEN" -H "Accept: application/vnd.github+json" \
  -d '{"event_type":"qualiof-sync","client_payload":{"raison":"programme PROD-0042 modifié"}}'
```

## Déployer

Depuis la racine du dépôt :

```bash
npx vercel --prod
```

## Points d'attention

- Tarifs : sur devis uniquement. Formations non éligibles au CPF à ce jour.
- Réglementation : loi Hoguet, RGPD, mentions DPE à respecter dans tout contenu.
- Les 17 objectifs marqués `data-a-valider` ne concernent que le catalogue de repli (liste intégrée à `outils/formations.py`), pas les fiches venues de QualiOF.
