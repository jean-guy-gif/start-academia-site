"""Génère /formations/ : le catalogue des formations réalisées (indicateur 1 Qualiopi).
Source : start-academy.fr/nos-formations (extraction du 05/11/2026), nettoyée.
AV = objectifs rédigés par Claude à partir du titre : à valider par le formateur."""
import re, pathlib, html as h
src = (pathlib.Path(__file__).resolve().parent / 'pages.py').read_text()
exec(src[:src.index("\npage('")])          # récupère page(), entete, pied, CAL...

AV = True
# (catégorie, image, alt, phrase d'intro)
CATS = [
 ('prospection', 'Prospection et estimation', 'agence.webp',
  "La vitrine d'une agence immobilière au crépuscule, lumières allumées, annonces affichées en vitrine.",
  'Trouver les vendeurs de votre secteur et transformer chaque estimation en rendez-vous utile.'),
 ('vendeur', 'Vendeur et mandat', 'mandat.webp',
  "Gros plan sur une main qui signe un mandat au stylo plume, un trousseau de clés posé sur le bureau.",
  'Du premier rendez-vous vendeur au compromis : découverte, estimation, exclusivité, objections, suivi.'),
 ('acheteur', 'Acheteur et visite', 'visite.webp',
  "Un agent fait visiter à un couple un appartement lumineux face à une baie vitrée donnant sur la mer.",
  'Qualifier les acquéreurs, mener des visites qui débouchent sur une offre, assurer le suivi.'),
 ('ia', 'Intelligence artificielle et outils', 'formation.webp',
  "Une salle de formation en agence, des conseillers devant leurs ordinateurs pendant une session.",
  "Utiliser l'IA et les logiciels du métier sur vos vrais dossiers, du premier prompt aux usages avancés."),
 ('marketing', 'Marketing digital', 'hero.webp',
  "La vieille ville d'Antibes au bord de la mer, au coucher du soleil.",
  'Réseaux sociaux, vidéo, newsletter, référencement local : être visible sur son secteur.'),
 ('manager', 'Direction et management', 'r1.webp',
  "Un agent immobilier en rendez-vous autour d'une table, un ordinateur ouvert, la mer visible au crépuscule.",
  'Recruter, intégrer, animer et fidéliser une équipe de conseillers.'),
 ('mindset', 'Posture et performance', 'formation.webp',
  "Une salle de formation en agence pendant une session.",
  'Préparation mentale, objectifs et méthode pour tenir dans la durée.'),
]
C = 'Conseillers immobiliers et responsables d’agence'
D = 'Directeurs et responsables d’agence'
F = [
 # cat, slug, titre, heures, public, prérequis, objectifs, à valider
 ('prospection','generer-de-la-recommandation','Générer de la recommandation',7,C,None,
  ['Utiliser sa base de données pour gagner en notoriété','Utiliser les réseaux sociaux pour obtenir des recommandations','Identifier des sources complémentaires de recommandation'],0),
 ('prospection','acquisition-et-traitement-de-leads-vendeurs','Acquisition et traitement de leads vendeurs',7,C,None,
  ['Analyser et segmenter un secteur de prospection','Identifier et exploiter les sources de leads vendeurs','Créer, gérer et entretenir une base de données de prospects'],0),
 ('prospection','limmobilier-et-sa-prospection-efficace-devenir-incontournable-sur-son-secteur','L’immobilier et sa prospection efficace : devenir incontournable sur son secteur',7,C,None,
  ['Connaître et choisir les méthodes de prospection immobilière','Créer et entretenir une base de données solide au quotidien','Définir sa sphère d’influence et la cultiver'],0),
 ('prospection','les-leviers-de-lestimation','Les leviers de l’estimation',7,C,None,
  ['Générer du chiffre d’affaires supplémentaire avec ses dossiers d’estimation','Utiliser les outils adaptés','Apporter de la valeur sur les réseaux sociaux'],0),
 ('vendeur','basic-vendeur','Basic vendeur',7,C,None,
  ['Conduire le rendez-vous et identifier les besoins du vendeur','Maîtriser les outils d’estimation et présenter le prix','Présenter ses services et adapter sa stratégie','Maîtriser la trame de traitement des objections','Argumenter pour obtenir l’exclusivité'],0),
 ('vendeur','decouverte-vendeur-et-estimation-percutante','Découverte vendeur et estimation percutante',7,C,None,
  ['Maîtriser les techniques de découverte vendeur','Réaliser des estimations précises','Convaincre le vendeur avec des arguments solides'],0),
 ('vendeur','face-a-face-vendeur-experience-100-mise-en-scene','Face à face vendeur : expérience 100 % mise en scène',7,C,None,
  ['S’entraîner au premier rendez-vous vendeur en situation réelle','S’entraîner à la remise d’estimation','Signer des mandats et traiter les objections','Conduire le bilan de commercialisation'],0),
 ('vendeur','vente-de-mandats-exclusifs-et-gestion-des-objections-3','Vente de mandats exclusifs et gestion des objections',7,C,None,
  ['Maîtriser la vente du mandat exclusif','Construire sa stratégie pour obtenir des exclusivités','Traiter efficacement les objections des vendeurs'],0),
 ('vendeur','suivi-vendeur-lessentiel-pour-reussir','Suivi vendeur : l’essentiel pour réussir',7,C,None,
  ['Rendre compte des actions menées et des résultats obtenus','Renforcer la relation pour obtenir des recommandations','Présenter et tenir ses engagements envers le vendeur'],0),
 ('vendeur','transformez-vos-mandats-et-decrochez-des-rendez-vous-de-suivi-avec-succes','Transformez vos mandats et décrochez des rendez-vous de suivi',4,C,None,
  ['Maîtriser le discours et le déroulé du rendez-vous de suivi','Préparer un dossier de suivi vendeur complet','Mettre en place des scripts d’appel pour obtenir les rendez-vous de suivi'],0),
 ('vendeur','lart-de-la-negociation-2','L’art de la négociation',7,C,None,
  ['Utiliser les questions ouvertes','Détecter les signaux d’achat et s’y adapter','Trouver les leviers pour conclure une négociation'],0),
 ('vendeur','vente-de-mandats-exclusifs-et-gestion-des-objections-2','Négociation et compromis',7,C,None,
  ['Maîtriser les techniques de négociation immobilière','Préparer des compromis de vente solides','Gérer les objections et trouver un accord'],0),
 ('vendeur','maitriser-les-bases-juridiques-et-analyser-son-secteur','Maîtriser les bases juridiques et analyser son secteur',7,C,None,
  ['Acquérir les bases juridiques de la transaction','Appliquer ces connaissances dans sa pratique','Analyser son secteur pour décider en connaissance de cause'],0),
 ('vendeur','formation-immobiliere-360-devenez-le-maitre-de-votre-succes-immobilier','Formation immobilière 360° : de la prospection à la signature',7,C,None,
  ['Relier les étapes de la transaction, de la prospection à la signature','Repérer ses points forts et ses points de progrès à chaque étape','Construire son plan d’action personnel'],AV),
 ('acheteur','basic-acheteur','Basic acheteur',7,C,None,
  ['Qualifier un acquéreur dès le premier contact','Mener une découverte acheteur complète','Sélectionner les biens à proposer et préparer la visite'],AV),
 ('acheteur','acquisition-et-traitement-leads-acquereurs','Acquisition et traitement des leads acquéreurs',9,C,None,
  ['Vendre un rendez-vous découverte au téléphone','Identifier les acquéreurs réellement acheteurs','Réaliser une découverte de qualité et installer la relation'],0),
 ('acheteur','generation-de-leads-efficaces-2','Génération de leads efficaces',7,C,None,
  ['Comprendre les principes de la génération de leads','Mettre en place ses sources de leads','Convertir les leads en clients'],0),
 ('acheteur','visites-libres-gagnantes','Visites libres gagnantes',7,C,None,
  ['Organiser et promouvoir une visite libre','Accueillir et qualifier les visiteurs sur place','Transformer les contacts en offres, en mandats et en compte rendu vendeur'],AV),
 ('acheteur','face-a-face-acheteurs-experience-100-mise-en-scene','Face à face acheteurs : expérience 100 % mise en scène',9,C,None,
  ['S’entraîner à la découverte acheteur en situation réelle','Conduire une visite qui fait avancer la décision','Recueillir et défendre une offre'],AV),
 ('acheteur','suivi-acheteurs','Suivi acheteurs',9,C,None,
  ['Organiser le suivi de son fichier acquéreurs','Relancer au bon moment avec le bon message','Rapprocher les acquéreurs des nouveaux biens'],AV),
 ('ia','super-heros-de-limmobilier-avec-lia-et-chatgpt','Super-héros de l’immobilier avec l’IA et ChatGPT',4,'Agents, collaborateurs et responsables d’agence','Aucun prérequis technique',
  ['Maîtriser les bases et les techniques avancées de rédaction de prompts','Construire des argumentaires avec ChatGPT','Préparer une communication multicanale qui génère des contacts','Créer des scripts de prospection personnalisés','Analyser les résultats et ajuster sa stratégie'],0),
 ('ia','les-super-pouvoirs-de-lia-et-chatgpt-pour-limmobilier','Les super-pouvoirs de l’IA et ChatGPT pour l’immobilier',4,'Agents, collaborateurs et responsables d’agence','Aucun prérequis technique',
  ['Comprendre ce que l’IA générative sait faire, et ce qu’elle ne sait pas faire','Rédiger des annonces, des courriers et des comptes rendus avec ChatGPT','Vérifier les contenus produits et respecter le RGPD'],AV),
 ('ia','conquete-vendeurs','Conquête vendeurs avec Cadastre.com',7,C,'Accès utilisateur à Cadastre.com',
  ['Trouver un bien et son adresse avec Cadastre.com','Utiliser l’analyse comparative de marché pour obtenir des rendez-vous d’estimation','Utiliser l’outil côté acquéreurs pour trouver des biens et organiser des visites'],0),
 ('ia','formation-logiciel-cadastre-com-level-1','Logiciel Cadastre.com, niveau 1',8,'Agents, collaborateurs et responsables d’agence','Bases des outils numériques. Accès utilisateur à Cadastre.com',
  ['Prendre en main l’interface et les recherches de biens','Identifier les propriétaires et les données utiles de son secteur','Intégrer l’outil dans sa prospection quotidienne'],AV),
 ('ia','formation-logiciel-cadastre-com-level-2-pour-les-professionnels-confirmes','Logiciel Cadastre.com, niveau 2',14,'Agents confirmés, gestionnaires de patrimoine, promoteurs','Maîtrise de base de Cadastre.com, expérience de la prospection, accès utilisateur',
  ['Exploiter les fonctions avancées de recherche et d’analyse','Construire des campagnes de prospection ciblées','Produire des analyses de marché pour ses clients'],AV),
 ('marketing','decouvrir-le-community-management-la-gestion-des-reseaux-sociaux','Découvrir le community management et la gestion des réseaux sociaux',14,'Dirigeants et collaborateurs',None,
  ['Connaître le fonctionnement des principaux réseaux sociaux','Comprendre le rôle du community manager et bâtir un plan de publication','Choisir ses réseaux selon sa clientèle','Créer et administrer ses pages Facebook, Instagram et LinkedIn','Lancer des publicités et suivre les indicateurs'],0),
 ('marketing','au-dela-des-basics-techniques-avancees-de-creation-pour-instagram-dans-limmobilier-pro-avance','Techniques avancées de création pour Instagram',7,'Dirigeants et collaborateurs','Utiliser déjà Instagram',
  ['Comprendre l’algorithme d’Instagram','Maîtriser les techniques avancées de création de contenu','Optimiser ses publications pour l’engagement','Raconter son agence et ses biens (storytelling)'],0),
 ('marketing','instagram-immobilier-pro-atelier-de-creation-et-planification-de-contenu-strategique-perfectionnement','Instagram immobilier : atelier de création et de planification',7,'Dirigeants et collaborateurs','Utiliser déjà Instagram',
  ['Produire images, vidéos et textes adaptés à Instagram','Construire son calendrier de publication du mois','Rédiger des légendes, choisir ses hashtags et ses appels à l’action','Créer et planifier ses publications en atelier'],0),
 ('marketing','maitrisez-la-video-pour-alimenter-vos-reseaux-sociaux','Maîtrisez la vidéo pour vos réseaux sociaux',7,'Dirigeants et collaborateurs',None,
  ['Découvrir le potentiel de la vidéo pour l’immobilier','Utiliser les stories pour engager son audience','Trouver des idées de réels, transitions et musiques','Réaliser un réel complet pour Instagram ou TikTok'],0),
 ('marketing','propulsez-votre-campagne-de-newsletters-creez-diffusez-et-suivez-son-impact','Créer, diffuser et suivre sa newsletter',14,'Dirigeants et collaborateurs',None,
  ['Concevoir et rédiger une newsletter','Respecter les obligations du RGPD','Diffuser avec un outil comme Brevo, Mailchimp ou Mailjet','Gérer et organiser ses contacts','Améliorer l’ouverture et mesurer les résultats'],0),
 ('marketing','maitrisez-votre-impact-numerique-maximisez-le-referencement-et-la-reputation-en-ligne','Référencement local et réputation en ligne',7,'Dirigeants d’agence',None,
  ['Comprendre les différentes formes de présence en ligne','Combiner référencement et gestion de l’e-réputation','Optimiser la fiche Google de son agence'],0),
 ('manager','transformez-votre-recrutement-en-un-jeu-gagnant','Transformez votre recrutement en un jeu gagnant',7,D,None,
  ['Définir le profil du conseiller recherché','Attirer des candidats avec une offre et des canaux adaptés','Conduire des entretiens qui révèlent le potentiel'],AV),
 ('manager','developpez-votre-equipe-immobiliere-avec-des-talents-dexception','Développez votre équipe avec des talents d’exception',7,D,None,
  ['Repérer les talents dans et hors du métier','Construire un parcours d’intégration','Faire progresser chaque conseiller selon son profil'],AV),
 ('manager','de-la-preparation-a-la-signature-le-secret-pour-recruter-avec-succes-et-faire-grandir-votre-equipe','Recruter de la préparation à la signature',7,D,None,
  ['Préparer son plan de recrutement','Mener le processus jusqu’à la signature du contrat','Réussir les premières semaines du nouveau conseiller'],AV),
 ('manager','organiser-un-evenement-carriere-qui-attire-les-talents-exceptionnels','Organiser un événement carrière',7,D,None,
  ['Concevoir un événement carrière pour son agence','Le promouvoir auprès des bons profils','Transformer les participants en candidats'],AV),
 ('manager','booster-animer-et-fideliser-les-performances-de-votre-equipe','Booster, animer et fidéliser son équipe',7,D,None,
  ['Fixer des objectifs et suivre les indicateurs de l’équipe','Animer des réunions qui font avancer','Fidéliser ses conseillers dans la durée'],AV),
 ('mindset','preparation-mentale-pour-excellence-immobiliere','Préparation mentale pour l’excellence immobilière',7,C,None,
  ['Identifier ses leviers de motivation et ses freins','Gérer son stress et ses émotions en rendez-vous','Mettre en place des routines de performance'],AV),
 ('mindset','forgez-votre-succes-immobilier-avec-la-preparation-mentale','Forgez votre succès avec la préparation mentale',7,D,None,
  ['Développer sa confiance et sa posture de dirigeant','Rebondir après un échec commercial','Transmettre ces outils à son équipe'],AV),
 ('mindset','gestion-strategique-des-objectifs-en-immobilier-2','Gestion stratégique des objectifs',7,C,None,
  ['Fixer des objectifs réalistes et mesurables','Les découper en actions quotidiennes','Suivre ses résultats et ajuster'],AV),
 ('mindset','accelerez-votre-succes-en-immobilier-de-la-theorie-a-la-pratique-pour-les-nouveaux-conseillers','Nouveaux conseillers : de la théorie à la pratique',7,'Conseillers débutants et responsables d’agence qui les intègrent',None,
  ['Organiser sa semaine de nouveau conseiller','Maîtriser les premiers gestes : prospection, estimation, mandat','Se fixer un plan d’action pour ses trois premiers mois'],AV),
]

