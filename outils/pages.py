"""Génère les sous-pages du site à partir de l'en-tête et du pied de page de index.html."""
import re, pathlib
racine = pathlib.Path('/home/claude/site3')
idx = (racine / 'index.html').read_text()
symboles = re.search(r'<svg width="0".*?</svg>', idx, re.S).group(0)
entete = re.search(r'<header class="entete">.*?</header>', idx, re.S).group(0).replace('href="#', 'href="/#')
pied = re.search(r'<footer class="pied">.*?</footer>', idx, re.S).group(0).replace('href="#', 'href="/#')
fonts = re.search(r'<link rel="preconnect" href="https://fonts.googleapis.com">.*?display=swap">', idx, re.S).group(0)
CAL = 'https://calendar.app.google/7XsB8TrXs1KSkHs4A'
fl = '<svg aria-hidden="true"><use href="#fleche"/></svg>'

def page(chemin, titre, desc, h1, intro, corps, robots='index, follow', appel=True):
    corps = re.sub(r'(<h2>.*?</h2>)(.*?)(\n  </div>)', r'\1<div class="corps">\2</div>\3', corps, flags=re.S)
    url = f'https://www.start-academia.fr/{chemin}'
    final = f'''
<section class="final final-simple" aria-labelledby="titre-final">
  <div class="contenu">
    <h2 id="titre-final">Parlons de votre agence.</h2>
    <p>30 minutes pour faire le point sur vos besoins et votre financement. Gratuit et sans engagement.</p>
    <a class="action" href="{CAL}" rel="noopener">Réserver mon appel découverte{fl}</a>
    <p class="tel">Vous préférez appeler&nbsp;? <a href="tel:+33610230060">06 10 23 00 60</a></p>
  </div>
</section>''' if appel else ''
    html = f'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titre}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#0b1033">
<meta property="og:type" content="website">
<meta property="og:locale" content="fr_FR">
<meta property="og:site_name" content="Start Academia">
<meta property="og:title" content="{h1}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="https://www.start-academia.fr/img/og.jpg">
<link rel="icon" href="/img/icon.webp" type="image/webp">
{fonts}
<link rel="stylesheet" href="/styles.css">
</head>
<body class="sous-page">
<a class="evite" href="#contenu">Aller au contenu</a>
{symboles}
{entete}
<main id="contenu">
<section class="page-tete">
  <div class="contenu">
    <p class="fil"><a href="/">Accueil</a> <span aria-hidden="true">/</span> {h1.rstrip('.')}</p>
    <h1>{h1}</h1>
    <p class="promesse">{intro}</p>
    {f'<a class="action" href="{CAL}" rel="noopener">Réserver mon appel découverte{fl}</a>' if appel else ''}
  </div>
