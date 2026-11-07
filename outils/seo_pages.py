"""Pages SEO prioritaires (audit du 6 nov. 2026) : une page par recherche commerciale.
Chaque page : H1 descriptif, programme, outils, public, financement, preuves, FAQ (+ données structurées)."""
import pathlib, json, html as h, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from simulateur_html import SIMULATEUR
src = (pathlib.Path(__file__).resolve().parent / 'pages.py').read_text()
exec(src[:src.index("\npage('")])

SITE = 'https://www.start-academia.fr'

def faq_html(faq):
    items = ''.join(f'\n      <details><summary>{q}</summary><p>{r}</p></details>' for q, r in faq)
    return f'''  <div class="bloc">
    <h2>Questions fréquentes</h2>
    <div class="faq-liste">{items}
    </div>
  </div>'''

def jsonld(chemin, titre_page, desc, faq, cours=None):
    graph = [
        {"@type": "WebPage", "@id": f"{SITE}/{chemin}", "url": f"{SITE}/{chemin}", "name": titre_page,
         "description": desc, "inLanguage": "fr-FR", "isPartOf": {"@id": f"{SITE}/#site"},
         "about": {"@id": f"{SITE}/#organisation"}},
        {"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": h.unescape(q).replace(' ', ' '),
             "acceptedAnswer": {"@type": "Answer", "text": h.unescape(r).replace(' ', ' ')}} for q, r in faq]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Accueil", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": titre_page, "item": f"{SITE}/{chemin}"}]},
    ]
    if cours:
        graph.append({"@type": "Course", "name": cours[0], "description": cours[1],
                      "provider": {"@id": f"{SITE}/#organisation"}, "inLanguage": "fr",
                      "hasCourseInstance": [{"@type": "CourseInstance", "courseMode": m,
                                             "location": "Alpes-Maritimes, France" if m == "Onsite" else None} for m in ("Onsite", "Online")],
                      "offers": {"@type": "Offer", "category": "Sur devis", "availability": "https://schema.org/InStock"}})
        for ci in graph[-1]["hasCourseInstance"]:
            if ci["location"] is None: del ci["location"]
    return '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False) + '</script>'

def ecrire(chemin, titre, desc, h1, intro, corps, faq, cours=None):
    page(chemin, titre, desc, h1, intro, corps + '\n' + faq_html(faq))
    p = racine / chemin / 'index.html'
    t = p.read_text()
    t = t.replace('</head>', jsonld(chemin, h.unescape(h1).rstrip('.'), desc, faq, cours) + '\n</head>', 1)
    p.write_text(t)
    print(chemin, len(titre), 'car. titre /', len(desc), 'car. description')

PREUVES = '''  <div class="bloc">
    <h2>Pourquoi Start Academia</h2>
    <ul class="points">
      <li><strong>Des formateurs du métier.</strong> Jean-Guy Ourmières et Laurent Marx ont plus de 10 ans de transaction et accompagnent encore des agences au quotidien.</li>
      <li><strong>Nos propres outils.</strong> Dossier d'adresse (Mon Secteur), Profiling, Localisateur, ACM&nbsp;: vos équipes repartent avec des outils prêts à servir.</li>
      <li><strong>Des preuves.</strong> 420 agents et collaborateurs formés, 225 avis Google notés 5 étoiles, des agences comme Laforêt, Nestenn, Century 21 ou Orpi parmi nos clients.</li>
      <li><strong>Certifié Qualiopi</strong> au titre des actions de formation. <a class="lien-texte" href="/documents/certificat-qualiopi.pdf">Voir le certificat</a></li>
    </ul>
  </div>'''

FINANCEMENT = '''  <div class="bloc">
    <h2>Financement et heures loi ALUR</h2>
    <p>Votre formation peut être prise en charge par votre <strong>OPCO</strong> (agences et salariés) ou par votre <strong>fonds d'assurance formation</strong>, comme l'AGEFICE ou le FIF PL (indépendants et mandataires). Nous montons le dossier avec vous. Nos formations ne sont pas éligibles au CPF à ce jour. <a class="lien-texte" href="/financement-formation-immobilier/#simulateur-financement">Calculer mes droits à la formation</a></p>
    <p>Les heures suivies comptent dans vos <strong>14 heures annuelles de formation continue</strong> exigées par la loi ALUR, avec attestation. <a class="lien-texte" href="/formation-loi-alur/">En savoir plus sur la loi ALUR</a></p>
  </div>'''

