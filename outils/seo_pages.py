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
    if chemin in GUIDES:
        graph[0]["dateModified"] = GUIDES[chemin][0]
        graph[0]["author"] = {"@type": "Person", "@id": AUTEURS[GUIDES[chemin][1]][2], "name": AUTEURS[GUIDES[chemin][1]][0]}
        if chemin in CAPTURES:
            graph[0]["primaryImageOfPage"] = {"@type": "ImageObject", "url": f"{SITE}/img/{CAPTURES[chemin][0]}"}
    if cours:
        graph.append({"@type": "Course", "name": cours[0], "description": cours[1],
                      "provider": {"@id": f"{SITE}/#organisation"}, "inLanguage": "fr",
                      "hasCourseInstance": [{"@type": "CourseInstance", "courseMode": m,
                                             "location": "Alpes-Maritimes, France" if m == "Onsite" else None} for m in ("Onsite", "Online")],
                      "offers": {"@type": "Offer", "category": "Paid", "availability": "https://schema.org/InStock"}})
        for ci in graph[-1]["hasCourseInstance"]:
            if ci["location"] is None: del ci["location"]
    return '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False) + '</script>'

PAGES = {}  # chemin -> (titre affiché, description), rempli par ecrire() ; sert à la rubrique Guides


def ecrire(chemin, titre, desc, h1, intro, corps, faq, cours=None):
    PAGES[chemin] = (h1.rstrip('.'), desc)
    if chemin in GUIDES:
        corps = habiller_guide(chemin, corps)
    page(chemin, titre, desc, h1, intro, corps + '\n' + faq_html(faq))
    p = racine / chemin / 'index.html'
    t = p.read_text()
    t = t.replace('</head>', jsonld(chemin, h.unescape(h1).rstrip('.'), desc, faq, cours) + '\n</head>', 1)
    p.write_text(t)
    print(chemin, len(titre), 'car. titre /', len(desc), 'car. description')

# Blocs communs, volontairement courts : répétés sur une quinzaine de pages, ils ne doivent pas peser
# plus que quelques lignes (Google recommande de limiter le contenu dupliqué). Le détail est sur les pages liées.
GARANTIES = '''  <div class="bloc">
    <h2>Financement et garanties</h2>
    <p>Formation finançable par votre <strong>OPCO</strong> ou votre fonds d'assurance formation (AGEFICE, FIF PL), non éligible au CPF à ce jour. Les heures comptent pour la <strong>loi ALUR</strong>. Organisme certifié <strong>Qualiopi</strong>&nbsp;: <span data-qualiof="apprenantsFormes">274</span> agents et collaborateurs formés, 227 avis Google.</p>
    <p><a class="lien-texte" href="/financement-formation-immobilier/#simulateur-financement">Calculer mes droits</a> &nbsp; <a class="lien-texte" href="/formation-loi-alur/">Loi ALUR</a> &nbsp; <a class="lien-texte" href="/resultats/">Résultats et avis</a></p>
  </div>'''

# Variante pour les pages Financement, qui détaillent déjà la prise en charge.
PREUVES_BREF = '''  <div class="bloc">
    <h2>Pourquoi Start Academia</h2>
    <p>Des formateurs du métier, nos propres outils, un organisme certifié <strong>Qualiopi</strong>&nbsp;: <span data-qualiof="apprenantsFormes">274</span> agents et collaborateurs formés, 227 avis Google.</p>
    <p><a class="lien-texte" href="/resultats/">Résultats et avis</a> &nbsp; <a class="lien-texte" href="/documents/certificat-qualiopi.pdf">Voir le certificat</a></p>
  </div>'''

# ---------------------------------------------------------------- Guides : signature, date et capture d'outil
# Date de dernière mise à jour du CONTENU de chaque guide (AAAA-MM-JJ). À changer à la main quand le texte
# du guide change : elle est affichée sous le titre et transmise à Google (dateModified).
# Chaque guide est signé par l'un des deux formateurs, en alternance dans l'ordre de la rubrique Guides.
AUTEURS = {
    'jg': ('Jean-Guy Ourmières', 'co-dirigeant et formateur', f'{SITE}/#jean-guy'),
    'lm': ('Laurent Marx', 'co-dirigeant et formateur', f'{SITE}/#laurent'),
}
# chemin -> (date de mise à jour, auteur)
GUIDES = {
    'prospecter-avec-le-dpe/': ('2026-11-12', 'jg'),
    'prospection-immobiliere-sans-pige/': ('2026-11-12', 'lm'),
    'ia-prospection-immobiliere/': ('2026-11-12', 'jg'),
    'vendeur-parti-trop-cher-reprendre-mandat/': ('2026-11-12', 'lm'),
    'ia-estimation-immobiliere/': ('2026-11-12', 'jg'),
    'ia-mandat-exclusif/': ('2026-11-12', 'lm'),
    'ia-annonce-immobiliere/': ('2026-11-12', 'jg'),
    'pv-assemblee-generale-gemini-notebook/': ('2026-11-12', 'lm'),
    'ia-decouverte-acquereur/': ('2026-11-12', 'jg'),
    'ia-visite-immobiliere/': ('2026-11-12', 'lm'),
    'ia-negociation-immobiliere/': ('2026-11-12', 'jg'),
    'financement-formation-auto-entrepreneur/': ('2026-11-12', 'lm'),
}
# Capture d'un outil maison cité dans le guide : (fichier dans /img, largeur, hauteur, description, légende).
# Elle est insérée après la première liste numérotée du guide (la méthode).
CAPTURES = {
    'ia-prospection-immobiliere/': ('dossier-carte.webp', 1100, 648, "La carte d'un dossier Academia Secteur : le cercle de 300 m autour de l'adresse, avec les ventes réelles et les copropriétés.", "Academia Secteur · la carte d'un dossier d'adresse"),
    'ia-estimation-immobiliere/': ('acm-analyse-prix.webp', 1100, 648, "L'analyse des prix présentée au vendeur : sa valeur perçue, le prix des concurrents, l'analyse du conseiller et les prix affichés sur une ligne.", "Academia ACM · l'analyse des prix présentée au vendeur"),
    'ia-mandat-exclusif/': ('profiling-strategie.webp', 1100, 422, "La stratégie d'approche : levier psychologique principal, pitch idéal à copier et points à éviter absolument.", "Academia Profiling · la stratégie d'approche"),
    'ia-decouverte-acquereur/': ('vivre-ici-carte.webp', 1100, 648, "La carte Vivre ici : boulangerie, parc, supermarché et arrêt de bus autour de l'adresse, avec les cercles de 5, 10 et 15 minutes à pied.", "Academia Vivre ici · le quotidien autour de l'adresse"),
    'ia-visite-immobiliere/': ('radar-fiche.webp', 1100, 648, "La fiche d'un acquéreur de démonstration : sa recherche, les étapes biens idéaux, présentation, réponse, visites, et sa sélection de 3 biens dans le budget.", "Academia Radar Acheteur · la fiche d'un acquéreur de démonstration"),
    'ia-negociation-immobiliere/': ('acm-danger.webp', 1100, 301, "Le point marché : le bien est 5e sur 6 face à ses concurrents, aucun concurrent n'a baissé depuis le rendez-vous.", "Academia ACM · le point marché"),
    'vendeur-parti-trop-cher-reprendre-mandat/': ('acm-suivi-prix.webp', 900, 248, "Le suivi d'un mandat exclusif : prix voulu par le vendeur, prix après le marché, prix signé aligné sur le marché (nom du vendeur masqué).", "Academia ACM · du prix voulu au prix signé"),
    'prospection-immobiliere-sans-pige/': ('dossier-dynamique.webp', 1100, 281, "Les graphiques du dossier : prix médian au m² et nombre de ventes par an depuis 2021.", "Academia Secteur · les graphiques d'un dossier d'adresse"),
}
MOIS = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']


def date_fr(iso):
    a, m, j = (int(x) for x in iso.split('-'))
    return f"{'1er' if j == 1 else j} {MOIS[m - 1]} {a}"


def habiller_guide(chemin, corps):
    """Ajoute la signature datée en tête du guide et, s'il y en a une, la capture d'outil après la méthode."""
    if chemin in CAPTURES:
        img, larg, haut, alt, legende = CAPTURES[chemin]
        figure = (f'\n    <figure class="capture"><img src="/img/{img}" width="{larg}" height="{haut}" loading="lazy" alt="{h.escape(alt)}">'
                  f'<figcaption>{h.escape(legende)}</figcaption></figure>')
        if '</ol>' not in corps:
            raise SystemExit(f'seo_pages : pas de liste numérotée où placer la capture dans {chemin}')
        corps = corps.replace('</ol>', '</ol>' + figure, 1)
    nom, role, _ = AUTEURS[GUIDES[chemin][1]]
    signature = (f'  <p class="signature">Par <a href="/#equipe">{nom}</a>, {role} '
                 f'<span aria-hidden="true">·</span> Mis à jour le <time datetime="{GUIDES[chemin][0]}">{date_fr(GUIDES[chemin][0])}</time></p>')
    return signature + '\n' + corps

# ---------------------------------------------------------------- 1. Formation IA immobilier
ecrire('formation-ia-immobilier/',
 'Formation IA immobilier : agents et agences | Start Academia',
 "Formation à l'IA et à ChatGPT pour agents immobiliers, mandataires et agences : prospection, estimation, mandat, suivi vendeur. Côte d'Azur ou à distance.",
 "Formation IA pour les professionnels de l'immobilier.",
 "Prospection, estimation, mandat, découverte, visite, négociation, suivi&nbsp;: on part des gestes de votre métier et on les rend plus rapides avec l'IA. Une formation pratique, sur vos propres dossiers, certifiée Qualiopi.",
 '''  <div class="bloc">
    <h2>Qu'est-ce qui vous mange votre semaine&nbsp;?</h2>
    <div class="semaine">
      <p class="plan-intro">Cochez vos tâches et indiquez le temps que vous y passez aujourd'hui. La seconde pile, c'est la même semaine avec la méthode.</p>
      <div class="plan-scene">
        <div class="semaine-choix">
          <fieldset class="semaine-etape" data-lien="/ia-prospection-immobiliere/"><legend>Prospection</legend><ul>
            <li class="tache"><label><input type="checkbox" data-ia="20" data-etape="prospection" data-unite="étude"><span class="tache-nom">Faire l'étude de marché de mon secteur</span><em class="tache-ia">20&nbsp;min avec la méthode</em></label></li>
            <li class="tache"><label><input type="checkbox" data-ia="5" data-etape="prospection" data-unite="recherche"><span class="tache-nom">Repérer les propriétaires à contacter en priorité</span><em class="tache-ia">5&nbsp;min avec la méthode</em></label></li>
            <li class="tache"><label><input type="checkbox" data-ia="5" data-etape="prospection" data-unite="support"><span class="tache-nom">Préparer un flyer ou un boîtage de quartier</span><em class="tache-ia">5&nbsp;min avec la méthode</em></label></li>
            <li class="tache"><label><input type="checkbox" data-ia="3" data-etape="prospection" data-unite="message"><span class="tache-nom">Rédiger mes messages de prospection</span><em class="tache-ia">3&nbsp;min avec la méthode</em></label></li>
            <li class="tache"><label><input type="checkbox" data-ia="5" data-etape="prospection" data-unite="courrier"><span class="tache-nom">Écrire aux vendeurs entre particuliers</span><em class="tache-ia">5&nbsp;min avec la méthode</em></label></li>
            <li class="tache"><label><input type="checkbox" data-ia="2" data-etape="prospection" data-unite="avis"><span class="tache-nom">Répondre à mes avis clients</span><em class="tache-ia">2&nbsp;min avec la méthode</em></label></li>
            <li class="tache"><label><input type="checkbox" data-ia="5" data-etape="prospection" data-unite="semaine"><span class="tache-nom">Planifier mes publications de la semaine</span><em class="tache-ia">5&nbsp;min avec la méthode</em></label></li>
          </ul></fieldset>
          <fieldset class="semaine-etape" data-lien="/ia-estimation-immobiliere/"><legend>Vendeur</legend><ul>
            <li class="tache"><label><input type="checkbox" data-ia="15" data-etape="vendeur" data-unite="rendez-vous"><span class="tache-nom">Préparer un premier rendez-vous vendeur</span><em class="tache-ia">15&nbsp;min avec la méthode</em></label></li>
            <li class="tache"><label><input type="checkbox" data-ia="5" data-etape="vendeur" data-unite="dossier"><span class="tache-nom">Monter le dossier après la découverte</span><em class="tache-ia">5&nbsp;min avec la méthode</em></label></li>
            <li class="tache"><label><input type="checkbox" data-ia="15" data-etape="vendeur" data-unite="rendez-vous"><span class="tache-nom">Préparer le second rendez-vous et la stratégie</span><em class="tache-ia">15&nbsp;min avec la méthode</em></label></li>
            <li class="tache"><label><input type="checkbox" data-ia="10" data-etape="vendeur" data-unite="bien"><span class="tache-nom">Défendre un prix par le potentiel de rénovation</span><em class="tache-ia">10&nbsp;min avec la méthode</em></label></li>
          </ul></fieldset>
          <fieldset class="semaine-etape" data-lien="/ia-mandat-exclusif/"><legend>Mandat</legend><ul>
            <li class="tache"><label><input type="checkbox" data-ia="5" data-etape="mandat" data-unite="annonce"><span class="tache-nom">Rédiger une annonce</span><em class="tache-ia">5&nbsp;min avec la méthode</em></label></li>
            <li class="tache"><label><input type="checkbox" data-ia="5" data-etape="mandat" data-unite="point"><span class="tache-nom">Faire le point de suivi avec un vendeur</span><em class="tache-ia">5&nbsp;min avec la méthode</em></label></li>
          </ul></fieldset>
          <fieldset class="semaine-etape" data-lien="/ia-decouverte-acquereur/"><legend>Acquéreurs</legend><ul>
            <li class="tache"><label><input type="checkbox" data-ia="3" data-etape="acquereurs" data-unite="recherche"><span class="tache-nom">Sélectionner des annonces pour un acquéreur</span><em class="tache-ia">3&nbsp;min avec la méthode</em></label></li>
          </ul></fieldset>
          <fieldset class="semaine-etape" data-lien="/ia-visite-immobiliere/"><legend>Visites</legend><ul>
            <li class="tache"><label><input type="checkbox" data-ia="1" data-etape="visites" data-unite="compte rendu"><span class="tache-nom">Rédiger un compte rendu de visite, dans la langue du client</span><em class="tache-ia">1&nbsp;min avec la méthode</em></label></li>
          </ul></fieldset>
        </div>
        <div class="plan-vue semaine-vue">
          <canvas class="plan-toile semaine-toile" aria-hidden="true"></canvas>
          <p class="plan-legende"><span class="pl-session">Aujourd'hui</span><span class="pl-deb">Avec la méthode</span><span class="plan-echelle">1 étage = 1 heure</span></p>
        </div>
      </div>
      <div class="plan-resultat" aria-live="polite">
        <div class="plan-chiffres">
          <p><strong id="sm-auj">0&nbsp;min</strong><span>aujourd'hui, par semaine</span></p>
          <p><strong id="sm-ia">0&nbsp;min</strong><span>avec la méthode</span></p>
          <p><strong id="sm-gain">–</strong><span>rendues à vos clients</span></p>
        </div>
        <p class="semaine-phrase" id="sm-phrase">Cochez une première tâche pour commencer.</p>
        <ul class="semaine-programme" id="sm-programme" hidden></ul>
        <div class="plan-actions">
          <a class="action semaine-appel" href="https://meet.brevo.com/jean-guy-ourmieres/appel-decouverte" rel="noopener">Réserver mon appel découverte<svg aria-hidden="true"><use href="#fleche"/></svg></a>
          <button type="button" class="plan-copier" hidden>Copier ma semaine</button>
          <span class="plan-note">Temps en routine annoncés dans nos formations et nos livrets tactiques, une fois l'outil en place.</span>
        </div>
      </div>
    </div>
  </div>
  <div class="bloc">
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
    <p>Nous choisissons l'outil le plus simple pour chaque tâche, et nous disons pourquoi&nbsp;: <strong>ChatGPT, Claude, Gemini, Gemini Notebook et Gamma</strong>, et nos outils maison conçus par des agents pour des agents. <a class="lien-texte" href="/#outils">Découvrir nos outils</a></p>
  </div>
  <div class="bloc">
    <h2>Format, durée et niveau</h2>
    <ul class="points">
      <li><strong>Modules courts</strong>, de 1 à 4&nbsp;heures par outil ou par usage (ChatGPT, Claude, Gemini Notebook, rédaction de prompts, génération de contenus, DPE…), combinés selon vos besoins.</li>
      <li><strong>Parcours complet</strong> «&nbsp;Intégrer l'intelligence artificielle pour gagner en productivité&nbsp;» pour les équipes qui veulent aller plus loin.</li>
      <li><strong>Version débutant ou avancée</strong>, avec un livret tactique pour chaque méthode.</li>
      <li><strong>En agence</strong> sur la Côte d'Azur, <strong>ou à distance</strong> partout en France, en individuel ou en groupe.</li>
      <li><strong>À partir de 42&nbsp;€ de l'heure</strong>, devis précis après l'appel découverte, et finançable par votre OPCO ou votre fonds d'assurance formation.</li>
    </ul>
    <p><a class="lien-texte" href="/formations/">Voir le détail des <span data-qualiof="nbFormations">27</span> formations</a></p>
    <p>Des exemples concrets, étape par étape&nbsp;: <a class="lien-texte" href="/ia-prospection-immobiliere/">prospection</a>, <a class="lien-texte" href="/ia-estimation-immobiliere/">estimation</a>, <a class="lien-texte" href="/ia-mandat-exclusif/">mandat exclusif</a>, <a class="lien-texte" href="/ia-annonce-immobiliere/">annonce</a>, <a class="lien-texte" href="/ia-decouverte-acquereur/">découverte acquéreur</a>, <a class="lien-texte" href="/ia-visite-immobiliere/">visite</a>, <a class="lien-texte" href="/ia-negociation-immobiliere/">négociation</a>.</p>
  </div>
  <div class="bloc">
    <h2>Pour qui</h2>
    <p>Agents immobiliers, négociateurs, mandataires et agents commerciaux en réseau, collaborateurs, directeurs et managers d'agence. Pour les réseaux, nous déployons la formation auprès de tous vos mandataires.</p>
  </div>
''' + GARANTIES,
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
    <p>Module ChatGPT de 4&nbsp;heures en version débutant, complété par un module avancé (assistants personnalisés, automatisations). En agence sur la Côte d'Azur ou à distance, en individuel ou en groupe. Le module peut aussi être combiné avec Claude, Gemini ou Gemini Notebook dans un parcours plus complet. <a class="lien-texte" href="/formation-ia-immobilier/">Voir la formation IA immobilier complète</a></p>
  </div>
''' + GARANTIES,
 [("ChatGPT gratuit suffit-il pour suivre la formation&nbsp;?", "Oui pour démarrer. Nous montrons aussi ce qu'apportent les versions payantes, pour que vous décidiez en connaissance de cause."),
  ("Peut-on rédiger une annonce conforme avec ChatGPT&nbsp;?", "Oui, à condition de lui donner les bonnes informations et de vérifier les mentions obligatoires (honoraires, DPE, copropriété). C'est un point travaillé pendant la formation."),
  ("Combien de temps dure la formation ChatGPT&nbsp;?", "Le module de base dure 4 heures. Il peut être complété par un module avancé ou intégré dans un parcours IA plus complet."),
  ("La formation est-elle finançable&nbsp;?", "Oui, par votre OPCO, l'AGEFICE ou le FIF PL selon votre statut. Elle n'est pas éligible au CPF à ce jour.")],
 ("Formation ChatGPT pour les agents immobiliers", "Maîtriser ChatGPT pour les tâches de l'agent immobilier : annonces conformes, prospection, préparation de rendez-vous, comptes rendus et relances."))

# ---------------------------------------------------------------- 3. Formation IA Nice
ecrire('formation-ia-nice/',
 "Formation IA immobilier à Nice et dans les Alpes-Maritimes",
 "Formation IA et ChatGPT pour agents immobiliers à Nice, Antibes, Cannes, Grasse et dans tout le 06, dans votre agence. Dès 42 €/h, certifié Qualiopi.",
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
    <p><a class="lien-texte" href="/formation-ia-immobilier/">Voir le programme complet de la formation IA immobilier</a> · <a class="lien-texte" href="/formation-immobilier-nice/">Formations immobilier hors IA à Nice et dans le 06</a></p>
  </div>
  <div class="bloc">
    <h2>Où nous intervenons</h2>
    <p>Nous nous déplaçons dans <strong>toutes les communes des Alpes-Maritimes</strong>, et notamment dans les dix plus grandes villes du département&nbsp;:</p>
    <ul class="points villes">
      <li><strong>Formation IA immobilier à Nice</strong>, dans votre agence ou à distance.</li>
      <li><strong>Formation IA immobilier à Antibes</strong> et Juan-les-Pins.</li>
      <li><strong>Formation IA immobilier à Cannes</strong>.</li>
      <li><strong>Formation IA immobilier à Cagnes-sur-Mer</strong>, où se trouve notre siège.</li>
      <li><strong>Formation IA immobilier à Grasse</strong> et dans le pays grassois.</li>
      <li><strong>Formation IA immobilier au Cannet</strong>.</li>
      <li><strong>Formation IA immobilier à Menton</strong> et sur la Riviera est.</li>
      <li><strong>Formation IA immobilier à Saint-Laurent-du-Var</strong>.</li>
      <li><strong>Formation IA immobilier à Vallauris</strong> et Golfe-Juan.</li>
      <li><strong>Formation IA immobilier à Mandelieu-la-Napoule</strong>.</li>
    </ul>
    <p>Mais aussi Vence, Mougins, Valbonne et Sophia Antipolis, Biot, Villefranche-sur-Mer, Roquebrune-Cap-Martin, Beausoleil, Carros et l'arrière-pays. La formation a lieu <strong>dans votre agence</strong>, ou <strong>à distance</strong> si votre équipe est répartie sur plusieurs sites. Nos formateurs sont basés à Cagnes-sur-Mer et à Antibes&nbsp;: les dates s'organisent facilement.</p>
  </div>
  <div class="bloc">
    <h2>227 avis Google, une note de 5,0 sur 5</h2>
    <p>Les agents et directeurs que nous formons le disent eux-mêmes&nbsp;: des formateurs du terrain, des exercices sur leurs propres dossiers, des outils qu'ils utilisent dès le lendemain. <span data-qualiof="apprenantsFormes">240</span> professionnels de l'immobilier formés, et une note de satisfaction de <span data-qualiof="note5">4,9</span> sur 5 dans nos questionnaires de fin de formation. <a class="lien-texte" href="/resultats/">Voir tous les résultats et les avis</a></p>
  </div>
  <div class="bloc">
    <h2>Les outils que vous utiliserez</h2>
    <p>ChatGPT, Claude, Gemini, Gemini Notebook et Gamma, choisis selon la tâche, et nos outils maison&nbsp;: dossier d'adresse, localisateur, analyse comparative de marché, profiling vendeur et assistant juridique. Chaque parcours existe en version débutant et en version avancée.</p>
  </div>
  <div class="bloc">
    <h2>Ils se sont formés près de chez vous</h2>
    <p>Des agences de la Côte d'Azur nous font confiance, dont Century 21 Albert 1er, Century 21 Azurim, Century 21 Villas d'Azur, Orpi MCH Immobilier, Akorimmo, Riviera King, L'Agence Signature, Octantimmo, Agence Bristol et Marclé Real Estate.</p>
  </div>
  <div class="bloc">
    <h2>Des heures qui comptent pour la loi ALUR</h2>
    <p>Nos formations sont centrées sur votre activité de transaction&nbsp;: elles donnent lieu à une attestation pour votre formation continue obligatoire. <a class="lien-texte" href="/formation-loi-alur/">Tout savoir sur la formation loi ALUR</a></p>
  </div>
''' + GARANTIES,
 [("Où ont lieu les formations IA immobilier dans les Alpes-Maritimes&nbsp;?", "Dans votre agence, à Nice, Cannes, Antibes, Grasse, Menton ou ailleurs dans le département, ou à distance. Nous adaptons le lieu et les dates à votre équipe."),
  ("La formation est-elle réservée aux agences&nbsp;?", "Non. Nous formons aussi les mandataires et agents commerciaux indépendants, seuls ou en petit groupe, ainsi que les directeurs d'agence."),
  ("La formation IA compte-t-elle dans les heures loi ALUR&nbsp;?", "Nos formations portent sur votre activité de transaction et donnent lieu à une attestation de formation continue. Lors de l'appel découverte, nous faisons le point sur vos heures restantes."),
  ("La formation est-elle finançable&nbsp;?", "Oui, par votre OPCO ou votre fonds d'assurance formation (AGEFICE, FIF PL…). Start Academia est certifié Qualiopi. La formation n'est pas éligible au CPF à ce jour."),
  ("Faut-il un niveau particulier en informatique&nbsp;?", "Non. Chaque parcours existe en version débutant et en version avancée."),
  ("Combien coûte une formation IA à Nice&nbsp;?", "À partir de 42 € de l'heure. Chaque formation est construite pour votre agence : le devis précis est établi après l'appel découverte, et la formation peut être prise en charge par votre OPCO ou votre fonds d'assurance formation."),
  ("Intervenez-vous à Antibes, Cannes ou Menton&nbsp;?", "Oui, dans toutes les communes des Alpes-Maritimes : Nice, Antibes, Cannes, Cagnes-sur-Mer, Grasse, Le Cannet, Menton, Saint-Laurent-du-Var, Vallauris, Mandelieu-la-Napoule et l'arrière-pays.")],
 ("Formation IA immobilier à Nice et dans les Alpes-Maritimes", "Formation pratique à l'IA et à ChatGPT pour les professionnels de l'immobilier, dans votre agence à Nice et dans les Alpes-Maritimes ou à distance."))


