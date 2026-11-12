"""Génère /resultats/ : la page « Les résultats de nos clients ».

Principe : chaque preuve porte son type et sa source. Rien d'inventé : les histoires
reprennent celles de l'accueil, les citations sont des avis Google publics (prénom + initiale),
les comptages d'avis ont été relevés sur la fiche Google le 11 novembre 2026.
Les vidéos et études de cas s'ajouteront ici quand elles existeront (protocole de mesure)."""
import pathlib, re, html as h

racine = pathlib.Path(__file__).resolve().parent.parent
idx = (racine / 'index.html').read_text()
symboles = re.search(r'<svg width="0".*?</svg>', idx, re.S).group(0)
entete = re.search(r'<header class="entete">.*?</header>', idx, re.S).group(0).replace('href="#', 'href="/#')
pied = re.search(r'<footer class="pied">.*?</footer>', idx, re.S).group(0).replace('href="#', 'href="/#')
fonts = re.search(r'<link rel="preconnect" href="https://fonts.googleapis.com">.*?display=swap">', idx, re.S).group(0)
mur = re.search(r'<ul class="mur">.*?</ul>', idx, re.S).group(0)
CAL = 'https://meet.brevo.com/jean-guy-ourmieres/appel-decouverte'
FICHE = 'https://www.google.com/maps?cid=14911917268621468356'
fl = '<svg aria-hidden="true"><use href="#fleche"/></svg>'

ETAPES = [('prospection', 'Prospection'), ('decouverte', 'Découverte'), ('estimation', 'Estimation'),
          ('mandat', 'Mandat'), ('acquereurs', 'Acquéreurs'), ('organisation', 'Organisation'),
          ('ia', 'IA au quotidien'), ('direction', 'Direction d\'agence')]
PROFILS = [('conseiller', 'Conseiller ou mandataire'), ('direction', 'Directeur ou manager'), ('equipe', 'Équipe d\'agence')]

# (étapes, profils, type de preuve, chiffre ou titre, phrase, qui)
HISTOIRES = [
    (['estimation', 'mandat'], ['conseiller'], 'apprenant', '2 exclusivités',
     "Brian a repris 2 exclusivités dans la semaine qui a suivi la formation.", 'Brian, conseiller immobilier'),
    (['mandat'], ['conseiller'], 'apprenant', '80 % du stock',
     "Esthel a obtenu une baisse de prix sur 80 % de son stock.", 'Esthel, conseillère immobilière'),
    (['prospection'], ['equipe', 'direction'], 'apprenant', '150 lots',
     "Une agence niçoise a récupéré 150 lots en gestion.", 'Agence à Nice'),
    (['acquereurs'], ['equipe'], 'apprenant', '+ 1 M€',
     "Une agence du neuf a conclu une vente à plus d'un million d'euros.", 'Agence spécialisée dans le neuf'),
    (['direction'], ['direction', 'equipe'], 'apprenant', 'Record',
     "Accompagnée toute l'année, l'agence a réalisé le meilleur chiffre d'affaires de son histoire.", 'Agence suivie à l\'année'),
    (['ia', 'organisation'], ['conseiller'], 'apprenant', 'Son site',
     "Grâce à la formation, Mathieu a créé lui-même le site de son activité.", 'Mathieu, agent immobilier'),
    (['decouverte'], ['conseiller', 'equipe'], 'analyse', '+ 25 %',
     "Nos apprenants augmentent leur taux de transformation de plus de 25 %.", 'Analyse Start Academia des suivis de formation'),
    (['organisation', 'ia'], ['conseiller', 'equipe'], 'analyse', '8 h',
     "Nos apprenants gagnent 8 heures par semaine en moyenne.", 'Analyse Start Academia des suivis de formation'),
]
TYPES = {'apprenant': 'Résultat d\'apprenant', 'analyse': 'Analyse Start Academia', 'google': 'Avis Google'}