# ---------------------------------------------------------------- 1. Formation IA immobilier
ecrire('formation-ia-immobilier/',
 'Formation IA immobilier : agents et agences | Start Academia',
 "Formation à l'IA et à ChatGPT pour agents immobiliers, mandataires et agences : prospection, estimation, mandat, suivi vendeur. Côte d'Azur ou à distance.",
 "Formation IA pour les professionnels de l'immobilier.",
 "Prospection, estimation, mandat, découverte, visite, négociation, suivi&nbsp;: on part des gestes de votre métier et on les rend plus rapides avec l'IA. Une formation pratique, sur vos propres dossiers, certifiée Qualiopi.",
 '''  <div class="bloc">
    <h2>Ce que vos équipes savent faire en sortant</h2>
    <ul class="points">
      <li><strong>Préparer un premier rendez-vous vendeur</strong> avec le dossier de marché de l'adresse&nbsp;: ventes réelles autour du bien, dynamique des prix, vie du quartier. Environ 2&nbsp;h de préparation ramenées à quelques minutes.</li>
      <li><strong>Prospecter avec méthode</strong>&nbsp;: cibler un secteur, repérer les logements concernés par la réforme du DPE, écrire des messages et des scripts d'appel personnalisés.</li>
      <li><strong>Rédiger annonces, comptes rendus et relances</strong> en respectant les mentions obligatoires (loi Hoguet, DPE) et le RGPD.</li>
      <li><strong>Défendre un prix</strong> avec une analyse comparative claire, comparable par comparable.</li>
      <li><strong>Suivre vendeurs et acquéreurs</strong> sans y passer ses soirées&nbsp;: bilans de commercialisation, relances, rapprochements.</li>
    </ul>
    <p>En moyenne, nos apprenants déclarent gagner 8&nbsp;heures par semaine.</p>
  </div>
  <div class="bloc">
    <h2>Les outils utilisés</h2>
    <p>Nous choisissons l'outil le plus simple pour chaque tâche, et nous disons pourquoi&nbsp;: <strong>ChatGPT, Claude, Gemini, NotebookLM et Gamma</strong>, et nos outils maison conçus par des agents pour des agents. <a class="lien-texte" href="/#outils">Découvrir nos outils</a></p>
  </div>
  <div class="bloc">
    <h2>Format, durée et niveau</h2>
    <ul class="points">
      <li><strong>Modules courts</strong>, de 1 à 4&nbsp;heures par outil ou par usage (ChatGPT, Claude, NotebookLM, rédaction de prompts, génération de contenus, DPE…), combinés selon vos besoins.</li>
      <li><strong>Parcours complet</strong> «&nbsp;Intégrer l'intelligence artificielle pour gagner en productivité&nbsp;» pour les équipes qui veulent aller plus loin.</li>
      <li><strong>Version débutant ou avancée</strong>, avec un livret tactique pour chaque méthode.</li>
      <li><strong>En agence</strong> sur la Côte d'Azur, <strong>ou à distance</strong> partout en France, en individuel ou en groupe.</li>
    </ul>
    <p><a class="lien-texte" href="/formations/">Voir le détail des 40 formations</a></p>
  </div>
  <div class="bloc">
    <h2>Pour qui</h2>
    <p>Agents immobiliers, négociateurs, mandataires et agents commerciaux en réseau, collaborateurs, directeurs et managers d'agence. Pour les réseaux, nous déployons la formation auprès de tous vos mandataires.</p>
  </div>
''' + FINANCEMENT + '\n' + PREUVES,
 [("Faut-il savoir utiliser l'IA avant la formation&nbsp;?", "Non. Chaque parcours existe en version débutant et en version avancée. On part de vos dossiers et de votre niveau, pas d'une liste de fonctionnalités."),
  ("Combien coûte une formation IA immobilier&nbsp;?", "La formation est construite sur mesure, le tarif est donc établi sur devis après l'appel découverte. Elle peut être prise en charge par votre OPCO, l'AGEFICE ou le FIF PL."),
  ("Est-ce que la formation compte pour la loi ALUR&nbsp;?", "Oui, les heures suivies comptent dans vos 14 heures annuelles de formation continue, avec une attestation remise à chaque participant."),
  ("Où se déroule la formation&nbsp;?", "Dans votre agence sur la Côte d'Azur (Nice, Antibes, Cannes, Cagnes-sur-Mer…) ou à distance, partout en France."),
  ("Les données de mes clients sont-elles protégées&nbsp;?", "Nous enseignons les bonnes pratiques RGPD : ce qu'on peut confier à une IA, ce qu'on anonymise, et quels réglages activer.")],
 ("Formation IA pour les professionnels de l'immobilier", "Utiliser l'IA et ChatGPT à chaque étape de la transaction immobilière : prospection, estimation, mandat, suivi vendeur et acquéreur."))

