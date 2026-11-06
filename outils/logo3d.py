"""Construit la géométrie 3D du « A » Start Academia (extrudé + biseauté) à partir des tracés SVG du logo.
Sortie : logo3d-geo.js à la racine du dépôt (positions + normales en base64), lu par logo3d.js (WebGL, sans bibliothèque)."""
import re, math, struct, base64, json, pathlib

W = "M136.5,371.9C124.1,369.0 118.4,361.9 119.2,350.1C119.6,343.8 124.1,331.9 135.2,307.1C136.3,304.7 142.3,290.3 148.6,275.1C155.0,259.9 160.9,245.7 161.9,243.5C164.2,238.5 167.6,230.5 173.3,216.5C175.8,210.4 180.8,198.3 184.5,189.5C188.1,180.7 192.7,169.7 194.7,165.0C196.6,160.3 198.8,155.2 199.5,153.5C200.2,151.8 201.6,148.5 202.6,146.0C207.0,134.8 214.7,125.2 223.2,120.1C230.2,116.0 236.7,114.6 250.5,114.6C266.1,114.6 273.7,116.8 282.5,123.7C289.8,129.5 291.9,132.9 299.6,151.6C303.1,160.3 306.7,168.8 307.4,170.5C308.2,172.2 310.0,176.4 311.5,180.0C312.9,183.6 314.7,187.8 315.5,189.5C316.2,191.2 318.1,195.7 319.6,199.5C321.1,203.3 322.6,206.9 323.0,207.5C325.6,211.4 328.0,225.6 328.0,237.1C328.0,246.5 327.4,250.7 324.8,260.5C320.5,276.8 308.5,295.1 295.0,305.9C289.2,310.6 272.6,319.3 245.8,331.9C229.8,339.3 225.8,341.2 213.7,346.9C206.6,350.3 200.7,353.0 200.5,353.0C200.4,353.0 194.0,356.0 186.4,359.6C164.6,369.9 162.7,370.7 158.5,371.7C153.4,373.0 141.7,373.1 136.5,371.9ZM210.9,287.1C214.0,285.5 220.1,282.5 224.5,280.4C252.7,267.3 255.1,266.0 260.3,261.1C266.3,255.4 271.7,245.8 272.6,239.0C273.1,235.0 272.5,233.0 267.7,222.0C264.7,215.1 259.4,203.0 256.0,195.0C248.5,177.8 247.7,176.5 246.2,178.2C245.7,178.9 243.5,183.8 241.5,189.0C239.4,194.2 237.0,200.3 236.0,202.5C235.0,204.7 233.5,208.5 232.7,211.0C231.3,215.2 229.0,220.9 227.0,225.5C226.6,226.6 222.5,236.9 218.0,248.5C213.5,260.1 209.2,270.9 208.5,272.5C200.3,291.3 200.5,292.4 210.9,287.1Z"
O = "M337.5,371.8C335.9,371.3 331.6,369.4 328.0,367.7C316.8,362.5 303.7,356.4 299.0,354.2C282.4,346.6 277.9,344.2 279.2,343.4C279.9,342.9 283.8,340.8 287.9,338.7C292.0,336.6 298.3,332.8 301.9,330.3C311.0,324.0 325.6,309.0 331.4,300.1C336.1,292.9 342.9,279.4 344.7,273.6C346.1,269.3 347.4,269.4 349.2,274.2C351.1,279.1 365.4,313.0 367.5,317.5C368.2,319.1 369.8,323.0 371.0,326.0C373.4,332.1 375.8,337.7 376.9,340.0C377.4,340.8 378.3,343.8 379.0,346.6C380.1,351.0 380.1,352.3 378.5,356.9C374.7,368.5 366.6,373.1 350.2,372.9C344.9,372.9 339.1,372.4 337.5,371.8Z"

def anneaux(d, pas=4):
    """Découpe un tracé (M, C, Z absolus) en polylignes fermées."""
    out, cur, p = [], None, None
    for cmd, args in re.findall(r'([MCZ])([^MCZ]*)', d):
        n = [float(v) for v in re.findall(r'-?\d+\.?\d*', args)]
        if cmd == 'M': p = (n[0], n[1]); cur = [p]
        elif cmd == 'C':
            for i in range(0, len(n), 6):
                a, b, c = (n[i], n[i+1]), (n[i+2], n[i+3]), (n[i+4], n[i+5])
                for k in range(1, pas + 1):
                    t = k / pas; u = 1 - t
                    cur.append((u**3*p[0] + 3*u*u*t*a[0] + 3*u*t*t*b[0] + t**3*c[0],
                                u**3*p[1] + 3*u*u*t*a[1] + 3*u*t*t*b[1] + t**3*c[1]))
                p = c
        elif cmd == 'Z':
            if math.dist(cur[0], cur[-1]) < 1e-6: cur.pop()
            # retire les points quasi confondus
            net = [cur[0]]
            for q in cur[1:]:
                if math.dist(q, net[-1]) > 1.2: net.append(q)
            out.append(net)
    return out