# Thèmes des avis : nombre d'avis écrits qui en parlent (208 avis avec texte, relevé du 11/11/2026)
THEMES = [
    ('L\'IA et les outils', 50, ['ia'], [
        ("Ils m'ont permis de comprendre comment utiliser l'IA pour gagner du temps, améliorer mes analyses et offrir un accompagnement encore plus précis à mes clients.", 'Jeremy H.'),
        ("Excellents formateurs IA, j'en ai appris beaucoup sur le sujet en très peu de temps et suis ravi de pouvoir mettre en pratique leurs nombreux conseils.", 'Brian P.'),
        ("Ils sont très pédagogue et mettent à disposition des outils très intéressant pour les professionnels de l'immobilier.", 'Nicolas T.'),
    ]),
    ('Des formateurs humains et pédagogues', 36, ['conseiller'], [
        ("Au-delà de la qualité de la formation, nous avons particulièrement apprécié les qualités humaines de Jean-Guy et Laurent.", 'Baptiste Q.'),
        ("Des formateurs incroyables, passionnés, pédagogues et généreux dans le partage de leur expérience.", 'Sabrina S.'),
        ("Ce sont des formateurs passionnés, accessibles et surtout très à l'écoute.", 'Naouel N.'),
    ]),
    ('Du concret, applicable tout de suite', 26, ['organisation'], [
        ("Leur grande expérience du terrain permet de transmettre des conseils concrets, immédiatement applicables au quotidien.", 'Baptiste Q.'),
        ("Leur manière d'enseigner est concrète, pratique et basée sur des situations réelles, ce qui fait toute la différence.", 'Roxana P.'),
        ("La formation était à la fois très instructive, concrète et motivante, avec de nombreux conseils applicables immédiatement.", 'Margaux B.'),
    ]),
    ('Résultats, gain de temps, efficacité', 17, ['direction'], [
        ("Une approche totalement différente des formations classiques, avec de vrais résultats sur le terrain.", 'Yannick R.'),
        ("Formations très intéressantes avec des cas concrets et des astuces pour obtenir des meilleurs résultats dans les différentes phases de notre métier.", 'Gavina F.'),
    ]),
]

etoile = '<svg aria-hidden="true"><use href="#etoile"/></svg>'


def carte(e, p, t, chiffre, phrase, qui):
    noms = dict(ETAPES)
    tags = ''.join(f'<li>{noms[x]}</li>' for x in e)
    return f'''
      <article class="rs-carte rs-{t}" data-etapes="{' '.join(e)}" data-profils="{' '.join(p)}">
        <span class="rs-type">{TYPES[t]}</span>
        <strong class="rs-chiffre">{h.escape(chiffre)}</strong>
        <p class="rs-phrase">{h.escape(phrase)}</p>
        <p class="rs-qui">{h.escape(qui)}</p>
        <ul class="rs-tags" aria-label="Étapes concernées">{tags}</ul>
      </article>'''


def theme(titre, n, _, citations):
    cit = ''.join(f'<figure><blockquote>{h.escape(c)}</blockquote><figcaption>{etoile*5}<span>{h.escape(a)} · Avis Google</span></figcaption></figure>' for c, a in citations)
    return f'''
      <section class="rs-theme" aria-label="{h.escape(titre)}">
        <div class="rs-theme-tete"><h3>{h.escape(titre)}</h3><p><strong>{n}</strong> avis en parlent</p>
          <span class="rs-barre"><i style="width:{round(n / 208 * 100)}%"></i></span></div>
        <div class="rs-cits">{cit}</div>
      </section>'''



