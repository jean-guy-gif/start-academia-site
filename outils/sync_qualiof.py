"""Récupère le catalogue et les indicateurs publics de QualiOF et les écrit dans data/qualiof.json.

    python3 outils/sync_qualiof.py                                     # API (QUALIOF_API_BASE, défaut https://qualiof.vercel.app)
    python3 outils/sync_qualiof.py --fixture data/qualiof.exemple.json # hors ligne

Le site ne doit jamais casser à cause de QualiOF : en cas d'échec ou de réponse invalide, le message
part sur stderr, data/qualiof.json n'est pas touché et le script sort quand même avec le code 0.

Ne sont conservés que les champs utilisés par le site. Les champs qui changent à chaque appel
(calculeLe) sont écartés pour que le fichier ne change que si le contenu change. Par précaution,
toute ligne de texte contenant un numéro de téléphone ou une adresse e-mail est retirée :
le site n'affiche aucune coordonnée nominative venant de QualiOF."""
import argparse, json, os, pathlib, re, sys, time, urllib.request

RACINE = pathlib.Path(__file__).resolve().parents[1]
SORTIE = RACINE / 'data' / 'qualiof.json'
BASE = os.environ.get('QUALIOF_API_BASE', 'https://qualiof.vercel.app').rstrip('/')
TIMEOUT = 20

CHAMPS_PROGRAMME = ['code', 'slug', 'titre', 'theme', 'dureeHeures', 'modalite', 'public', 'prerequis',
                    'objectifs', 'programme', 'misAJourLe', 'indicateurs']
TEXTES = ['titre', 'public', 'prerequis', 'programme']
COORDONNEES = re.compile(r'(?:\+33[\s.]?|\b0)[1-9](?:[\s.-]?\d{2}){4}\b|[\w.+-]+@[\w-]+(?:\.[\w-]+)+')


class Invalide(Exception):
    pass


def lire_api(chemin, v):
    url = f'{BASE}{chemin}?v={v}'
    req = urllib.request.Request(url, headers={'Cache-Control': 'no-cache', 'Accept': 'application/json',
                                               'User-Agent': 'start-academia-site/sync-qualiof'})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            if r.status != 200:
                raise Invalide(f'{url} : HTTP {r.status}')
            return json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        raise Invalide(f'{url} : HTTP {e.code}')
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise Invalide(f'{url} : injoignable ({getattr(e, "reason", e)})')
    except ValueError as e:
        raise Invalide(f'{url} : JSON illisible ({e})')


def sans_coordonnees(texte, ou, retraits):
    if not isinstance(texte, str):
        return texte
    lignes = texte.split('\n')
    gardees = [l for l in lignes if not COORDONNEES.search(l)]
    if len(gardees) != len(lignes):
        retraits.append(f'{ou} : {len(lignes) - len(gardees)} ligne(s)')
    return '\n'.join(gardees)


def valider(prog, ind):
    for nom, rep in (('programmes', prog), ('indicateurs', ind)):
        if not isinstance(rep, dict):
            raise Invalide(f'{nom} : la réponse n’est pas un objet JSON')
        if rep.get('version') != '1':
            raise Invalide(f'{nom} : version {rep.get("version")!r}, attendu "1"')
    liste = prog.get('programmes')
    if not isinstance(liste, list) or not liste:
        raise Invalide('programmes : aucun programme')
    for i, p in enumerate(liste):
        if not isinstance(p, dict):
            raise Invalide(f'programmes[{i}] : pas un objet')
        manque = [c for c in ('code', 'titre', 'dureeHeures', 'objectifs') if p.get(c) in (None, '')]
        if manque:
            raise Invalide(f'programme {p.get("code") or i} : champ(s) manquant(s) {", ".join(manque)}')
        if not isinstance(p['objectifs'], list):
            raise Invalide(f'programme {p["code"]} : objectifs n’est pas une liste')
    codes = [p['code'] for p in liste]
    if len(set(codes)) != len(codes):
        raise Invalide('programmes : codes en double')
    if not isinstance(ind.get('total'), dict):
        raise Invalide('indicateurs : total manquant')


def normaliser(prog, ind):
    retraits, programmes = [], []
    for p in sorted(prog['programmes'], key=lambda p: p['code']):
        q = {c: p.get(c) for c in CHAMPS_PROGRAMME}
        for c in TEXTES:
            q[c] = sans_coordonnees(q[c], f'{p["code"]}.{c}', retraits)
        q['objectifs'] = [o for o in p['objectifs'] if not COORDONNEES.search(str(o))]
        if len(q['objectifs']) != len(p['objectifs']):
            retraits.append(f'{p["code"]}.objectifs : {len(p["objectifs"]) - len(q["objectifs"])} objectif(s)')
        programmes.append(q)
    if retraits:
        print('sync-qualiof : coordonnées retirées (à corriger dans QualiOF) : ' + ' ; '.join(retraits), file=sys.stderr)
    return {
        'source': prog.get('source', 'QualiOF'),
        'version': '1',
        'methodeIndicateurs': prog.get('methodeIndicateurs') or ind.get('methode'),
        'programmes': programmes,
        'indicateurs': {'total': ind['total'], 'parAnnee': ind.get('parAnnee') or []},
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--fixture', help='fichier JSON {"programmes": <réponse>, "indicateurs": <réponse>} à utiliser au lieu de l’API')
    args = ap.parse_args()
    try:
        if args.fixture:
            try:
                f = json.loads(pathlib.Path(args.fixture).read_text(encoding='utf-8'))
            except (OSError, ValueError) as e:
                raise Invalide(f'fixture {args.fixture} illisible ({e})')
            prog, ind = f.get('programmes'), f.get('indicateurs')
        else:
            v = int(time.time())  # contourne le cache CDN d'une heure de l'API
            prog = lire_api('/api/public/v1/programmes', v)
            ind = lire_api('/api/public/v1/indicateurs', v)
        valider(prog, ind)
        donnees = normaliser(prog, ind)
    except Invalide as e:
        etat = f'{SORTIE.relative_to(RACINE)} conservé' if SORTIE.exists() else f'pas de {SORTIE.relative_to(RACINE)}, le site garde son catalogue intégré'
        print(f'sync-qualiof : ÉCHEC, {e}. {etat}.', file=sys.stderr)
        return 0
    texte = json.dumps(donnees, ensure_ascii=False, indent=2, sort_keys=True) + '\n'
    SORTIE.parent.mkdir(exist_ok=True)
    tmp = SORTIE.with_suffix('.json.tmp')
    tmp.write_text(texte, encoding='utf-8')
    tmp.replace(SORTIE)
    n = sum(1 for p in donnees['programmes'] if ((p.get('indicateurs') or {}).get('apprenantsFormes') or 0) > 0)
    print(f'sync-qualiof : {len(donnees["programmes"])} programmes ({n} avec apprenants formés) -> {SORTIE.relative_to(RACINE)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