# ---------------------------------------------------------------- Formation immobilier Nice / 06 (formation continue, hors IA)
VILLES_06 = '''    <ul class="points villes">
      <li><strong>Formation immobilier à Nice</strong>, dans votre agence ou en groupe.</li>
      <li><strong>Formation immobilier à Antibes</strong> et Juan-les-Pins.</li>
      <li><strong>Formation immobilier à Cannes</strong>.</li>
      <li><strong>Formation immobilier à Cagnes-sur-Mer</strong>, où se trouve notre siège.</li>
      <li><strong>Formation immobilier à Grasse</strong> et dans le pays grassois.</li>
      <li><strong>Formation immobilier au Cannet</strong>.</li>
      <li><strong>Formation immobilier à Menton</strong> et sur la Riviera est.</li>
      <li><strong>Formation immobilier à Saint-Laurent-du-Var</strong>.</li>
      <li><strong>Formation immobilier à Vallauris</strong> et Golfe-Juan.</li>
      <li><strong>Formation immobilier à Mandelieu-la-Napoule</strong>.</li>
    </ul>'''

ecrire('formation-immobilier-nice/',
 "Formation immobilier à Nice et dans les Alpes-Maritimes",
 "Formation continue pour agents immobiliers, mandataires et agences à Nice et dans tout le 06 : prospection, mandat, vente, loi ALUR. Dès 42 €/h, Qualiopi.",
 "Formation immobilier à Nice et dans les Alpes-Maritimes.",
 "Des formations pour les professionnels de l'immobilier en activité&nbsp;: agents, mandataires, négociateurs, assistants et directeurs d'agence. Directement dans votre agence, partout dans le 06, ou à distance. Par des formateurs qui ont fait de la transaction sur la Côte d'Azur.",
 '''  <div class="bloc">
    <h2>Pour qui&nbsp;?</h2>
    <p>Start Academia est un organisme de <strong>formation continue</strong>&nbsp;: nous formons des professionnels déjà en poste, ou en train de démarrer leur activité, sur les gestes du métier. Nous ne préparons pas de diplôme (BTS, licence ou bachelor).</p>
    <ul class="points">
      <li><strong>Agents et mandataires indépendants</strong>, seuls ou en petit groupe.</li>
      <li><strong>Équipes d'agence</strong>&nbsp;: négociateurs, assistants commerciaux, chargés de clientèle.</li>
      <li><strong>Directeurs et managers</strong> qui veulent faire progresser leur équipe et piloter leur activité.</li>
    </ul>
  </div>
  <div class="bloc">
    <h2>Les formations, étape par étape</h2>
    <p>Chaque parcours suit la chaîne du métier et se construit avec vous, selon vos besoins et les heures loi ALUR qu'il vous reste à faire. Quelques exemples de notre catalogue&nbsp;:</p>
    <ul class="points">
      <li><strong>Prospection</strong>&nbsp;: devenir incontournable sur son secteur, dossier d'adresse, cadastre (niveaux 1 et 2), prospection par les DPE.</li>
      <li><strong>Estimation et mandat</strong>&nbsp;: préparer le rendez-vous vendeur, défendre son prix avec une analyse comparative de marché, signer et tenir l'exclusivité.</li>
      <li><strong>Vente</strong>&nbsp;: techniques de vente immobilière, découverte acquéreur, visite, négociation et suivi client.</li>
      <li><strong>Investissement locatif</strong>&nbsp;: conseiller les investisseurs sur la rentabilité et la rénovation énergétique.</li>
      <li><strong>Direction d'agence</strong>&nbsp;: piloter son équipe, ses chiffres et ses entretiens individuels.</li>
      <li><strong>Obligations réglementaires</strong>&nbsp;: non-discrimination, Tracfin et déontologie.</li>
    </ul>
    <p>L'intelligence artificielle est intégrée à chaque étape, avec nos outils maison. Pour un parcours centré sur l'IA&nbsp;: <a class="lien-texte" href="/formation-ia-nice/">formation IA immobilier à Nice</a>. <a class="lien-texte" href="/formations/">Voir les 40 formations du catalogue</a></p>
  </div>
  <div class="bloc">
    <h2>Pensée pour le marché azuréen</h2>
    <p>Résidences secondaires, clientèle internationale, biens de prestige sur le littoral, villages et maisons de l'arrière-pays, copropriétés anciennes, vendeurs exigeants et forte concurrence entre agences&nbsp;: nos exercices partent de ces situations et de vos dossiers réels, pas de cas d'école.</p>
  </div>
  <div class="bloc">
    <h2>Où nous intervenons</h2>
    <p>Nous nous déplaçons dans <strong>toutes les communes des Alpes-Maritimes</strong>, et notamment dans les dix plus grandes villes du département&nbsp;:</p>
''' + VILLES_06 + '''
    <p>Mais aussi Vence, Mougins, Valbonne et Sophia Antipolis, Biot, Villefranche-sur-Mer, Roquebrune-Cap-Martin, Beausoleil, Carros et l'arrière-pays. Nos formateurs sont basés à Cagnes-sur-Mer et à Antibes. Vos collaborateurs sont répartis sur plusieurs agences&nbsp;? La formation peut aussi se faire à distance.</p>
  </div>
  <div class="bloc">
    <h2>Format et tarif</h2>
    <ul class="points">
      <li><strong>En agence, en groupe ou en individuel</strong>, sur des journées ou des séances courtes.</li>
      <li><strong>À partir de 42&nbsp;€ de l'heure</strong>, devis précis après l'appel découverte.</li>
      <li><strong>Une attestation</strong> pour vos heures de formation continue loi ALUR. <a class="lien-texte" href="/formation-loi-alur/">Tout savoir sur la loi ALUR</a></li>
    </ul>
  </div>
  <div class="bloc">
    <h2>Ils se sont formés près de chez vous</h2>
    <p>Des agences de la Côte d'Azur nous font confiance, dont Century 21 Albert 1er, Century 21 Azurim, Century 21 Villas d'Azur, Orpi MCH Immobilier, Akorimmo, Riviera King, L'Agence Signature, Octantimmo, Agence Bristol et Marclé Real Estate. <a class="lien-texte" href="/resultats/">Voir les résultats et les 227 avis Google</a></p>
  </div>
''' + GARANTIES,
 [("Quelle formation immobilier suivre à Nice quand on est déjà agent&nbsp;?", "Une formation continue centrée sur votre métier : prospection, estimation, mandat, vente ou direction d'agence. Nous construisons le parcours avec vous lors de l'appel découverte, selon vos besoins et vos heures loi ALUR restantes."),
  ("Préparez-vous au BTS ou à un diplôme de l'immobilier&nbsp;?", "Non. Start Academia forme les professionnels en activité ou en démarrage. Pour un diplôme (BTS Professions immobilières, licence, bachelor), il faut vous tourner vers une école ou un établissement d'enseignement."),
  ("Intervenez-vous à Cannes, Antibes ou Menton&nbsp;?", "Oui, dans toutes les communes des Alpes-Maritimes : Nice, Antibes, Cannes, Cagnes-sur-Mer, Grasse, Le Cannet, Menton, Saint-Laurent-du-Var, Vallauris, Mandelieu-la-Napoule et l'arrière-pays, ou à distance."),
  ("Combien coûte une formation immobilier&nbsp;?", "À partir de 42 € de l'heure. Le devis précis est établi après l'appel découverte. La formation peut être prise en charge par votre OPCO ou votre fonds d'assurance formation (AGEFICE, FIF PL). Elle n'est pas éligible au CPF à ce jour."),
  ("Ces formations comptent-elles pour la loi ALUR&nbsp;?", "Oui. Elles portent sur votre activité de transaction et donnent lieu à une attestation pour vos heures de formation continue obligatoires.")],
 ("Formation immobilier à Nice et dans les Alpes-Maritimes", "Formation continue pour les professionnels de l'immobilier : prospection, estimation, mandat, vente, direction d'agence et obligations réglementaires, dans votre agence à Nice et dans les Alpes-Maritimes ou à distance."))

# ---------------------------------------------------------------- 5. Loi ALUR (enrichie, audit du 7 nov. 2026)
ecrire('formation-loi-alur/',
 'Formation loi ALUR à Nice et à distance | Start Academia',
 'Formation loi ALUR à Nice, dans le 06 ou à distance : 14 h par an, déontologie, non-discrimination. Agents et mandataires, dès 42 €/h, certifié Qualiopi.',
 'Formation loi ALUR pour les agents immobiliers, à Nice et à distance.',
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
    <h2>Votre formation loi ALUR à Nice et dans les Alpes-Maritimes</h2>
    <p>Nous venons dans votre agence, partout dans le 06, pour former toute l'équipe en une fois&nbsp;: Nice, Antibes, Cannes, Cagnes-sur-Mer, Grasse, Le Cannet, Menton, Saint-Laurent-du-Var, Vallauris, Mandelieu-la-Napoule et l'arrière-pays. Les mandataires et agents indépendants peuvent se regrouper sur une session ou suivre leurs heures à distance.</p>
    <p>Dans les Alpes-Maritimes, la carte professionnelle est délivrée et renouvelée par la CCI Nice Côte d'Azur&nbsp;: c'est à elle que vous présenterez vos attestations tous les 3 ans. <a class="lien-texte" href="/formation-immobilier-nice/">Nos formations immobilier à Nice et dans le 06</a></p>
  </div>
  <div class="bloc">
    <h2>À distance ou en présentiel&nbsp;?</h2>
    <p>Le texte n'impose pas de format&nbsp;: une formation suivie à distance compte autant qu'une formation en salle, si elle remplit les conditions de durée et de contenu. Nous proposons les deux, et beaucoup d'agences combinent une journée en présentiel et des séances courtes à distance.</p>
  </div>
''' + GARANTIES,
 [("Combien d'heures de formation loi ALUR faut-il faire&nbsp;?", "14 heures par an, ou 42 heures au cours de 3 années consécutives d'exercice. Sur ces 3 années, au moins 2 heures doivent porter sur la déontologie et au moins 2 heures sur la non-discrimination dans l'accès au logement."),
  ("Une formation à l'IA compte-t-elle pour la loi ALUR&nbsp;?", "Oui, si elle a un lien direct avec votre activité professionnelle. Nos formations sont appliquées à la transaction immobilière (prospection, estimation, mandat, vente) et donnent lieu à une attestation."),
  ("La formation loi ALUR peut-elle se faire à distance&nbsp;?", "Oui. Le texte n'impose pas de format : une formation à distance compte dès lors qu'elle respecte les conditions de durée et de contenu."),
  ("Les agents commerciaux et mandataires sont-ils concernés&nbsp;?", "Oui. Toutes les personnes habilitées à négocier pour le compte du titulaire de la carte, salariées ou non, doivent suivre la formation continue."),
  ("Qui contrôle les heures de formation&nbsp;?", "La CCI, lors du renouvellement de la carte professionnelle tous les 3 ans. Le titulaire de la carte vérifie de son côté les heures de ses collaborateurs."),
  ("Où suivre sa formation loi ALUR à Nice&nbsp;?", "Directement dans votre agence, partout dans les Alpes-Maritimes, ou à distance. Start Academia est installé à Cagnes-sur-Mer et forme les équipes d'agence comme les mandataires indépendants, avec une attestation pour chaque participant."),
  ("Combien coûte une formation loi ALUR&nbsp;?", "À partir de 42 € de l'heure, soit à partir de 588 € pour 14 heures. Le devis précis est établi après l'appel découverte, et la formation peut être prise en charge par votre OPCO ou votre fonds d'assurance formation."),
  ("Comment financer sa formation loi ALUR&nbsp;?", "Par l'OPCO de l'agence pour les salariés, par le FIF PL ou l'AGEFICE pour les indépendants. Start Academia est certifié Qualiopi. Nos formations ne sont pas éligibles au CPF à ce jour.")],
 ("Formation continue loi ALUR pour agents immobiliers", "Formations immobilier et IA sur mesure validant les heures de formation continue obligatoires des professionnels de l'immobilier, en agence à Nice et dans les Alpes-Maritimes ou à distance."))


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
    <p><strong>Auto-entrepreneur&nbsp;?</strong> <a class="lien-texte" href="/financement-formation-auto-entrepreneur/">Avez-vous droit aux 3&nbsp;000&nbsp;€ de l'AGEFICE&nbsp;? Conditions et calcul</a></p>
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
      <li><strong>Demande de prise en charge</strong>&nbsp;: vous la déposez sur l'espace de votre OPCO ou de votre fonds, avec notre aide. Déposez-la avant le début de la formation&nbsp;: au moins 15&nbsp;jours avant pour l'AGEFICE.</li>
      <li><strong>Formation</strong>, en agence sur la Côte d'Azur ou à distance.</li>
      <li><strong>Attestation et facture</strong>&nbsp;: vous les transmettez à votre financeur pour le remboursement.</li>
    </ol>
  </div>
  <div class="bloc">
    <h2>Et le CPF&nbsp;?</h2>
    <p>Nos formations ne sont pas éligibles au CPF à ce jour. Les heures suivies comptent en revanche dans vos <strong>14&nbsp;heures annuelles de formation continue</strong> exigées par la loi ALUR, avec attestation. <a class="lien-texte" href="/formation-loi-alur/">En savoir plus sur la loi ALUR</a></p>
  </div>
''' + PREUVES_BREF,
 [("Comment calculer mes droits à la formation&nbsp;?", "Avec le simulateur de cette page : indiquez votre chiffre d'affaires de l'année précédente déclaré à l'URSSAF (ou le montant de votre attestation CFP) si vous êtes indépendant, ou votre nombre de salariés si vous êtes employeur. Vous obtenez une estimation du budget AGEFICE ou OPCO EP mobilisable, à confirmer avec votre financeur. Vos droits CPF, eux, se consultent sur moncompteformation.gouv.fr."),
  ("Comment payer ma formation&nbsp;?", "Le plus souvent, vous n'avancez qu'une partie des frais, voire rien : votre OPCO (si vous êtes salarié), l'AGEFICE ou le FIF PL (si vous êtes indépendant) prend en charge la formation dans la limite de ses plafonds. Nous préparons le devis, le programme et la convention, et vous aidons à déposer la demande."),
  ("Quelles aides pour financer une formation dans l'immobilier&nbsp;?", "Les principales aides sont l'OPCO EP pour les salariés des agences, l'AGEFICE ou le FIF PL pour les indépendants et dirigeants, et le CPF pour les formations éligibles. Les formations Start Academia sont finançables par OPCO, AGEFICE ou FIF PL, mais pas par le CPF à ce jour."),
  ("Un auto-entrepreneur ou une micro-entreprise a-t-il un OPCO&nbsp;?", "Non. Les OPCO financent la formation des salariés. Un auto-entrepreneur (micro-entreprise), agent commercial ou mandataire, dépend d'un fonds d'assurance formation : le plus souvent le FIF PL pour les agents immobiliers, parfois l'AGEFICE. Le nom du fonds figure sur votre attestation de contribution à la formation professionnelle, dans votre espace URSSAF."),
  ("Quel OPCO pour une agence immobilière&nbsp;?", "Les agences de la branche de l'immobilier relèvent en général de l'OPCO EP. Il finance la formation des salariés, pas celle des agents commerciaux indépendants."),
  ("Quel montant puis-je obtenir&nbsp;?", "Il dépend de votre financeur et de votre statut. Pour 2026, le FIF PL prévoit pour les agents immobiliers jusqu'à 900 € par an et 300 € par jour, avec des plafonds proportionnels pour les micro-entrepreneurs. Nous vérifions avec vous les critères en vigueur."),
  ("Qui monte le dossier&nbsp;?", "La demande est déposée par vous ou votre employeur, mais nous fournissons tous les documents (devis, programme, convention, attestation) et nous vous guidons pas à pas."),
  ("Les formations Start Academia sont-elles éligibles au CPF&nbsp;?", "Pas à ce jour. Elles sont finançables par OPCO, FIF PL ou AGEFICE, et comptent pour la formation continue loi ALUR.")])


