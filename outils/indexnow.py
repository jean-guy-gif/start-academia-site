"""Prévient Bing (et les autres moteurs IndexNow) des pages modifiées du site.

Usage :
  python3 outils/indexnow.py AVANT APRES   # pages modifiées entre deux commits
  python3 outils/indexnow.py --tout        # toutes les pages du sitemap

Seules les URL présentes dans sitemap.xml sont envoyées (les pages noindex
comme /merci-rendez-vous/ sont donc exclues d'office).
Le script attend que Vercel ait mis le site à jour avant d'envoyer, et ne fait
jamais échouer le workflow : un échec d'IndexNow n'empêche pas la mise en ligne.
"""
import json
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
HOTE = "www.start-academia.fr"
CLE = "62f2ab297f13a71e6dc94e5b6e794bb9"
ATTENTE_DEPLOIEMENT = 120  # secondes laissées à Vercel pour publier


def urls_sitemap():
    texte = (RACINE / "sitemap.xml").read_text(encoding="utf-8")
    return re.findall(r"<loc>([^<]+)</loc>", texte)


def url_de_fichier(fichier):
    if fichier == "index.html":
        return f"https://{HOTE}/"
    if fichier.endswith("/index.html"):
        return f"https://{HOTE}/{fichier[: -len('index.html')]}"
    return None


def urls_modifiees(avant, apres):
    if not avant or set(avant) == {"0"}:
        return []
    sortie = subprocess.run(
        ["git", "diff", "--name-only", avant, apres],
        cwd=RACINE, capture_output=True, text=True,
    )
    if sortie.returncode != 0:
        print("git diff impossible :", sortie.stderr.strip())
        return []
    connues = set(urls_sitemap())
    urls = []
    for fichier in sortie.stdout.split():
        url = url_de_fichier(fichier)
        if url and url in connues and url not in urls:
            urls.append(url)
    return urls


def envoyer(urls):
    corps = json.dumps({
        "host": HOTE,
        "key": CLE,
        "keyLocation": f"https://{HOTE}/{CLE}.txt",
        "urlList": urls,
    }).encode("utf-8")
    requete = urllib.request.Request(
        "https://api.indexnow.org/indexnow",
        data=corps,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(requete, timeout=30) as reponse:
            print(f"IndexNow : réponse {reponse.status} pour {len(urls)} URL.")
    except urllib.error.HTTPError as e:
        print(f"IndexNow : erreur {e.code} ({e.reason}).")
    except Exception as e:  # réseau, délai…
        print(f"IndexNow : envoi impossible ({e}).")


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--tout":
        urls = urls_sitemap()
    elif len(sys.argv) == 3:
        urls = urls_modifiees(sys.argv[1], sys.argv[2])
    else:
        print(__doc__)
        return
    if not urls:
        print("Aucune page du sitemap modifiée : rien à envoyer.")
        return
    print("Pages à signaler :", *urls, sep="\n  ")
    print(f"Attente de {ATTENTE_DEPLOIEMENT} s pour laisser Vercel publier…")
    time.sleep(ATTENTE_DEPLOIEMENT)
    envoyer(urls)


if __name__ == "__main__":
    main()
