# Site Start Academia

Site vitrine de Start Academia (anciennement Start Academy), organisme de formation immobilier et IA certifié Qualiopi.
Objectif unique de conversion : réserver un appel découverte.

- Production : https://start-academia.vercel.app (domaine final prévu : https://www.start-academia.fr)
- Hébergement : Vercel, projet `start-academia`
- Technique : HTML, CSS et JavaScript simples, sans framework ni étape de build

## Arborescence

| Chemin | Rôle |
|---|---|
| `index.html` | Accueil (vidéo défilante, paperboard, A en 3D, outils, résultats, FAQ) |
| `formations/` | Catalogue des formations (généré) |
| `formation-ia-immobilier/`, `formation-chatgpt-immobilier/`, `formation-ia-nice/` | Pages SEO (générées) |
| `financement-formation-immobilier/` | Page financement + simulateur AGEFICE / OPCO EP (générée) |
| `formation-loi-alur/`, `coaching-pour-directeur-dagence-immobiliere-dans-le-06/`, `mentions-legales/`, `404.html` | Pages secondaires (générées) |
| `styles.css` | Feuille de style unique (charte : #2F44CE, #6988EE, #B9CDFF, #FE5500) |
| `voyage.js` | Vidéo du bateau pilotée par le défilement (choix 1080 carré / 1920 / 2560 selon l'écran) |
| `simulateur.js` | Simulateur de financement. **Barèmes, taux et années dans `CONFIG` en tête de fichier**, à mettre à jour chaque année (rien n'est reconduit automatiquement) |
| `paperboard.js`, `logo3d.js`, `logo3d-geo.js`, `logo.js`, `fin.js`, `demo.js` | Animations de l'accueil |
| `img/`, `documents/` | Images, vidéos, PDF (CGV, règlement intérieur, charte handicap, certificat Qualiopi valable jusqu'au 23/07/2029) |
| `vercel.json` | Redirections 301 de l'ancien site WordPress, redirection des autres domaines vers www.start-academia.fr, `noindex` sur *.vercel.app |
| `outils/` | Générateurs Python des pages (non déployés, voir `.vercelignore`) |

## Régénérer les pages

L'en-tête et le pied de page sont repris de `index.html`. Après une modification de ceux-ci ou du contenu des pages, lancer dans cet ordre :

```bash
python3 outils/pages.py && python3 outils/formations.py && python3 outils/seo_pages.py && python3 outils/jsonld_pages.py
```

Les scripts utilisent encore des chemins absolus (`/home/claude/site3`, `/home/claude/outils`) : les adapter au dossier du dépôt avant de les lancer ailleurs.

## Déployer

Depuis la racine du dépôt :

```bash
npx vercel --prod
```

## Points d'attention

- Tarifs : sur devis uniquement. Formations non éligibles au CPF à ce jour.
- Réglementation : loi Hoguet, RGPD, mentions DPE à respecter dans tout contenu.
- Les 17 objectifs de formation marqués `data-a-valider` dans le catalogue restent à valider par les formateurs.