# ================================================================ Pages cas pratiques (une étape du métier = une page)
def prompt_bloc(titre, texte):
    return f'''  <div class="bloc">
    <h2>{titre}</h2>
    <p>Copiez ce prompt dans ChatGPT ou Claude, remplacez les zones entre crochets, et relisez toujours le résultat avant de l'utiliser.</p>
    <pre class="prompt-bloc">{texte}</pre>
  </div>'''


def formation_bloc(texte):
    return f'''  <div class="bloc">
    <h2>La formation qui va avec</h2>
    <p>{texte}</p>
    <p><a class="lien-texte" href="/formations/">Voir le catalogue des formations</a> &nbsp; <a class="lien-texte" href="/formation-ia-immobilier/">Voir la formation IA immobilier complète</a></p>
  </div>'''


AUTRES = '''  <div class="bloc">
    <h2>Les autres étapes boostées à l'IA</h2>
    <ul class="points">
      <li><a class="lien-texte" href="/prospection-immobiliere-sans-pige/">Prospecter sans pige depuis le 11 août 2026</a></li>
      <li><a class="lien-texte" href="/ia-prospection-immobiliere/">Prospection immobilière avec l'IA</a></li>
      <li><a class="lien-texte" href="/ia-estimation-immobiliere/">Estimation immobilière avec l'IA</a></li>
      <li><a class="lien-texte" href="/ia-mandat-exclusif/">Rentrer un mandat exclusif avec l'IA</a></li>
      <li><a class="lien-texte" href="/ia-annonce-immobiliere/">Rédiger une annonce immobilière avec l'IA</a></li>
      <li><a class="lien-texte" href="/ia-decouverte-acquereur/">Découverte acquéreur avec l'IA</a></li>
      <li><a class="lien-texte" href="/ia-visite-immobiliere/">Préparer et suivre une visite avec l'IA</a></li>
      <li><a class="lien-texte" href="/ia-negociation-immobiliere/">Négocier une offre avec l'IA</a></li>
    </ul>
  </div>'''

# ---------------------------------------------------------------- Cas pratique 1 : prospection
ecrire('ia-prospection-immobiliere/',
 "Prospection immobilière avec l'IA | Start Academia",
 "Prospecter son secteur avec l'IA : dossier d'adresse, signaux de vente, courriers personnalisés, routine de 45 minutes. Méthode, prompt gratuit et formation.",
 "Prospection immobilière avec l'IA.",
 "Le boîtage au hasard et les scripts d'appel tout faits ne rentrent plus de vendeurs. L'IA ne remplace pas le terrain&nbsp;: elle vous aide à arriver chez le bon propriétaire, au bon moment, avec quelque chose d'utile à lui apporter.",
 '''  <div class="bloc">
    <h2>Le cas en agence</h2>
    <p>Un conseiller finit sa semaine épuisé&nbsp;: photos, visites, flyers, mails, publications. À la question «&nbsp;quel vendeur as-tu fait avancer cette semaine&nbsp;?&nbsp;», le silence. Il n'a pas manqué d'activité, il a confondu activité et prospection. Le problème n'est pas le temps passé, c'est l'absence de méthode pour choisir où frapper et quoi dire.</p>
  </div>
  <div class="bloc">
    <h2>La méthode classique, boostée à l'IA</h2>
    <ol class="points numerotes">
      <li><strong>Choisir son secteur.</strong> Les fondamentaux ne changent pas&nbsp;: un périmètre que vous connaissez, où vous pouvez être reconnu. L'IA vous aide à le lire&nbsp;: ventes passées, types de biens, signaux de vente.</li>
      <li><strong>Préparer chaque adresse.</strong> Avec <strong>Academia Secteur</strong>, notre outil maison, vous générez un <strong>dossier d'adresse</strong>&nbsp;: environnement, ventes récentes du quartier, vie locale avec «&nbsp;Vivre ici&nbsp;». Vous arrivez avec une information utile, pas avec un prix.</li>
      <li><strong>Écrire le bon message.</strong> ChatGPT ou Claude rédigent un courrier ou un message adapté au propriétaire et à la situation (succession, départ en retraite, bien vacant), que vous relisez et signez.</li>
      <li><strong>Tenir une routine.</strong> Une <strong>routine secteur de 45 minutes</strong> par jour&nbsp;: signaux du jour, deux dossiers d'adresse, trois messages, une relance. La régularité fait la différence, l'IA la rend tenable.</li>
    </ol>
  </div>
  <div class="bloc">
    <h2>Ce que vous gagnez</h2>
    <ul class="points">
      <li><strong>Un dossier d'adresse en quelques minutes</strong> au lieu d'une recherche à la main sur plusieurs sites.</li>
      <li><strong>Une routine de 45 minutes</strong> qui remplace des après-midi de boîtage sans suivi.</li>
      <li><strong>Des messages personnalisés</strong> au lieu du même courrier pour toute la rue.</li>
    </ul>
  </div>
''' + prompt_bloc("Prompt gratuit : le courrier de prospection", '''Rôle : tu es un conseiller immobilier expérimenté sur [VILLE / QUARTIER].
Contexte : je prospecte la rue [NOM DE LA RUE]. Ventes récentes du quartier : [2 OU 3 EXEMPLES, TYPE ET SURFACE, SANS NOM DE PROPRIÉTAIRE]. Mon point fort : [CE QUE TU APPORTES].
Tâche : rédige un courrier de prospection de 120 mots pour les propriétaires de la rue. Apporte une information utile sur le marché local, ne promets aucun prix, termine par une proposition simple (un échange de 15 minutes).
Format : un objet, le courrier, une signature avec [TON NOM], [TON AGENCE], [TA CARTE PRO].''') + '''
  <div class="bloc">
    <h2>Erreurs fréquentes et règles à respecter</h2>
    <ul class="points">
      <li><strong>Annoncer un prix par courrier.</strong> Une estimation se fait après visite. Le courrier ouvre la porte, il ne la referme pas.</li>
      <li><strong>Mettre des données personnelles dans l'IA.</strong> Pas de nom, de téléphone ou de situation familiale de propriétaires dans ChatGPT. Travaillez avec des informations anonymisées.</li>
      <li><strong>Prospecter sans respecter le RGPD.</strong> Le courrier postal est possible, avec un moyen simple de ne plus être sollicité. Depuis le 11 août 2026, appeler un particulier exige son consentement préalable, même s'il a publié une annonce. Pour l'e-mail ou le SMS, il faut aussi son accord préalable. <a class="lien-texte" href="/prospection-immobiliere-sans-pige/">Notre guide pour prospecter sans pige</a></li>
      <li><strong>Envoyer sans relire.</strong> L'IA peut inventer un chiffre ou un nom de rue. Vous signez, vous vérifiez.</li>
    </ul>
  </div>
''' + formation_bloc("La prospection est au cœur de nos formations IA, avec un atelier sur votre propre secteur et l'accès à nos outils maison (Academia Secteur, Academia Localisateur). Nous proposons aussi des parcours dédiés à la prospection et au développement d'un secteur.") + '\n' + AUTRES + '\n' + GARANTIES,
 [("L'IA peut-elle trouver des vendeurs à ma place&nbsp;?", "Non. Elle vous fait gagner du temps sur la préparation et l'écriture, et vous aide à repérer les bons signaux. La relation avec le propriétaire reste votre métier."),
  ("Quel outil utiliser pour prospecter avec l'IA&nbsp;?", "ChatGPT ou Claude pour écrire, et un outil de dossier d'adresse comme Academia Secteur pour préparer le terrain. Nous choisissons toujours l'outil le plus simple pour la tâche."),
  ("Peut-on envoyer des e-mails de prospection à des particuliers&nbsp;?", "Seulement avec leur accord préalable. Le courrier postal reste possible, avec un moyen simple de s'opposer à la sollicitation. Pour le téléphone, il faut le consentement préalable du particulier depuis le 11 août 2026."),
  ("Combien de temps faut-il pour voir des résultats&nbsp;?", "La prospection reste un travail de régularité. La méthode vise une routine courte et tenue chaque jour plutôt que de gros efforts ponctuels.")],
 ("Prospection immobilière avec l'IA", "Méthode de prospection de secteur augmentée par l'IA : dossier d'adresse, signaux de vente, courriers personnalisés et routine quotidienne."))

# ---------------------------------------------------------------- Cas pratique 2 : estimation
ecrire('ia-estimation-immobiliere/',
 "Estimation immobilière avec l'IA | Start Academia",
 "Estimer un bien avec l'IA : analyse comparative de marché, avis de valeur argumenté, présentation au vendeur. Méthode, prompt gratuit et formation.",
 "Estimation immobilière avec l'IA.",
 "Le vendeur a déjà vu trois estimations en ligne et deux confrères. Ce qui fait la différence, ce n'est pas le chiffre&nbsp;: c'est la façon dont vous l'expliquez. L'IA vous aide à construire une analyse comparative solide et à la présenter clairement.",
 '''  <div class="bloc">
    <h2>Le cas en agence</h2>
    <p>Un vendeur vous reçoit avec un prix en tête, souvent trop haut. Si vous arrivez avec un simple chiffre, vous entrez dans une enchère avec les autres agences. Si vous arrivez avec une analyse claire du marché, vous devenez celui qui conseille.</p>
  </div>
  <div class="bloc">
    <h2>La méthode classique, boostée à l'IA</h2>
    <ol class="points numerotes">
      <li><strong>Visiter et relever.</strong> Rien ne remplace la visite&nbsp;: état, exposition, nuisances, travaux à prévoir. Vous dictez vos observations à l'IA au lieu de les retaper le soir.</li>
      <li><strong>Construire l'ACM.</strong> Avec notre outil <strong>Academia ACM</strong>, vous rassemblez les biens comparables (vendus, en vente, retirés) et vous les comparez point par point.</li>
      <li><strong>Argumenter.</strong> ChatGPT ou Claude transforment vos relevés et votre ACM en un avis de valeur lisible&nbsp;: points forts, points faibles, fourchette, stratégie de prix.</li>
      <li><strong>Présenter.</strong> Gamma met l'avis de valeur en forme en quelques minutes, à vos couleurs, pour le présenter au vendeur ou le lui envoyer.</li>
    </ol>
  </div>
  <div class="bloc">
    <h2>Ce que vous gagnez</h2>
    <ul class="points">
      <li><strong>Un avis de valeur argumenté</strong> au lieu d'un chiffre seul, qui défend le prix par le marché.</li>
      <li><strong>Une présentation professionnelle</strong> sans passer votre soirée sur la mise en page.</li>
      <li><strong>Un vendeur qui comprend</strong> pourquoi le prix est juste, et qui revient vers vous.</li>
    </ul>
  </div>
''' + prompt_bloc("Prompt gratuit : l'avis de valeur argumenté", '''Rôle : tu es un conseiller immobilier qui prépare un avis de valeur pour un vendeur.
Contexte : bien = [TYPE, SURFACE, PIÈCES, ÉTAGE, EXTÉRIEUR, DPE]. Mes relevés de visite : [POINTS FORTS / POINTS FAIBLES / TRAVAUX]. Biens comparables : [3 À 5 BIENS : SURFACE, PRIX, VENDU OU EN VENTE, DÉLAI].
Tâche : rédige un avis de valeur clair. Explique comment chaque comparable justifie la fourchette, sans jargon. Propose une stratégie de prix et ce qui se passe si le prix est trop haut.
Format : 1. Le bien en 3 lignes. 2. Le marché en 5 lignes. 3. La fourchette argumentée. 4. La stratégie conseillée.''') + '''
  <div class="bloc">
    <h2>Erreurs fréquentes et règles à respecter</h2>
    <ul class="points">
      <li><strong>Laisser l'IA fixer le prix.</strong> ChatGPT n'a pas accès à vos ventes réelles et peut inventer des références. Le prix vient de vos comparables, l'IA aide à l'expliquer.</li>
      <li><strong>Estimer sans visite.</strong> Un avis de valeur sérieux suppose d'avoir vu le bien.</li>
      <li><strong>Mettre le nom du vendeur ou l'adresse exacte dans l'IA.</strong> Décrivez le bien sans données personnelles.</li>
      <li><strong>Oublier le DPE.</strong> La performance énergétique pèse sur le prix et sur les possibilités de location&nbsp;: intégrez-la dans l'analyse.</li>
    </ul>
  </div>
''' + formation_bloc("L'estimation est travaillée dans nos formations IA avec votre propre dossier&nbsp;: relevés de visite, ACM avec notre outil maison Academia ACM, avis de valeur et présentation au vendeur.") + '\n' + AUTRES + '\n' + GARANTIES,
 [("L'IA peut-elle estimer un bien immobilier&nbsp;?", "Elle peut aider à analyser et à présenter, mais elle ne remplace ni la visite ni vos comparables. Les estimations automatiques en ligne servent de repère, pas d'avis de valeur."),
  ("Qu'est-ce qu'une ACM&nbsp;?", "Une analyse comparative de marché : la comparaison du bien avec des biens similaires vendus, en vente ou retirés du marché. C'est la base d'un prix argumenté."),
  ("Quel outil pour présenter une estimation&nbsp;?", "Gamma permet de mettre en forme un avis de valeur en quelques minutes. Nous montrons aussi comment garder la charte de votre agence."),
  ("Peut-on utiliser ChatGPT avec des données de vendeur&nbsp;?", "Évitez les données personnelles (nom, adresse exacte, situation). Décrivez le bien : c'est suffisant pour obtenir une bonne analyse.")],
 ("Estimation immobilière avec l'IA", "Construire une analyse comparative de marché et un avis de valeur argumenté avec l'IA, puis le présenter au vendeur."))

# ---------------------------------------------------------------- Cas pratique 3 : mandat exclusif
ecrire('ia-mandat-exclusif/',
 "Rentrer un mandat exclusif avec l'IA | Start Academia",
 "Préparer le rendez-vous vendeur en 15 minutes, comprendre son profil, envoyer le compte rendu dans la demi-heure : rentrer des mandats exclusifs avec l'IA.",
 "Rentrer un mandat exclusif avec l'IA.",
 "Le mandat exclusif se gagne avant, pendant et juste après le rendez-vous vendeur. L'IA vous aide à arriver préparé, à comprendre la personne en face de vous et à envoyer un suivi plus rapide que tous vos confrères.",
 '''  <div class="bloc">
    <h2>Le cas en agence</h2>
    <p>Trois agences ont vu le même vendeur dans la semaine. Elles ont toutes parlé de leur réseau et de leurs portails. Celle qui signe l'exclusivité est souvent celle qui a le mieux compris le projet du vendeur et qui lui a envoyé, le jour même, un compte rendu clair avec la suite.</p>
  </div>
  <div class="bloc">
    <h2>La méthode classique, boostée à l'IA</h2>
    <ol class="points numerotes">
      <li><strong>Préparer le premier rendez-vous en 15 minutes.</strong> Dossier d'adresse avec Academia Secteur, ventes du quartier, questions de découverte&nbsp;: vos outils de prospection deviennent vos outils de préparation.</li>
      <li><strong>Comprendre le vendeur.</strong> Avec <strong>Academia Profiling</strong>, notre outil maison, vous identifiez le profil de votre interlocuteur et la façon de lui parler. Gemini Notebook vous aide à retrouver l'essentiel dans ses documents (diagnostics, règlement de copropriété).</li>
      <li><strong>Envoyer le compte rendu dans la demi-heure.</strong> Vous dictez vos notes après le rendez-vous, l'IA les met en forme, vous relisez et vous envoyez&nbsp;: le vendeur reçoit un récapitulatif avant même d'avoir appelé une autre agence.</li>
      <li><strong>Revenir avec le bon dossier.</strong> Au deuxième rendez-vous, l'analyse de marché et le plan de commercialisation défendent l'exclusivité par les faits, pas par la promesse.</li>
      <li><strong>Suivre le vendeur.</strong> Un process de suivi régulier, préparé avec l'IA, montre au vendeur ce que vous faites pour lui chaque semaine.</li>
    </ol>
  </div>
  <div class="bloc">
    <h2>Ce que vous gagnez</h2>
    <ul class="points">
      <li><strong>15 minutes de préparation</strong> pour un premier rendez-vous vendeur, au lieu d'arriver les mains vides ou d'y passer une heure.</li>
      <li><strong>Un compte rendu envoyé dans la demi-heure</strong> au lieu du lendemain, ou jamais.</li>
      <li><strong>Un discours adapté au profil du vendeur</strong>, ce qui change le rapport de force sur l'exclusivité.</li>
    </ul>
  </div>
''' + prompt_bloc("Prompt gratuit : le compte rendu du rendez-vous vendeur", '''Rôle : tu es mon assistant de conseiller immobilier.
Contexte : je sors d'un premier rendez-vous avec un vendeur. Mes notes brutes : [COLLE OU DICTE TES NOTES, SANS NOM NI ADRESSE]. Ce que je propose : [MANDAT EXCLUSIF, DURÉE, PLAN D'ACTION].
Tâche : rédige le mail de compte rendu au vendeur. Reprends son projet avec ses mots, les points clés du bien, ce que j'ai compris de ses attentes, puis les prochaines étapes datées.
Format : un objet, 150 mots maximum, ton chaleureux et professionnel, vouvoiement, signature [TON NOM], [TON AGENCE].''') + '''
  <div class="bloc">
    <h2>Erreurs fréquentes et règles à respecter</h2>
    <ul class="points">
      <li><strong>Envoyer le compte rendu sans relire.</strong> L'IA peut mal comprendre une note. Ce mail engage votre agence.</li>
      <li><strong>Utiliser le profiling pour manipuler.</strong> Il sert à mieux écouter et à adapter votre discours, pas à forcer une décision.</li>
      <li><strong>Négocier sans mandat signé.</strong> La loi Hoguet impose un mandat écrit avant toute action de commercialisation. La clause d'exclusivité doit figurer en caractères très apparents.</li>
      <li><strong>Mettre des données sensibles dans l'IA.</strong> Pas de situation de santé, de divorce ou de succession nominative dans ChatGPT&nbsp;: gardez ces informations dans votre dossier.</li>
    </ul>
  </div>
''' + formation_bloc("Le rendez-vous vendeur est un des modules les plus demandés&nbsp;: préparation du premier rendez-vous, découverte avec Academia Profiling et Gemini Notebook, compte rendu immédiat, deuxième rendez-vous et suivi vendeur, avec un atelier sur vos propres dossiers.") + '\n' + AUTRES + '\n' + GARANTIES,
 [("Comment l'IA aide-t-elle à rentrer un mandat exclusif&nbsp;?", "En vous faisant arriver mieux préparé, en vous aidant à comprendre le vendeur et en envoyant un compte rendu clair très vite après le rendez-vous. La signature reste une affaire de confiance."),
  ("Qu'est-ce que l'outil Academia Profiling&nbsp;?", "Un outil maison de Start Academia qui aide à identifier le profil d'un vendeur pour adapter sa façon de lui parler. Il est utilisé pendant la formation."),
  ("Peut-on enregistrer un rendez-vous vendeur&nbsp;?", "Seulement avec l'accord explicite du vendeur, en lui expliquant à quoi sert l'enregistrement. Sinon, prenez des notes et dictez-les après."),
  ("Que dit la loi Hoguet sur le mandat exclusif&nbsp;?", "Le mandat doit être écrit et signé avant toute action de commercialisation, et la clause d'exclusivité doit apparaître en caractères très apparents.")],
 ("Rentrer un mandat exclusif avec l'IA", "Préparer le rendez-vous vendeur, comprendre le profil du vendeur, envoyer un compte rendu immédiat et suivre le vendeur avec l'IA."))

