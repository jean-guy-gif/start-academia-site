"""Une page par formation stratégique : /formations/<slug>/.
Contenu factuel (titre, durée, public, prérequis, objectifs, programme, satisfaction) tiré de QualiOF,
via formations.catalogue() : il se met à jour à chaque synchronisation. Seuls l'accroche, le « pourquoi »,
les liens et la FAQ sont écrits ici. Liste des formations concernées : fiches_map.py.
À lancer après seo_pages.py (réutilise ses blocs Financement et Preuves)."""
import io, json, re, sys, pathlib, contextlib, datetime, html as h

OUTILS = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(OUTILS))
with contextlib.redirect_stdout(io.StringIO()):
    import formations as fo                       # catalogue(), duree(), prix(), TAUX_HORAIRE
from fiches_map import FICHES

_src = (OUTILS / 'seo_pages.py').read_text()
exec(_src[:_src.index("\necrire('")])            # page(), racine, CAL, PREUVES, FINANCEMENT, faq_html...

SITE = 'https://www.start-academia.fr'

TEXTES = {
 'formation-ia-conseillers-immobiliers-72h': dict(
  titre='Formation IA 72 h pour agents immobiliers | Start Academia',
  desc="9 jours pour passer du premier prompt à votre assistant IA, sur vos vrais dossiers : prospection, vendeurs, suivi, automatisations. Dès 3 024 €, Qualiopi.",
  intro="Notre parcours le plus complet. En 9 jours, vous passez des bases de ChatGPT aux automatisations et à votre propre assistant IA, toujours sur vos dossiers.",
  pourquoi='''<p>Une journée d'initiation donne des idées&nbsp;; elle change rarement les habitudes. Ce parcours est construit pour que l'IA entre <strong>dans chaque étape de votre semaine</strong>&nbsp;: prospection, préparation du rendez-vous vendeur, suivi, annonces et marketing, puis automatisation des tâches répétitives.</p>
    <p>Chaque journée se termine par un atelier sur vos propres dossiers. À la fin, chaque conseiller repart avec ses prompts, ses modèles, son assistant IA et un plan d'action individuel.</p>
    <p><strong>Financement&nbsp;:</strong> à 42&nbsp;€ de l'heure en présentiel, l'enveloppe AGEFICE de 3&nbsp;000&nbsp;€ couvre presque tout le parcours (3&nbsp;024&nbsp;€)&nbsp;: il reste 24&nbsp;€ à votre charge. <a class="lien-texte" href="/financement-formation-auto-entrepreneur/">Vérifier vos droits</a></p>''',
  liens=[('/formation-ia-immobilier/', "Toutes nos formations IA pour l'immobilier"),
         ('/formation-chatgpt-immobilier/', 'Formation ChatGPT immobilier'),
         ('/prospection-immobiliere-sans-pige/', 'Guide : prospecter sans pige'),
         ('/formations/formation-ia-conseillers-immobiliers-16h/', 'La version en 2 jours (16 h)'),
         ('/financement-formation-auto-entrepreneur/', 'Auto-entrepreneur : 3 000 € de formation')],
  faq=[("Faut-il des connaissances techniques&nbsp;?", "Non. Aucune compétence technique n'est nécessaire : le parcours commence par la création et le réglage de votre compte ChatGPT."),
       ("Combien coûte la formation de 72 heures&nbsp;?", "À partir de 3 024 € (42 € de l'heure). Elle est finançable par l'OPCO de l'agence, par l'AGEFICE (jusqu'à 3 000 € par an) ou par le FIF PL."),
       ("Où se déroule-t-elle&nbsp;?", "Dans votre agence, dans les Alpes-Maritimes et alentours, ou à distance, en individuel ou en groupe."),
       ("Existe-t-il une version plus courte&nbsp;?", "Oui. La même formation existe en 16 heures et en 8 heures, pour découvrir les usages essentiels avant d'aller plus loin.")]),

 'formation-tracfin-immobilier': dict(
  titre='Formation TRACFIN immobilier en 4 h | Start Academia',
  desc="Formation TRACFIN pour agents immobiliers : obligations de vigilance, signaux d'alerte, déclaration de soupçon sur ERMES, jeux de rôle. 4 h, certifié Qualiopi.",
  intro="Lutte contre le blanchiment&nbsp;: savoir repérer un dossier à risque et savoir quoi faire. 4 heures, dont la moitié en mises en situation sur des dossiers clients complets.",
  pourquoi='''<p>Les professionnels de l'immobilier sont soumis aux obligations de lutte contre le blanchiment de capitaux et le financement du terrorisme (LCB-FT)&nbsp;: connaître son client, être vigilant sur l'origine des fonds, déclarer ses soupçons à TRACFIN. Encore faut-il savoir reconnaître une situation anormale au milieu d'une transaction.</p>
    <p>La formation alterne <strong>2 heures d'apports</strong> (rôle de TRACFIN, obligations, signaux d'alerte) et <strong>2 heures de jeux de rôle</strong>&nbsp;: chaque équipe analyse un dossier client fictif complet et décide de la suite à donner. Vos équipes repartent avec des fiches-outils&nbsp;: cartographie des risques, modèle de fiche client, check-list de contrôle.</p>
    <p>Elle se combine souvent avec notre <a class="lien-texte" href="/formations/formation-non-discrimination-deontologie-tracfin/">formation non-discrimination, TRACFIN et déontologie</a> (8&nbsp;h) pour la formation continue loi ALUR.</p>''',
  liens=[('/formation-loi-alur/', 'Formation continue loi ALUR'),
         ('/formations/formation-non-discrimination-deontologie-tracfin/', 'Non-discrimination, TRACFIN et déontologie (8 h)'),
         ('/financement-formation-immobilier/', 'Financement : calculer mes droits')],
  faq=[("Qui doit être formé à TRACFIN&nbsp;?", "Les agents immobiliers et leurs collaborateurs qui participent aux transactions : négociateurs salariés, agents commerciaux, assistants."),
       ("La formation compte-t-elle pour la loi ALUR&nbsp;?", "Oui. Elle entre dans la formation continue obligatoire des professionnels de l'immobilier, avec une attestation remise en fin de formation."),
       ("Combien coûte-t-elle&nbsp;?", "À partir de 168 € (42 € de l'heure), finançable par l'OPCO de l'agence, l'AGEFICE ou le FIF PL."),
       ("Comment se déroule-t-elle&nbsp;?", "Deux heures d'apports sur le rôle de TRACFIN, les obligations et les signaux d'alerte, puis deux heures de mises en situation par équipes sur des dossiers clients fictifs.")]),
}