# ---------- La chaîne vivante : les 8 étapes du métier (accueil) + le pilotage d'agence
import math
CHAINE = [
    ('Prospection', "Repérer les propriétaires de votre secteur, puis leur parler au bon moment.", "Un dossier d'adresse complet en quelques minutes et des messages personnalisés, avec Academia Secteur et Academia Vivre ici.", [2]),
    ('Découverte', "Comprendre le vendeur : son projet, ses motivations, ses freins, sa façon de décider.", "Son profil et la manière de lui parler avant le rendez-vous avec Academia Profiling, ses documents analysés avec Gemini Notebook.", [6]),
    ('Estimation', "Justifier un prix réaliste, comparables à l'appui.", "Une analyse comparative claire et un avis de valeur argumenté, avec Academia ACM.", [0]),
    ('Mandat', "Signer l'exclusivité, puis prouver au vendeur, semaine après semaine, que vous travaillez pour lui.", "Un argumentaire adapté au vendeur et un process de suivi qui le tient informé, préparé avec l'IA.", [1, 0]),
    ('Acquéreurs', "Comprendre l'acquéreur et son projet de vie, pas seulement ses critères.", "Une découverte qui va jusqu'à sa vie dans le quartier, avec Academia Vivre ici et Academia Profiling.", [3]),
    ('Visites et offres', "Sélectionner les bons biens, faire visiter, puis défendre l'offre devant le vendeur.", "Une sélection ciblée et des offres argumentées par le marché, avec Academia ACM et Academia Radar Acheteur.", []),
    ('Organisation', "Tenir son agenda, ses relances et ses priorités sans y passer ses soirées.", "Une semaine planifiée, des mails et comptes rendus rédigés en quelques minutes, avec ChatGPT et Claude.", [7, 5]),
    ('Administratif', "Traiter les documents, la conformité et les tâches répétitives.", "Des synthèses de documents, des réponses juridiques vérifiées et des tâches automatisées, avec Gemini Notebook, Academia Juridique et nos outils IA.", []),
    ("Pilotage d'agence", "Suivre l'activité de l'équipe, accompagner chaque conseiller, fixer les bons objectifs.", "Les indicateurs de l'agence et de chaque conseiller avec Academia Pilotage, les diagnostics et objectifs avec Academia Parcours.", [4]),
]
N = len(CHAINE)


def pos(i):
    return round(5 + i * (90 / (N - 1)), 2), round(50 + 30 * math.sin(i * 0.95 + 0.4), 2)


pts = [pos(i) for i in range(N)]
chemin = 'M' + ' '.join(f'{x},{y * 0.3:.2f}' for x, y in pts)


def noeud(i, c):
    x, y = pts[i]
    vide = '' if c[3] else ' vide'
    actif = 'true' if i == 0 else 'false'
    nb = len(c[3]) or ''
    return (f'<button type="button" class="ch-noeud{vide}" style="left:{x}%;top:{y}%" data-i="{i}" aria-pressed="{actif}" aria-controls="ch-panneau">'
            f'<span class="ch-point"><b>{nb}</b></span><span class="ch-nom"><small>{i + 1:02d}</small>{h.escape(c[0])}</span></button>')


def panneau(i, c):
    nom, geste, ia, ids = c
    cartes_e = ''.join(carte(*HISTOIRES[k]) for k in ids)
    if not cartes_e:
        cartes_e = ('<article class="rs-carte rs-vide"><p>Pas encore de résultat publié à cette étape.</p>'
                    f'<p>Ce sera peut-être le vôtre&nbsp;: <a href="{CAL}" rel="noopener">parlons-en</a>.</p></article>')
    cache = '' if i == 0 else ' hidden'
    return (f'\n      <div class="ch-etape" data-i="{i}"{cache}>'
            f'<div class="ch-texte"><p class="ch-num">Étape {i + 1:02d} sur {N}</p><h3>{h.escape(nom)}</h3>'
            f'<p class="ch-geste">{h.escape(geste)}</p><p class="ch-ia"><span>Avec l\'IA</span>{h.escape(ia)}</p>'
            '<div class="ch-nav"><button type="button" data-pas="-1" aria-label="Étape précédente">←</button>'
            '<button type="button" data-pas="1" aria-label="Étape suivante">→</button></div></div>'
            f'<div class="ch-preuves">{cartes_e}</div></div>')


noeuds = ''.join(noeud(i, c) for i, c in enumerate(CHAINE))
panneaux = ''.join(panneau(i, c) for i, c in enumerate(CHAINE))

themes = ''.join(theme(*x) for x in THEMES)

TITRE = 'Résultats et avis de nos clients | Start Academia'
DESC = 'Ce qui change dans une agence après une formation Start Academia : résultats d\'apprenants, 227 avis Google, méthode de mesure. Formation IA immobilier.'
URL = 'https://www.start-academia.fr/resultats/'