# ---------------------------------------------------------------- Cas pratique 4 : annonce
ecrire('ia-annonce-immobiliere/',
 "Rédiger une annonce immobilière avec l'IA | Start Academia",
 "Écrire une annonce immobilière avec ChatGPT ou Claude : texte qui donne envie, déclinaisons par portail, mentions obligatoires et DPE. Prompt gratuit.",
 "Rédiger une annonce immobilière avec l'IA.",
 "Une annonce n'est neuve qu'une seule fois. L'IA vous aide à écrire un texte qui donne envie de visiter, à le décliner pour chaque portail et réseau social, sans jamais oublier les mentions obligatoires.",
 '''  <div class="bloc">
    <h2>Le cas en agence</h2>
    <p>Le mandat est signé, le vendeur attend de voir son bien en ligne. L'annonce est souvent écrite vite, le soir, sur le même modèle que les autres&nbsp;: «&nbsp;Rare&nbsp;!&nbsp;», «&nbsp;Coup de cœur assuré&nbsp;». Elle ne se distingue pas et le vendeur le voit.</p>
  </div>
  <div class="bloc">
    <h2>La méthode classique, boostée à l'IA</h2>
    <ol class="points numerotes">
      <li><strong>Partir des faits.</strong> Surface, pièces, exposition, extérieur, DPE, charges, ce qui rend le bien unique. Vous les dictez ou les collez depuis votre logiciel.</li>
      <li><strong>Écrire l'annonce principale.</strong> ChatGPT ou Claude rédigent un texte qui parle à l'acquéreur visé (famille, investisseur, résidence secondaire), sans superlatifs vides.</li>
      <li><strong>Décliner par canal.</strong> Une version portail, une version réseaux sociaux, une version en anglais ou en italien pour la clientèle étrangère, à partir du même texte.</li>
      <li><strong>Faire vivre l'annonce.</strong> Une rotation sur 15 jours&nbsp;: nouvel angle, nouvelle photo de tête, nouveau titre, pour relancer l'intérêt sans baisser le prix.</li>
      <li><strong>Vérifier les mentions.</strong> Une relecture systématique des mentions obligatoires avant publication.</li>
    </ol>
  </div>
  <div class="bloc">
    <h2>Ce que vous gagnez</h2>
    <ul class="points">
      <li><strong>Une annonce et ses déclinaisons</strong> rédigées en une fois, au lieu de réécrire pour chaque portail.</li>
      <li><strong>Des annonces en langue étrangère</strong> sans passer par un traducteur.</li>
      <li><strong>Un vendeur rassuré</strong> qui voit son bien mis en valeur dès la mise en ligne.</li>
    </ul>
  </div>
''' + prompt_bloc("Prompt gratuit : l'annonce qui donne envie", '''Rôle : tu es un rédacteur d'annonces immobilières qui connaît [VILLE / QUARTIER].
Contexte : bien = [TYPE, SURFACE, PIÈCES, ÉTAGE, EXPOSITION, EXTÉRIEUR, STATIONNEMENT]. Ce qui le rend unique : [2 OU 3 POINTS]. Acquéreur visé : [FAMILLE / INVESTISSEUR / RÉSIDENCE SECONDAIRE].
Tâche : rédige une annonce de 150 mots qui donne envie de visiter, concrète, sans superlatifs vides (pas de « rare », « coup de cœur », « exceptionnel »). Puis une version de 50 mots pour les réseaux sociaux.
Format : un titre de 60 caractères, l'annonce, la version courte. Laisse à la fin les champs à compléter : prix, honoraires, DPE et GES, coûts annuels d'énergie, copropriété.''') + '''
  <div class="bloc">
    <h2>Erreurs fréquentes et règles à respecter</h2>
    <ul class="points">
      <li><strong>Publier sans les mentions obligatoires.</strong> Prix, honoraires et à qui ils incombent, classes énergie et climat du DPE, estimation des coûts annuels d'énergie, et pour une copropriété le nombre de lots, les charges annuelles et les éventuelles procédures en cours.</li>
      <li><strong>Laisser l'IA inventer.</strong> Une vue mer «&nbsp;dégagée&nbsp;» ou une surface arrondie engagent votre responsabilité. Chaque information doit être vérifiée.</li>
      <li><strong>Écrire une annonce discriminante.</strong> Aucune mention sur le profil des acquéreurs ou des locataires recherchés.</li>
      <li><strong>Copier l'annonce d'un confrère.</strong> L'IA réécrit, mais c'est votre bien et votre texte.</li>
    </ul>
  </div>
''' + formation_bloc("La rédaction d'annonces est travaillée dans nos formations ChatGPT et IA immobilier&nbsp;: annonce principale, déclinaisons par canal, version en langue étrangère, rotation et vérification des mentions obligatoires.") + '\n' + AUTRES + '\n' + GARANTIES,
 [("Peut-on rédiger une annonce immobilière avec ChatGPT&nbsp;?", "Oui, à condition de lui donner des informations exactes et de relire. L'IA écrit, vous vérifiez les faits et les mentions obligatoires."),
  ("Quelles sont les mentions obligatoires d'une annonce immobilière&nbsp;?", "Le prix, les honoraires et la partie qui les paie, les classes énergie et climat du DPE, l'estimation des coûts annuels d'énergie et, en copropriété, le nombre de lots, les charges annuelles et les procédures en cours."),
  ("ChatGPT ou Claude pour écrire une annonce&nbsp;?", "Les deux conviennent. Nous montrons les deux en formation et vous gardez celui qui écrit le plus comme vous."),
  ("Peut-on traduire une annonce avec l'IA&nbsp;?", "Oui, c'est un vrai gain sur la Côte d'Azur. Faites relire la version traduite si l'enjeu est important.")],
 ("Rédiger une annonce immobilière avec l'IA", "Rédiger une annonce immobilière conforme et efficace avec l'IA, la décliner par canal et en langue étrangère."))


# ---------------------------------------------------------------- Cas pratique 5 : découverte acquéreur
ecrire('ia-decouverte-acquereur/',
 "Découverte acquéreur avec l'IA | Start Academia",
 "Réussir la découverte acquéreur avec l’IA : profil, vrais critères, quartier, financement. Méthode, prompt gratuit et formation pour agents immobiliers.",
 "Découverte acquéreur avec l'IA.",
 "Un acquéreur mal découvert, c'est dix visites pour rien. L'IA ne fait pas la découverte à votre place&nbsp;: elle vous aide à la préparer, à aller chercher les vrais critères derrière la liste de souhaits, et à transformer vos notes en fiche exploitable.",
 '''  <div class="bloc">
    <h2>Le cas en agence</h2>
    <p>Un acquéreur appelle pour un T3 vu sur un portail. Le conseiller prend ses critères au téléphone&nbsp;: budget, surface, quartier. Trois visites plus tard, rien ne lui plaît. Ses vrais critères (le trajet de l'école, le bruit, le financement pas encore validé) n'ont jamais été posés.</p>
  </div>
  <div class="bloc">
    <h2>La méthode classique, boostée à l'IA</h2>
    <ol class="points numerotes">
      <li><strong>Comprendre la personne.</strong> Avec <strong>Academia Profiling</strong>, notre outil maison, vous repérez la façon dont l'acquéreur décide (rapide, analytique, besoin d'être rassuré) et vous adaptez vos questions et votre discours.</li>
      <li><strong>Creuser les vrais critères.</strong> Derrière «&nbsp;un T3 lumineux&nbsp;», il y a un projet de vie. L'IA vous prépare une trame de questions ouvertes&nbsp;: pourquoi acheter, pourquoi maintenant, ce qui est négociable et ce qui ne l'est pas.</li>
      <li><strong>Vendre le quartier, pas seulement le bien.</strong> Avec <strong>Academia Vivre ici</strong>, vous montrez écoles, commerces, transports et vie locale autour d'une adresse. L'acquéreur se projette avant même la visite.</li>
      <li><strong>Valider le financement.</strong> Apport, simulation bancaire, courtier&nbsp;: posé dès la découverte, ça évite les offres qui tombent.</li>
      <li><strong>Transformer les notes en fiche.</strong> Vous dictez vos notes en sortant du rendez-vous, l'IA en fait une fiche acquéreur claire à reporter dans votre CRM.</li>
    </ol>
  </div>
  <div class="bloc">
    <h2>Ce que vous gagnez</h2>
    <ul class="points">
      <li><strong>Moins de visites inutiles</strong>, parce que vous ne montrez que les biens qui collent aux vrais critères.</li>
      <li><strong>Une fiche acquéreur propre</strong> sans retaper vos notes le soir.</li>
      <li><strong>Un acquéreur qui vous fait confiance</strong>, parce qu'il se sent compris dès le premier échange.</li>
    </ul>
  </div>
''' + prompt_bloc("Prompt gratuit : la trame de découverte", """Rôle : tu es un conseiller immobilier expérimenté qui prépare une découverte acquéreur.
Contexte : l'acquéreur a appelé pour [TYPE DE BIEN, SECTEUR, BUDGET ANNONCÉ]. Ce que je sais déjà : [PROJET : PREMIER ACHAT / AGRANDISSEMENT / INVESTISSEMENT / RÉSIDENCE SECONDAIRE].
Tâche : prépare-moi une trame de 12 questions ouvertes pour un entretien de 20 minutes : motivation et délai, vrais critères (indispensables / souhaitables / rédhibitoires), quartier et trajets, financement (apport, banque, courtier). Pas de question sur l'origine, la religion, la santé ou la situation familiale si l'acquéreur ne l'aborde pas.
Format : 4 blocs de 3 questions, puis un modèle de fiche acquéreur à remplir.""") + '''
  <div class="bloc">
    <h2>Erreurs fréquentes et règles à respecter</h2>
    <ul class="points">
      <li><strong>Se contenter des critères du portail.</strong> Budget, surface et quartier ne disent pas pourquoi la personne achète.</li>
      <li><strong>Filtrer les acquéreurs sur des critères discriminatoires.</strong> Origine, nom, âge, situation de famille ou handicap ne peuvent jamais servir à choisir à qui présenter un bien.</li>
      <li><strong>Coller des données personnelles dans l'IA.</strong> Pas de nom, de téléphone ou de revenus détaillés dans ChatGPT&nbsp;: décrivez le projet de façon anonyme.</li>
      <li><strong>Faire visiter sans financement validé.</strong> C'est la première cause d'offre qui tombe.</li>
    </ul>
  </div>
''' + formation_bloc("La découverte acquéreur est travaillée dans nos formations avec nos outils maison Academia Profiling et Academia Vivre ici&nbsp;: trame de questions, mise en situation et fiche acquéreur.") + '\n' + AUTRES + '\n' + GARANTIES,
 [("L'IA peut-elle faire la découverte acquéreur à ma place&nbsp;?", "Non. L'échange reste humain. L'IA vous aide à préparer les questions, à adapter votre discours au profil et à mettre vos notes au propre."),
  ("Qu'est-ce que le profiling acquéreur&nbsp;?", "C'est repérer la façon dont une personne prend ses décisions pour adapter votre discours : certains veulent des chiffres, d'autres être rassurés, d'autres aller vite. Notre outil Academia Profiling vous y aide."),
  ("Peut-on mettre les informations d'un acquéreur dans ChatGPT&nbsp;?", "Évitez les données personnelles. Décrivez le projet (type de bien, budget, motivation) sans nom ni coordonnées : c'est suffisant pour obtenir une bonne trame."),
  ("Quand parler du financement&nbsp;?", "Dès la découverte. Apport, simulation et accord de principe évitent les visites et les offres qui n'aboutissent pas.")],
 ("Découverte acquéreur avec l'IA", "Préparer et mener une découverte acquéreur avec l'IA : profil de décision, vrais critères, quartier, financement et fiche acquéreur."))

# ---------------------------------------------------------------- Cas pratique 6 : visite
ecrire('ia-visite-immobiliere/',
 "Préparer une visite immobilière avec l'IA | Start Academia",
 "Préparer une visite avec l'IA, sélectionner les bons biens, faire le compte rendu au vendeur et relancer l'acquéreur. Méthode, prompt gratuit et formation.",
 "Préparer et suivre une visite avec l'IA.",
 "La visite se gagne avant et après le rendez-vous. Avant, en choisissant les bons biens et en préparant les réponses. Après, avec un compte rendu au vendeur et une relance de l'acquéreur le jour même. C'est là que l'IA fait gagner du temps.",
 '''  <div class="bloc">
    <h2>Le cas en agence</h2>
    <p>Un conseiller enchaîne quatre visites l'après-midi. Le soir, il doit faire le retour à quatre vendeurs et relancer quatre acquéreurs. Faute de temps, il appelle deux vendeurs et oublie le reste. Le vendeur sans nouvelles pense que rien ne se passe&nbsp;; l'acquéreur qui n'est pas relancé visite chez le confrère.</p>
  </div>
  <div class="bloc">
    <h2>La méthode classique, boostée à l'IA</h2>
    <ol class="points numerotes">
      <li><strong>Sélectionner les bons biens.</strong> Avec <strong>Academia Radar Acheteur</strong>, vous croisez la fiche acquéreur avec les biens disponibles et vous ne proposez que ceux qui correspondent aux vrais critères.</li>
      <li><strong>Préparer la visite.</strong> L'IA vous prépare les points forts à montrer, les objections probables (travaux, DPE, charges) et les réponses, à partir de la fiche du bien.</li>
      <li><strong>Situer le prix.</strong> Avec <strong>Academia ACM</strong>, vous montrez à l'acquéreur où se situe le bien par rapport au marché&nbsp;: il sait si le prix est juste avant de faire une offre.</li>
      <li><strong>Faire le compte rendu au vendeur.</strong> Vous dictez vos impressions en sortant, l'IA rédige un compte rendu factuel&nbsp;: ce qui a plu, ce qui freine, la suite.</li>
      <li><strong>Relancer l'acquéreur.</strong> Un message personnalisé le jour même, qui reprend ce qu'il a aimé et propose la prochaine étape.</li>
    </ol>
  </div>
  <div class="bloc">
    <h2>Ce que vous gagnez</h2>
    <ul class="points">
      <li><strong>Des visites mieux ciblées</strong>, donc moins nombreuses pour une offre.</li>
      <li><strong>Un compte rendu au vendeur après chaque visite</strong>, sans y passer la soirée. C'est ce qui fait rester un vendeur avec vous.</li>
      <li><strong>Une relance acquéreur le jour même</strong>, au moment où il est le plus motivé.</li>
    </ul>
  </div>
''' + prompt_bloc("Prompt gratuit : le compte rendu de visite au vendeur", """Rôle : tu es un conseiller immobilier qui fait son retour de visite au vendeur.
Contexte : bien = [TYPE, SECTEUR, PRIX AFFICHÉ]. Visite du [DATE] avec un acquéreur [PROFIL ANONYME : FAMILLE, INVESTISSEUR…]. Ce qui a plu : [POINTS]. Ce qui freine : [POINTS]. Suite prévue : [SECONDE VISITE / RÉFLEXION / OFFRE POSSIBLE / PAS DE SUITE].
Tâche : rédige un compte rendu de 120 mots, factuel et rassurant, sans enjoliver. Si plusieurs visites font la même remarque, propose une piste d'action (présentation, prix, petits travaux) sans l'imposer.
Format : un e-mail avec un objet, 3 paragraphes courts, une signature avec [TON NOM] et [TON AGENCE].""") + '''
  <div class="bloc">
    <h2>Erreurs fréquentes et règles à respecter</h2>
    <ul class="points">
      <li><strong>Faire visiter sans bon de visite.</strong> Il protège votre travail et votre droit à honoraires.</li>
      <li><strong>Enjoliver le retour au vendeur.</strong> Un compte rendu trop positif empêche ensuite de parler du prix.</li>
      <li><strong>Donner le nom de l'acquéreur à l'IA.</strong> Le profil suffit, sans nom ni coordonnées.</li>
      <li><strong>Laisser l'IA inventer un argument.</strong> Une école «&nbsp;à 5 minutes&nbsp;» ou un DPE «&nbsp;bientôt amélioré&nbsp;» engagent votre responsabilité&nbsp;: tout doit être vérifié.</li>
    </ul>
  </div>
''' + formation_bloc("La visite est travaillée dans nos formations avec nos outils maison Academia Radar Acheteur et Academia ACM&nbsp;: sélection des biens, préparation des objections, compte rendu vendeur et relance acquéreur.") + '\n' + AUTRES + '\n' + GARANTIES,
 [("Comment faire un compte rendu de visite au vendeur&nbsp;?", "Rapidement après la visite, de façon factuelle : ce qui a plu, ce qui freine, la suite prévue. L'IA rédige le texte à partir de vos notes dictées, vous relisez et envoyez."),
  ("L'IA peut-elle choisir les biens à faire visiter&nbsp;?", "Elle vous aide à croiser les critères de l'acquéreur avec vos biens disponibles. La décision reste la vôtre, avec votre connaissance du terrain."),
  ("Quels outils utiliser pour les visites&nbsp;?", "ChatGPT ou Claude pour les comptes rendus et les relances, et nos outils maison Academia Radar Acheteur et Academia ACM pour la sélection et le prix."),
  ("Le bon de visite est-il obligatoire&nbsp;?", "Il n'est pas imposé par la loi, mais il est vivement recommandé : il prouve que vous avez présenté le bien et protège votre droit à honoraires.")],
 ("Préparer et suivre une visite immobilière avec l'IA", "Sélection des biens, préparation des objections, compte rendu au vendeur et relance acquéreur avec l'IA."))

# ---------------------------------------------------------------- Cas pratique 7 : négociation
ecrire('ia-negociation-immobiliere/',
 "Négocier une offre immobilière avec l'IA | Start Academia",
 "Négocier une offre d'achat avec l'IA : argumenter avec le marché, préparer l'appel au vendeur, présenter l'offre. Méthode, prompt gratuit et formation.",
 "Négocier une offre avec l'IA.",
 "Une offre arrive en dessous du prix. Le vendeur se vexe, l'acquéreur se braque, et la vente se joue dans les heures qui suivent. L'IA vous aide à préparer les arguments, à choisir les mots et à présenter l'offre clairement aux deux parties.",
 '''  <div class="bloc">
    <h2>Le cas en agence</h2>
    <p>Un acquéreur fait une offre à 6&nbsp;% sous le prix affiché. Le conseiller appelle le vendeur et lui annonce le chiffre sans préparation. Le vendeur refuse par principe, l'acquéreur part sur un autre bien. Avec les bons arguments, présentés dans le bon ordre, la vente se serait peut-être faite.</p>
  </div>
  <div class="bloc">
    <h2>La méthode classique, boostée à l'IA</h2>
    <ol class="points numerotes">
      <li><strong>Recevoir une offre écrite.</strong> Prix, conditions suspensives, financement, délai&nbsp;: une offre claire et écrite, à transmettre au vendeur.</li>
      <li><strong>Argumenter avec le marché.</strong> Avec <strong>Academia ACM</strong>, vous montrez au vendeur les ventes comparables et le temps passé sur le marché. Ce n'est plus votre avis contre le sien, c'est le marché.</li>
      <li><strong>Préparer l'échange.</strong> L'IA vous aide à anticiper les réactions du vendeur selon son profil, repéré avec <strong>Academia Profiling</strong>, et à préparer vos réponses.</li>
      <li><strong>Mettre l'offre en forme.</strong> Avec <strong>Academia Radar Acheteur</strong>, vous présentez l'offre et le dossier de l'acquéreur (financement, délai) de façon professionnelle, avec le courrier de transmission.</li>
      <li><strong>Garder le lien des deux côtés.</strong> Un message à l'acquéreur pour le tenir informé pendant la réflexion du vendeur, sans promettre de réponse.</li>
    </ol>
  </div>
  <div class="bloc">
    <h2>Ce que vous gagnez</h2>
    <ul class="points">
      <li><strong>Un vendeur qui discute au lieu de refuser par principe</strong>, parce que vous lui montrez le marché.</li>
      <li><strong>Une offre présentée proprement en quelques minutes</strong>, avec le dossier de l'acquéreur.</li>
      <li><strong>Moins de ventes perdues</strong> par manque de préparation dans les heures qui comptent.</li>
    </ul>
  </div>
''' + prompt_bloc("Prompt gratuit : préparer la présentation de l'offre au vendeur", """Rôle : tu es un conseiller immobilier qui prépare l'appel au vendeur pour lui présenter une offre.
Contexte : prix affiché [PRIX], en vente depuis [DURÉE], [NOMBRE] visites. Offre reçue : [MONTANT], financement [COMPTANT / PRÊT AVEC ACCORD DE PRINCIPE / PRÊT SANS ACCORD], délai [DÉLAI]. Comparables : [2 OU 3 VENTES : SURFACE, PRIX, DÉLAI]. Profil du vendeur : [PRESSÉ / ATTACHÉ AU BIEN / TRÈS ANALYTIQUE].
Tâche : prépare le déroulé de l'appel : comment introduire l'offre, les 3 arguments de marché à utiliser, les 3 objections probables du vendeur et une réponse pour chacune. Reste neutre : je transmets l'offre, c'est le vendeur qui décide.
Format : déroulé en 5 étapes, puis un tableau objection / réponse.""") + '''
  <div class="bloc">
    <h2>Erreurs fréquentes et règles à respecter</h2>
    <ul class="points">
      <li><strong>Garder une offre pour soi.</strong> Toute offre reçue doit être transmise au vendeur, même si elle vous paraît trop basse.</li>
      <li><strong>Annoncer le chiffre sans contexte.</strong> Présentez d'abord le marché et le sérieux de l'acquéreur, ensuite le montant.</li>
      <li><strong>Laisser l'IA rédiger un compromis.</strong> L'IA prépare l'échange, pas les actes&nbsp;: le compromis et ses clauses relèvent du notaire ou d'un modèle juridique validé.</li>
      <li><strong>Mettre les noms et la situation des clients dans l'IA.</strong> Travaillez avec des données anonymisées.</li>
    </ul>
  </div>
''' + formation_bloc("La négociation est travaillée dans nos formations avec nos outils maison Academia ACM, Academia Profiling et Academia Radar Acheteur&nbsp;: préparation de l'appel vendeur, mise en forme de l'offre et suivi des deux parties.") + '\n' + AUTRES + '\n' + GARANTIES,
 [("L'IA peut-elle négocier à ma place&nbsp;?", "Non. Elle vous aide à préparer les arguments, anticiper les objections et mettre l'offre en forme. La négociation reste un échange humain."),
  ("Faut-il transmettre une offre très basse au vendeur&nbsp;?", "Oui. Le conseiller transmet toutes les offres qu'il reçoit. C'est la façon de les présenter, avec le marché, qui fait la différence."),
  ("Comment convaincre un vendeur de baisser son prix&nbsp;?", "Avec des faits : ventes comparables, temps passé sur le marché, retours de visites. Une analyse comparative de marché comme Academia ACM rend la discussion objective."),
  ("Peut-on rédiger une offre d'achat avec ChatGPT&nbsp;?", "L'IA peut aider à mettre en forme une lettre de présentation. Pour l'offre elle-même et le compromis, utilisez les modèles validés de votre agence ou du notaire.")],
 ("Négocier une offre immobilière avec l'IA", "Préparer la négociation d'une offre d'achat avec l'IA : arguments de marché, profil du vendeur, mise en forme et transmission de l'offre."))