</section>
<section class="clair texte-page">
{corps}
</section>{final}
</main>
{pied}
<script src="/logo.js" defer></script>
</body>
</html>
'''
    corps_html = None
    dossier = racine / chemin
    dossier.mkdir(parents=True, exist_ok=True)
    (dossier / 'index.html').write_text(html)

page('formation-loi-alur/',
 'Formation loi ALUR pour agents immobiliers | Start Academia',
 'Validez vos heures de formation continue loi ALUR avec des formations immobilier et IA sur mesure. Organisme certifié Qualiopi, Côte d’Azur et à distance.',
 'Formation loi ALUR pour les agents immobiliers.',
 'Validez vos heures de formation continue obligatoires avec des formations utiles dès le lendemain, sur votre métier et vos dossiers.',
 '''  <div class="bloc">
    <h2>Ce que la loi vous demande</h2>
    <p>Pour renouveler votre carte professionnelle, ou votre attestation si vous êtes collaborateur ou agent commercial, vous devez justifier de <strong>14 heures de formation continue par an, ou 42 heures sur 3 années consécutives</strong>.</p>
    <p>Parmi ces heures, certains thèmes sont obligatoires sur la période, notamment la déontologie et la non-discrimination dans l'accès au logement. Lors de l'appel découverte, on fait le point sur les heures qu'il vous reste et sur les thèmes à couvrir.</p>
  </div>
  <div class="bloc">
    <h2>Ce que nous vous proposons</h2>
    <ul class="points">
      <li><strong>Des heures qui servent à vendre.</strong> Prospection, estimation, mandat, découverte, visite, négociation, suivi&nbsp;: chaque module travaille une étape de votre métier, avec l'IA et nos outils maison.</li>
      <li><strong>Sur mesure.</strong> Le programme et la durée sont fixés avec vous selon vos besoins et vos heures restantes.</li>
      <li><strong>En agence sur la Côte d'Azur ou à distance</strong>, partout en France, en individuel ou en groupe.</li>
      <li><strong>Une attestation</strong> de formation remise à chaque participant pour vos heures ALUR.</li>
    </ul>
  </div>
  <div class="bloc">
    <h2>Pour qui</h2>
    <p>Agents immobiliers, négociateurs, mandataires et agents commerciaux, collaborateurs, directeurs et directrices d'agence. Débutants avec l'IA comme utilisateurs avancés&nbsp;: chaque parcours existe en version débutant et en version avancée.</p>
  </div>
  <div class="bloc">
    <h2>Financement</h2>
    <p>Start Academia est certifié Qualiopi au titre des actions de formation. Votre formation peut être prise en charge par votre OPCO (salariés et agences) ou par votre fonds d'assurance formation, comme l'AGEFICE ou le FIF PL (indépendants). Nos formations ne sont pas éligibles au CPF à ce jour. Nous vous aidons gratuitement à monter votre dossier.</p>
    <p><a class="lien-texte" href="/financement-formation-immobilier/">OPCO, FIF PL, AGEFICE&nbsp;: qui finance selon votre statut</a> · <a class="lien-texte" href="/documents/certificat-qualiopi.pdf">Voir notre certificat Qualiopi</a></p>
  </div>''')

page('coaching-pour-directeur-dagence-immobiliere-dans-le-06/',
 'Coaching de directeur d’agence immobilière | Start Academia',
 'Audit et coaching pour directeurs d’agence immobilière dans les Alpes-Maritimes : organisation, équipe, résultats et outils IA. Accompagnement sur l’année.',
 'Coaching et audit de direction.',
 'Pour les directeurs et managers d’agence qui veulent une équipe plus efficace, plus de mandats et des résultats qui tiennent dans la durée.',
 '''  <div class="bloc">
    <h2>Comment ça se passe</h2>
    <ol class="points numerotes">
      <li><strong>Appel découverte.</strong> 30 minutes pour comprendre votre agence, votre équipe et vos objectifs.</li>
      <li><strong>Audit de l'agence.</strong> Vos process, votre organisation commerciale et administrative, vos résultats&nbsp;: ce qui fonctionne et ce qui freine.</li>
      <li><strong>Plan d'action.</strong> Des recommandations concrètes, priorisées, et la place de l'IA et de nos outils dans votre organisation.</li>
      <li><strong>Coaching sur le terrain.</strong> Du directeur et de l'équipe&nbsp;: management, organisation, techniques de vente, temps.</li>
      <li><strong>Suivi dans la durée.</strong> On mesure les résultats avec vous et on ajuste.</li>
    </ol>
  </div>
  <div class="bloc">
    <h2>Ce que vous en retirez</h2>
    <ul class="points">
      <li>Une équipe qui suit la même méthode, à chaque étape de la transaction.</li>
      <li>Des outils partagés par tous&nbsp;: dossier d'adresse, analyse comparative de marché, profiling, assistant juridique.</li>
      <li>Un regard extérieur de gens du terrain, pas de consultants.</li>
    </ul>
    <p class="preuve-texte">Accompagnée toute l'année, une agence a réalisé le meilleur chiffre d'affaires de son histoire.</p>
  </div>
  <div class="bloc">
    <h2>Informations pratiques</h2>
    <p>Accompagnement sur mesure dans les Alpes-Maritimes et alentours, ou à distance. Tarif sur devis après l'appel découverte. Prise en charge possible par votre OPCO.</p>
  </div>''')

page('mentions-legales/',
 'Mentions légales | Start Academia',
 'Mentions légales, données personnelles et documents de Start Academia, organisme de formation certifié Qualiopi.',
 'Mentions légales.',
 'Les informations sur l’éditeur du site, l’hébergement, vos données et nos documents.',
 '''  <div class="bloc">
    <h2>Éditeur du site</h2>
    <p>START ACADEMY (marque Start Academia), SAS au capital de 7&nbsp;€, 12 avenue des Camélias, 06800 Cagnes-sur-Mer.<br>
    RCS Antibes 951&nbsp;319&nbsp;094 · SIRET&nbsp;: 951&nbsp;319&nbsp;094&nbsp;00029 · TVA intracommunautaire&nbsp;: FR14951319094<br>
    Organisme de formation enregistré sous le numéro de déclaration d'activité 93&nbsp;06&nbsp;10481&nbsp;06 auprès du préfet de la région Provence-Alpes-Côte d'Azur. Cet enregistrement ne vaut pas agrément de l'État.<br>
    Directeur de la publication&nbsp;: Laurent Marx, président.<br>
    Contact&nbsp;: <a href="mailto:info@start-academy.fr">info@start-academy.fr</a>, <a href="tel:+33610230060">06 10 23 00 60</a></p>
  </div>
  <div class="bloc">
    <h2>Hébergement</h2>
    <p>Vercel Inc., 440 N Barranca Avenue #4133, Covina, CA 91723, États-Unis. <a href="https://vercel.com" rel="noopener">vercel.com</a></p>
  </div>
  <div class="bloc">
    <h2>Propriété intellectuelle</h2>
    <p>Les textes, images, logos et contenus de ce site appartiennent à Start Academia ou sont utilisés avec autorisation. Toute reproduction sans accord écrit est interdite. Les logos des réseaux et agences partenaires appartiennent à leurs propriétaires.</p>
  </div>
  <div class="bloc" id="donnees">
    <h2>Données personnelles</h2>
    <p>Ce site ne comporte pas de formulaire et ne dépose aucun cookie publicitaire ni de mesure d'audience. Les polices de caractères sont chargées depuis le service Google Fonts. La démonstration de l'accueil envoie l'adresse tapée au service de géocodage de l'IGN (Base Adresse Nationale) et ses coordonnées à l'API publique DVF du Cerema, uniquement pour afficher le résultat ; nous ne conservons rien. La prise de rendez-vous se fait sur Google Agenda, qui traite vos données selon sa propre politique de confidentialité.</p>
    <p>Les données que vous nous transmettez (appel, e-mail, rendez-vous) servent uniquement à vous répondre et à organiser votre formation. Elles ne sont ni vendues ni cédées. Vous pouvez demander leur accès, leur rectification ou leur suppression en écrivant à <a href="mailto:info@start-academy.fr">info@start-academy.fr</a>. Vous pouvez aussi saisir la CNIL (<a href="https://www.cnil.fr" rel="noopener">cnil.fr</a>).</p>
  </div>
  <div class="bloc">
    <h2>Documents</h2>
    <ul class="points">
      <li><a class="lien-texte" href="/documents/conditions-generales-de-vente.pdf">Conditions générales de vente</a></li>
      <li><a class="lien-texte" href="/documents/reglement-interieur.pdf">Règlement intérieur</a></li>
      <li><a class="lien-texte" href="/documents/charte-accueil-handicap.pdf">Charte d'accueil des personnes en situation de handicap</a>. Référent handicap&nbsp;: Jean-Guy Ourmières, <a href="tel:+33610230060">06 10 23 00 60</a></li>
      <li><a class="lien-texte" href="/documents/certificat-qualiopi.pdf">Certificat Qualiopi</a></li>
    </ul>
  </div>
  <div class="bloc">
    <h2>Droit applicable</h2>
    <p>Le présent site est soumis au droit français.</p>
  </div>''', appel=False)

# Page 404
page('404-tmp/', 'Page introuvable | Start Academia', 'Cette page n’existe pas ou plus.', 'Page introuvable.',
 'Cette page n’existe pas ou a été déplacée lors de la refonte du site.',
 '''  <div class="bloc"><p><a class="lien-texte" href="/">Revenir à l'accueil</a> ou <a class="lien-texte" href="/#chaine">découvrir notre méthode</a>.</p></div>''', robots='noindex')
(racine / '404.html').write_text((racine / '404-tmp/index.html').read_text().replace('<link rel="canonical" href="https://www.start-academia.fr/404-tmp/">\n',''))
import shutil; shutil.rmtree(racine / '404-tmp')
print('ok')