# ---------------------------------------------------------------- 2. Formation ChatGPT immobilier
ecrire('formation-chatgpt-immobilier/',
 'Formation ChatGPT pour agents immobiliers | Start Academia',
 "Formation ChatGPT pour agents immobiliers et agences : prompts métier, annonces conformes, prospection, comptes rendus et relances. Certifié Qualiopi.",
 "Formation ChatGPT pour les agents immobiliers.",
 "Apprenez à faire travailler ChatGPT sur votre quotidien d'agent&nbsp;: annonces, scripts de prospection, préparation de rendez-vous, comptes rendus et relances. Avec des prompts prêts à l'emploi pour votre métier.",
 '''  <div class="bloc">
    <h2>Le programme</h2>
    <ol class="points numerotes">
      <li><strong>Les bases utiles.</strong> Comment ChatGPT raisonne, ce qu'il fait bien, ce qu'il invente, et comment le vérifier.</li>
      <li><strong>Le prompt métier.</strong> La structure Rôle, Contexte, Tâche, Format appliquée à l'immobilier, avec vos propres exemples.</li>
      <li><strong>Annonces et descriptifs.</strong> Des textes qui donnent envie, avec les mentions obligatoires (honoraires, DPE, copropriété).</li>
      <li><strong>Prospection.</strong> Courriers, messages et scripts d'appel personnalisés selon le secteur et le profil du propriétaire.</li>
      <li><strong>Rendez-vous et suivi.</strong> Préparer un premier rendez-vous vendeur, rédiger un compte rendu de visite, relancer au bon moment.</li>
      <li><strong>Aller plus loin.</strong> Créer ses assistants personnalisés (GPTs) pour les tâches qui reviennent chaque semaine.</li>
    </ol>
  </div>
  <div class="bloc">
    <h2>Un exemple de ce que vous repartez avec</h2>
    <p class="preuve-texte">«&nbsp;Tu es un agent immobilier expérimenté sur [ville]. Contexte&nbsp;: [type de bien, surface, points forts, DPE]. Tâche&nbsp;: rédige une annonce de 120 mots qui donne envie de visiter, sans superlatifs vides. Format&nbsp;: un titre, un paragraphe, puis les mentions obligatoires.&nbsp;»</p>
    <p>Chaque prompt est livré dans un livret tactique, avec les zones à personnaliser entre crochets et les erreurs à éviter.</p>
  </div>
  <div class="bloc">
    <h2>Durée et format</h2>
    <p>Module ChatGPT de 4&nbsp;heures en version débutant, complété par un module avancé (assistants personnalisés, automatisations). En agence sur la Côte d'Azur ou à distance, en individuel ou en groupe. Le module peut aussi être combiné avec Claude, Gemini ou NotebookLM dans un parcours plus complet. <a class="lien-texte" href="/formation-ia-immobilier/">Voir la formation IA immobilier complète</a></p>
  </div>
''' + FINANCEMENT + '\n' + PREUVES,
 [("ChatGPT gratuit suffit-il pour suivre la formation&nbsp;?", "Oui pour démarrer. Nous montrons aussi ce qu'apportent les versions payantes, pour que vous décidiez en connaissance de cause."),
  ("Peut-on rédiger une annonce conforme avec ChatGPT&nbsp;?", "Oui, à condition de lui donner les bonnes informations et de vérifier les mentions obligatoires (honoraires, DPE, copropriété). C'est un point travaillé pendant la formation."),
  ("Combien de temps dure la formation ChatGPT&nbsp;?", "Le module de base dure 4 heures. Il peut être complété par un module avancé ou intégré dans un parcours IA plus complet."),
  ("La formation est-elle finançable&nbsp;?", "Oui, par votre OPCO, l'AGEFICE ou le FIF PL selon votre statut. Elle n'est pas éligible au CPF à ce jour.")],
 ("Formation ChatGPT pour les agents immobiliers", "Maîtriser ChatGPT pour les tâches de l'agent immobilier : annonces conformes, prospection, préparation de rendez-vous, comptes rendus et relances."))