# ---------------------------------------------------------------- Formation Claude immobilier
ecrire('formation-claude-immobilier/',
 "Formation Claude pour agents immobiliers | Start Academia",
 "Formation Claude (Anthropic) pour agents immobiliers : projets, documents longs, annonces. Dans votre agence dans le 06 ou à distance. Dès 42 €/h.",
 "Formation Claude pour agents immobiliers.",
 "Claude est l'assistant IA d'Anthropic. Il excelle là où un agent perd le plus de temps à l'écrit&nbsp;: lire un dossier de 80 pages, écrire comme vous, garder le contexte d'une agence d'un jour à l'autre. Nous vous apprenons à vous en servir sur vos vrais dossiers.",
 '''  <div class="bloc">
    <h2>Pourquoi Claude en agence</h2>
    <ul class="points">
      <li><strong>Les documents longs.</strong> Règlement de copropriété, procès-verbaux d'assemblée générale, diagnostics, PLU&nbsp;: Claude les lit en entier et en sort les points qui comptent pour votre vendeur ou votre acquéreur.</li>
      <li><strong>Un style d'écriture naturel.</strong> Annonces, courriers, comptes rendus de visite&nbsp;: des textes qui sonnent comme vous, pas comme un robot.</li>
      <li><strong>Les projets.</strong> Vous déposez une fois votre charte, vos modèles de courriers et vos argumentaires&nbsp;: Claude s'en sert à chaque demande, sans tout réexpliquer.</li>
      <li><strong>ChatGPT ou Claude&nbsp;?</strong> Les deux sont utiles. En formation, nous vous montrons lequel choisir selon la tâche, et pourquoi.</li>
    </ul>
  </div>
  <div class="bloc">
    <h2>Ce que vous apprenez, étape par étape</h2>
    <ol class="points numerotes">
      <li><strong>Prendre en main Claude</strong>&nbsp;: compte, versions, conversations, confidentialité des données clients.</li>
      <li><strong>Créer le projet de votre agence</strong>&nbsp;: vos modèles, votre ton, vos secteurs, vos mentions obligatoires.</li>
      <li><strong>Analyser un dossier de copropriété</strong>&nbsp;: synthèse des PV d'AG, travaux votés, charges, points de vigilance pour l'acquéreur.</li>
      <li><strong>Écrire au quotidien</strong>&nbsp;: annonces, comptes rendus vendeur, relances acquéreur, réponses aux avis Google.</li>
      <li><strong>Construire votre bibliothèque de prompts</strong>, livrée avec un livret tactique pour chaque méthode.</li>
    </ol>
  </div>
''' + prompt_bloc("Prompt gratuit : synthèse d'un procès-verbal d'assemblée générale", """Rôle : tu es un conseiller immobilier qui prépare la visite d'un appartement en copropriété.
Contexte : je te joins les 3 derniers procès-verbaux d'assemblée générale de la copropriété (sans les noms des copropriétaires).
Tâche : fais-moi une synthèse claire pour un acquéreur : travaux votés et à venir avec leur montant, procédures en cours, évolution des charges, points de vigilance. Signale ce que tu n'as pas trouvé dans les documents au lieu de l'inventer.
Format : 5 rubriques avec des puces, puis 3 questions à poser au syndic.""") + '''
  <div class="bloc">
    <h2>Les règles à respecter</h2>
    <ul class="points">
      <li><strong>Données personnelles</strong>&nbsp;: retirez noms, coordonnées et situations des clients avant de déposer un document.</li>
      <li><strong>Vérification</strong>&nbsp;: Claude peut se tromper. Toute information transmise à un client est vérifiée par vous.</li>
      <li><strong>Pas d'actes juridiques</strong>&nbsp;: Claude aide à comprendre et à préparer, pas à rédiger un compromis.</li>
    </ul>
  </div>
''' + formation_bloc("Claude est enseigné dans nos formations IA immobilier, en module dédié ou aux côtés de ChatGPT, Gemini Notebook et Gamma, avec nos outils maison.") + '\n' + AUTRES + '\n' + GARANTIES,
 [("Quelle différence entre Claude et ChatGPT pour un agent immobilier&nbsp;?", "Les deux sont efficaces. Claude est particulièrement à l'aise avec les documents longs et une écriture naturelle ; ChatGPT a d'autres atouts, comme la génération d'images. Nous vous montrons les deux et quand utiliser l'un ou l'autre."),
  ("Faut-il un abonnement payant à Claude&nbsp;?", "Une version gratuite existe. Pour un usage quotidien en agence et les projets, l'abonnement payant devient vite utile ; nous en parlons pendant l'appel découverte selon votre usage."),
  ("Peut-on mettre les documents d'un client dans Claude&nbsp;?", "Uniquement après avoir retiré les données personnelles (noms, coordonnées, situation). Nous montrons comment faire en formation."),
  ("Combien coûte la formation Claude&nbsp;?", "À partir de 42 € de l'heure, finançable par votre OPCO ou votre fonds d'assurance formation (AGEFICE, FIF PL). Le devis précis est établi après l'appel découverte.")],
 ("Formation Claude pour agents immobiliers", "Formation pratique à Claude (Anthropic) pour les professionnels de l'immobilier : projets d'agence, documents longs, rédaction et bibliothèque de prompts."))

# ---------------------------------------------------------------- Formation IA directeurs et managers d'agence
ecrire('formation-ia-directeur-agence-immobiliere/',
 "Formation IA directeur d'agence immobilière | Start Academia",
 "Formation IA pour directeurs et managers d'agence immobilière : pilotage, entretiens individuels, recrutement, déploiement de l'IA dans l'équipe. Dès 42 €/h.",
 "Formation IA pour directeurs et managers d'agence immobilière.",
 "Vos conseillers commencent à utiliser l'IA, chacun à sa façon. Votre rôle&nbsp;: en faire un levier collectif, mesurable et conforme. Cette formation vous donne les outils pour piloter l'activité, accompagner chaque conseiller et déployer l'IA dans toute l'agence.",
 '''  <div class="bloc">
    <h2>Le rythme de votre agence</h2>
    <div class="agence">
      <p class="plan-intro">Composez votre équipe et choisissez la fréquence de vos entretiens. Votre agence se dessine, votre mois de pilotage s'écrit en dessous.</p>
      <div class="plan-scene">
        <div class="agence-reglages">
          <div class="agence-postes">
            <div class="agence-poste" data-poste="conseillers" data-max="40"><span class="tr-label">Conseillers</span><button type="button" aria-label="Un de moins">−</button><output>6</output><button type="button" aria-label="Un de plus">+</button></div>
            <div class="agence-poste" data-poste="assistantes" data-max="10"><span class="tr-label">Assistantes</span><button type="button" aria-label="Un de moins">−</button><output>1</output><button type="button" aria-label="Un de plus">+</button></div>
            <div class="agence-poste" data-poste="managers" data-max="10"><span class="tr-label">Managers</span><button type="button" aria-label="Un de moins">−</button><output>1</output><button type="button" aria-label="Un de plus">+</button></div>
            <div class="agence-poste agence-vous"><span class="tr-label">Directeur</span><output>Vous</output></div>
          </div>
          <div class="plan-champ">
            <span class="plan-label" id="agence-freq-l">Vos entretiens individuels</span>
            <div class="plan-format agence-freq" role="group" aria-labelledby="agence-freq-l">
              <button type="button" data-freq="4" aria-pressed="false">Chaque semaine</button>
              <button type="button" data-freq="2" aria-pressed="false">Tous les quinze jours</button>
              <button type="button" data-freq="1" aria-pressed="true">Chaque mois</button>
            </div>
          </div>
        </div>
        <div class="plan-vue">
          <canvas class="plan-toile agence-toile" aria-hidden="true"></canvas>
          <p class="plan-legende"><span class="pl-session">Vous</span><span class="pl-av">Managers</span><span class="pl-deb">Conseillers</span><span class="pl-ass">Assistantes</span></p>
        </div>
      </div>
      <div class="plan-resultat" aria-live="polite">
        <div class="plan-chiffres">
          <p><strong id="ag-equipe">9</strong><span id="ag-equipe-l">personnes dans l'agence</span></p>
          <p><strong id="ag-entretiens">8</strong><span id="ag-entretiens-l">entretiens par mois</span></p>
          <p><strong id="ag-prepa">40&nbsp;min</strong><span>pour les préparer tous</span></p>
        </div>
        <ol class="plan-etapes agence-etapes">
          <li><strong>Le lundi</strong><span>Quinze minutes pour lire l'activité de l'agence et de chaque conseiller&nbsp;: rendez-vous, mandats, exclusivités, ventes.</span></li>
          <li><strong>La réunion</strong><span>Quarante-cinq minutes au plus, debout, avec un support et une sortie en action.</span></li>
          <li><strong>Les entretiens</strong><span id="ag-e3">Un entretien chaque mois avec chacun, soit 8 entretiens par mois. Cinq minutes de préparation chacun, à partir des indicateurs du conseiller&nbsp;: 40 min par mois.</span></li>
          <li><strong>Le cadre</strong><span>Une charte d'usage de l'IA pour toute l'agence&nbsp;: données clients, RGPD, relecture de ce que l'IA produit.</span></li>
        </ol>
        <ul class="semaine-programme" id="ag-plan"></ul>
        <div class="plan-actions">
          <a class="action agence-appel" href="https://meet.brevo.com/jean-guy-ourmieres/appel-decouverte" rel="noopener">Parler de mon agence&nbsp;: réserver l'appel<svg aria-hidden="true"><use href="#fleche"/></svg></a>
          <button type="button" class="plan-copier" hidden>Copier mon plan</button>
          <span class="plan-note">Devis établi après l'appel découverte de 30 minutes.</span>
        </div>
      </div>
    </div>
  </div>
  <div class="bloc">
    <h2>Et votre semaine de directeur&nbsp;?</h2>
    <div class="semaine" data-pour="votre équipe et vos clients" data-evenement="semaine_directeur">
      <p class="plan-intro">Cochez vos tâches et indiquez le temps que vous y passez aujourd'hui. La seconde pile, c'est la même semaine avec la méthode.</p>
      <div class="plan-scene">
        <div class="semaine-choix">
          <fieldset class="semaine-etape"><legend>Piloter</legend><ul>
            <li class="tache"><label><input type="checkbox" data-ia="15"><span class="tache-nom">Lire l'activité de l'agence et de chaque conseiller</span><em class="tache-ia">15&nbsp;min avec la méthode</em></label></li>
            <li class="tache"><label><input type="checkbox" data-ia="5"><span class="tache-nom">Préparer un entretien individuel</span><em class="tache-ia">5&nbsp;min avec la méthode</em></label></li>
          </ul></fieldset>
          <fieldset class="semaine-etape"><legend>Animer</legend><ul>
            <li class="tache"><label><input type="checkbox" data-ia="1"><span class="tache-nom">Préparer la réunion d'équipe</span><em class="tache-ia">1&nbsp;min avec la méthode</em></label></li>
            <li class="tache"><label><input type="checkbox" data-ia="5"><span class="tache-nom">Préparer une formation ou un atelier pour l'équipe</span><em class="tache-ia">5&nbsp;min avec la méthode</em></label></li>
          </ul></fieldset>
          <fieldset class="semaine-etape"><legend>Faire grandir l'équipe</legend><ul>
            <li class="tache"><label><input type="checkbox" data-ia="30"><span class="tache-nom">Coacher un agent, mail de récap et plan d'action compris</span><em class="tache-ia">30&nbsp;min avec la méthode</em></label></li>
            <li class="tache"><label><input type="checkbox" data-ia="10"><span class="tache-nom">Recruter&nbsp;: annonce, tri des candidatures, préparation de l'entretien</span><em class="tache-ia">10&nbsp;min avec la méthode</em></label></li>
          </ul></fieldset>
          <fieldset class="semaine-etape"><legend>Gérer l'agence</legend><ul>
            <li class="tache"><label><input type="checkbox" data-gain="30"><span class="tache-nom">Traiter l'administratif&nbsp;: courriers, mails, comptes rendus</span><em class="tache-ia">30&nbsp;% de temps gagné</em></label></li>
            <li class="tache"><label><input type="checkbox" data-gain="50"><span class="tache-nom">Suivre la comptabilité&nbsp;: honoraires et commissions</span><em class="tache-ia">50&nbsp;% de temps gagné</em></label></li>
            <li class="tache"><label><input type="checkbox" data-ia="2"><span class="tache-nom">Répondre à une question juridique de l'équipe</span><em class="tache-ia">2&nbsp;min avec la méthode</em></label></li>
            <li class="tache"><label><input type="checkbox" data-ia="5"><span class="tache-nom">Planifier les publications de l'agence</span><em class="tache-ia">5&nbsp;min avec la méthode</em></label></li>
            <li class="tache"><label><input type="checkbox" data-ia="2"><span class="tache-nom">Répondre à un avis client</span><em class="tache-ia">2&nbsp;min avec la méthode</em></label></li>
          </ul></fieldset>
        </div>
        <div class="plan-vue semaine-vue">
          <canvas class="plan-toile semaine-toile" aria-hidden="true"></canvas>
          <p class="plan-legende"><span class="pl-session">Aujourd'hui</span><span class="pl-deb">Avec la méthode</span><span class="plan-echelle">1 étage = 1 heure</span></p>
        </div>
      </div>
      <div class="plan-resultat" aria-live="polite">
        <div class="plan-chiffres">
          <p><strong id="sm-auj">0&nbsp;min</strong><span>aujourd'hui, par semaine</span></p>
          <p><strong id="sm-ia">0&nbsp;min</strong><span>avec la méthode</span></p>
          <p><strong id="sm-gain">–</strong><span>rendues à votre équipe</span></p>
        </div>
        <p class="semaine-phrase" id="sm-phrase">Cochez une première tâche pour commencer.</p>
        <ul class="semaine-programme" id="sm-programme" hidden></ul>
        <div class="plan-actions">
          <a class="action semaine-appel" href="https://meet.brevo.com/jean-guy-ourmieres/appel-decouverte" rel="noopener">Parler de mon agence&nbsp;: réserver l'appel<svg aria-hidden="true"><use href="#fleche"/></svg></a>
          <button type="button" class="plan-copier" hidden>Copier ma semaine</button>
          <span class="plan-note">Temps annoncés dans nos formations, une fois l'outil en place. Les pourcentages s'appliquent à votre temps actuel.</span>
        </div>
      </div>
    </div>
  </div>
  <div class="bloc">
    <h2>Le cas en agence</h2>
    <p>Un directeur passe ses lundis à compiler des chiffres dans trois logiciels, prépare ses entretiens individuels de mémoire, et découvre que deux conseillers collent les coordonnées de vendeurs dans ChatGPT. Il n'a pas besoin d'un outil de plus&nbsp;: il a besoin d'une méthode de pilotage et de règles communes.</p>
  </div>
  <div class="bloc">
    <h2>La méthode classique, boostée à l'IA</h2>
    <ol class="points numerotes">
      <li><strong>Piloter avec les bons indicateurs.</strong> Avec <strong>Academia Pilotage</strong>, notre outil maison, vous suivez l'activité de l'agence et de chaque conseiller&nbsp;: rendez-vous, mandats, exclusivités, ventes.</li>
      <li><strong>Préparer des entretiens individuels utiles.</strong> Avec <strong>Academia Parcours</strong>, chaque conseiller a son diagnostic de performance immobilière et ses objectifs. L'entretien part des faits, pas des impressions.</li>
      <li><strong>Recruter et intégrer plus vite.</strong> L'IA vous aide à rédiger l'annonce de recrutement, à préparer l'entretien et à construire le parcours d'intégration du nouveau conseiller.</li>
      <li><strong>Déployer l'IA dans l'équipe.</strong> Une charte d'usage de l'IA pour l'agence (RGPD, données clients, vérification), des prompts partagés, et un plan de formation par poste.</li>
    </ol>
  </div>
  <div class="bloc">
    <h2>Ce que vous gagnez</h2>
    <ul class="points">
      <li><strong>Un point d'activité hebdomadaire prêt.</strong> Sans compiler les chiffres à la main.</li>
      <li><strong>Des entretiens individuels préparés.</strong> À partir de données, avec des objectifs suivis.</li>
      <li><strong>Une équipe qui utilise l'IA de la même façon.</strong> Dans un cadre conforme.</li>
    </ul>
  </div>
''' + prompt_bloc("Prompt gratuit : préparer un entretien individuel", """Rôle : tu es un directeur d'agence immobilière expérimenté qui prépare l'entretien mensuel d'un conseiller.
Contexte : indicateurs du mois du conseiller [RENDEZ-VOUS VENDEURS, ESTIMATIONS, MANDATS, DONT EXCLUSIFS, VISITES, OFFRES, VENTES] et ceux du mois précédent. Objectifs fixés : [OBJECTIFS]. Ce que j'ai observé : [POINTS FORTS / DIFFICULTÉS].
Tâche : prépare-moi un déroulé d'entretien de 30 minutes : ce qui progresse, le point bloquant principal dans la chaîne (prospection, estimation, mandat, visite, offre), 2 actions concrètes pour le mois prochain et la façon de les suivre. Ton bienveillant et exigeant.
Format : déroulé en 4 temps, puis 5 questions ouvertes à poser au conseiller.""") + '''
  <div class="bloc">
    <h2>Erreurs fréquentes et règles à respecter</h2>
    <ul class="points">
      <li><strong>Laisser chacun utiliser l'IA sans cadre.</strong> Sans charte commune, les données clients finissent dans des outils non maîtrisés.</li>
      <li><strong>Piloter uniquement au chiffre d'affaires.</strong> Il arrive trop tard. Les indicateurs d'activité permettent d'agir avant.</li>
      <li><strong>Mettre les données nominatives des salariés dans l'IA.</strong> Travaillez avec des indicateurs anonymisés.</li>
      <li><strong>Former l'équipe d'un bloc.</strong> Un débutant et un conseiller avancé n'ont pas les mêmes besoins&nbsp;: un parcours par niveau.</li>
    </ul>
  </div>
''' + formation_bloc("Pour les directeurs et managers, la formation s'appuie sur nos outils maison Academia Pilotage et Academia Parcours, et peut se compléter d'un <a class=\"lien-texte\" href=\"/coaching-pour-directeur-dagence-immobiliere-dans-le-06/\">coaching de direction et d'un audit d'agence</a>.") + '\n' + AUTRES + '\n' + GARANTIES,
 [("Cette formation est-elle réservée aux directeurs&nbsp;?", "Elle s'adresse aux directeurs, managers, responsables d'équipe et animateurs de réseau de mandataires, c'est-à-dire à toute personne qui accompagne des conseillers."),
  ("Faut-il déjà utiliser l'IA&nbsp;?", "Non. La formation existe en version débutant et en version avancée. Le but est de piloter l'agence et d'encadrer les usages, pas de devenir technicien."),
  ("Peut-on former toute l'équipe ensuite&nbsp;?", "Oui. Nous construisons un plan de formation par poste et formons vos conseillers dans l'agence ou à distance."),
  ("Combien coûte la formation&nbsp;?", "À partir de 42 € de l'heure, finançable par l'OPCO de l'agence ou par le fonds d'assurance formation du dirigeant (AGEFICE, FIF PL). Le devis précis est établi après l'appel découverte.")],
 ("Formation IA pour directeurs et managers d'agence immobilière", "Piloter une agence immobilière avec l'IA : indicateurs, entretiens individuels, recrutement et déploiement de l'IA dans l'équipe."))