TEXTES.update({
 'formation-ia-conseillers-immobiliers-16h': dict(
  titre='Formation IA 16 h pour agents immobiliers | Start Academia',
  desc="2 jours pour maîtriser ChatGPT, Gamma et les données DVF sur vos dossiers : prospection, relation vendeur, plan d'action. Dès 672 €, certifié Qualiopi.",
  intro="Deux jours pour mettre l'IA au travail sur vos dossiers&nbsp;: prospection, présentation vendeur, suivi.",
  pourquoi='''<p>Le bon format pour une équipe qui veut des résultats sans bloquer l'agence une semaine. Jour 1&nbsp;: ChatGPT bien réglé (mémoire, projets par dossier, commandes personnalisées), puis les présentations vendeur avec Gamma. Jour 2&nbsp;: la prospection à partir des données DVF et la relation vendeur.</p>
    <p>Chaque séquence se termine par un atelier sur vos propres dossiers, et chacun repart avec son plan d'action pour intégrer l'IA dans sa semaine.</p>''',
  liens=[('/formations/formation-ia-conseillers-immobiliers-72h/', 'Le parcours complet en 72 h'),
         ('/formations/formation-ia-conseillers-immobiliers-8h/', 'La version en 1 jour'),
         ('/formation-chatgpt-immobilier/', 'Formation ChatGPT immobilier'),
         ('/ia-prospection-immobiliere/', 'Guide : prospecter avec l\'IA')],
  faq=[("Faut-il déjà utiliser ChatGPT&nbsp;?", "Non. Aucune connaissance préalable en intelligence artificielle n'est requise : la formation commence par la création et le réglage du compte."),
       ("Combien coûte la formation de 16 heures&nbsp;?", "À partir de 672 € (42 € de l'heure), finançable par l'OPCO de l'agence, l'AGEFICE ou le FIF PL."),
       ("Quelle différence avec la version de 72 heures&nbsp;?", "La version de 16 heures couvre les usages essentiels. Le parcours de 72 heures va jusqu'aux automatisations et à la création de votre propre assistant IA.")]),

 'formation-ia-conseillers-immobiliers-8h': dict(
  titre='Formation IA immobilier en 1 jour (8 h) | Start Academia',
  desc="Une journée pour démarrer avec ChatGPT : prompts, prospection avec les données DVF, relation vendeur, plan d'action. Dès 336 €, certifié Qualiopi.",
  intro="Une journée pour démarrer avec l'IA sur des cas concrets&nbsp;: prospection le matin, relation vendeur l'après-midi, et un plan d'action pour la suite.",
  pourquoi='''<p>Pour un conseiller ou une équipe qui n'a jamais utilisé l'IA, ou seulement par curiosité. Le matin&nbsp;: ChatGPT bien paramétré, les règles d'un bon prompt, puis l'analyse d'un secteur avec les données DVF et la rédaction de courriers. L'après-midi&nbsp;: la relation vendeur, de la préparation du rendez-vous au suivi.</p>
    <p>À la fin de la journée, chacun sait quoi faire de l'IA lundi matin. Pour aller plus loin, la version de 16 heures ajoute Gamma et les projets ChatGPT par dossier.</p>''',
  liens=[('/formations/formation-ia-conseillers-immobiliers-16h/', 'La version en 2 jours (16 h)'),
         ('/formations/formation-ia-conseillers-immobiliers-72h/', 'Le parcours complet en 72 h'),
         ('/formation-ia-immobilier/', "Toutes nos formations IA pour l'immobilier")],
  faq=[("Une journée suffit-elle pour utiliser l'IA&nbsp;?", "Pour démarrer, oui : vous repartez avec vos premiers prompts et un plan d'action. Pour ancrer les usages dans toute votre activité, la version de 16 heures ou le parcours de 72 heures vont plus loin."),
       ("Combien coûte la formation d'une journée&nbsp;?", "À partir de 336 € (42 € de l'heure), finançable par l'OPCO de l'agence, l'AGEFICE ou le FIF PL."),
       ("Peut-on la faire dans l'agence&nbsp;?", "Oui. Nous venons dans votre agence, dans les Alpes-Maritimes et alentours, ou nous la faisons à distance.")]),

 'formation-non-discrimination-deontologie-tracfin': dict(
  titre='Formation déontologie et non-discrimination immobilier',
  desc="Formation obligatoire loi ALUR en 8 h : non-discrimination dans l'accès au logement, déontologie et TRACFIN, avec cas pratiques. Dès 336 €, Qualiopi.",
  intro="Les trois thèmes réglementaires en une journée&nbsp;: non-discrimination dans l'accès au logement, déontologie et lutte contre le blanchiment, avec des cas pratiques.",
  pourquoi='''<p>La formation continue loi ALUR impose des heures de <strong>déontologie</strong> et de <strong>non-discrimination dans l'accès au logement</strong>. Cette journée les traite ensemble, avec en plus le module TRACFIN&nbsp;: un seul jour pour être à jour sur les trois sujets réglementaires.</p>
    <p>Le format est concret&nbsp;: critères de sélection objectifs, grilles d'évaluation, simulation d'une sélection non discriminante, étude de cas de blanchiment. Une attestation est remise à chaque participant.</p>''',
  liens=[('/formations/formation-tracfin-immobilier/', 'Formation TRACFIN seule (4 h)'),
         ('/formation-loi-alur/', 'Formation continue loi ALUR'),
         ('/financement-formation-immobilier/', 'Financement : calculer mes droits')],
  faq=[("Cette formation compte-t-elle pour la loi ALUR&nbsp;?", "Oui. Elle couvre la déontologie et la non-discrimination exigées dans la formation continue des professionnels de l'immobilier, avec attestation."),
       ("Combien coûte-t-elle&nbsp;?", "À partir de 336 € (42 € de l'heure), finançable par l'OPCO de l'agence, l'AGEFICE ou le FIF PL."),
       ("Peut-on former toute l'agence le même jour&nbsp;?", "Oui. La formation se fait en groupe dans votre agence ou à distance, et chacun reçoit son attestation.")]),

 'formation-cadastre-com': dict(
  titre='Formation Cadastre.com niveau 1 | Start Academia',
  desc="Une journée pour maîtriser Cadastre.com : recherche foncière, prospection ciblée, valeurs foncières, suivi des mandats et des prix. Dès 336 €, Qualiopi.",
  intro="Une journée pour tirer tout le parti de Cadastre.com&nbsp;: recherche de biens, prospection ciblée, analyse des valeurs foncières et suivi de vos mandats.",
  pourquoi='''<p>Beaucoup d'agences ont un abonnement Cadastre.com et n'en utilisent qu'une petite partie. Cette formation part de l'interface et va jusqu'aux usages qui rentrent des mandats&nbsp;: cibler des biens par localisation et caractéristiques, exploiter les valeurs foncières pour une analyse comparative, suivre ses mandats et ajuster les prix.</p>
    <p>La journée alterne démonstrations et exercices sur votre secteur. Un niveau 2 existe pour les utilisateurs confirmés.</p>''',
  liens=[('/ia-prospection-immobiliere/', 'Guide : prospecter avec l\'IA'),
         ('/ia-estimation-immobiliere/', 'Guide : estimer avec l\'IA'),
         ('/formations/', 'Toutes nos formations')],
  faq=[("Faut-il déjà avoir un compte Cadastre.com&nbsp;?", "Il faut des connaissances de base des outils numériques et du métier. L'accès à l'outil pendant la formation se prépare avec vous lors de l'appel découverte."),
       ("Combien coûte la formation&nbsp;?", "À partir de 336 € (42 € de l'heure), finançable par l'OPCO de l'agence, l'AGEFICE ou le FIF PL."),
       ("Existe-t-il un niveau avancé&nbsp;?", "Oui, un niveau 2 pour les professionnels qui utilisent déjà Cadastre.com au quotidien.")]),

 'formation-prospection-negociation-immobiliere': dict(
  titre='Formation prospection et négociation immobilière (87 h)',
  desc="Parcours complet de 87 h : prospection et leads vendeurs, base de données, outils numériques, techniques de vente, négociation, réseaux sociaux. Qualiopi.",
  intro="Le parcours métier complet, de la prospection à la négociation&nbsp;: leads vendeurs, base de prospects, outils numériques, relation client, vente et réseaux sociaux.",
  pourquoi='''<p>Pour un conseiller qui démarre ou qui veut reconstruire sa méthode de A à Z. Le parcours suit la chaîne du métier&nbsp;: segmenter son secteur, trouver et traiter les leads vendeurs, entretenir sa base de prospects, communiquer en ligne, puis mener le rendez-vous, vendre et négocier.</p>
    <p>Chaque journée combine apports, mises en situation et débriefing avec axes d'amélioration. Depuis le 11 août 2026, la prospection se fait sans démarchage téléphonique à froid&nbsp;: les méthodes enseignées en tiennent compte.</p>''',
  liens=[('/prospection-immobiliere-sans-pige/', 'Guide : prospecter sans pige'),
         ('/ia-negociation-immobiliere/', 'Guide : négocier une offre avec l\'IA'),
         ('/formations/formation-mandat-exclusif-pilotage/', 'Mandat exclusif et pilotage (11 h)')],
  faq=[("Ce parcours convient-il à un débutant&nbsp;?", "Oui. Il s'adresse aux conseillers débutants comme confirmés, et aux responsables d'agence qui veulent développer leur notoriété."),
       ("Combien coûte le parcours de 87 heures&nbsp;?", "À partir de 3 654 € (42 € de l'heure). Il est finançable par l'OPCO de l'agence, l'AGEFICE ou le FIF PL, dans la limite de leurs plafonds."),
       ("Peut-on suivre seulement une partie&nbsp;?", "Oui. Chaque bloc existe aussi en formation courte : prospection, relation vendeur, négociation. Nous construisons le parcours avec vous lors de l'appel découverte.")]),

 'formation-ia-suivi-vendeur-annonces': dict(
  titre='Formation IA : suivi vendeur et annonces | Start Academia',
  desc="Une journée pour vendre mieux avec l'IA : suivi vendeur automatisé, annonces qui se démarquent, photos retouchées, reporting professionnel. Dès 336 €.",
  intro="Une journée sur ce que le vendeur voit de votre travail&nbsp;: un suivi régulier et professionnel, des annonces qui se démarquent et des visuels soignés, avec l'IA.",
  pourquoi='''<p>Le vendeur juge votre travail sur trois choses&nbsp;: la qualité de l'annonce, l'allure des photos et la régularité des nouvelles. Cette journée les traite une par une. Le matin&nbsp;: un suivi vendeur hebdomadaire rédigé avec ChatGPT et des modèles de rapport. Puis l'annonce, en plusieurs styles à partir d'un même bien. L'après-midi&nbsp;: la retouche des visuels avec des outils simples et le reporting automatisé.</p>
    <p>Résultat attendu&nbsp;: moins de vendeurs qui se plaignent de ne pas avoir de nouvelles, et des baisses de prix plus faciles à obtenir.</p>''',
  liens=[('/ia-annonce-immobiliere/', "Guide : rédiger une annonce avec l'IA"),
         ('/ia-mandat-exclusif/', 'Guide : rentrer un mandat exclusif'),
         ('/formations/formation-ia-conseillers-immobiliers-16h/', 'Formation IA en 16 h')],
  faq=[("Faut-il savoir retoucher des photos&nbsp;?", "Non. Les outils IA utilisés sont simples et pris en main pendant la formation."),
       ("Les annonces générées respectent-elles les mentions obligatoires&nbsp;?", "C'est au conseiller de les vérifier avant publication : prix, honoraires, DPE et mentions obligatoires. L'IA rédige, vous relisez."),
       ("Combien coûte la formation&nbsp;?", "À partir de 336 € (42 € de l'heure), finançable par l'OPCO de l'agence, l'AGEFICE ou le FIF PL.")]),

 'formation-anglais-immobilier-ia': dict(
  titre="Formation anglais immobilier boostée par l'IA (21 h)",
  desc="3 jours pour gagner en aisance en anglais avec les clients étrangers : vocabulaire métier, e-mails, échanges oraux, entraînement avec l'IA. Dès 882 €.",
  intro="Trois jours pour accueillir et suivre vos clients étrangers en anglais, avec l'IA comme partenaire d'entraînement entre les séances.",
  pourquoi='''<p>Sur la Côte d'Azur, de nombreux acquéreurs sont étrangers. Cette formation en petit groupe (5 personnes au maximum) consolide les bases, le vocabulaire du métier et l'écrit professionnel, puis met chacun en situation à l'oral.</p>
    <p>L'IA sert à s'entraîner&nbsp;: dialogues, quiz et simulations créés sur mesure avec ChatGPT, correcteurs et traducteurs pour vérifier ses e-mails. Chacun repart avec ses outils d'entraînement.</p>''',
  liens=[('/formation-ia-nice/', 'Formation IA à Nice'),
         ('/formation-chatgpt-immobilier/', 'Formation ChatGPT immobilier'),
         ('/formations/', 'Toutes nos formations')],
  faq=[("Quel niveau faut-il&nbsp;?", "Débutant à intermédiaire. La formation consolide les bases avant les mises en situation."),
       ("Combien coûte la formation de 21 heures&nbsp;?", "À partir de 882 € (42 € de l'heure), finançable par l'OPCO de l'entreprise, l'AGEFICE ou le FIF PL."),
       ("Combien de participants par session&nbsp;?", "Cinq au maximum, pour que chacun pratique l'oral.")]),

 'formation-mandat-exclusif-pilotage': dict(
  titre="Formation mandat exclusif et pilotage d'activité (11 h)",
  desc="1,5 jour pour piloter son activité avec ses chiffres et rentrer des exclusivités : rendez-vous d'estimation, honoraires, objections, suivi. Dès 462 €.",
  intro="Une journée et demie pour piloter votre activité à partir de vos propres chiffres et rentrer plus de mandats exclusifs, honoraires défendus.",
  pourquoi='''<p>«&nbsp;Du surfeur au pilote&nbsp;»&nbsp;: arrêter de subir les vagues du marché pour piloter son activité. Chaque participant vient avec ses chiffres des 12 derniers mois (estimations, mandats, exclusivités, ventes)&nbsp;; ils servent de matière dès le premier atelier.</p>
    <p>Le premier jour consolide le pilotage&nbsp;: objectifs, priorités, organisation de la semaine. Le second suit la route de l'exclusivité&nbsp;: préparer et conduire le rendez-vous d'estimation, annoncer un prix argumenté, présenter le mandat exclusif et ses honoraires, traiter les objections, puis suivre jusqu'à la signature. En groupe restreint de 9 à 10 conseillers.</p>''',
  liens=[('/ia-mandat-exclusif/', 'Guide : rentrer un mandat exclusif'),
         ('/ia-estimation-immobiliere/', "Guide : estimer avec l'IA"),
         ('/formation-ia-directeur-agence-immobiliere/', "Formation IA pour directeurs d'agence")],
  faq=[("Faut-il avoir suivi l'étape 1&nbsp;?", "C'est un plus mais ce n'est pas obligatoire : les notions de base sont reprises la première demi-journée."),
       ("Que faut-il apporter&nbsp;?", "Vos chiffres d'activité des 12 derniers mois : estimations, mandats, exclusivités et ventes."),
       ("Combien coûte la formation&nbsp;?", "À partir de 462 € (42 € de l'heure), finançable par l'AGEFICE, le FIF PL ou l'OPCO.")]),
})


