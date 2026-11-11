"""Régénère tout le site, depuis n'importe quel dossier : python3 outils/build.py

Enchaîne les générateurs dans l'ordre requis (chacun relit ce que le précédent a écrit).
S'arrête au premier script en erreur, avec son code de sortie."""
import pathlib, subprocess, sys

OUTILS = pathlib.Path(__file__).resolve().parent
ETAPES = ['pages.py', 'formations.py', 'seo_pages.py', 'fiches_formations.py', 'resultats.py', 'jsonld_pages.py', 'chiffres.py']

for script in ETAPES:
    print(f'--- {script}', flush=True)
    r = subprocess.run([sys.executable, str(OUTILS / script)], cwd=OUTILS.parent)
    if r.returncode:
        sys.exit(f'build : {script} a échoué (code {r.returncode})')
print('--- site régénéré')