# ---------------------------------------------------------------- Formation IA réseaux de mandataires
ecrire('formation-ia-reseau-mandataires/',
 "Formation IA réseau de mandataires | Start Academia",
 "Formation IA pour réseaux de mandataires immobiliers : diagnostic par mandataire, groupes de niveau, à distance ou sur place, outils inclus. Certifié Qualiopi.",
 "Formation IA pour réseaux de mandataires immobiliers.",
 "Vos mandataires testent déjà l'IA, chacun dans son coin et avec des résultats inégaux. Nous déployons une formation concrète dans tout le réseau&nbsp;: mêmes méthodes, mêmes outils, un cadre conforme, et un parcours adapté au niveau de chacun.",
 '''  <div class="bloc">
    <h2>Construisez votre plan de déploiement</h2>
    <div class="plan-reseau">
      <p class="plan-intro">Réglez les quatre curseurs&nbsp;: votre réseau se répartit en groupes de niveau et votre plan s'écrit en dessous.</p>
      <div class="plan-scene">
        <form class="plan-reglages" onsubmit="return false">
          <div class="plan-champ">
            <label for="plan-n">Votre réseau</label>
            <output class="plan-val plan-val-n" for="plan-n">120 mandataires</output>
            <input id="plan-n" type="range" min="10" max="1000" step="10" value="120">
          </div>
          <div class="plan-champ">
            <label for="plan-deb">Part de débutants en IA</label>
            <output class="plan-val plan-val-deb" for="plan-deb">72 débutants · 48 déjà utilisateurs</output>
            <input id="plan-deb" type="range" min="0" max="100" step="10" value="60">
          </div>
          <div class="plan-champ">
            <label for="plan-h">Durée du parcours</label>
            <output class="plan-val plan-val-h" for="plan-h">16 h par mandataire</output>
            <input id="plan-h" type="range" min="4" max="32" step="4" value="16">
          </div>
          <div class="plan-champ">
            <span class="plan-label" id="plan-format-l">Format des sessions</span>
            <div class="plan-format" role="group" aria-labelledby="plan-format-l">
              <button type="button" data-format="visio" aria-pressed="true">Visio</button>
              <button type="button" data-format="presentiel" aria-pressed="false">Présentiel</button>
              <button type="button" data-format="mixte" aria-pressed="false">Les deux</button>
            </div>
          </div>
        </form>
        <div class="plan-vue">
          <canvas class="plan-toile" aria-hidden="true"></canvas>
          <p class="plan-legende"><span class="pl-deb">Débutants</span><span class="pl-av">Déjà utilisateurs</span><span class="pl-session">Une session, 50 au plus</span><span class="plan-echelle">1 point = 1 mandataire</span></p>
        </div>
      </div>
      <div class="plan-resultat" aria-live="polite">
        <div class="plan-chiffres">
          <p><strong id="pt-groupes">3</strong><span id="pt-groupes-l">groupes de niveau</span></p>
          <p><strong id="pt-h">16&nbsp;h</strong><span>par mandataire</span></p>
          <p><strong id="pt-format">Visio</strong><span>format des sessions</span></p>
        </div>
        <ol class="plan-etapes">
          <li><strong>Diagnostic</strong><span id="pe-1">Les 120 mandataires font leur diagnostic avec Academia Parcours&nbsp;: vous savez qui débute et qui est avancé.</span></li>
          <li><strong>Groupes</strong><span id="pe-2">2 groupes débutants et 1 groupe avancé, 50 mandataires au plus par session.</span></li>
          <li><strong>Sessions</strong><span id="pe-3">16 h par mandataire, en visio. Les heures comptent pour la loi ALUR.</span></li>
          <li><strong>Outils et cadre</strong><span>Nos outils maison remis à chaque mandataire, et une charte d'usage de l'IA commune au réseau.</span></li>
        </ol>
        <div class="plan-actions">
          <a class="action plan-appel" href="https://meet.brevo.com/jean-guy-ourmieres/appel-decouverte" rel="noopener">Recevoir mon devis&nbsp;: réserver l'appel<svg aria-hidden="true"><use href="#fleche"/></svg></a>
          <button type="button" class="plan-copier" hidden>Copier mon plan</button>
          <span class="plan-note">Devis établi après l'appel découverte de 30 minutes.</span>
        </div>
      </div>
    </div>
  </div>
  <div class="bloc">
    <h2>Le cas en réseau</h2>
    <p>Un réseau réunit des mandataires qui démarrent et d'autres qui signent depuis dix ans. Certains rédigent déjà leurs annonces avec ChatGPT, d'autres n'ont jamais ouvert l'outil, et quelques-uns y collent les coordonnées de leurs vendeurs. L'animateur n'a ni le temps ni le support pour remettre tout le monde au même niveau. Il lui faut un programme commun, découpé par niveau, que chaque mandataire applique dès le lendemain sur ses propres dossiers.</p>
  </div>
  <div class="bloc">
    <h2>La méthode classique, boostée à l'IA</h2>
    <ol class="points numerotes">
      <li><strong>Situer chaque mandataire.</strong> Avec <strong>Academia Parcours</strong>, notre outil maison gratuit, chacun fait son diagnostic de performance immobilière. Vous savez qui est débutant, qui est avancé, et sur quelle étape du métier chacun perd du temps.</li>
      <li><strong>Un programme calé sur la chaîne du métier.</strong> Prospection, découverte vendeur, estimation, mandat, acquéreurs, visites et offres, organisation, administratif&nbsp;: on part des fondamentaux que vos mandataires connaissent, puis on les accélère avec l'IA. Le programme reprend vos process et vos outils réseau.</li>
      <li><strong>Des groupes de niveau.</strong> Version débutant et version avancée, à distance ou en présentiel, sur des dossiers réels apportés par les participants.</li>
      <li><strong>Les outils pour chaque mandataire.</strong> Nos outils maison (Academia Secteur, Localisateur, Profiling, ACM) sont utilisés pendant la formation et restent accessibles ensuite.</li>
      <li><strong>Un cadre commun.</strong> Une charte d'usage de l'IA pour le réseau&nbsp;: données clients et RGPD, mentions obligatoires des annonces, relecture systématique de ce que l'IA produit.</li>
    </ol>
  </div>
  <div class="bloc">
    <h2>Ce que le réseau y gagne</h2>
    <ul class="points">
      <li><strong>Des mandataires autonomes plus vite.</strong> Y compris ceux qui démarrent dans le métier.</li>
      <li><strong>Des pratiques homogènes et conformes.</strong> Les mêmes méthodes et le même cadre d'un mandataire à l'autre.</li>
      <li><strong>Un argument de recrutement et de fidélisation.</strong> Une formation certifiée Qualiopi, avec des outils fournis.</li>
      <li><strong>Des heures qui comptent pour la loi ALUR.</strong> Avec une attestation pour chaque participant.</li>
    </ul>
  </div>
  <div class="bloc">
    <h2>Deux façons de financer</h2>
    <ul class="points">
      <li><strong>Partenariat réseau.</strong> Le réseau prend en charge la formation pour tout ou partie de ses mandataires. Le devis est établi après l'appel découverte.</li>
      <li><strong>Financement individuel.</strong> Chaque mandataire indépendant mobilise son fonds d'assurance formation (AGEFICE, FIF PL selon son statut). Nous montons le dossier avec lui.</li>
    </ul>
  </div>
''' + prompt_bloc("Prompt gratuit : préparer le plan de montée en compétence du réseau", """Rôle : tu es un animateur de réseau de mandataires immobiliers expérimenté, responsable de la formation.
Contexte : mon réseau compte [NOMBRE] mandataires, dont [NOMBRE] en première année. Niveau en IA : [DÉBUTANTS / QUELQUES UTILISATEURS / USAGE RÉGULIER]. Les étapes du métier où ils perdent le plus de temps : [EX. PROSPECTION, RÉDACTION D'ANNONCES, SUIVI VENDEUR]. Format possible : [VISIO / PRÉSENTIEL / LES DEUX].
Tâche : propose un plan de montée en compétence sur 3 mois, avec un parcours débutant et un parcours avancé. Pour chaque mois : l'étape du métier travaillée, l'objectif concret pour le mandataire, et l'indicateur que je peux suivre.
Format : un tableau par parcours, puis 5 règles d'usage de l'IA à faire respecter dans le réseau (données clients, mentions obligatoires, relecture).""") + '''
  <div class="bloc">
    <h2>Erreurs fréquentes et règles à respecter</h2>
    <ul class="points">
      <li><strong>Une visio unique pour tout le réseau.</strong> Les débutants décrochent, les avancés s'ennuient. Mieux vaut deux groupes de niveau.</li>
      <li><strong>Former à un outil plutôt qu'au métier.</strong> Un mandataire retient ce qui lui fait gagner un mandat ou une heure, pas une liste de fonctionnalités.</li>
      <li><strong>Laisser circuler les données clients.</strong> Sans règle commune, des coordonnées de vendeurs finissent dans des outils grand public.</li>
      <li><strong>Publier sans relire.</strong> Une annonce rédigée par l'IA reste soumise aux mentions obligatoires (honoraires, DPE, statut du mandataire).</li>
    </ul>
  </div>
''' + formation_bloc("Pour un réseau, le programme est construit avec vous à partir de nos formations existantes. Les animateurs et managers de réseau peuvent suivre en complément la <a class=\"lien-texte\" href=\"/formation-ia-directeur-agence-immobiliere/\">formation IA pour directeurs et managers</a>.") + '\n' + GARANTIES,
 [("La formation peut-elle se faire entièrement à distance&nbsp;?", "Oui. Les sessions peuvent avoir lieu en visio, en présentiel, ou en combinant les deux, selon l'implantation de vos mandataires."),
  ("Nos mandataires n'ont pas tous le même niveau. Comment faites-vous&nbsp;?", "Chacun fait d'abord son diagnostic avec Academia Parcours. Nous constituons ensuite des groupes de niveau, avec une version débutant et une version avancée du programme."),
  ("Qui finance la formation&nbsp;?", "Soit le réseau, dans le cadre d'un partenariat, soit chaque mandataire par son fonds d'assurance formation (AGEFICE, FIF PL selon son statut). Nous montons les dossiers avec vous. La formation n'est pas éligible au CPF à ce jour."),
  ("Les outils restent-ils accessibles après la formation&nbsp;?", "Oui. Les outils maison utilisés pendant la formation restent accessibles ensuite. Les conditions sont précisées dans le devis."),
  ("Combien coûte la formation&nbsp;?", "À partir de 42 € de l'heure. Le devis dépend du nombre de mandataires, du format et de la durée&nbsp;: il est établi après l'appel découverte.")],
 ("Formation IA pour réseaux de mandataires immobiliers", "Déployer l'IA dans un réseau de mandataires immobiliers : diagnostic par mandataire, groupes de niveau, outils fournis et cadre d'usage commun."))



# ================================================================ Guide : auto-entrepreneur et 3 000 € (reprise de l'article le plus vu de l'ancien site)
ecrire('financement-formation-auto-entrepreneur/',
 'OPCO auto-entrepreneur : avez-vous droit aux 3 000 € ?',
 "Auto-entrepreneur, agent commercial, mandataire : pas d'OPCO, mais jusqu'à 3 000 € par an avec l'AGEFICE. Conditions 2026, calcul et démarches.",
 "Auto-entrepreneur&nbsp;: avez-vous droit aux 3&nbsp;000&nbsp;€ de formation&nbsp;?",
 "Un auto-entrepreneur n'a pas d'OPCO. Mais il cotise pour sa formation, et peut obtenir jusqu'à <strong>3&nbsp;000&nbsp;€ par an</strong> s'il dépend de l'AGEFICE. Voici qui y a droit en 2026, comment le vérifier en 5 minutes, et ce que ça finance concrètement.",
 '''  <div class="bloc">
    <h2>La réponse en 30 secondes</h2>
    <ul class="points">
      <li><strong>Pas d'OPCO pour un auto-entrepreneur.</strong> Les OPCO financent la formation des salariés. Vous, vous dépendez d'un <strong>fonds d'assurance formation</strong> (FAF), financé par la contribution à la formation professionnelle (CFP) prélevée avec vos cotisations URSSAF.</li>
      <li><strong>Si votre fonds est l'AGEFICE</strong>&nbsp;: jusqu'à <strong>3&nbsp;000&nbsp;€ par an</strong> si votre CFP de l'année est d'au moins 7&nbsp;€, et <strong>600&nbsp;€</strong> si elle est comprise entre 0 et 7&nbsp;€.</li>
      <li><strong>Si votre fonds est le FIF PL</strong>, fréquent chez les agents immobiliers&nbsp;: d'autres plafonds s'appliquent (voir plus bas).</li>
      <li><strong>Une seule façon d'être sûr</strong>&nbsp;: votre attestation CFP, dans votre espace URSSAF. Le nom du fonds y figure.</li>
    </ul>
  </div>
  <div class="bloc">
    <h2>AGEFICE ou FIF PL&nbsp;: de quel fonds dépendez-vous&nbsp;?</h2>
    <p>L'AGEFICE finance les <strong>dirigeants non salariés</strong>&nbsp;: commerçants, gérants majoritaires, entrepreneurs individuels et auto-entrepreneurs. Les <strong>professions libérales non médicales</strong> relèvent du <strong>FIF PL</strong>. Dans l'immobilier, les deux cas existent&nbsp;:</p>
    <ul class="points">
      <li><strong>Agent commercial ou mandataire en réseau</strong>&nbsp;: souvent le FIF PL, parfois l'AGEFICE selon votre code d'activité.</li>
      <li><strong>Dirigeant non salarié d'une agence</strong> (gérant majoritaire, entreprise individuelle)&nbsp;: généralement l'AGEFICE.</li>
      <li><strong>Dirigeant salarié de sa société</strong> (président de SAS, gérant minoritaire)&nbsp;: c'est l'OPCO de l'agence, comme pour vos salariés.</li>
    </ul>
    <p>Le fonds indiqué sur votre attestation CFP fait foi. Pour l'AGEFICE, il faut aussi être <strong>à jour du versement de votre CFP</strong>.</p>
  </div>
  <div class="bloc">
    <h2>Vérifier votre attestation en 5 minutes</h2>
    <ol class="points numerotes">
      <li><strong>Connectez-vous</strong> à votre espace sur autoentrepreneur.urssaf.fr.</li>
      <li><strong>Ouvrez la rubrique des attestations</strong> et téléchargez l'<strong>attestation de contribution à la formation professionnelle</strong> (CFP) de l'année.</li>
      <li><strong>Lisez le nom du fonds</strong>&nbsp;: AGEFICE, FIF PL ou autre.</li>
      <li><strong>Relevez le montant de CFP versé</strong>&nbsp;: c'est lui qui fixe votre plafond.</li>
    </ol>
    <p>Gardez ce PDF&nbsp;: il fait partie des pièces demandées pour la prise en charge.</p>
  </div>
  <div class="bloc">
    <h2>Le calcul&nbsp;: de votre chiffre d'affaires à votre plafond</h2>
    <p>En micro-entreprise, la CFP est un pourcentage du chiffre d'affaires encaissé&nbsp;: <strong>0,20&nbsp;%</strong> pour une activité libérale (BNC, cas de la plupart des agents commerciaux) et <strong>0,10&nbsp;%</strong> pour une activité commerciale. Pour atteindre les 7&nbsp;€ qui ouvrent le plafond de 3&nbsp;000&nbsp;€, il suffit donc d'environ <strong>3&nbsp;500&nbsp;€ de chiffre d'affaires annuel en BNC</strong>, ou 7&nbsp;000&nbsp;€ en activité commerciale.</p>
    <ul class="points">
      <li><strong>Exemple 1</strong>&nbsp;: agent commercial en micro-BNC, 30&nbsp;000&nbsp;€ de chiffre d'affaires en 2025. CFP&nbsp;: 30&nbsp;000 × 0,20&nbsp;% = <strong>60&nbsp;€</strong>. Si son attestation indique l'AGEFICE, son plafond 2026 est de <strong>3&nbsp;000&nbsp;€</strong>.</li>
      <li><strong>Exemple 2</strong>&nbsp;: mandataire qui démarre, 2&nbsp;000&nbsp;€ de chiffre d'affaires en 2025. CFP&nbsp;: <strong>4&nbsp;€</strong>, sous le seuil de 7&nbsp;€. Plafond AGEFICE&nbsp;: <strong>600&nbsp;€</strong>.</li>
    </ul>
    <p>Ces calculs sont théoriques&nbsp;: c'est le montant réellement versé, inscrit sur l'attestation, qui compte. <a class="lien-texte" href="/financement-formation-immobilier/#simulateur-financement">Faire le calcul avec notre simulateur</a></p>
  </div>
  <div class="bloc">
    <h2>Ce que financent les 3&nbsp;000&nbsp;€ en pratique</h2>
    <p>L'AGEFICE paie les frais de formation dans la limite d'un <strong>coût horaire maximum</strong>&nbsp;: <strong>42&nbsp;€ de l'heure en présentiel</strong>, 35&nbsp;€ en classe virtuelle et 20&nbsp;€ en e-learning. Nos formations sont à 42&nbsp;€ de l'heure&nbsp;: en présentiel, le taux est donc couvert en entier.</p>
    <ul class="points">
      <li><strong>Formation IA de 21&nbsp;heures en présentiel</strong>&nbsp;: 882&nbsp;€, pris en charge en totalité.</li>
      <li><strong>Parcours IA complet de 72&nbsp;heures en présentiel</strong>&nbsp;: 3&nbsp;024&nbsp;€. L'AGEFICE couvre 3&nbsp;000&nbsp;€, il reste <strong>24&nbsp;€</strong> à votre charge.</li>
      <li><strong>La même formation de 21&nbsp;heures en classe virtuelle</strong>&nbsp;: plafond de 35&nbsp;€ de l'heure, soit 735&nbsp;€ pris en charge et 147&nbsp;€ à votre charge.</li>
    </ul>
    <p>En plus, l'AGEFICE prévoit une <strong>indemnité pour perte de ressources</strong> de 8&nbsp;€ par heure de formation en présentiel ou en classe virtuelle, proportionnelle à la CFP versée. Elle ne s'impute pas sur l'enveloppe de 3&nbsp;000&nbsp;€.</p>
    <p>Montants calculés sur une enveloppe 2026 non encore utilisée et sous réserve de l'accord de l'AGEFICE.</p>
  </div>
  <div class="bloc" id="fif-pl">
    <h2>Si votre attestation indique le FIF PL</h2>
    <p>Pour 2026, les critères du FIF PL pour les agents immobiliers (code NAF 6831Z) prévoient une prise en charge plafonnée à <strong>900&nbsp;€ par an</strong> et <strong>300&nbsp;€ par jour</strong>. Pour les micro-entrepreneurs, la prise en charge est <strong>proportionnelle à la CFP versée</strong>&nbsp;: une petite contribution donne droit à une partie seulement de ces plafonds. <a class="lien-texte" href="/financement-formation-immobilier/#fif-pl">Le détail sur notre page financement</a></p>
  </div>
  <div class="bloc">
    <h2>Les démarches, dans l'ordre</h2>
    <ol class="points numerotes">
      <li><strong>Vérifiez votre fonds et votre CFP</strong> sur l'attestation URSSAF.</li>
      <li><strong>Demandez le devis et le programme</strong> à l'organisme de formation, qui doit être déclaré et certifié Qualiopi. Start Academia l'est.</li>
      <li><strong>Déposez la demande de prise en charge au moins 15&nbsp;jours avant le début de la formation</strong>, auprès de votre point d'accueil AGEFICE (souvent la CCI). Une demande tardive est refusée.</li>
      <li><strong>Suivez la formation</strong>, puis récupérez la facture acquittée et l'attestation d'assiduité.</li>
      <li><strong>Envoyez la demande de remboursement</strong> dans les 4&nbsp;mois qui suivent la fin de la formation.</li>
    </ol>
    <p>Nous préparons avec vous tous les documents&nbsp;: devis, programme, convention et attestations.</p>
  </div>
  <div class="bloc">
    <h2>Les erreurs qui font perdre la prise en charge</h2>
    <ul class="points">
      <li><strong>Chercher son OPCO.</strong> Un auto-entrepreneur n'en a pas&nbsp;: c'est le fonds de l'attestation CFP qui compte.</li>
      <li><strong>Déposer la demande après le début de la formation.</strong> C'est le premier motif de refus.</li>
      <li><strong>Oublier une CFP impayée ou nulle.</strong> Sans CFP versée, pas de prise en charge AGEFICE.</li>
      <li><strong>Consommer son enveloppe sur une formation sans lien avec son activité.</strong> Elle est annuelle&nbsp;: choisissez la formation qui vous fera rentrer des mandats.</li>
    </ul>
  </div>
  <div class="bloc">
    <h2>Sources officielles</h2>
    <ul class="points">
      <li><a class="lien-texte" href="https://communication-agefice.fr/plafonds-financiers-annee-2026/" rel="noopener">AGEFICE&nbsp;: plafonds financiers 2026</a></li>
      <li><a class="lien-texte" href="https://communication-agefice.fr/les-ressortissants-de-lagefice/" rel="noopener">AGEFICE&nbsp;: qui sont les ressortissants</a></li>
      <li><a class="lien-texte" href="https://entreprendre.service-public.gouv.fr/vosdroits/R72935" rel="noopener">Service-public&nbsp;: demande de prise en charge d'une formation pour un commerçant</a></li>
      <li><a class="lien-texte" href="https://www.fifpl.fr/" rel="noopener">FIF PL</a></li>
    </ul>
    <p>Critères en vigueur au 11 novembre 2026. Ils changent chaque année&nbsp;: nous les vérifions avec vous au moment de votre demande.</p>
  </div>
''' + PREUVES_BREF,
 [("Un auto-entrepreneur a-t-il un OPCO&nbsp;?", "Non. Les OPCO financent la formation des salariés. Un auto-entrepreneur dépend d'un fonds d'assurance formation : l'AGEFICE, le FIF PL ou un autre fonds selon son activité. Le nom figure sur l'attestation de contribution à la formation professionnelle, dans l'espace URSSAF."),
  ("Qui a droit aux 3 000 € de l'AGEFICE&nbsp;?", "Les dirigeants non salariés qui dépendent de l'AGEFICE, auto-entrepreneurs compris, à jour de leur contribution à la formation professionnelle et dont la CFP de l'année atteint au moins 7 €. En dessous de 7 €, le plafond est de 600 € par an."),
  ("Quel chiffre d'affaires faut-il pour atteindre 7 € de CFP&nbsp;?", "En micro-entreprise, environ 3 500 € de chiffre d'affaires annuel pour une activité libérale (taux de 0,20 %) et 7 000 € pour une activité commerciale (taux de 0,10 %). Le montant réellement versé, inscrit sur l'attestation URSSAF, fait foi."),
  ("Un agent commercial immobilier dépend-il de l'AGEFICE&nbsp;?", "Pas toujours. Beaucoup d'agents commerciaux et de mandataires dépendent du FIF PL, d'autres de l'AGEFICE selon leur code d'activité. Seule l'attestation CFP permet de le savoir."),
  ("Quand déposer la demande&nbsp;?", "Au moins 15 jours avant le début de la formation, auprès de votre point d'accueil AGEFICE. Une demande déposée après le début de la formation est refusée."),
  ("Combien reste-t-il à payer sur une formation Start Academia&nbsp;?", "Nos formations sont à 42 € de l'heure, le coût horaire maximum de l'AGEFICE en présentiel. Dans la limite de votre enveloppe annuelle, une formation en présentiel est donc prise en charge en totalité. En classe virtuelle, le plafond est de 35 € de l'heure : il reste 7 € de l'heure à votre charge."),
  ("Les formations Start Academia sont-elles éligibles au CPF&nbsp;?", "Pas à ce jour. Elles sont finançables par l'AGEFICE, le FIF PL ou l'OPCO, et comptent pour la formation continue loi ALUR.")])


