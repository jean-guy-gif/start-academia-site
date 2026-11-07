"""Met à jour les chiffres de toutes les pages (index.html et sous-pages) depuis le total des indicateurs QualiOF.

Dans index.html :
    data-qualiof="champ"       élément dont le texte contient le chiffre (texte simple, sans balise) :
                               le premier nombre est remplacé, ainsi que data-compte s'il existe
                               (animation de fin.js) ;
    data-qualiof-bloc="champ"  bloc à masquer (attribut hidden) si la valeur vaut null.
Champs : apprenantsFormes, tauxRecommandation, note5.
Sans data/qualiof.json, index.html n'est pas modifié. Les avis Google ne viennent pas de QualiOF."""
import json, pathlib, re, sys

RACINE = pathlib.Path(__file__).resolve().parents[1]
QUALIOF = RACINE / 'data' / 'qualiof.json'
INDEX = RACINE / 'index.html'


def valeurs(total):
    sat = total.get('satisfaction') or {}
    v = {'apprenantsFormes': total.get('apprenantsFormes'),
         'tauxRecommandation': sat.get('tauxRecommandation'),
         'note5': sat.get('note5')}
    texte = {
        'apprenantsFormes': None if v['apprenantsFormes'] is None else str(int(v['apprenantsFormes'])),
        'tauxRecommandation': None if v['tauxRecommandation'] is None else str(round(v['tauxRecommandation'])),
        'note5': None if v['note5'] is None else f'{v["note5"]:.1f}'.replace('.', ','),
    }
    return texte


def basculer_hidden(balise, masquer):
    balise = re.sub(r'\s+hidden(?=[\s>/])', '', balise)
    return balise[:-1] + ' hidden>' if masquer else balise


def appliquer(t, champ, val):
    def element(m):
        ouvre, nom, contenu, ferme = m.group(1), m.group(2), m.group(3), m.group(4)
        if val is not None:
            contenu = re.sub(r'\d+(?:[.,]\d+)?', val, contenu, count=1)
            if 'data-compte=' in ouvre and val.isdigit():
                ouvre = re.sub(r'data-compte="[^"]*"', f'data-compte="{val}"', ouvre)
        return basculer_hidden(ouvre, val is None) + contenu + ferme

    t, n = re.subn(rf'(<(\w+)\b[^>]*\bdata-qualiof="{champ}"[^>]*>)([^<]*)(</\2>)', element, t)
    t = re.sub(rf'<\w+\b[^>]*\bdata-qualiof-bloc="{champ}"[^>]*>', lambda m: basculer_hidden(m.group(0), val is None), t)
    return t, n


def main():
    if not QUALIOF.exists():
        print('chiffres : pas de data/qualiof.json, index.html inchangé')
        return
    try:
        total = json.loads(QUALIOF.read_text(encoding='utf-8'))['indicateurs']['total']
        texte = valeurs(total)
    except (ValueError, KeyError, TypeError) as e:
        print(f'chiffres : data/qualiof.json illisible ({e!r}), index.html inchangé', file=sys.stderr)
        return
    pages = [INDEX] + sorted(p for p in RACINE.glob('*/index.html') if p.parent.name not in ('.git', 'outils', 'data'))
    totaux, modifiees = {champ: 0 for champ in texte}, 0
    for page in pages:
        t0 = page.read_text(encoding='utf-8')
        t = t0
        for champ, val in texte.items():
            t, n = appliquer(t, champ, val)
            totaux[champ] += n
        if t != t0:
            page.write_text(t, encoding='utf-8')
            modifiees += 1
    bilan = [f'{c}={texte[c] if texte[c] is not None else "masqué"} ({totaux[c]})' for c in texte]
    print('chiffres :', ', '.join(bilan), f'- {modifiees} page(s) modifiée(s) sur {len(pages)}')


if __name__ == '__main__':
    main()