def objectifs_propres(obj):
    """Objectifs QualiOF nettoyés : sans phrase d'introduction, sans puce, sans doublon, lignes coupées recollées."""
    out = []
    for o in obj:
        s = re.sub(r'^[●•\-–\s]+', '', str(o)).strip()
        if not s or s.endswith(':'):
            continue
        if out and s[0].islower():
            out[-1] = out[-1] + ' ' + s
            continue
        if s not in out:
            out.append(s)
    return out


def euros(hh):
    return f'{round(hh * fo.TAUX_HORAIRE):,}'.replace(',', ' ') + '&nbsp;€'


def jsonld(chemin, f, t, faq):
    url = f'{SITE}/{chemin}'
    heures = f'PT{int(round(f["heures"]))}H'
    desc = h.unescape(re.sub('<[^>]+>', '', t['intro'])).replace('\xa0', ' ')
    graph = [
        {"@type": "WebPage", "@id": url, "url": url, "name": f['titre'], "description": t['desc'], "inLanguage": "fr-FR",
         "isPartOf": {"@id": f"{SITE}/#site"}, "about": {"@id": f"{SITE}/#organisation"}},
        {"@type": "Course", "name": f['titre'], "description": desc, "url": url, "inLanguage": "fr",
         "provider": {"@id": f"{SITE}/#organisation"}, "timeRequired": heures,
         "teaches": [o.rstrip('.;') for o in objectifs_propres(f['obj'])],
         "hasCourseInstance": [{"@type": "CourseInstance", "courseMode": "Onsite", "courseWorkload": heures, "location": "Alpes-Maritimes, France"},
                               {"@type": "CourseInstance", "courseMode": "Online", "courseWorkload": heures}],
         "offers": {"@type": "Offer", "category": "Paid", "price": round(f['heures'] * fo.TAUX_HORAIRE), "priceCurrency": "EUR",
                    "availability": "https://schema.org/InStock"}},
        {"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": h.unescape(q).replace('\xa0', ' '),
             "acceptedAnswer": {"@type": "Answer", "text": h.unescape(r).replace('\xa0', ' ')}} for q, r in faq]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Accueil", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Formations", "item": f"{SITE}/formations/"},
            {"@type": "ListItem", "position": 3, "name": f['titre'], "item": url}]},
    ]
    return '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False) + '</script>'