# ================================================================ Guide : prospecter sans pige (fin du démarchage téléphonique, 11 août 2026)
# Inspiré de la masterclass Immo2 « Les nouvelles techniques de prospection dans un monde sans pige »
# (Sébastien Tedesco et Jean-Guy Ourmières, 21 mai 2026).
ecrire('prospection-immobiliere-sans-pige/',
 'Prospection immobilière sans pige : la méthode 2026',
 "Pige interdite depuis le 11 août 2026 : ce qui reste permis et 7 tactiques pour rentrer des vendeurs sans appel à froid. Méthode et prompt gratuit.",
 "Prospecter sans pige&nbsp;: la méthode qui remplace le téléphone.",
 "Depuis le 11 août 2026, appeler un particulier repéré sur une annonce est interdit sans son accord. Vous perdez une tactique, la pige. Vous gagnez une méthode&nbsp;: apporter de la valeur à la bonne personne, par le bon canal, assez souvent pour devenir l'agent du quartier.",
 """  <div class="bloc">
    <h2>Ce qui a changé le 11 août 2026</h2>
    <ul class="points">
      <li><strong>Plus d'appel sans consentement.</strong> La loi du 30 juin 2025 interdit de démarcher un consommateur par téléphone s'il n'a pas donné son accord au préalable. Le numéro affiché dans une annonce de particulier ne vaut pas accord&nbsp;: la pige téléphonique classique est terminée.</li>
      <li><strong>Un consentement encadré.</strong> Le décret du 23 juillet 2026 limite sa durée à un an, sans reconduction tacite. Il doit résulter d'un acte clair, et vous devez pouvoir le prouver.</li>
      <li><strong>Des sanctions lourdes.</strong> Jusqu'à 75&nbsp;000&nbsp;€ d'amende pour une personne physique et 375&nbsp;000&nbsp;€ pour une société.</li>
      <li><strong>Bloctel n'existe plus.</strong> Il n'y a plus de liste à consulter&nbsp;: sans accord, on n'appelle pas.</li>
    </ul>
    <p><strong>Ce qui reste permis</strong>&nbsp;: le courrier adressé, le boîtage (en respectant le «&nbsp;Stop Pub&nbsp;»), le terrain, les réseaux sociaux, et l'appel d'une personne qui vous l'a demandé, par exemple via un formulaire. L'e-mail et le SMS de prospection vers un particulier demandent, eux, son accord préalable.</p>
  </div>
  <div class="bloc">
    <h2>La grammaire de la prospection&nbsp;: cible × contenu × canal</h2>
    <p>La pige n'était qu'une seule combinaison&nbsp;: vendeur particulier × «&nbsp;je peux vous aider&nbsp;» × téléphone. Une tactique, c'est toujours trois choix&nbsp;:</p>
    <ul class="points">
      <li><strong>La cible</strong>&nbsp;: voisins d'un bien que vous venez de rentrer, vendeurs particuliers, acquéreurs reçus en agence, anciens clients vendeurs ou acheteurs, réseau personnel, habitants du secteur.</li>
      <li><strong>Le contenu</strong>&nbsp;: baromètre de la résidence, dossier expert (DPE, succession), guide vendeur, foire aux questions interactive, étude de cas, gazette du quartier, avis clients, simple «&nbsp;j'ai pensé à vous&nbsp;».</li>
      <li><strong>Le canal</strong>&nbsp;: courrier adressé, boîtage, e-mail, SMS, QR code, réseaux sociaux, rencontre terrain, téléphone quand la personne l'a accepté.</li>
    </ul>
    <p>7 cibles × 8 contenus × 8 canaux&nbsp;: plus de 400 combinaisons possibles. Et une règle pour les faire fonctionner&nbsp;: <strong>régularité × présence sur plusieurs canaux × valeur apportée</strong>. Un propriétaire ne vous confie pas son bien au premier contact&nbsp;: il faut passer d'une prospection <em>intéressée</em> à une prospection <em>intéressante</em>.</p>
  </div>
  <div class="bloc">
    <h2>7 tactiques qui rentrent des vendeurs sans appel à froid</h2>
    <ol class="points numerotes">
      <li><strong>Le baromètre de la résidence.</strong> Vous venez de faire une estimation&nbsp;? Compilez en moins d'une semaine un baromètre de la résidence (prix au m², évolution, délais de vente) et déposez-le dans toutes les boîtes. Une estimation devient 70 points de contact qui apportent une information, pas une sollicitation.</li>
      <li><strong>Le dossier DPE.</strong> À un vendeur dont le logement est mal classé, ne dites pas «&nbsp;j'ai vu votre DPE, je peux vous aider&nbsp;» (rejet immédiat). Envoyez par courrier un dossier qui montre comment gagner une classe avec un budget réaliste. Vous créez un capital de confiance.</li>
      <li><strong>La FAQ «&nbsp;vendre seul, bien accompagné&nbsp;» par QR code.</strong> Un courrier avec un QR code mène à un assistant qui répond aux questions du vendeur particulier. Pour obtenir la réponse détaillée ou être rappelé, il laisse ses coordonnées <strong>et coche son accord</strong>&nbsp;: c'est un consentement documenté, et un contact qualifié.</li>
      <li><strong>Les zones qui tournent.</strong> Le fichier public des ventes (DVF), analysé avec l'IA, fait ressortir les rues où les biens changent de mains plus souvent que la moyenne. Vous concentrez vos baromètres et vos courriers là où ça vend.</li>
      <li><strong>Les acquéreurs reçus en agence.</strong> Recevez vos acheteurs physiquement et poussez la découverte&nbsp;: beaucoup sont aussi vendeurs, et ils repèrent sur les portails des biens que vous n'avez pas vus.</li>
      <li><strong>Les avis Google aux bons moments.</strong> Demandez l'avis à chaque moment fort (offre acceptée, signature, remise des clés). Les avis nourrissent votre visibilité locale et sont lus par les assistants comme ChatGPT ou Claude quand on leur demande «&nbsp;quel agent choisir&nbsp;».</li>
      <li><strong>Les anciens clients, à vie.</strong> Quatre moments dans l'année&nbsp;: l'anniversaire de l'achat avec un point sur la valeur, le baromètre de leur résidence, les vœux personnalisés, un «&nbsp;j'ai pensé à vous&nbsp;». Par courrier, ou par e-mail et SMS s'ils l'ont accepté.</li>
    </ol>
  </div>
  <div class="bloc">
    <h2>Recueillir un consentement qui tient</h2>
    <p>Pour pouvoir rappeler quelqu'un, votre formulaire (estimation en ligne, QR code, page de contact) doit indiquer clairement&nbsp;:</p>
    <ul class="points">
      <li>l'identité de votre agence et la nature des appels (estimation, vente, recherche)&nbsp;;</li>
      <li>un choix libre d'accepter ou de refuser, avec une case non cochée par défaut&nbsp;;</li>
      <li>la durée de l'accord, un an au maximum&nbsp;;</li>
      <li>la façon de le retirer à tout moment, aussi simplement qu'il a été donné.</li>
    </ul>
    <p>Gardez la preuve (date, formulaire, texte accepté) dans votre logiciel de transaction. Un lead acheté à un fournisseur ne vous autorise à appeler que si ce consentement vous couvre aussi.</p>
  </div>
  <div class="bloc">
    <h2>Ce que change l'IA</h2>
    <ul class="points">
      <li><strong>Le baromètre de résidence</strong>&nbsp;: 2&nbsp;heures de compilation à la main, environ 20&nbsp;minutes avec un dossier d'adresse <strong>Academia Secteur</strong> et ChatGPT ou Claude pour la mise en forme.</li>
      <li><strong>Le dossier DPE</strong>&nbsp;: données publiques de l'ADEME, travaux chiffrés par l'IA, mise en page avec Gamma.</li>
      <li><strong>Les zones qui tournent</strong>&nbsp;: un fichier DVF donné à Claude ou ChatGPT, qui en sort les secteurs les plus actifs.</li>
      <li><strong>La FAQ vendeur</strong>&nbsp;: un assistant personnalisé, signé de votre nom, qui répond la nuit et le week-end.</li>
    </ul>
    <p>Temps indicatifs, constatés en formation. La relecture reste obligatoire&nbsp;: vous signez, vous vérifiez.</p>
  </div>
""" + prompt_bloc("Prompt gratuit : le baromètre de la résidence", """Rôle : tu es un conseiller immobilier qui connaît bien [VILLE / QUARTIER].
Contexte : je viens d'estimer un bien dans la résidence [NOM OU RUE]. Voici les ventes des 3 dernières années dans la résidence et la rue, sans aucun nom de propriétaire : [DATE, TYPE, SURFACE, PRIX POUR CHAQUE VENTE]. Prix moyen du quartier : [PRIX AU M²].
Tâche : rédige un baromètre d'une page pour les habitants de la résidence : prix moyen au m² et son évolution, délai de vente constaté, 3 conseils pour vendre au bon prix. Ton neutre et informatif, aucune promesse de prix, aucune information permettant d'identifier un vendeur.
Format : un titre, 3 chiffres clés, 3 conseils, une signature avec [TON NOM], [TON AGENCE], [TA CARTE PRO] et un QR code vers [TA PAGE DE CONTACT AVEC CONSENTEMENT].""") + """
  <div class="bloc">
    <h2>Erreurs fréquentes et règles à respecter</h2>
    <ul class="points">
      <li><strong>Appeler le numéro d'une annonce.</strong> Depuis le 11 août 2026, c'est un démarchage sans consentement. Et un mandat obtenu ainsi peut être contesté.</li>
      <li><strong>Envoyer des e-mails ou des SMS sans accord.</strong> La prospection par message vers un particulier demande aussi son accord préalable.</li>
      <li><strong>Se servir du fichier DVF pour retrouver un vendeur.</strong> Ses conditions d'utilisation interdisent de réidentifier les personnes. Utilisez-le pour des statistiques de rue ou de quartier, jamais pour cibler un propriétaire.</li>
      <li><strong>Le flyer centré sur l'agence.</strong> «&nbsp;Nous avons vendu, nous recherchons&nbsp;» n'apporte rien au lecteur. Apportez une information qu'il ne trouve nulle part ailleurs.</li>
      <li><strong>Une seule action, sans suite.</strong> Un propriétaire a besoin de plusieurs contacts avant d'identifier un professionnel. La régularité fait la différence.</li>
    </ul>
  </div>
  <div class="bloc">
    <h2>D'où vient cette méthode</h2>
    <p>Ces tactiques ont été présentées en direct lors de la masterclass Immo2 «&nbsp;Les nouvelles techniques de prospection dans un monde sans pige&nbsp;», animée par Sébastien Tedesco et Jean-Guy Ourmières. Nous les déployons depuis en agence, sur les dossiers des conseillers.</p>
    <p>Sources&nbsp;: <a class="lien-texte" href="https://www.economie.gouv.fr/dgccrf/les-fiches-pratiques/les-regles-du-demarchage-telephonique-simposant-aux-entreprises" rel="noopener">DGCCRF, les règles du démarchage téléphonique</a> · <a class="lien-texte" href="https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres/" rel="noopener">DVF, conditions d'utilisation</a></p>
  </div>
""" + formation_bloc("La prospection sans pige est un module de nos formations IA&nbsp;: atelier sur votre propre secteur, baromètre et dossier DPE construits en séance, formulaire de consentement prêt à l'emploi, avec nos outils maison Academia Secteur et Academia Vivre ici.") + '\n' + AUTRES.replace('      <li><a class="lien-texte" href="/prospection-immobiliere-sans-pige/">Prospecter sans pige depuis le 11 août 2026</a></li>\n', '') + '\n' + GARANTIES,
 [("La pige immobilière est-elle interdite&nbsp;?", "La pige téléphonique l'est depuis le 11 août 2026 : appeler un particulier repéré sur une annonce sans son accord préalable est un démarchage interdit. Repérer les annonces reste possible ; c'est l'appel à froid qui ne l'est plus."),
  ("Peut-on encore envoyer un courrier à un vendeur particulier&nbsp;?", "Oui. Le courrier adressé et le boîtage restent possibles, en respectant le Stop Pub pour le boîtage et le droit de la personne à ne plus être sollicitée."),
  ("Comment obtenir le consentement d'un vendeur&nbsp;?", "Par une démarche où il vous demande de le recontacter : formulaire d'estimation, QR code sur un courrier, page de contact. Le formulaire doit indiquer votre identité, l'objet des appels, la durée de l'accord (un an maximum) et la façon de le retirer, avec une case non cochée par défaut."),
  ("Combien de temps dure un consentement&nbsp;?", "Un an au maximum, sans reconduction tacite, selon le décret du 23 juillet 2026. Au-delà, il faut le redemander."),
  ("Peut-on appeler un ancien client&nbsp;?", "Pour lui proposer vos services, seulement s'il a donné son accord. Le courrier reste possible, et l'e-mail aussi pour des services analogues à ceux qu'il a déjà utilisés, avec un lien pour se désinscrire."),
  ("Qu'est-ce que la formation apporte de plus&nbsp;?", "Un atelier sur votre secteur réel : baromètre, dossier DPE et formulaire de consentement construits en séance avec l'IA et nos outils, pour repartir avec une routine de prospection conforme.")])


# ================================================================ Guides tirés des formations (novembre 2026)
# Rédigés à partir de ce qui est dit en formation. Règles de rédaction : aucun nom de client, d'agence,
# de notaire ou de concurrent ; aucun chiffre d'agence cliente ; toute règle de droit citée avec sa source.

# ---------------------------------------------------------------- Guide : le vendeur parti plus cher ailleurs
ecrire('vendeur-parti-trop-cher-reprendre-mandat/',
 "Vendeur parti ailleurs : reprendre le mandat | Start Academia",
 "Votre vendeur a signé chez un concurrent qui annonçait plus haut ? La méthode pour garder le lien, le rappeler chaque mois et reprendre le mandat au bon prix.",
 "Vendeur parti plus cher ailleurs&nbsp;: comment reprendre le mandat.",
 "Vous estimez un bien, un concurrent annonce 100&nbsp;000&nbsp;€ de plus, le vendeur signe chez lui. La plupart des conseillers tournent la page. C'est une erreur&nbsp;: trois à quatre mois plus tard, ce vendeur a besoin de quelqu'un qui a tenu le même discours depuis le début.",
 '''  <div class="bloc">
    <h2>Le cas en agence</h2>
    <p>Vous estimez une maison entre 450&nbsp;000 et 480&nbsp;000&nbsp;€. Un confrère passe derrière vous et annonce entre 550&nbsp;000 et 580&nbsp;000&nbsp;€. Le vendeur signe avec lui.</p>
    <p>Le réflexe est de ne plus rappeler&nbsp;: la frustration, l'ego. Vu du vendeur, le message est clair&nbsp;: ce conseiller souriant au deuxième rendez-vous ne s'intéressait qu'à son mandat. Vous venez de lui donner raison d'avoir choisi quelqu'un d'autre.</p>
    <p class="preuve-texte">Ce n'est pas à vous que le vendeur a dit non, c'est à votre prix.</p>
  </div>
  <div class="bloc">
    <h2>La méthode classique, boostée à l'IA</h2>
    <ol class="points numerotes">
      <li><strong>Annoncer la suite dès le deuxième rendez-vous.</strong> Dites-le avant de donner votre prix&nbsp;: «&nbsp;Vous allez recevoir des estimations plus hautes que la mienne. Si vous choisissez un autre professionnel, je ne le prendrai pas mal, et avec votre accord je continuerai à prendre de vos nouvelles.&nbsp;» Le vendeur sait qu'il garde le choix, la tension du rendez-vous retombe.</li>
      <li><strong>Maîtriser le projet et le délai.</strong> Départ, décès, divorce, dettes&nbsp;: derrière un projet sérieux, il y a une échéance. Un vendeur qui n'a pas de délai en tête choisira toujours le prix le plus haut. C'est la question à creuser avant de parler de prix.</li>
      <li><strong>Rappeler chaque mois, en position neutre.</strong> Vous n'êtes plus en concurrence, vous êtes un regard extérieur. Les questions suffisent&nbsp;: combien de visites, qu'en disent les visiteurs, y a-t-il eu des offres, qu'en pense votre conseiller, et vous, comment le vivez-vous&nbsp;? Au bout de deux ou trois mois, c'est souvent le vendeur qui prononce le mot «&nbsp;prix&nbsp;».</li>
      <li><strong>Préparer chaque appel en quelques minutes.</strong> Un projet par vendeur dans ChatGPT ou Claude&nbsp;: vous y dictez le compte rendu du rendez-vous, puis chaque échange. Avant de rappeler, l'IA vous ressort ce qui a été dit, les questions à poser et ce qui a changé sur le marché.</li>
      <li><strong>Tenir son prix au retour.</strong> Quand le vendeur revient, il propose une petite baisse. Vous réactualisez votre estimation avec <strong>Academia ACM</strong>, notre outil maison, et vous gardez le même discours qu'au premier jour&nbsp;: pas de magie, un prix stratégique, argumenté par les biens concurrents.</li>
    </ol>
  </div>
  <div class="bloc">
    <h2>Ce que vous gagnez</h2>
    <ul class="points">
      <li><strong>Des mandats récupérés</strong> sur des estimations que vous aviez déjà faites, sans nouvelle prospection.</li>
      <li><strong>Un rapport de force inversé</strong>&nbsp;: le vendeur revient vers celui qui avait raison, au prix que vous défendiez.</li>
      <li><strong>Un suivi qui tient dans la durée</strong>&nbsp;: l'historique de chaque vendeur est prêt avant l'appel, vous ne repartez jamais de zéro.</li>
    </ul>
  </div>
''' + prompt_bloc("Prompt gratuit : préparer l'appel mensuel", '''Rôle : tu es mon assistant de conseiller immobilier.
Contexte : j'ai estimé le bien de [PRÉNOM DU VENDEUR] le [DATE] entre [FOURCHETTE]. Il a signé avec un autre professionnel à [PRIX AFFICHÉ]. Il m'a autorisé à le rappeler. Son projet : [PROJET ET DÉLAI]. Mes notes des échanges précédents : [NOTES].
Tâche : prépare mon appel de ce mois. Je ne critique jamais le confrère et je ne propose pas mes services : je prends des nouvelles et je pose des questions.
Format : 1. Rappel en 3 lignes de ce que le vendeur m'a dit la dernière fois. 2. Cinq questions ouvertes, de la plus simple à la plus engageante. 3. Ce que je note après l'appel.''') + '''
  <div class="bloc">
    <h2>Erreurs fréquentes et règles à respecter</h2>
    <ul class="points">
      <li><strong>Rappeler sans accord.</strong> Depuis le 11&nbsp;août 2026, appeler un particulier pour lui proposer ses services suppose son consentement, valable un an au plus. Demandez-le au deuxième rendez-vous et gardez-en la trace. <a class="lien-texte" href="/prospection-immobiliere-sans-pige/">Notre guide sur la prospection sans pige</a></li>
      <li><strong>Critiquer le confrère.</strong> Le dénigrement se retourne contre vous. Posez des questions, laissez le vendeur conclure.</li>
      <li><strong>Pousser à rompre une exclusivité.</strong> Un mandat exclusif ne se dénonce qu'après trois mois, avec un préavis de quinze jours par lettre recommandée. Vous ne signez rien tant que l'ancien mandat n'est pas régulièrement résilié.</li>
      <li><strong>Baisser son estimation pour signer.</strong> Si vous cédez au retour du vendeur, vous perdez ce qui vous a fait revenir&nbsp;: la cohérence.</li>
      <li><strong>Laisser l'IA décider du prix.</strong> Elle prépare l'appel et met en forme l'analyse. L'estimation reste la vôtre.</li>
    </ul>
  </div>
''' + formation_bloc("Le deuxième rendez-vous, l'annonce du prix et le suivi des vendeurs non signés sont travaillés dans nos formations, en jeux de rôle et sur vos propres dossiers, avec Academia ACM pour suivre la position d'un bien face à ses concurrents.") + '\n' + GARANTIES,
 [("Faut-il rappeler un vendeur qui a signé ailleurs&nbsp;?", "Oui, s'il vous y a autorisé. Il vous a fait venir pour une estimation : il vous connaît et il a vu votre travail. Un appel par mois, sans rien demander, entretient ce lien."),
  ("Au bout de combien de temps un vendeur revient-il&nbsp;?", "Souvent après trois à quatre mois sans offre. C'est le moment où les visites se raréfient et où le professionnel choisi commence à parler de baisse de prix."),
  ("Que dire à un vendeur qui dit ne pas être pressé&nbsp;?", "Lui faire préciser son projet et son échéance. Sans délai clair, il n'a aucune raison de se placer au prix du marché, et c'est normal."),
  ("Comment éviter de perdre le mandat au deuxième rendez-vous&nbsp;?", "En expliquant d'entrée le déroulé du rendez-vous et votre méthode d'estimation, en le prévenant des estimations plus hautes qu'il recevra, et en lui disant qu'il garde le choix.")])