# ---------------------------------------------------------------- 3. Formation IA Nice
ecrire('formation-ia-nice/',
 "Formation IA immobilier à Nice et dans les Alpes-Maritimes",
 "Formation IA et ChatGPT pour agents immobiliers à Nice, Cannes, Antibes, Grasse et dans tout le 06 : dans votre agence ou à distance. Certifié Qualiopi.",
 "Formation IA immobilier à Nice et dans les Alpes-Maritimes.",
 "Nous formons les agents, mandataires et équipes d'agence de la Côte d'Azur à l'IA, directement dans leurs locaux. Des formateurs installés dans le département, qui connaissent votre marché parce qu'ils y ont fait de la transaction.",
 '''  <div class="bloc">
    <h2>Une formation IA pensée pour l'immobilier azuréen</h2>
    <p>Le marché des Alpes-Maritimes ne ressemble à aucun autre&nbsp;: clientèle internationale, résidences secondaires, biens de prestige sur le littoral, villages et maisons dans l'arrière-pays, vendeurs exigeants et concurrence forte entre agences. Une formation IA générique ne répond pas à ces situations. La nôtre part de vos dossiers réels, à chaque étape de la transaction.</p>
    <ul class="points">
      <li><strong>Prospection</strong>&nbsp;: préparer un secteur, cibler les propriétaires, écrire des messages qui donnent envie de vous rappeler.</li>
      <li><strong>Estimation et rendez-vous vendeur</strong>&nbsp;: un dossier d'adresse complet en quelques minutes avec nos outils maison, une analyse comparative claire, un argumentaire prêt.</li>
      <li><strong>Mandat et annonces</strong>&nbsp;: des annonces conformes (mentions obligatoires, DPE) et adaptées à votre clientèle, y compris en anglais ou en italien pour les acquéreurs étrangers.</li>
      <li><strong>Découverte, visite, négociation, suivi</strong>&nbsp;: comptes rendus, relances et synthèses de documents sans y passer vos soirées.</li>
    </ul>
    <p><a class="lien-texte" href="/formation-ia-immobilier/">Voir le programme complet de la formation IA immobilier</a></p>
  </div>
  <div class="bloc">
    <h2>Où nous intervenons</h2>
    <ul class="points">
      <li><strong>Nice et la métropole</strong>&nbsp;: Nice, Saint-Laurent-du-Var, Cagnes-sur-Mer, Villefranche-sur-Mer, Vence, Saint-Jeannet, Carros.</li>
      <li><strong>Antibes, Cannes et l'ouest</strong>&nbsp;: Antibes, Juan-les-Pins, Vallauris, Golfe-Juan, Cannes, Le Cannet, Mandelieu-la-Napoule, Mougins.</li>
      <li><strong>Grasse et le moyen pays</strong>&nbsp;: Grasse, Mouans-Sartoux, Valbonne, Sophia Antipolis, Biot, Roquefort-les-Pins.</li>
      <li><strong>L'est du département</strong>&nbsp;: Menton, Roquebrune-Cap-Martin, Beausoleil, Èze.</li>
    </ul>
    <p>La formation a lieu <strong>dans votre agence</strong>, ou <strong>à distance</strong> si votre équipe est répartie sur plusieurs sites. Nos formateurs sont basés à Cagnes-sur-Mer et à Antibes&nbsp;: les dates s'organisent facilement.</p>
  </div>
  <div class="bloc">
    <h2>Les outils que vous utiliserez</h2>
    <p>ChatGPT, Claude, Gemini, NotebookLM et Gamma, choisis selon la tâche, et nos outils maison&nbsp;: dossier d'adresse, localisateur, analyse comparative de marché, profiling vendeur et assistant juridique. Chaque parcours existe en version débutant et en version avancée.</p>
  </div>
  <div class="bloc">
    <h2>Ils se sont formés près de chez vous</h2>
    <p>Des agences de la Côte d'Azur nous font confiance, dont Century 21 Albert 1er, Century 21 Azurim, Century 21 Villas d'Azur, Orpi MCH Immobilier, Akorimmo, Riviera King, L'Agence Signature, Octantimmo, Agence Bristol et Marclé Real Estate.</p>
  </div>
  <div class="bloc">
    <h2>Des heures qui comptent pour la loi ALUR</h2>
    <p>Nos formations sont centrées sur votre activité de transaction&nbsp;: elles donnent lieu à une attestation pour votre formation continue obligatoire. <a class="lien-texte" href="/formation-loi-alur/">Tout savoir sur la formation loi ALUR</a></p>
  </div>
''' + FINANCEMENT + '\n' + PREUVES,
 [("Où ont lieu les formations IA immobilier dans les Alpes-Maritimes&nbsp;?", "Dans votre agence, à Nice, Cannes, Antibes, Grasse, Menton ou ailleurs dans le département, ou à distance. Nous adaptons le lieu et les dates à votre équipe."),
  ("La formation est-elle réservée aux agences&nbsp;?", "Non. Nous formons aussi les mandataires et agents commerciaux indépendants, seuls ou en petit groupe, ainsi que les directeurs d'agence."),
  ("La formation IA compte-t-elle dans les heures loi ALUR&nbsp;?", "Nos formations portent sur votre activité de transaction et donnent lieu à une attestation de formation continue. Lors de l'appel découverte, nous faisons le point sur vos heures restantes."),
  ("La formation est-elle finançable&nbsp;?", "Oui, par votre OPCO ou votre fonds d'assurance formation (AGEFICE, FIF PL…). Start Academia est certifié Qualiopi. La formation n'est pas éligible au CPF à ce jour."),
  ("Faut-il un niveau particulier en informatique&nbsp;?", "Non. Chaque parcours existe en version débutant et en version avancée.")],
 ("Formation IA immobilier à Nice et dans les Alpes-Maritimes", "Formation pratique à l'IA et à ChatGPT pour les professionnels de l'immobilier, dans votre agence à Nice et dans les Alpes-Maritimes ou à distance."))