html = f'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITRE}</title>
<meta name="description" content="{DESC}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{URL}">
<meta name="theme-color" content="#0b1033">
<meta property="og:type" content="website">
<meta property="og:locale" content="fr_FR">
<meta property="og:site_name" content="Start Academia">
<meta property="og:title" content="Ce qui change dans une agence après Start Academia">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="{URL}">
<meta property="og:image" content="https://www.start-academia.fr/img/og.jpg">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/favicon-96x96.png" type="image/png" sizes="96x96">
<link rel="icon" href="/favicon-192x192.png" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="/apple-touch-icon.png" sizes="180x180">
{fonts}
<link rel="stylesheet" href="/styles.css">
</head>
<body class="sous-page">
<a class="evite" href="#contenu">Aller au contenu</a>
{symboles}
{entete}
<main id="contenu">
<section class="page-tete rs-tete">
  <div class="contenu">
    <p class="fil"><a href="/">Accueil</a> <span aria-hidden="true">/</span> Résultats</p>
    <h1>Ce qui change dans une agence après Start Academia.</h1>
    <p class="promesse">Pas un carrousel d'avis : des résultats concrets, classés par étape du métier, avec pour chacun le type de preuve et sa source.</p>
    <div class="rs-compteurs">
      <div><strong><span data-qualiof="apprenantsFormes">240</span></strong><span>apprenants formés</span><small>Source&nbsp;: QualiOF</small></div>
      <div><strong>5,0<em>/5</em></strong><span>227 avis Google</span><small>Relevé le 11/11/2026</small></div>
      <div><strong><span data-qualiof="tauxRecommandation">100</span><em>&nbsp;%</em></strong><span>recommandent la formation</span><small>Source&nbsp;: QualiOF</small></div>
      <div><strong>37</strong><span>agences et réseaux clients</span><small>Logos en bas de page</small></div>
    </div>
  </div>
</section>

<section class="rs-chaine" aria-labelledby="titre-chaine">
  <div class="rs-large">
    <p class="surtitre">La chaîne du métier</p>
    <h2 id="titre-chaine" class="rs-h2">Choisissez une étape.<br>Voyez ce qui a changé.</h2>
  </div>
  <p class="ch-glisser" aria-hidden="true">← Glissez pour voir les 9 étapes →</p>
  <div class="ch-scene">
    <div class="ch-reseau">
      <svg class="ch-svg" viewBox="0 0 100 30" preserveAspectRatio="none" aria-hidden="true"><path class="ch-trace" d="{chemin}"/><path class="ch-flux" d="{chemin}"/></svg>
      {noeuds}
    </div>
  </div>
  <div class="rs-large">
    <div id="ch-panneau" class="ch-panneau" aria-live="polite">{panneaux}
    </div>
    <p class="rs-legende"><span class="rs-type rs-apprenant">Résultat d'apprenant</span> rapporté par l'apprenant ou l'agence après la formation · <span class="rs-type rs-analyse">Analyse Start Academia</span> calculé à partir des suivis de nos formations</p>
  </div>
</section>

<section class="rs-avis" aria-labelledby="titre-avis">
  <div class="rs-large">
    <p class="surtitre">227 avis Google</p>
    <h2 id="titre-avis" class="rs-h2">Ce qui revient le plus dans les avis.</h2>
    <div class="rs-repartition">
      <div class="rs-note"><strong>5,0</strong><span class="etoiles">{etoile*5}</span><span>227 avis</span></div>
      <ul aria-label="Répartition des notes">
        <li><span>5</span><i><b style="width:96.5%"></b></i><em>219</em></li>
        <li><span>4</span><i><b style="width:3.1%"></b></i><em>7</em></li>
        <li><span>3</span><i><b style="width:.5%"></b></i><em>1</em></li>
        <li><span>2</span><i><b style="width:0"></b></i><em>0</em></li>
        <li><span>1</span><i><b style="width:0"></b></i><em>0</em></li>
      </ul>
      <p>On affiche toute la répartition, pas seulement la moyenne. Les avis à 4 et 3 étoiles comptent aussi.</p>
    </div>
    {themes}
    <p class="rs-source">Thèmes repérés dans les 208 avis rédigés (relevé du 11 novembre 2026). Citations extraites d'avis publics, signées du prénom et de l'initiale. <a href="{FICHE}" rel="noopener">Lire tous les avis sur Google</a></p>
  </div>
