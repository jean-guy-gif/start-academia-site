"""Génère /formations/ : le catalogue des formations réalisées (indicateur 1 Qualiopi).

Source principale : data/qualiof.json (écrit par sync_qualiof.py). Seuls les programmes qui ont
au moins un apprenant formé sont affichés (décision du 06/11/2026), avec leurs indicateurs.
Catégories et ancres : qualiof_mapping.py.

Repli, si data/qualiof.json est absent ou illisible : la liste F ci-dessous, rendue comme avant
(start-academy.fr/nos-formations, extraction du 05/11/2026). Elle n'est jamais fusionnée avec QualiOF.
AV = objectifs rédigés par Claude à partir du titre : à valider par le formateur (repli seulement)."""
import re, sys, json, pathlib, unicodedata, html as h
OUTILS = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(OUTILS))
from qualiof_mapping import THEME_VERS_CATEGORIE, CODE_VERS_SLUG_SITE, CODE_VERS_CATEGORIE
from fiches_map import FICHES
src = (OUTILS / 'pages.py').read_text()
exec(src[:src.index("\npage('")])          # récupère racine, page(), entete, pied, CAL...

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
 ('autres', 'Autres formations', 'formation.webp',      # affichée seulement si elle contient une fiche
  "Une salle de formation en agence pendant une session.",
  'Réglementation, langues et autres formations dispensées à nos apprenants.'),
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

QUALIOF = racine / 'data' / 'qualiof.json'
NOMS_CATS = {c[0] for c in CATS}


TAUX_HORAIRE = 42  # € HT de l'heure (tarif plancher communiqué par Jean-Guy, nov. 2026)


def prix(hh):
    return 'dès ' + f'{round(hh * TAUX_HORAIRE):,}'.replace(',', '\u202f') + '&nbsp;€&nbsp;HT'


def duree(hh):
    if hh != int(hh):
        return f'{hh:g}'.replace('.', ',') + ' h'
    hh = int(hh)
    j = {7: ' (1 jour)', 14: ' (2 jours)'}.get(hh, '')
    return f'{hh} h{j}'


