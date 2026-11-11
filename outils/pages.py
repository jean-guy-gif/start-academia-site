"""Génère les sous-pages du site à partir de l'en-tête et du pied de page de index.html."""
import re, pathlib
racine = pathlib.Path(__file__).resolve().parents[1]  # racine du dépôt
idx = (racine / 'index.html').read_text()
symboles = re.search(r'<svg width="0".*?</svg>', idx, re.S).group(0)
entete = re.search(r'<header class="entete">.*?</header>', idx, re.S).group(0).replace('href="#', 'href="/#')
pied = re.search(r'<footer class="pied">.*?</footer>', idx, re.S).group(0).replace('href="#', 'href="/#')
fonts = re.search(r'<link rel="preconnect" href="https://fonts.googleapis.com">.*?display=swap">', idx, re.S).group(0)
CAL = 'https://meet.brevo.com/jean-guy-ourmieres/appel-decouverte'
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
<section class="page-tete">
  <div class="contenu">
    <nav class="fil" aria-label="Fil d'Ariane"><a href="/">Accueil</a> <span aria-hidden="true">/</span> {h1.rstrip('.')}</nav>
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
    Contact&nbsp;: <a href="mailto:info@start-academia.fr">info@start-academia.fr</a>, <a href="tel:+33610230060">06 10 23 00 60</a></p>
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
    <p>Ce site ne comporte pas de formulaire et ne dépose aucun cookie publicitaire ni de mesure d'audience. Les polices de caractères sont chargées depuis le service Google Fonts. La démonstration de l'accueil envoie l'adresse tapée au service de géocodage de l'IGN (Base Adresse Nationale) et ses coordonnées à l'API publique DVF du Cerema, uniquement pour afficher le résultat ; nous ne conservons rien.</p>
    <p>Les données que vous nous transmettez (appel, e-mail, rendez-vous) servent uniquement à vous répondre et à organiser votre formation. Elles ne sont ni vendues ni cédées. La réservation d'un appel découverte passe par le service Brevo Meetings (Sendinblue SAS, Paris), qui nous transmet les informations saisies dans le formulaire et envoie les e-mails et SMS de confirmation et de rappel ; le rendez-vous a lieu sur Google Meet. Vous pouvez demander leur accès, leur rectification ou leur suppression en écrivant à <a href="mailto:info@start-academia.fr">info@start-academia.fr</a>. Vous pouvez aussi saisir la CNIL (<a href="https://www.cnil.fr" rel="noopener">cnil.fr</a>).</p>
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


# Page de remerciement après réservation Brevo
page('merci-rendez-vous/', 'Appel réservé | Start Academia', 'Votre appel découverte est réservé.', 'Votre appel est réservé.',
 'Merci. Vous recevez une confirmation par e-mail avec le lien Google Meet, puis un rappel la veille et une heure avant.',
 '''  <div class="bloc">
    <h2>Pour gagner du temps pendant l'appel</h2>
    <ul class="points">
      <li>Notez vos 2 ou 3 tâches les plus chronophages de la semaine (annonces, relances, estimations, compte rendu…).</li>
      <li>Dites-nous les outils que vous utilisez déjà&nbsp;: logiciel de transaction, CRM, ChatGPT ou Claude.</li>
      <li>Si vous êtes salarié ou en réseau, pensez à votre financement possible (OPCO, AGEFICE, FIF PL…)&nbsp;: on regarde ensemble pendant l'appel.</li>
    </ul>
  </div>
  <div class="bloc">
    <h2>En attendant&nbsp;: faites votre diagnostic gratuit</h2>
    <p>Academia Parcours mesure votre activité sur les étapes du métier (prospection, mandat, acquéreurs, visites…) et vous donne votre diagnostic de performance immobilière en quelques minutes. On s'en servira pendant l'appel pour aller droit à l'essentiel.</p>
    <p><a class="action" href="https://app.myacademia.ai" rel="noopener">Faire mon diagnostic gratuit<svg aria-hidden="true"><use href="#fleche"/></svg></a></p>
  </div>
  <div class="bloc">
    <h2>Un empêchement&nbsp;?</h2>
    <p>Utilisez le lien « modifier ou annuler » de votre e-mail de confirmation, ou appelez-nous au <a href="tel:+33610230060">06 10 23 00 60</a>. Ça libère le créneau pour un autre conseiller.</p>
  </div>''', robots='noindex', appel=False)

# Page 404
page('404-tmp/', 'Page introuvable | Start Academia', 'Cette page n’existe pas ou plus.', 'Page introuvable.',
 'Cette page n’existe pas ou a été déplacée lors de la refonte du site.',
 '''  <div class="bloc"><p><a class="lien-texte" href="/">Revenir à l'accueil</a> ou <a class="lien-texte" href="/#chaine">découvrir notre méthode</a>.</p></div>''', robots='noindex')
(racine / '404.html').write_text((racine / '404-tmp/index.html').read_text().replace('<link rel="canonical" href="https://www.start-academia.fr/404-tmp/">\n',''))
import shutil; shutil.rmtree(racine / '404-tmp')
print('ok')