aire = lambda r: sum(r[i-1][0]*r[i][1] - r[i][0]*r[i-1][1] for i in range(len(r))) / 2  # > 0 : sens trigonométrique

def orienter(r, ccw):
    return r if (aire(r) > 0) == ccw else r[::-1]

def normales2d(r):
    """Normale sortante (côté matière -> extérieur) à chaque sommet, avec onglet limité."""
    n = len(r); res = []
    for i in range(n):
        a, b, c = r[i-1], r[i], r[(i+1) % n]
        e1 = (b[0]-a[0], b[1]-a[1]); e2 = (c[0]-b[0], c[1]-b[1])
        l1 = math.hypot(*e1) or 1; l2 = math.hypot(*e2) or 1
        n1 = (e1[1]/l1, -e1[0]/l1); n2 = (e2[1]/l2, -e2[0]/l2)
        m = (n1[0]+n2[0], n1[1]+n2[1]); lm = math.hypot(*m) or 1; m = (m[0]/lm, m[1]/lm)
        k = 1 / max(.5, m[0]*n1[0] + m[1]*n1[1])
        res.append((m, k))
    return res

def pont(ext, trou):
    """Relie le trou au contour extérieur pour obtenir un seul polygone (pour la triangulation)."""
    hi = max(range(len(trou)), key=lambda i: trou[i][0])
    h = trou[hi]
    def coupe(p1, p2, p3, p4):
        d = lambda a, b, c: (c[0]-a[0])*(b[1]-a[1]) - (c[1]-a[1])*(b[0]-a[0])
        return d(p1, p2, p3)*d(p1, p2, p4) < 0 and d(p3, p4, p1)*d(p3, p4, p2) < 0
    cand = sorted(range(len(ext)), key=lambda i: math.dist(ext[i], h))
    for oi in cand:
        o = ext[oi]; ok = True
        for r in (ext, trou):
            for j in range(len(r)):
                a, b = r[j], r[(j+1) % len(r)]
                if a in (o, h) or b in (o, h): continue
                if coupe(o, h, a, b): ok = False; break
            if not ok: break
        if ok: break
    return ext[:oi+1] + trou[hi:] + trou[:hi+1] + ext[oi:]

def oreilles(poly):
    """Triangulation par oreilles (polygone CCW, éventuellement avec pont)."""
    idx = list(range(len(poly))); tris = []
    cross = lambda a, b, c: (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])
    def dedans(p, a, b, c):  # strictement à l'intérieur : les points posés sur un bord ne bloquent pas
        e = 1e-12
        return cross(a, b, p) > e and cross(b, c, p) > e and cross(c, a, p) > e
    garde = 0
    while len(idx) > 3 and garde < 200000:
        garde += 1; trouve = False
        for k in range(len(idx)):
            i0, i1, i2 = idx[k-1], idx[k], idx[(k+1) % len(idx)]
            a, b, c = poly[i0], poly[i1], poly[i2]
            cr = cross(a, b, c)
            if abs(cr) < 1e-10 and poly[i0] != poly[i2]:   # sommet aligné : on le retire sans triangle
                idx.pop(k); trouve = True; break
            if cr <= 0: continue
            if any(dedans(poly[j], a, b, c) for j in idx if j not in (i0, i1, i2)): continue
            tris.append((i0, i1, i2)); idx.pop(k); trouve = True; break
        if not trouve:
            print('  ! triangulation : sommet forcé'); tris.append((idx[-1], idx[0], idx[1])); idx.pop(0)
    if len(idx) == 3: tris.append(tuple(idx))
    return tris