def duree(hh):
    j = {7: ' (1 jour)', 14: ' (2 jours)'}.get(hh, '')
    return f'{hh} h{j}'

nav = ''.join(f'<li><a href="#{c[0]}">{c[1]} <span>{sum(1 for f in F if f[0]==c[0])}</span></a></li>' for c in CATS)
corps = f'''  <div class="catalogue">
    <nav class="sommaire" aria-label="Catégories de formations"><ol>{nav}</ol></nav>
    <aside class="communs" aria-labelledby="titre-communs">
      <h2 id="titre-communs">Valable pour toutes les formations</h2>
      <dl>
        <div><dt>Modalités</dt><dd>En agence (Alpes-Maritimes et alentours) ou à distance, en individuel ou en groupe.</dd></div>
        <div><dt>Méthodes</dt><dd>Apports courts, mises en situation professionnelles, exercices sur vos propres dossiers et échanges de pratiques.</dd></div>
        <div><dt>Évaluation</dt><dd>Positionnement de départ, évaluation des acquis en fin de formation, questionnaire de satisfaction, attestation remise.</dd></div>
        <div><dt>Tarif</dt><dd>Sur devis après l’appel découverte. Prise en charge possible par votre OPCO ou votre fonds d’assurance formation (AGEFICE, FIF PL…). Non éligible au CPF à ce jour.</dd></div>
        <div><dt>Délai d’accès</dt><dd>Démarrage selon vos disponibilités et le délai de prise en charge de votre financeur.</dd></div>
        <div><dt>Accessibilité</dt><dd>Référent handicap : Jean-Guy Ourmières, <a href="tel:+33610230060">06 10 23 00 60</a>. <a href="/documents/charte-accueil-handicap.pdf">Charte d’accueil</a></dd></div>
        <div><dt>Formateurs</dt><dd>Laurent Marx et Jean-Guy Ourmières, plus de 10 ans de transaction.</dd></div>
      </dl>
    </aside>
  </div>
'''
for slug_c, nom, img, alt, intro in CATS:
    fiches = ''
    for cat, slug, titre, hh, public, prereq, obj, av in [f for f in F if f[0] == slug_c]:
        lis = ''.join(f'<li>{h.escape(o)}</li>' for o in obj)
        fiches += f'''
      <details class="fiche" id="{slug}"{' data-a-valider' if av else ''}>
        <summary><span class="nom">{h.escape(titre)}</span><span class="duree">{duree(hh)}</span></summary>
        <div class="detail">
          <div><h4>Objectifs</h4><ul>{lis}</ul></div>
          <dl>
            <div><dt>Public</dt><dd>{h.escape(public)}</dd></div>
            <div><dt>Prérequis</dt><dd>{h.escape(prereq or 'Aucun')}</dd></div>
            <div><dt>Durée</dt><dd>{duree(hh)}</dd></div>
          </dl>
        </div>
      </details>'''
    corps += f'''  <section class="famille" id="{slug_c}" aria-labelledby="t-{slug_c}">
    <div class="famille-tete">
      <img src="/img/{img}" width="2000" height="1117" loading="lazy" alt="{h.escape(alt)}">
      <div><h2 id="t-{slug_c}">{nom}</h2><p>{intro}</p></div>
    </div>
    <div class="fiches">{fiches}
    </div>
  </section>
'''

page('formations/',
 'Catalogue des formations immobilier et IA | Start Academia',
 'Toutes nos formations pour agents et agences immobilières : prospection, mandat, acheteur, IA, marketing, management. Objectifs, durées et modalités.',
 'Nos formations.',
 f'{len(F)} formations construites sur les étapes de votre métier. Chacune peut être adaptée à votre agence et combinée dans un parcours sur mesure.',
 corps)

# le wrapper .corps ajouté par page() ne doit pas s'appliquer ici
p = racine / 'formations' / 'index.html'
t = p.read_text()
t = re.sub(r'<div class="corps">(.*?)</div>(\n  </div>)', r'\1\2', t, flags=re.S) if '<div class="corps">' in t else t
t = t.replace('<section class="clair texte-page">', '<section class="clair texte-page page-catalogue">')
p.write_text(t)
print(len(F), 'formations,', sum(1 for f in F if f[7]), 'à valider')
