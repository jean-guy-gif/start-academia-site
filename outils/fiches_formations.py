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
  intro="Notre parcours le plus complet, et notre formation la plus suivie. En 9 jours, vous passez des bases de ChatGPT aux automatisations et à votre propre assistant IA, toujours sur vos dossiers.",
  pourquoi='''<p>Une journée d'initiation donne des idées&nbsp;; elle change rarement les habitudes. Ce parcours est construit pour que l'IA entre <strong>dans chaque étape de votre semaine</strong>&nbsp;: prospection, préparation du rendez-vous vendeur, suivi, annonces et marketing, puis automatisation des tâches répétitives.</p>
    <p>Chaque journée se termine par un atelier sur vos propres dossiers. À la fin, chaque conseiller repart avec ses prompts, ses modèles, son assistant IA et un plan d'action individuel.</p>
    <p><strong>Financement&nbsp;:</strong> à 42&nbsp;€ de l'heure en présentiel, l'enveloppe AGEFICE de 3&nbsp;000&nbsp;€ couvre presque tout le parcours (3&nbsp;024&nbsp;€)&nbsp;: il reste 24&nbsp;€ à votre charge. <a class="lien-texte" href="/financement-formation-auto-entrepreneur/">Vérifier vos droits</a></p>''',
  liens=[('/formation-ia-immobilier/', "Toutes nos formations IA pour l'immobilier"),
         ('/formation-chatgpt-immobilier/', 'Formation ChatGPT immobilier'),
         ('/prospection-immobiliere-sans-pige/', 'Guide : prospecter sans pige'),
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
    <p>Elle se combine souvent avec notre <a class="lien-texte" href="/formations/#non-discrimination-tracfin-et-deontologie">formation non-discrimination, TRACFIN et déontologie</a> (8&nbsp;h) pour la formation continue loi ALUR.</p>''',
  liens=[('/formation-loi-alur/', 'Formation continue loi ALUR'),
         ('/formations/#non-discrimination-tracfin-et-deontologie', 'Non-discrimination, TRACFIN et déontologie (8 h)'),
         ('/financement-formation-immobilier/', 'Financement : calculer mes droits')],
  faq=[("Qui doit être formé à TRACFIN&nbsp;?", "Les agents immobiliers et leurs collaborateurs qui participent aux transactions : négociateurs salariés, agents commerciaux, assistants."),
       ("La formation compte-t-elle pour la loi ALUR&nbsp;?", "Oui. Elle entre dans la formation continue obligatoire des professionnels de l'immobilier, avec une attestation remise en fin de formation."),
       ("Combien coûte-t-elle&nbsp;?", "À partir de 168 € (42 € de l'heure), finançable par l'OPCO de l'agence, l'AGEFICE ou le FIF PL."),
       ("Comment se déroule-t-elle&nbsp;?", "Deux heures d'apports sur le rôle de TRACFIN, les obligations et les signaux d'alerte, puis deux heures de mises en situation par équipes sur des dossiers clients fictifs.")]),
}


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
         "teaches": [str(o).rstrip('.') for o in f['obj']],
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
        objectifs = ''.join(f'<li>{h.escape(str(o))}</li>' for o in f['obj'])
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