def generer():
    fiches = {f['id']: f for f in fo.catalogue()[0]}
    faites = []
    for ident, slug in FICHES.items():
        f, t = fiches.get(ident), TEXTES.get(slug)
        if not f or not t:
            print(f'fiches : {ident} absente de QualiOF ou sans texte, page non générée', file=sys.stderr)
            continue
        chemin = f'formations/{slug}/'
        objectifs = ''.join(f'<li>{h.escape(o)}</li>' for o in objectifs_propres(f['obj']))
        programme = f'''
  <div class="bloc">
    <h2>Programme détaillé</h2>
    <div class="programme">{f['programme']}</div>
  </div>''' if f['programme'] else ''
        satisfaction = f'<li><strong>Résultats&nbsp;:</strong> {f["indicateurs"]}</li>' if f['indicateurs'] else ''
        liens = ''.join(f'<li><a class="lien-texte" href="{u}">{x}</a></li>' for u, x in t['liens'])
        corps = f'''  <div class="bloc">
    <h2>En bref</h2>
    <ul class="points">
      <li><strong>Durée&nbsp;:</strong> {fo.duree(f['heures'])}</li>
      <li><strong>Public&nbsp;:</strong> {f['public']}</li>
      <li><strong>Prérequis&nbsp;:</strong> {f['prereq']}</li>
      <li><strong>Format&nbsp;:</strong> dans votre agence (Alpes-Maritimes et alentours) ou à distance, en individuel ou en groupe.</li>
      <li><strong>Tarif&nbsp;:</strong> à partir de {euros(f['heures'])} ({fo.TAUX_HORAIRE}&nbsp;€ de l'heure), finançable OPCO, AGEFICE ou FIF PL. Non éligible au CPF à ce jour.</li>
      {satisfaction}
    </ul>
  </div>
  <div class="bloc">
    <h2>Pourquoi cette formation</h2>
    {t['pourquoi']}
  </div>
  <div class="bloc">
    <h2>Objectifs</h2>
    <ul class="points">{objectifs}</ul>
  </div>{programme}
  <div class="bloc">
    <h2>Pour aller plus loin</h2>
    <ul class="points">{liens}</ul>
  </div>
''' + FINANCEMENT + '\n' + PREUVES + '\n' + faq_html(t['faq'])
        page(chemin, t['titre'], t['desc'], h.escape(f['titre']) + '.', t['intro'], corps)
        p = racine / chemin / 'index.html'
        html = p.read_text()
        html = html.replace('<a href="/">Accueil</a> <span aria-hidden="true">/</span> ',
                            '<a href="/">Accueil</a> <span aria-hidden="true">/</span> <a href="/formations/">Formations</a> <span aria-hidden="true">/</span> ', 1)
        html = html.replace('</head>', jsonld(chemin, f, t, t['faq']) + '\n</head>', 1)
        p.write_text(html)
        faites.append(chemin)
        print(chemin, len(t['titre']), 'car. titre /', len(t['desc']), 'car. description')

    # plan du site : une ligne par fiche
    s = racine / 'sitemap.xml'
    x = s.read_text()
    for chemin in faites:
        loc = f'<loc>{SITE}/{chemin}</loc>'
        if loc not in x:
            x = x.replace('</urlset>', f'  <url>{loc}<lastmod>{datetime.date.today().isoformat()}</lastmod></url>\n</urlset>')
    s.write_text(x)


if __name__ == '__main__':
    generer()