# ---------------------------------------------------------------- Guide : prospecter avec le DPE
ecrire('prospecter-avec-le-dpe/',
 "Prospecter avec le DPE : la réforme 2027 | Start Academia",
 "Le calcul du DPE change encore au 1er janvier 2027. Comment apporter leur nouvelle étiquette aux propriétaires de votre secteur, avec l'IA et sans démarchage.",
 "Prospecter avec le DPE&nbsp;: la réforme de 2027 comme motif de contact.",
 "Le 1<sup>er</sup>&nbsp;janvier 2027, des logements chauffés à l'électricité gagneront une classe sans travaux. La plupart de leurs propriétaires ne le sauront pas. Leur apporter l'information est un motif de contact utile, légitime et daté.",
 '''  <div class="bloc">
    <h2>Le cas en agence</h2>
    <p>Un flyer «&nbsp;estimation gratuite&nbsp;» ne dit rien au propriétaire qui le reçoit. «&nbsp;Votre étiquette énergie vient de passer de E à D, voici l'attestation officielle&nbsp;» lui apprend quelque chose sur son bien, et ne lui demande rien en retour.</p>
    <p class="preuve-texte">Une prospection intéressante, pas une prospection intéressée.</p>
  </div>
  <div class="bloc">
    <h2>Ce qui change, et quand</h2>
    <ul class="points">
      <li><strong>Depuis le 1<sup>er</sup>&nbsp;janvier 2026</strong>, le coefficient de conversion de l'électricité utilisé dans le calcul du DPE est passé de 2,3 à 1,9.</li>
      <li><strong>Au 1<sup>er</sup>&nbsp;janvier 2027</strong>, il passera de 1,9 à 1,7 (arrêté du 19&nbsp;août 2026).</li>
      <li><strong>Pas de nouvelle visite.</strong> Le DPE existant reste valable dix ans. Si l'étiquette s'améliore, une attestation gratuite se télécharge sur l'Observatoire DPE-Audit de l'ADEME, à partir du numéro du diagnostic.</li>
      <li><strong>Rien d'automatique.</strong> L'amélioration dépend du logement, et aucune étiquette ne peut être dégradée par ce changement.</li>
    </ul>
    <p>Sources&nbsp;: <a class="lien-texte" href="https://www.service-public.gouv.fr/particuliers/actualites/A18446" rel="noopener">Service-Public.fr, nouveau calcul du DPE</a> &nbsp; <a class="lien-texte" href="https://www.economie.gouv.fr/actualites/un-nouveau-dpe-au-1er-janvier-2026-pour-favoriser-le-chauffage-electrique" rel="noopener">ministère de l'Économie, DPE 2026</a></p>
  </div>
  <div class="bloc">
    <h2>La méthode classique, boostée à l'IA</h2>
    <ol class="points numerotes">
      <li><strong>Commencer par vos mandats.</strong> Vérifiez l'étiquette de chaque bien en vente ou en location dans votre portefeuille. Si un confrère apporte l'attestation à votre vendeur avant vous, le signal est mauvais.</li>
      <li><strong>Repérer les logements du secteur.</strong> Avec <strong>Academia Secteur</strong>, notre outil maison, vous voyez autour d'une adresse les DPE récents et les logements susceptibles de gagner une classe. À la main, compter une demi-journée pour une vingtaine de biens.</li>
      <li><strong>Apporter l'attestation.</strong> En main propre ou par courrier&nbsp;: «&nbsp;Votre étiquette a changé, je vous l'ai imprimée. Si un jour vous avez un projet, vous savez où me trouver.&nbsp;»</li>
      <li><strong>Aller plus loin avec un dossier.</strong> À partir des données du diagnostic, l'IA rédige un dossier clair&nbsp;: ce qui pèse sur la note, les travaux qui la feraient évoluer, un ordre de grandeur des coûts. Mis en page dans Gamma, il se laisse au propriétaire, qui peut le transmettre à un acquéreur.</li>
      <li><strong>Préparer janvier dès maintenant.</strong> Le 1<sup>er</sup>&nbsp;janvier 2027 ouvre une fenêtre de quelques semaines. Listez les adresses concernées en décembre, rédigez le courrier, et soyez le premier dans les boîtes aux lettres.</li>
    </ol>
  </div>
  <div class="bloc">
    <h2>Ce que vous gagnez</h2>
    <ul class="points">
      <li><strong>Un motif de contact daté</strong>, que tout propriétaire concerné a intérêt à recevoir.</li>
      <li><strong>Quelques minutes par adresse</strong> avec l'outil, au lieu d'une recherche diagnostic par diagnostic.</li>
      <li><strong>Une image d'expert du quartier</strong>, pas de chasseur de mandats.</li>
    </ul>
  </div>
''' + prompt_bloc("Prompt gratuit : le dossier « comprendre mon DPE »", '''Rôle : tu es un conseiller immobilier pédagogue. Tu n'es pas diagnostiqueur et tu le dis.
Contexte : voici les données du DPE du logement situé [QUARTIER, SANS ADRESSE NI NOM] : [COLLER LES DONNÉES DU DIAGNOSTIC]. Étiquette actuelle : [LETTRE].
Tâche : rédige un dossier de 2 pages pour le propriétaire. Explique ce qui pèse le plus sur la note, les travaux qui pourraient la faire évoluer et un ordre de grandeur de leur coût, à faire confirmer par des devis. Ne promets aucune étiquette.
Format : 1. Votre DPE en clair (5 lignes). 2. Les 3 postes qui pèsent le plus. 3. Les pistes de travaux, de la plus simple à la plus lourde. 4. Une mention : « Document d'information, seul un diagnostiqueur certifié peut établir un DPE. » 5. Signature : [TON NOM], [TON AGENCE], [TA CARTE PRO].''') + '''
  <div class="bloc">
    <h2>Erreurs fréquentes et règles à respecter</h2>
    <ul class="points">
      <li><strong>Annoncer une étiquette que l'attestation ne confirme pas.</strong> Seule l'attestation officielle de l'ADEME fait foi. Dans une annonce, affichez l'étiquette du document que vous avez en main.</li>
      <li><strong>Se substituer au diagnostiqueur.</strong> Le dossier de l'IA est une explication, pas un diagnostic. Écrivez-le noir sur blanc.</li>
      <li><strong>Téléphoner au propriétaire.</strong> Sans son accord, l'appel de prospection est interdit depuis le 11&nbsp;août 2026. Le courrier et la remise en main propre restent possibles. <a class="lien-texte" href="/prospection-immobiliere-sans-pige/">Notre guide sur la prospection sans pige</a></li>
      <li><strong>Mettre des noms dans l'IA.</strong> Les données du diagnostic suffisent. Pas de nom ni d'adresse complète dans le prompt.</li>
      <li><strong>Confondre les deux réformes de 2027.</strong> L'une modifie le calcul, donc l'étiquette. L'autre ajoute des informations au document, sans changer la lettre.</li>
    </ul>
  </div>
''' + formation_bloc("La prospection par le DPE est travaillée dans nos formations sur votre propre secteur&nbsp;: repérage des adresses avec Academia Secteur, courrier, dossier et calendrier de janvier.") + '\n' + GARANTIES,
 [("Qu'est-ce qui change pour le DPE au 1er janvier 2027&nbsp;?", "Le coefficient de conversion de l'électricité passe de 1,9 à 1,7. Certains logements chauffés à l'électricité gagnent une classe, sans travaux ni nouvelle visite."),
  ("Faut-il refaire le DPE&nbsp;?", "Non. Le DPE reste valable dix ans. Si l'étiquette s'améliore, une attestation gratuite se télécharge sur l'Observatoire DPE-Audit de l'ADEME avec le numéro du diagnostic."),
  ("Un agent immobilier peut-il télécharger l'attestation d'un bien&nbsp;?", "L'attestation se génère à partir du numéro du DPE. Pour vos mandats, vous l'avez au dossier. Pour un propriétaire que vous ne connaissez pas, le plus simple est de lui indiquer la démarche, ou de lui remettre le document en lui expliquant d'où il vient."),
  ("L'IA peut-elle recalculer un DPE&nbsp;?", "Non. Elle explique un diagnostic existant et met en forme des pistes de travaux. Seul un diagnostiqueur certifié établit un DPE.")])

# ---------------------------------------------------------------- Guide : PV d'AG avec Gemini Notebook (ex-NotebookLM)
ecrire('pv-assemblee-generale-gemini-notebook/',
 "PV d'AG : les lire avec Gemini Notebook | Start Academia",
 "Trois ans de PV d'assemblée générale, un règlement de copropriété scanné : comment en tirer une synthèse vérifiable pour l'acquéreur avec Gemini Notebook.",
 "Lire trois ans de PV d'AG avec Gemini Notebook, l'ancien NotebookLM.",
 "Travaux votés, fonds travaux, charges, procédures en cours&nbsp;: les réponses sont dans les procès-verbaux d'assemblée générale, que personne ne lit en entier. L'outil gratuit de Google les lit pour vous, et vous montre où il a trouvé chaque réponse.",
 '''  <div class="bloc">
    <h2>Le cas en agence</h2>
    <p>En visite, l'acquéreur demande s'il y a des travaux votés dans la copropriété. Vous avez trois PV d'assemblée générale, un règlement de 1972 scanné de travers et les diagnostics. Soit vous répondez «&nbsp;je vérifie et je reviens vers vous&nbsp;», soit vous avez la réponse sur votre téléphone, avec la page du PV qui la justifie.</p>
  </div>
  <div class="bloc">
    <h2>Pourquoi cet outil plutôt que ChatGPT</h2>
    <p>Gemini Notebook, qui s'appelait NotebookLM jusqu'à l'été 2026, ne répond qu'à partir des documents que vous lui donnez. Chaque réponse porte un numéro&nbsp;: vous cliquez, vous voyez le passage exact du document. Le contrôle prend quelques secondes, au lieu de relire tout le dossier.</p>
    <p>La version gratuite accepte 50&nbsp;sources par dossier, ce qui couvre largement un bien.</p>
  </div>
  <div class="bloc">
    <h2>La méthode classique, boostée à l'IA</h2>
    <ol class="points numerotes">
      <li><strong>Un dossier par bien.</strong> Dès la prise de mandat, vous déposez les trois derniers PV d'assemblée générale, le règlement de copropriété, les diagnostics et l'avis de taxe foncière.</li>
      <li><strong>Poser les questions de l'acquéreur avant lui.</strong> Travaux votés et restant à payer, fonds travaux, évolution des charges, procédures en cours, ce qui est partie commune ou privative.</li>
      <li><strong>Vérifier chaque réponse.</strong> Un clic sur le numéro affiche la source. Si la réponse ne renvoie à aucun passage, vous ne l'utilisez pas.</li>
      <li><strong>Restituer en clair.</strong> Une synthèse d'une page, une infographie, ou un court résumé audio que l'acquéreur écoute chez lui.</li>
      <li><strong>Parler la langue du client.</strong> Pour un acquéreur étranger, le même résumé se génère en anglais, à partir des documents en français.</li>
    </ol>
  </div>
  <div class="bloc">
    <h2>Ce que vous gagnez</h2>
    <ul class="points">
      <li><strong>Une réponse immédiate et sourcée</strong> aux questions sur la copropriété, en visite comme au téléphone.</li>
      <li><strong>Un dossier lisible</strong> à remettre à l'acquéreur, au lieu d'une pile de PDF que personne n'ouvre.</li>
      <li><strong>Un argument de mandat</strong>&nbsp;: montrer au vendeur comment son bien sera présenté.</li>
    </ul>
  </div>
''' + prompt_bloc("Prompt gratuit : la synthèse copropriété pour l'acquéreur", '''Rôle : tu es l'assistant d'un conseiller immobilier. Tu réponds uniquement à partir des documents fournis et tu indiques la source de chaque information.
Contexte : les documents concernent le lot [NUMÉRO DE LOT] d'une copropriété. Lecteur : un acquéreur qui n'a jamais lu un PV d'assemblée générale.
Tâche : rédige une synthèse de la copropriété sur les trois dernières années. Si une information ne figure pas dans les documents, écris « non précisé dans les documents » au lieu de supposer.
Format : 1. La copropriété en 5 lignes (nombre de lots, syndic, budget annuel). 2. Travaux votés : nature, montant, date, part restant à payer. 3. Fonds travaux et évolution des charges. 4. Procédures et points de vigilance. 5. Les 3 questions à poser au syndic.''') + '''
  <div class="bloc">
    <h2>Erreurs fréquentes et règles à respecter</h2>
    <ul class="points">
      <li><strong>Croire que l'outil ne se trompe jamais.</strong> Il limite ses réponses à vos documents, ce qui réduit fortement les erreurs sans les supprimer. Un scan illisible ou un PV manquant donnent une réponse fausse ou incomplète. Vous vérifiez toujours la source.</li>
      <li><strong>Remplacer les documents par la synthèse.</strong> La synthèse aide à comprendre. Elle ne dispense jamais de remettre à l'acquéreur les documents que la loi impose d'annexer à la promesse de vente.</li>
      <li><strong>Laisser des données personnelles.</strong> Un PV cite des copropriétaires, parfois leurs impayés. La synthèse remise à l'acquéreur ne nomme personne.</li>
      <li><strong>Diffuser un PV à des tiers.</strong> Les documents confiés par votre vendeur servent à vendre son bien, pas à démarcher l'immeuble.</li>
      <li><strong>Garder les défauts pour soi.</strong> Si la synthèse révèle une procédure ou de gros travaux, l'acquéreur doit le savoir. Votre devoir de conseil passe avant la vente.</li>
    </ul>
  </div>
''' + formation_bloc("L'analyse des documents de copropriété est travaillée dans nos formations IA sur un dossier réel de votre agence&nbsp;: questions à poser, vérification des sources, synthèse et résumé audio pour l'acquéreur.") + '\n' + GARANTIES,
 [("NotebookLM existe-t-il encore&nbsp;?", "Oui, sous un autre nom. L'outil de Google s'appelle Gemini Notebook depuis l'été 2026. Le fonctionnement est le même : il répond à partir de vos documents et cite ses sources."),
  ("Est-ce gratuit&nbsp;?", "La version gratuite suffit pour un usage en agence : 50 sources par dossier et quelques résumés audio par jour. Un compte Google est nécessaire."),
  ("Peut-on y déposer les documents d'un client&nbsp;?", "Oui pour les documents du bien à vendre, dans le cadre de votre mandat. Informez votre vendeur des outils que vous utilisez et ne déposez pas de pièces d'identité ni de documents sans rapport avec la vente."),
  ("Combien de temps faut-il pour un dossier&nbsp;?", "Le dépôt des documents prend quelques minutes. Le plus long reste votre relecture : chaque réponse utilisée doit être vérifiée dans sa source.")])


# ================================================================ Rubrique Guides (/guides/)
# Liste tous les guides, rangés par étape du métier. Pour ajouter un guide : l'écrire avec ecrire() plus haut,
# l'inscrire dans GUIDES (date) et dans une rubrique ci-dessous.
RUBRIQUES = [
    ('Prospection', ['prospecter-avec-le-dpe/', 'prospection-immobiliere-sans-pige/', 'ia-prospection-immobiliere/']),
    ('Estimation et prix', ['vendeur-parti-trop-cher-reprendre-mandat/', 'ia-estimation-immobiliere/']),
    ('Mandat et annonce', ['ia-mandat-exclusif/', 'ia-annonce-immobiliere/']),
    ('Acquéreurs', ['pv-assemblee-generale-gemini-notebook/', 'ia-decouverte-acquereur/', 'ia-visite-immobiliere/', 'ia-negociation-immobiliere/']),
    ('Financement', ['financement-formation-auto-entrepreneur/']),
]


def rubrique_guides():
    classes = [c for _, liste in RUBRIQUES for c in liste]
    oublis = sorted(set(GUIDES) - set(classes))
    if oublis or len(classes) != len(set(classes)):
        raise SystemExit(f'seo_pages : guides absents ou en double dans RUBRIQUES : {oublis}')
    sections, elements = [], []
    for nom, liste in RUBRIQUES:
        cartes = ''
        for c in liste:
            titre, desc = PAGES[c]
            cartes += (f'\n      <a class="guide-carte" href="/{c}"><span class="gc-etape">{nom}</span><strong>{titre}</strong>'
                       f'<span class="gc-desc">{desc}</span><span class="gc-date">Mis à jour le <time datetime="{GUIDES[c][0]}">{date_fr(GUIDES[c][0])}</time> · {AUTEURS[GUIDES[c][1]][0]}</span></a>')
            elements.append({"@type": "ListItem", "position": len(elements) + 1, "name": h.unescape(titre).replace('\xa0', ' '), "url": f"{SITE}/{c}"})
        sections.append(f'  <section class="guides-rubrique" aria-label="{nom}">\n    <h2>{nom}</h2>\n    <div class="guides-grille">{cartes}\n    </div>\n  </section>')
    chemin = 'guides/'
    desc = "Les guides pratiques de Start Academia pour les agents immobiliers : prospection, estimation, mandat, acquéreurs. Méthode, prompt gratuit et règles à respecter."
    page(chemin, 'Guides pratiques IA et immobilier | Start Academia', desc, 'Les guides.',
         f"{len(classes)} guides tirés de nos formations, rangés par étape du métier. Chacun part d'un cas d'agence, donne la méthode, un prompt prêt à copier et les règles à respecter.",
         '\n'.join(sections))
    graph = [
        {"@type": "CollectionPage", "@id": f"{SITE}/{chemin}", "url": f"{SITE}/{chemin}", "name": "Guides pratiques IA et immobilier",
         "description": desc, "inLanguage": "fr-FR", "isPartOf": {"@id": f"{SITE}/#site"}, "about": {"@id": f"{SITE}/#organisation"}},
        {"@type": "ItemList", "itemListElement": elements},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Accueil", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Guides", "item": f"{SITE}/{chemin}"}]},
    ]
    p = racine / chemin / 'index.html'
    p.write_text(p.read_text().replace('</head>', '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False) + '</script>\n</head>', 1))
    print(chemin, len(classes), 'guides')


rubrique_guides()