def solide(rings, P, N, profondeur, biseau, etapes=3):
    """rings : contour extérieur CCW + trous CW, en unités finales. Remplit P (positions) et N (normales)."""
    def tri(a, b, c, na, nb, nc):
        P.extend(a + b + c); N.extend(na + nb + nc)
    h = profondeur / 2
    for r in rings:
        nm = normales2d(r)
        # profil : arrondi arrière (θ -π/2..0), flanc, arrondi avant (θ 0..π/2)
        prof = []
        for k in range(etapes + 1):
            t = -math.pi/2 + k/etapes * math.pi/2
            prof.append((biseau*(math.cos(t)-1), -h + biseau*math.sin(t), math.cos(t), math.sin(t)))
        for k in range(etapes + 1):
            t = k/etapes * math.pi/2
            prof.append((biseau*(math.cos(t)-1), h + biseau*math.sin(t), math.cos(t), math.sin(t)))
        n = len(r)
        for i in range(n):
            j = (i+1) % n
            for s in range(len(prof)-1):
                pts = []
                for (v, (m, kk)) in ((r[i], nm[i]), (r[j], nm[j])):
                    for (off, z, cn, sz) in (prof[s], prof[s+1]):
                        pts.append(((v[0]+m[0]*off*kk, v[1]+m[1]*off*kk, z), (m[0]*cn, m[1]*cn, sz)))
                (a, na), (b, nb), (c, nc), (d, nd) = pts  # a=i,s  b=i,s+1  c=j,s  d=j,s+1
                tri(a, c, b, na, nc, nb); tri(b, c, d, nb, nc, nd)
    # faces avant et arrière, rentrées de la valeur du biseau
    rentres = []
    for r in rings:
        nm = normales2d(r)
        rentres.append([(v[0]-m[0]*biseau*kk, v[1]-m[1]*biseau*kk) for v, (m, kk) in zip(r, nm)])
    poly = rentres[0]
    for t in rentres[1:]: poly = pont(poly, t)
    for (i0, i1, i2) in oreilles(poly):
        a, b, c = poly[i0], poly[i1], poly[i2]
        zf = h + biseau
        tri((*a, zf), (*b, zf), (*c, zf), (0, 0, 1), (0, 0, 1), (0, 0, 1))
        tri((*a, -zf), (*c, -zf), (*b, -zf), (0, 0, -1), (0, 0, -1), (0, 0, -1))

# repère : centre de l'ensemble, y vers le haut, 2 unités de haut
blanc, orange = anneaux(W), anneaux(O)
tous = [p for r in blanc + orange for p in r]
xs, ys = [p[0] for p in tous], [p[1] for p in tous]
cx, cy = (min(xs)+max(xs))/2, (min(ys)+max(ys))/2
ech = 2.0 / max(max(xs)-min(xs), max(ys)-min(ys))
conv = lambda r: [((x-cx)*ech, -(y-cy)*ech) for x, y in r]
blanc = [conv(r) for r in blanc]; orange = [conv(r) for r in orange]
blanc = [orienter(blanc[0], True)] + [orienter(r, False) for r in blanc[1:]]
orange = [orienter(orange[0], True)]

def centre(r):
    return (sum(p[0] for p in r)/len(r), sum(p[1] for p in r)/len(r))
co = centre(orange[0])
orange_local = [[(x-co[0], y-co[1]) for x, y in orange[0]]]

PROF, BIS = 64*ech, 12*ech
BIS_ORANGE = 7*ech
sortie = {}
for nom, rings in (('blanc', blanc), ('orange', orange_local)):
    P, N = [], []
    solide(rings, P, N, PROF, BIS if nom == 'blanc' else BIS_ORANGE)
    # positions en entiers 16 bits (÷ 16000), normales en entiers 8 bits (÷ 127) : 4 fois plus léger
    data = struct.pack(f'<{len(P)}h', *[max(-32767, min(32767, round(v*16000))) for v in P])
    data += struct.pack(f'<{len(N)}b', *[max(-127, min(127, round(v*127))) for v in N])
    sortie[nom] = {'n': len(P)//3, 'b64': base64.b64encode(data).decode()}
sortie['co'] = [round(co[0], 4), round(co[1], 4)]
js = '// Géométrie générée par outils/logo3d.py à partir des tracés du logo. Ne pas modifier à la main.\nwindow.LOGO3D = ' + json.dumps(sortie) + ';\n'
(pathlib.Path(__file__).resolve().parents[1] / 'logo3d-geo.js').write_text(js)
print('blanc', sortie['blanc']['n'], 'sommets ; orange', sortie['orange']['n'], '; taille', len(js)//1024, 'Ko')