# ---------------------------------------------------------------- 5. Loi ALUR (enrichie, audit du 7 nov. 2026)
ecrire('formation-loi-alur/',
 'Formation loi ALUR pour agents immobiliers | Start Academia',
 'Formation continue loi ALUR : 14 h par an ou 42 h sur 3 ans, déontologie, non-discrimination. Formations immobilier et IA sur mesure, à distance ou en agence.',
 'Formation loi ALUR pour les agents immobiliers.',
 "Validez vos heures de formation continue obligatoires avec des formations utiles dès le lendemain, sur votre métier et vos vrais dossiers. En agence sur la Côte d'Azur ou à distance, partout en France.",
 '''  <div class="bloc">
    <h2>Ce que la loi vous demande</h2>
    <p>Depuis la loi ALUR du 24 mars 2014, les professionnels de l'immobilier doivent suivre une formation continue. Son contenu est fixé par le décret n°&nbsp;2016-173 du 18 février 2016, complété par le décret n°&nbsp;2020-1259 du 14 octobre 2020.</p>
    <ul class="points">
      <li><strong>Durée</strong>&nbsp;: 14 heures par an, ou 42 heures au cours de 3 années consécutives d'exercice.</li>
      <li><strong>Thèmes obligatoires sur 3 ans</strong>&nbsp;: au moins 2 heures sur la déontologie et au moins 2 heures sur la non-discrimination dans l'accès au logement.</li>
      <li><strong>Contenu</strong>&nbsp;: les formations doivent avoir un lien direct avec l'activité professionnelle exercée.</li>
    </ul>
  </div>
  <div class="bloc">
    <h2>Qui est concerné</h2>
    <ul class="points">
      <li>Les titulaires de la carte professionnelle (transaction, gestion, syndic) et les directeurs d'établissement.</li>
      <li>Les collaborateurs habilités à négocier pour le compte de l'agence, salariés ou non&nbsp;: négociateurs salariés, agents commerciaux, mandataires.</li>
    </ul>
    <p>Le titulaire de la carte justifie ses heures lors du renouvellement de sa carte, tous les 3 ans. Il lui revient aussi de vérifier que ses collaborateurs ont suivi leurs propres heures avant de renouveler leur attestation d'habilitation.</p>
  </div>
  <div class="bloc">
    <h2>Ce que nous vous proposons</h2>
    <ul class="points">
      <li><strong>Des heures qui servent à vendre.</strong> Prospection, estimation, mandat, découverte, visite, négociation, suivi&nbsp;: chaque module travaille une étape de votre métier, avec l'IA et nos outils maison.</li>
      <li><strong>Sur mesure.</strong> Le programme et la durée sont fixés avec vous selon vos besoins et les heures qu'il vous reste à faire.</li>
      <li><strong>En agence sur la Côte d'Azur ou à distance</strong>, partout en France, en individuel ou en groupe.</li>
      <li><strong>Une attestation</strong> de formation remise à chaque participant, à conserver pour le renouvellement de la carte ou de l'attestation.</li>
    </ul>
  </div>
  <div class="bloc">
    <h2>Exemple de parcours de 14 heures</h2>
    <p>Un parcours se construit avec vous. À titre d'exemple, sur deux journées de 7 heures&nbsp;:</p>
    <ol class="points numerotes">
      <li><strong>Jour 1, rentrer des mandats</strong>&nbsp;: prospection de secteur, dossier d'adresse, préparation du rendez-vous vendeur, estimation argumentée.</li>
      <li><strong>Jour 2, vendre et suivre</strong>&nbsp;: annonces conformes, découverte acquéreur, visite, négociation et suivi client, avec les bons réflexes pour protéger les données de vos clients.</li>
    </ol>
    <p>Chaque séquence part d'un cas réel de votre agence, avec un exercice pratique et un livret tactique pour réutiliser les méthodes au quotidien.</p>
    <p><strong>Déontologie et non-discrimination couvertes.</strong> Pour les heures obligatoires, nous proposons le module <a href="/formations/#non-discrimination-tracfin-et-deontologie">Non-discrimination, Tracfin et déontologie</a> (8&nbsp;h), à intégrer à votre parcours.</p>
  </div>
  <div class="bloc">
    <h2>À distance ou en présentiel&nbsp;?</h2>
    <p>Le texte n'impose pas de format&nbsp;: une formation suivie à distance compte autant qu'une formation en salle, si elle remplit les conditions de durée et de contenu. Nous proposons les deux, et beaucoup d'agences combinent une journée en présentiel et des séances courtes à distance.</p>
  </div>
''' + FINANCEMENT + '\n' + PREUVES,
 [("Combien d'heures de formation loi ALUR faut-il faire&nbsp;?", "14 heures par an, ou 42 heures au cours de 3 années consécutives d'exercice. Sur ces 3 années, au moins 2 heures doivent porter sur la déontologie et au moins 2 heures sur la non-discrimination dans l'accès au logement."),
  ("Une formation à l'IA compte-t-elle pour la loi ALUR&nbsp;?", "Oui, si elle a un lien direct avec votre activité professionnelle. Nos formations sont appliquées à la transaction immobilière (prospection, estimation, mandat, vente) et donnent lieu à une attestation."),
  ("La formation loi ALUR peut-elle se faire à distance&nbsp;?", "Oui. Le texte n'impose pas de format : une formation à distance compte dès lors qu'elle respecte les conditions de durée et de contenu."),
  ("Les agents commerciaux et mandataires sont-ils concernés&nbsp;?", "Oui. Toutes les personnes habilitées à négocier pour le compte du titulaire de la carte, salariées ou non, doivent suivre la formation continue."),
  ("Qui contrôle les heures de formation&nbsp;?", "La CCI, lors du renouvellement de la carte professionnelle tous les 3 ans. Le titulaire de la carte vérifie de son côté les heures de ses collaborateurs."),
  ("Comment financer sa formation loi ALUR&nbsp;?", "Par l'OPCO de l'agence pour les salariés, par le FIF PL ou l'AGEFICE pour les indépendants. Start Academia est certifié Qualiopi. Nos formations ne sont pas éligibles au CPF à ce jour.")],
 ("Formation continue loi ALUR pour agents immobiliers", "Formations immobilier et IA sur mesure validant les heures de formation continue obligatoires des professionnels de l'immobilier, en agence ou à distance."))