def cle(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode()
    return ' '.join(s.lower().split())


THEMES = {cle(k): v for k, v in THEME_VERS_CATEGORIE.items()}
CAT_DU_SLUG = {f[1]: f[0] for f in F}


def categorie(p):
    c = (CODE_VERS_CATEGORIE.get(p['code']) or THEMES.get(cle(p.get('theme')))
         or CAT_DU_SLUG.get(CODE_VERS_SLUG_SITE.get(p['code'])) or 'autres')
    if c not in NOMS_CATS:
        print(f'formations : catégorie inconnue {c!r} pour {p["code"]}, classé dans autres', file=sys.stderr)
        c = 'autres'
    return c


def en_ligne(md):
    """**gras** et *italique* sur un texte déjà échappé."""
    md = re.sub(r'\*\*(\S(?:.*?\S)?)\*\*', r'<strong>\1</strong>', md)
    return re.sub(r'(?<![\w*])\*(\S(?:.*?\S)?)\*(?![\w*])', r'<em>\1</em>', md)


def markdown(md):
    """Markdown simple de QualiOF -> HTML : titres, listes à puces ou numérotées, paragraphes."""
    out, para, liste = [], [], None

    def fermer():
        nonlocal liste
        if para:
            out.append('<p>' + '<br>'.join(para) + '</p>'); para.clear()
        if liste:
            out.append(f'</{liste}>'); liste = None

    for brut in (md or '').replace('\r', '').split('\n'):
        l = brut.strip()
        m_t = re.match(r'#{1,6}\s+(.*)', l)
        m_ul = re.match(r'[-*•]\s+(.*)', l)
        m_ol = re.match(r'\d+[.)]\s+(.*)', l)
        if not l:
            fermer()
        elif m_t:
            fermer(); out.append(f'<h5>{en_ligne(h.escape(m_t.group(1).rstrip("# ")))}</h5>')
        elif m_ul or m_ol:
            if para:
                out.append('<p>' + '<br>'.join(para) + '</p>'); para.clear()
            balise = 'ul' if m_ul else 'ol'
            if liste != balise:
                if liste:
                    out.append(f'</{liste}>')
                out.append(f'<{balise}>'); liste = balise
            out.append(f'<li>{en_ligne(h.escape((m_ul or m_ol).group(1)))}</li>')
        else:
            if liste:
                out.append(f'</{liste}>'); liste = None
            para.append(en_ligne(h.escape(l.lstrip('> '))))
    fermer()
    return ''.join(out)


def texte(s):
    return '<br>'.join(h.escape(l.strip()) for l in (s or '').strip().split('\n') if l.strip())


def ligne_indicateurs(ind):
    """« 38 apprenants formés · 4,8/5 · 96 % recommandent (24 réponses) »."""
    n = ind.get('apprenantsFormes') or 0
    if not n:
        return ''
    s = 's' if n > 1 else ''
    parts = [f'{n} apprenant{s} formé{s}']
    sat = ind.get('satisfaction') or {}
    if sat.get('note5') is None:
        parts.append('Nouvelle formation')
    else:
        parts.append(f'{sat["note5"]:.1f}/5'.replace('.', ','))
        if sat.get('tauxRecommandation') is not None:
            parts.append(f'{round(sat["tauxRecommandation"])}&nbsp;% recommandent')
        k = sat.get('nbReponses') or 0
        if k:
            parts[-1] += f' ({k} réponse{"s" if k > 1 else ""})'
    return ' · '.join(parts)


def depuis_qualiof(d):
    fiches, vus = [], set()
    for p in d['programmes']:
        ind = p.get('indicateurs') or {}
        if (ind.get('apprenantsFormes') or 0) <= 0:
            continue                      # jamais dispensé : n'apparaît pas sur le site
        ancre = CODE_VERS_SLUG_SITE.get(p['code']) or p.get('slug') or cle(p['code']).replace(' ', '-')
        if ancre in vus or ancre in NOMS_CATS:
            ancre = f'{ancre}-{cle(p["code"]).replace(" ", "-")}'
        vus.add(ancre)
        fiches.append({'cat': categorie(p), 'id': ancre, 'titre': p['titre'], 'heures': p['dureeHeures'],
                       'public': texte(p.get('public')), 'prereq': texte(p.get('prerequis')) or 'Aucun',
                       'obj': [o for o in p['objectifs'] if str(o).strip()], 'av': False,
                       'programme': markdown(p.get('programme')), 'indicateurs': ligne_indicateurs(ind), 'ind': ind,
                       'texte': ' '.join([p['titre'], ' '.join(map(str, p['objectifs']))]),
                       'corps': str(p.get('programme') or '')})
    return fiches


def depuis_repli():
    return [{'cat': cat, 'id': slug, 'titre': titre, 'heures': hh, 'public': h.escape(public),
             'prereq': h.escape(prereq or 'Aucun'), 'obj': obj, 'av': av, 'programme': '', 'indicateurs': '',
             'ind': {}, 'texte': titre + ' ' + ' '.join(obj)}
            for cat, slug, titre, hh, public, prereq, obj, av in F]


def catalogue():
    """(fiches, source). Repli sur F si data/qualiof.json est absent, illisible ou sans formation dispensée."""
    if QUALIOF.exists():
        try:
            fiches = depuis_qualiof(json.loads(QUALIOF.read_text(encoding='utf-8')))
            if fiches:
                return fiches, 'QualiOF'
            print('formations : aucun programme QualiOF avec apprenants formés, repli sur le catalogue intégré', file=sys.stderr)
        except (ValueError, KeyError, TypeError) as e:
            print(f'formations : {QUALIOF.name} illisible ({e!r}), repli sur le catalogue intégré', file=sys.stderr)
    return depuis_repli(), 'repli'


# La chaîne de production du métier (même ordre que l'accueil). Une formation couvre une ou plusieurs
# étapes, repérées par mots-clés dans son titre et ses objectifs (textes QualiOF).
ETAPES = [
 ('prospection', 'Prospection', ['prospect', 'lead', 'capter', 'captation', 'sphere d', 'base de donnees', 'referencement', 'seo', 'reseaux sociaux', 'marketing', 'recherche fonciere']),
 ('decouverte', 'Découverte', ['relation client', 'relation vendeur', 'decouverte', 'persona', 'qualification']),
 ('estimation', 'Estimation', ['estimation', 'evaluation', 'analyse de biens', 'analyse approfondie', 'cadastre', 'prix']),
 ('mandat', 'Mandat', ['mandat', 'exclusi', 'suivi vendeur', 'reporting vendeur']),
 ('acquereurs', 'Acquéreurs', ['acquereur', 'acheteur']),
 ('visites', 'Visites et offres', ['visite', 'offre d', 'negociation', 'conclusion de vente', 'techniques de vente', 'annonce']),
 ('organisation', 'Organisation', ['productivite', 'automatis', 'organisation', "plan d'action", "plan d'utilisation", 'prompt', 'ia generative', 'assistant', 'tableau de bord', "systeme d'information"]),
 ('administratif', 'Administratif', ['administrat', 'tracfin', 'deontologie', 'discrimination', 'juridique', 'blanchiment', 'anglais']),
]

SEUIL_ACQUEREURS = 3

VISUELS = {
 'prospection': ['agence-a', 'secteur', 'localisateur', 'agence-b', 'antibes-a'],
 'decouverte': ['r1-a', 'profiling', 'r1-b', 'strategie', 'equipe'],
 'estimation': ['acm', 'dynamique', 'antibes-b'],
 'mandat': ['mandat-a', 'point-marche', 'mandat-b', 'mandat-c'],
 'acquereurs': ['radar', 'vivre-ici', 'visite-a'],
 'visites': ['visite-a', 'criteres', 'visite-b'],
 'organisation': ['formation-a', 'parcours', 'pilotage', 'formation-b', 'formation-c'],
 'administratif': ['final-a', 'final-b', 'mandat-c', 'formation-c'],
}

COMMUNS = '''  <aside class="communs" aria-labelledby="titre-communs">
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
'''

SCRIPT = '''<script src="/trouver.js" defer></script>
<script>
(() => {
  const boutons = [...document.querySelectorAll('.cf-chaine button')];
  const cartes = [...document.querySelectorAll('.carte-f')];
  const vide = document.querySelector('.cf-vide');
  const filtrer = (k) => {
    boutons.forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.etape === k)));
    let n = 0;
    cartes.forEach((c) => { const ok = !k || c.dataset.etapes.split(' ').includes(k); c.hidden = !ok; if (ok) n++; });
    vide.hidden = n > 0;
  };
  boutons.forEach((b) => b.addEventListener('click', () => filtrer(b.dataset.etape)));
  // Lien direct vers une fiche (/formations/#ancre) : on l'ouvre.
  const id = decodeURIComponent(location.hash.slice(1));
  const cible = id && document.getElementById(id);
  if (cible && cible.classList.contains('carte-f')) { cible.querySelector('details').open = true; cible.classList.add('ciblee'); }
})();
</script>
'''


def etapes_de(f):
    s = cle(f.get('texte', ''))
    etapes = [e[0] for e in ETAPES if any(m in s for m in e[2])]
    # Acquéreurs : les titres et objectifs QualiOF n'en parlent presque jamais, alors que le programme
    # détaillé y consacre des séquences. On retient la fiche à partir de 3 mentions dans le programme.
    corps = cle(f.get('corps', ''))
    if 'acquereurs' not in etapes and corps.count('acquereur') + corps.count('acheteur') >= SEUIL_ACQUEREURS:
        etapes.append('acquereurs')
        etapes.sort(key=[e[0] for e in ETAPES].index)
    return etapes or ['organisation']


def chiffres(ind):
    n = ind.get('apprenantsFormes') or 0
    sat = ind.get('satisfaction') or {}
    out = []
    if n:
        s = 's' if n > 1 else ''
        out.append(f'<div><strong>{n}</strong><span>apprenant{s} formé{s}</span></div>')
    if sat.get('note5') is not None:
        note = f'{sat["note5"]:.1f}'.replace('.', ',')
        out.append(f'<div><strong>{note}<small>/5</small></strong><span>satisfaction</span></div>')
    if sat.get('tauxRecommandation') is not None:
        k = sat.get('nbReponses') or 0
        avis = f' ({k} avis)' if k else ''
        out.append(f'<div><strong>{round(sat["tauxRecommandation"])}<small>&nbsp;%</small></strong><span>recommandent{avis}</span></div>')
    elif n:
        out.append('<div><strong class="neuf">Avis</strong><span>en cours de collecte</span></div>')
    return ''.join(out)


def niveau_de(f):
    """Niveau en IA d'une formation, classé par Claude à la demande de Jean-Guy (12 nov. 2026) :
    « avance » : suite d'une première formation (niveau 2, étape 2, Booster) ou prérequis métier ;
    « debutant » : format court d'entrée (16 h au plus) sans prérequis, niveau 1, ou public débutant ;
    « tous » : parcours long sans prérequis, qui part des bases et va jusqu'aux usages avancés.
    QualiOF ne porte pas ce niveau : il est déduit du titre, de la durée et du champ prérequis."""
    titre, pre = cle(h.unescape(f['titre'])), cle(h.unescape(f['prereq'])).strip()
    if re.search(r'niveau 2|etape 2|booster', titre):
        return 'avance'
    if 'niveau 1' in titre or 'debutant' in pre:
        return 'debutant'
    sans = pre.startswith('aucun') or 'connaissances de base' in pre
    if not sans:
        return 'avance'
    return 'debutant' if f['heures'] <= 16 else 'tous'


def profils_de(f):
    """Profils de visiteur (portes de l'accueil) auxquels le champ « public » fait écho. Texte libre : approximatif."""
    t = cle(h.unescape(f['public']))
    out = []
    if re.search(r'conseiller|agent|negociat|mandataire', t): out.append('conseiller')
    if re.search(r'responsable|manager|dirigeant|direct|gerant|chef d', t): out.append('agence')
    if re.search(r'mandataire|independant|agents commerciaux|agent commercial', t): out.append('reseau')
    return out


def carte(f, noms):
    lis = ''.join(f'<li>{h.escape(o)}</li>' for o in f['obj'])
    puces = ''.join(f'<li>{noms[k]}</li>' for k in f['etapes'])
    prog = f'<h4>Programme</h4><div class="programme">{f["programme"]}</div>' if f['programme'] else ''
    stats = chiffres(f['ind'])
    stats = f'<div class="cf-chiffres">{stats}</div>' if stats else ''
    av = ' data-a-valider' if f['av'] else ''
    fiche = (f'<a class="cf-fiche" href="/formations/{FICHES[f["id"]]}/">Voir la fiche complète</a>'
             if f['id'] in FICHES else '')
    return (f'''
    <article class="carte-f" id="{f['id']}" data-etapes="{' '.join(f['etapes'])}" data-heures="{f['heures']:g}" data-niveau="{niveau_de(f)}" data-profils="{' '.join(profils_de(f))}" data-appr="{f['ind'].get('apprenantsFormes') or 0}" data-immo="{int('immobili' in cle(h.unescape(f['titre'] + ' ' + f['public'])))}"{av}>
      <div class="cf-visuel"><img src="/img/cf-{f['visuel']}.webp" width="720" height="260" loading="lazy" alt="{h.escape(f['titre'], quote=True)}"><span class="cf-duree">{duree(f['heures'])}</span><span class="cf-prix">{prix(f['heures'])}</span></div>
      <ul class="cf-etapes" aria-label="Étapes du métier">{puces}</ul>
      <h3>{h.escape(f['titre'])}</h3>
      {stats}{fiche}
      <details class="cf-plus">
        <summary><span class="ouvrir">Voir les objectifs et le programme</span><span class="fermer">Masquer le détail</span></summary>
        <div class="cf-detail">
          <h4>Objectifs</h4><ul>{lis}</ul>
          {prog}
          <dl>
            <div><dt>Public</dt><dd>{f['public']}</dd></div>
            <div><dt>Prérequis</dt><dd>{f['prereq']}</dd></div>
            <div><dt>Durée</dt><dd>{duree(f['heures'])}</dd></div>
            <div><dt>Tarif</dt><dd>À partir de {prix(f['heures'])[4:]} ({TAUX_HORAIRE}&nbsp;€&nbsp;HT de l'heure), finançable OPCO, AGEFICE ou FIF PL</dd></div>
          </dl>
        </div>
      </details>
    </article>''')


def generer():
    fiches_toutes, source = catalogue()
    for f in fiches_toutes:
        f['etapes'] = etapes_de(f)
    # visuel de chaque carte : une image différente par formation, prise d'abord dans la réserve de
    # l'étape la plus spécifique (la plus rare) qu'elle couvre, puis dans la réserve commune.
    freq = {e[0]: sum(1 for f in fiches_toutes if e[0] in f['etapes']) for e in ETAPES}
    pris = set()
    for f in fiches_toutes:
        prefs = [v for k in sorted(f['etapes'], key=lambda k: freq[k]) for v in VISUELS[k]]
        libres = [v for v in prefs + [v for l in VISUELS.values() for v in l] if v not in pris]
        f['visuel'] = libres[0] if libres else VISUELS[f['etapes'][0]][0]
        pris.add(f['visuel'])
    ordre = {e[0]: i for i, e in enumerate(ETAPES)}
    fiches_toutes.sort(key=lambda f: (ordre[f['etapes'][0]], -(f['ind'].get('apprenantsFormes') or 0)))
    noms = {e[0]: e[1] for e in ETAPES}

    chaine = ''.join(
        f'<li><button type="button" data-etape="{k}" aria-pressed="false"><span class="ch-num">{i + 1}</span>{nom}'
        f'<span class="ch-nb">{sum(1 for f in fiches_toutes if k in f["etapes"])}</span></button></li>'
        for i, (k, nom, _) in enumerate(ETAPES))
    cartes = ''.join(carte(f, noms) for f in fiches_toutes)

    choix_etapes = ''.join(f'<label><input type="radio" name="t-etape" value="{k}"><span>{nom}</span></label>' for k, nom, _ in ETAPES)
    corps = (f'''  <section class="trouver" aria-labelledby="titre-trouver" hidden>
    <h2 id="titre-trouver">Trois questions, votre formation.</h2>
    <div class="trouver-scene">
      <div class="trouver-questions">
        <fieldset><legend>Vous êtes</legend><label><input type="radio" name="t-profil" value="conseiller"><span>Conseiller ou indépendant</span></label><label><input type="radio" name="t-profil" value="agence"><span>Directeur d'agence</span></label><label><input type="radio" name="t-profil" value="reseau"><span>Animateur de réseau</span></label></fieldset>
        <fieldset><legend>L'étape qui vous coûte le plus</legend>{choix_etapes}</fieldset>
        <fieldset><legend>Votre niveau en IA</legend><label><input type="radio" name="t-niveau" value="debutant"><span>Je débute</span></label><label><input type="radio" name="t-niveau" value="avance"><span>Je l'utilise déjà</span></label></fieldset>
      </div>
      <div class="trouver-resultat" aria-live="polite"><p class="trouver-attente">Répondez aux trois questions&nbsp;: une formation passe devant les autres.</p></div>
    </div>
  </section>
  <div class="chaine-f">
    <p class="cf-consigne">Choisissez une étape de votre métier&nbsp;: nous affichons les formations qui la travaillent.</p>
    <ol class="cf-chaine"><li><button type="button" data-etape="" aria-pressed="true">Toutes<span class="ch-nb">{len(fiches_toutes)}</span></button></li>{chaine}</ol>
  </div>
  <div class="grille-f">{cartes}
  </div>
  <p class="cf-vide" hidden>Aucune formation pour cette étape pour l'instant&nbsp;: <a href="{CAL}">parlons-en</a>, nous construisons le parcours avec vous.</p>
''' + COMMUNS + SCRIPT)

    page('formations/',
     'Catalogue des formations immobilier et IA | Start Academia',
     'Nos formations pour agents et agences immobilières, classées par étape du métier : prospection, estimation, mandat, acquéreurs, organisation. Avis et résultats.',
     'Nos formations.',
     f'{len(fiches_toutes)} formations construites sur les étapes de votre métier, avec les résultats de nos apprenants. Chacune peut être adaptée à votre agence et combinée dans un parcours sur mesure.',
     corps)

    # le wrapper .corps ajouté par page() ne doit pas s'appliquer ici
    p = racine / 'formations' / 'index.html'
    t = p.read_text()
    t = re.sub(r'<div class="corps">(.*?)</div>(\n  </div>)', r'\1\2', t, flags=re.S) if '<div class="corps">' in t else t
    t = t.replace('<section class="clair texte-page">', '<section class="clair texte-page page-catalogue">')
    p.write_text(t)
    print(len(fiches_toutes), 'formations (source :', source + '),', sum(1 for f in fiches_toutes if f['av']), 'à valider')


if __name__ == '__main__':
    generer()
