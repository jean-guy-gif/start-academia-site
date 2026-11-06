"""Correspondances entre QualiOF et le catalogue du site. À compléter à la main.

Catégories du site (voir CATS dans formations.py) :
    prospection, vendeur, acheteur, ia, marketing, manager, mindset
    autres : section « Autres formations », créée seulement si elle contient au moins une fiche.

Catégorie d'un programme, par ordre de priorité :
    1. CODE_VERS_CATEGORIE[code]
    2. THEME_VERS_CATEGORIE[theme]
    3. la catégorie de la fiche du site désignée par CODE_VERS_SLUG_SITE[code]
    4. autres

Ancre d'une fiche (/formations/#ancre) : CODE_VERS_SLUG_SITE[code] si présent, sinon le slug de QualiOF.
"""

# Thème QualiOF -> catégorie du site. La casse, les accents et les espaces ne comptent pas
# (« IA immo » trouve « IA Immo »). Thèmes relevés dans l'API le 06/11/2026 ; au 06/11, aucun
# programme qui a des apprenants formés n'a de thème renseigné dans QualiOF.
THEME_VERS_CATEGORIE = {
    # Thèmes qui portent le nom d'une catégorie (la spec QualiOF donne « Vendeur » en exemple)
    'Prospection': 'prospection',
    'Vendeur': 'vendeur',
    'Acheteur': 'acheteur',
    'Intelligence artificielle': 'ia',
    'Marketing': 'marketing',
    'Management': 'manager',
    'Posture': 'mindset',
    'Mindset': 'mindset',
    # Thèmes saisis dans QualiOF
    'IA': 'ia',
    'IA Immo': 'ia',
    'IA, Immobilier': 'ia',
    'Immobilier – IA': 'ia',
    'Commerce – IA': 'ia',
    'Développement commercial immobilier et intégration de l’intelligence artificielle dans les pratiques professionnelles': 'ia',
    'Acquisition / IA': 'prospection',
    'Acquisition / Pilotage': 'prospection',
    'Notoriété / IA': 'marketing',
    'Management / IA': 'manager',
    # 'Immobilier': ?  (FRM-0013, investisseurs locatifs : à classer si la formation est dispensée)
}

# Code QualiOF -> slug d'une des 40 fiches de la liste F de formations.py, pour garder les URL et
# ancres existantes. Première version obtenue le 06/11/2026 par rapprochement des titres
# normalisés (sans accents ni durées) entre F et l'API : seul PROD-0003 est identique, les
# autres sont des rapprochements plausibles à confirmer. Les autres programmes QualiOF n'ont pas
# d'équivalent dans l'ancien catalogue.
CODE_VERS_SLUG_SITE = {
    'PROD-0003': 'limmobilier-et-sa-prospection-efficace-devenir-incontournable-sur-son-secteur',
    'PROD-0041': 'formation-logiciel-cadastre-com-level-1',  # À VÉRIFIER : « Cadastre Niveau 1 - Présentiel Collectif » / « Logiciel Cadastre.com, niveau 1 »
    'PROD-0060': 'formation-logiciel-cadastre-com-level-2-pour-les-professionnels-confirmes',  # À VÉRIFIER : « Cadastre Niveau 2 - Présentiel collectif » / « Logiciel Cadastre.com, niveau 2 »
    'PROD-0059': 'basic-vendeur',  # À VÉRIFIER : « Booster vendeur (8h) » / « Basic vendeur », titres différents
}

# Code QualiOF -> catégorie, quand le thème QualiOF est vide ou ne convient pas. Proposition
# faite d'après les titres le 06/11/2026, pour les programmes qui ont des apprenants formés :
# à valider. Mieux : renseigner le thème dans QualiOF puis retirer la ligne d'ici.
CODE_VERS_CATEGORIE = {
    'PROD-053': 'prospection',   # Cycle complet de prospection, relation client et négociation
    'PROD-055': 'vendeur',       # Maîtrise des techniques de vente immobilière
    'PROD-0042': 'ia',           # L'IA au service des conseillers immobiliers (72h)
    'PROD-0044': 'ia',           # Vendez mieux avec l'IA
    'PROD-0057': 'ia',           # Intégrer l'IA pour gagner en productivité - 105h
    'PROD-0058': 'ia',           # L'IA au service des conseillers immobiliers (8h)
    'PROD-0061': 'ia',           # Intégrer l'IA pour gagner en productivité - 77h
    'PROD-0063': 'ia',           # Intégrer l'IA dans son entreprise - 40h
    'PROD-0064': 'ia',           # Maîtriser l'IA pour booster la performance commerciale - 72h
    'PROD-0065': 'ia',           # Exploiter l'IA dans l'immobilier - 24h
    'PROD-0066': 'ia',           # L'IA au service des conseillers immobiliers - 16h
    'PROD-0662': 'ia',           # Maîtriser l'IA pour développer son activité
    'PROD-0668': 'ia',           # Optimisation des systèmes d'information avec l'IA
    'PROD-0670': 'ia',           # IA générative
    'PROD-0673': 'ia',           # Optimiser son activité immobilière grâce à l'IA - 40h
    'PROD-c0c85e08': 'ia',       # L'IA et sa maîtrise au service des conseillers immobiliers
    'PROD-047': 'marketing',     # Formation complète en marketing digital et IA
    # Laissés dans « Autres formations » : PROD-0062 (Non discrimination, Tracfin et déontologie),
    # PROD-0671 (Tracfin), PROD-0667 (Anglais professionnel boosté par l'IA).
}