# ---------------------------------------------------------------- 4. Financement (reprend l'ancienne page OPCO)
ecrire('financement-formation-immobilier/',
 'Financement formation : calculez vos droits AGEFICE et OPCO',
 "Simulateur gratuit : calculez vos droits à la formation AGEFICE ou OPCO en 1 minute. Agent, mandataire ou agence : qui paie votre formation et comment.",
 "Financement de formation&nbsp;: calculez vos droits.",
 "Comment payer votre formation, quelle aide demander selon votre statut, et combien vous pouvez obtenir&nbsp;: estimez vos droits AGEFICE ou OPCO en une minute avec notre simulateur gratuit. Start Academia est certifié Qualiopi, condition indispensable pour une prise en charge.",
 '''  <div class="bloc">
    <h2>Qui paie votre formation&nbsp;: OPCO, AGEFICE ou FIF PL&nbsp;?</h2>
    <ul class="points">
      <li><strong>Vous êtes salarié d'une agence</strong> (négociateur salarié, assistant, manager)&nbsp;: c'est l'<strong>OPCO de l'agence</strong> qui finance, dans le cadre du plan de développement des compétences. Pour les agences immobilières (branche de l'immobilier), il s'agit en général de l'<strong>OPCO EP</strong>. La demande est faite par l'employeur.</li>
      <li><strong>Vous êtes agent commercial, mandataire en réseau ou auto-entrepreneur</strong>&nbsp;: vous n'avez <strong>pas d'OPCO</strong>, mais un <strong>fonds d'assurance formation</strong> (FAF), alimenté par votre contribution à la formation professionnelle. Pour les agents immobiliers, c'est le plus souvent le <strong>FIF PL</strong>&nbsp;; certains dirigeants relevant du commerce dépendent de l'<strong>AGEFICE</strong>.</li>
      <li><strong>Vous dirigez une agence</strong>&nbsp;: si vous êtes salarié de votre société, vos formations passent par l'OPCO comme celles de vos équipes&nbsp;; sinon, par votre fonds d'assurance formation.</li>
    </ul>
    <p><strong>Pour savoir à coup sûr de quel fonds vous dépendez</strong>, téléchargez votre <strong>attestation de contribution à la formation professionnelle</strong> dans votre espace URSSAF&nbsp;: le nom du fonds y figure.</p>
  </div>
''' + SIMULATEUR + '''
  <div class="bloc" id="fif-pl">
    <h2>Ce que prend en charge le FIF PL pour les agents immobiliers</h2>
    <p>Pour 2026, les critères du FIF PL pour les agents immobiliers (code NAF 6831Z) prévoient notamment&nbsp;:</p>
    <ul class="points">
      <li>une prise en charge plafonnée à <strong>900&nbsp;€ par an et par professionnel</strong>, et à <strong>300&nbsp;€ par jour</strong> de formation&nbsp;;</li>
      <li>pour les <strong>micro-entrepreneurs</strong>, des plafonds proportionnels à la contribution versée&nbsp;;</li>
      <li>des formations <strong>à distance</strong> prises en charge à hauteur de 50&nbsp;% du critère journalier&nbsp;;</li>
      <li>une condition obligatoire&nbsp;: un organisme <strong>certifié Qualiopi</strong>, ce qui est notre cas.</li>
    </ul>
    <p>Ces critères changent chaque année&nbsp;: nous vérifions avec vous ceux en vigueur au moment de votre demande. <a class="lien-texte" href="https://www.fifpl.fr/" rel="noopener">Site du FIF PL</a></p>
  </div>
  <div class="bloc">
    <h2>Comment ça se passe avec nous</h2>
    <ol class="points numerotes">
      <li><strong>Appel découverte</strong>&nbsp;: on fait le point sur votre statut, vos besoins et vos heures loi ALUR.</li>
      <li><strong>Devis, programme et convention</strong>&nbsp;: vous recevez les documents exigés par votre financeur.</li>
      <li><strong>Demande de prise en charge</strong>&nbsp;: vous la déposez sur l'espace de votre OPCO ou de votre fonds, avec notre aide. Faites-la de préférence avant le début de la formation.</li>
      <li><strong>Formation</strong>, en agence sur la Côte d'Azur ou à distance.</li>
      <li><strong>Attestation et facture</strong>&nbsp;: vous les transmettez à votre financeur pour le remboursement.</li>
    </ol>
  </div>
  <div class="bloc">
    <h2>Et le CPF&nbsp;?</h2>
    <p>Nos formations ne sont pas éligibles au CPF à ce jour. Les heures suivies comptent en revanche dans vos <strong>14&nbsp;heures annuelles de formation continue</strong> exigées par la loi ALUR, avec attestation. <a class="lien-texte" href="/formation-loi-alur/">En savoir plus sur la loi ALUR</a></p>
  </div>
''' + PREUVES,
 [("Comment calculer mes droits à la formation&nbsp;?", "Avec le simulateur de cette page : indiquez votre chiffre d'affaires de l'année précédente déclaré à l'URSSAF (ou le montant de votre attestation CFP) si vous êtes indépendant, ou votre nombre de salariés si vous êtes employeur. Vous obtenez une estimation du budget AGEFICE ou OPCO EP mobilisable, à confirmer avec votre financeur. Vos droits CPF, eux, se consultent sur moncompteformation.gouv.fr."),
  ("Comment payer ma formation&nbsp;?", "Le plus souvent, vous n'avancez qu'une partie des frais, voire rien : votre OPCO (si vous êtes salarié), l'AGEFICE ou le FIF PL (si vous êtes indépendant) prend en charge la formation dans la limite de ses plafonds. Nous préparons le devis, le programme et la convention, et vous aidons à déposer la demande."),
  ("Quelles aides pour financer une formation dans l'immobilier&nbsp;?", "Les principales aides sont l'OPCO EP pour les salariés des agences, l'AGEFICE ou le FIF PL pour les indépendants et dirigeants, et le CPF pour les formations éligibles. Les formations Start Academia sont finançables par OPCO, AGEFICE ou FIF PL, mais pas par le CPF à ce jour."),
  ("Un auto-entrepreneur ou une micro-entreprise a-t-il un OPCO&nbsp;?", "Non. Les OPCO financent la formation des salariés. Un auto-entrepreneur (micro-entreprise), agent commercial ou mandataire, dépend d'un fonds d'assurance formation : le plus souvent le FIF PL pour les agents immobiliers, parfois l'AGEFICE. Le nom du fonds figure sur votre attestation de contribution à la formation professionnelle, dans votre espace URSSAF."),
  ("Quel OPCO pour une agence immobilière&nbsp;?", "Les agences de la branche de l'immobilier relèvent en général de l'OPCO EP. Il finance la formation des salariés, pas celle des agents commerciaux indépendants."),
  ("Quel montant puis-je obtenir&nbsp;?", "Il dépend de votre financeur et de votre statut. Pour 2026, le FIF PL prévoit pour les agents immobiliers jusqu'à 900 € par an et 300 € par jour, avec des plafonds proportionnels pour les micro-entrepreneurs. Nous vérifions avec vous les critères en vigueur."),
  ("Qui monte le dossier&nbsp;?", "La demande est déposée par vous ou votre employeur, mais nous fournissons tous les documents (devis, programme, convention, attestation) et nous vous guidons pas à pas."),
  ("Les formations Start Academia sont-elles éligibles au CPF&nbsp;?", "Pas à ce jour. Elles sont finançables par OPCO, FIF PL ou AGEFICE, et comptent pour la formation continue loi ALUR.")])
