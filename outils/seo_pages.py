"""Pages SEO prioritaires (audit du 6 nov. 2026) : une page par recherche commerciale.
Chaque page : H1 descriptif, programme, outils, public, financement, preuves, FAQ (+ données structurées)."""
import pathlib, json, html as h, sys
sys.path.insert(0, '/home/claude/outils')
from simulateur_html import SIMULATEUR
src = pathlib.Path('/home/claude/outils/pages.py').read_text()
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
    p = pathlib.Path(f'/home/claude/site3/{chemin}index.html')
    t = p.read_text()
    t = t.replace('</head>', jsonld(chemin, h.unescape(h1).rstrip('.'), desc, faq, cours) + '\n</head>', 1)
    p.write_text(t)
    print(chemin, len(titre), 'car. titre /', len(desc), 'car. description')

PREUVES = '''  <div class="bloc">
    <h2>Pourquoi Start Academia</h2>
    <ul class="points">
      <li><strong>Des formateurs du métier.</strong> Jean-Guy Ourmières et Laurent Marx ont plus de 10 ans de transaction et accompagnent encore des agences au quotidien.</li>
      <li><strong>Nos propres outils.</strong> Dossier d'adresse (Mon Secteur), Profiling, Localisateur, ACM&nbsp;: vos équipes repartent avec des outils prêts à servir.</li>
      <li><strong>Des preuves.</strong> 420 agents et collaborateurs formés, 224 avis Google notés 5 étoiles, des agences comme Laforêt, Nestenn, Century 21 ou Orpi parmi nos clients.</li>
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
 "Formation IA et ChatGPT à Nice | Start Academia",
 "Formation à l'IA et à ChatGPT à Nice et dans les Alpes-Maritimes : en agence, dans vos locaux ou à distance. Organisme certifié Qualiopi, financement possible.",
 "Formation IA et ChatGPT à Nice et dans les Alpes-Maritimes.",
 "Nous venons former vos équipes sur place, à Nice et partout sur la Côte d'Azur. Une formation pratique, sur vos vrais dossiers, par des formateurs installés dans le département.",
 '''  <div class="bloc">
    <h2>Où nous intervenons</h2>
    <p>Nice, Antibes, Cannes, Cagnes-sur-Mer, Sophia Antipolis, Vence, Grasse, Menton, Villefranche-sur-Mer, Saint-Laurent-du-Var et tout le département des Alpes-Maritimes. La formation a lieu <strong>dans vos locaux</strong>, ou <strong>à distance</strong> si votre équipe est répartie.</p>
    <p>Nos formateurs sont basés à Cagnes-sur-Mer et à Antibes&nbsp;: les dates s'organisent facilement, sans frais de déplacement lointains.</p>
  </div>
  <div class="bloc">
    <h2>Ce que vous apprenez</h2>
    <ul class="points">
      <li><strong>ChatGPT et les assistants IA</strong> (Claude, Gemini, NotebookLM) appliqués à vos tâches réelles&nbsp;: rédaction, prospection, préparation de rendez-vous, synthèse de documents.</li>
      <li><strong>Les présentations et supports</strong> générés en quelques minutes avec Gamma.</li>
      <li><strong>Les bons réflexes</strong>&nbsp;: vérifier ce que l'IA produit, protéger les données de vos clients, respecter la réglementation de votre métier.</li>
    </ul>
    <p>Notre spécialité est l'immobilier&nbsp;: agences, réseaux, mandataires et directeurs. <a class="lien-texte" href="/formation-ia-immobilier/">Voir la formation IA immobilier</a></p>
  </div>
  <div class="bloc">
    <h2>Ils se sont formés près de chez vous</h2>
    <p>Des agences de la Côte d'Azur nous font confiance, dont Century 21 Albert 1er, Century 21 Azurim, Century 21 Villas d'Azur, Orpi MCH Immobilier, Akorimmo, Riviera King, L'Agence Signature, Octantimmo, Agence Bristol et Marclé Real Estate.</p>
  </div>
''' + FINANCEMENT + '\n' + PREUVES,
 [("Où ont lieu les formations IA à Nice&nbsp;?", "Dans vos locaux, à Nice ou ailleurs dans les Alpes-Maritimes, ou à distance. Nous adaptons le lieu et les dates à votre équipe."),
  ("La formation IA est-elle finançable&nbsp;?", "Oui, par votre OPCO ou votre fonds d'assurance formation (AGEFICE, FIF PL…). Start Academia est certifié Qualiopi. La formation n'est pas éligible au CPF à ce jour."),
  ("Faut-il un niveau particulier&nbsp;?", "Non. Chaque parcours existe en version débutant et en version avancée."),
  ("Combien de personnes par session&nbsp;?", "En individuel ou en groupe : le format est défini avec vous lors de l'appel découverte.")],
 ("Formation IA et ChatGPT à Nice", "Formation pratique à l'intelligence artificielle et à ChatGPT, dans vos locaux à Nice et dans les Alpes-Maritimes ou à distance."))


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