</section>

<section class="rs-methode" aria-labelledby="titre-methode">
  <div class="rs-large rs-methode-in">
    <div>
      <p class="surtitre">Transparence</p>
      <h2 id="titre-methode" class="rs-h2">Comment on compte.</h2>
      <p>Un chiffre sans source ne vaut rien. Voici d'où viennent les nôtres.</p>
    </div>
    <dl>
      <div><dt>Apprenants, satisfaction, recommandation</dt><dd>Questionnaires de fin de formation enregistrés dans QualiOF, notre outil de suivi qualité. Mis à jour automatiquement chaque nuit.</dd></div>
      <div><dt>Avis Google</dt><dd>Fiche publique Start Academy (notre ancien nom). Note, nombre et répartition relevés le 11 novembre 2026.</dd></div>
      <div><dt>Résultats d'apprenants</dt><dd>Résultats rapportés par les apprenants ou leur agence après la formation. Ils dépendent aussi du marché et de leur travail&nbsp;: ils ne garantissent pas un résultat identique ailleurs.</dd></div>
      <div><dt>Analyses Start Academia</dt><dd>Calculées à partir des suivis de nos formations. Depuis novembre 2026, nous mesurons les formations IA avant et après (mêmes tâches chronométrées à J0 et J+30)&nbsp;: les premières études de cas seront publiées ici.</dd></div>
    </dl>
  </div>
</section>

<section class="rs-logos" aria-labelledby="titre-logos">
  <div class="rs-large">
    <h2 id="titre-logos" class="rs-h2">Ils nous ont fait confiance.</h2>
    {mur}
  </div>
</section>

<section class="final final-simple" aria-labelledby="titre-final">
  <div class="contenu">
    <h2 id="titre-final">Votre agence, prochaine étude de cas&nbsp;?</h2>
    <p>30 minutes pour faire le point sur votre agence, ce que vous voulez améliorer et votre financement. Gratuit et sans engagement.</p>
    <a class="action" href="{CAL}" rel="noopener">Réserver mon appel découverte{fl}</a>
    <p class="tel">Vous préférez appeler&nbsp;? <a href="tel:+33610230060">06 10 23 00 60</a></p>
  </div>
</section>
</main>
{pied}
<script src="/logo.js" defer></script>
<script src="/mur.js" defer></script>
<script>
(function () {{
  var noeuds = [].slice.call(document.querySelectorAll('.ch-noeud')), etapes = [].slice.call(document.querySelectorAll('.ch-etape')), cur = 0;
  function aller(i) {{
    cur = (i + noeuds.length) % noeuds.length;
    noeuds.forEach(function (n, k) {{ n.setAttribute('aria-pressed', k === cur ? 'true' : 'false'); n.classList.toggle('passe', k < cur); }});
    etapes.forEach(function (e, k) {{ e.hidden = k !== cur; }});
    var sc = document.querySelector('.ch-scene'), n = noeuds[cur];
    if (sc.scrollWidth > sc.clientWidth) sc.scrollTo({{ left: n.offsetLeft - sc.clientWidth / 2, behavior: 'smooth' }});
  }}
  noeuds.forEach(function (n, k) {{ n.addEventListener('click', function () {{ aller(k); }}); }});
  document.querySelectorAll('[data-pas]').forEach(function (b) {{ b.addEventListener('click', function () {{ aller(cur + (+b.dataset.pas)); }}); }});
  aller(0);
}})();
</script>
</body>
</html>
'''
(racine / 'resultats').mkdir(exist_ok=True)
(racine / 'resultats' / 'index.html').write_text(html)
print('resultats/ générée')
