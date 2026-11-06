"""Données structurées des pages secondaires (catalogue, loi ALUR, coaching, mentions légales).
À lancer après pages.py, formations.py et seo_pages.py."""
import pathlib, json, re
from formations import catalogue   # même liste que la page : QualiOF ou repli

SITE = 'https://www.start-academia.fr'
ORG = {"@id": f"{SITE}/#organisation"}
RACINE = pathlib.Path(__file__).resolve().parents[1]
F, _ = catalogue()


def base(chemin, nom, desc):
    return [
        {"@type": "WebPage", "@id": f"{SITE}/{chemin}", "url": f"{SITE}/{chemin}", "name": nom,
         "description": desc, "inLanguage": "fr-FR", "isPartOf": {"@id": f"{SITE}/#site"}, "about": ORG},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Accueil", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": nom, "item": f"{SITE}/{chemin}"}]},
    ]


def cours(nom, desc, heures=None):
    c = {"@type": "Course", "name": nom, "description": desc, "provider": ORG, "inLanguage": "fr",
         "hasCourseInstance": [{"@type": "CourseInstance", "courseMode": "Onsite", "location": "Alpes-Maritimes, France"},
                               {"@type": "CourseInstance", "courseMode": "Online"}],
         "offers": {"@type": "Offer", "category": "Sur devis", "availability": "https://schema.org/InStock"}}
    if heures:
        c["timeRequired"] = f"PT{int(round(heures))}H"
    return c


def injecter(chemin, graph):
    p = RACINE / chemin / 'index.html'
    t = p.read_text()
    t = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', t, flags=re.S)
    bloc = '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False) + '</script>'
    p.write_text(t.replace('</head>', bloc + '\n</head>', 1))
    print(chemin, len(graph), 'blocs')


def desc_de(chemin):
    t = (RACINE / chemin / 'index.html').read_text()
    return re.search(r'<meta name="description" content="([^"]*)"', t).group(1)


# Catalogue : liste des formations
d = desc_de('formations/')
liste = {"@type": "ItemList", "name": "Catalogue des formations Start Academia", "numberOfItems": len(F),
         "itemListElement": [
             {"@type": "ListItem", "position": i + 1, "url": f"{SITE}/formations/#{f['id']}",
              "item": cours(f['titre'], (f['obj'][0] if f['obj'] else f['titre']), f['heures'])} for i, f in enumerate(F)]}
for el in liste["itemListElement"]:
    el["item"]["url"] = el.pop("url")
injecter('formations/', base('formations/', 'Catalogue des formations', d) + [liste])

d = desc_de('formation-loi-alur/')
injecter('formation-loi-alur/', base('formation-loi-alur/', 'Formation loi ALUR', d) +
         [cours('Formation continue loi ALUR pour agents immobiliers', d)])

c = 'coaching-pour-directeur-dagence-immobiliere-dans-le-06/'
d = desc_de(c)
injecter(c, base(c, 'Coaching et audit de direction d’agence immobilière', d) +
         [{"@type": "Service", "name": "Coaching de directeur d’agence immobilière", "description": d,
           "provider": ORG, "areaServed": "Alpes-Maritimes", "serviceType": "Coaching et audit"}])

d = desc_de('mentions-legales/')
injecter('mentions-legales/', base('mentions-legales/', 'Mentions légales', d))
