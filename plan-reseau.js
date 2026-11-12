/* Page réseaux : l'animateur règle la taille de son réseau, le niveau de ses mandataires, le format
   et la durée ; la page construit son plan de déploiement et dessine le réseau en groupes de niveau.
   Règles données par Jean-Guy (12/11/2026) : 50 mandataires au plus par session, parcours de 4 à 32 h,
   visio ou présentiel au choix, aucun prix affiché (devis après l'appel découverte). */
(function () {
  var racine = document.querySelector('.plan-reseau');
  if (!racine) return;
  var MAX_GROUPE = 50, MAX_POINTS = 360;
  var calme = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var etat = { n: 120, deb: 60, format: 'visio', h: 16 };
  function q(s) { return racine.querySelector(s); }
  function fr(x) { return x.toLocaleString('fr-FR'); }
  function pl(n, s, p) { return n + ' ' + (n > 1 ? p : s); }
  var FORMATS = { visio: ['Visio', 'en visio'], presentiel: ['Présentiel', 'en présentiel'], mixte: ['Visio et présentiel', 'en visio et en présentiel, selon les groupes'] };

  var cN = q('#plan-n'), cD = q('#plan-deb'), cH = q('#plan-h');
  var boutons = [].slice.call(racine.querySelectorAll('.plan-format button'));

  function calcul() {
    var d = Math.round(etat.n * etat.deb / 100), a = etat.n - d;
    return { n: etat.n, d: d, a: a, gd: Math.ceil(d / MAX_GROUPE), ga: Math.ceil(a / MAX_GROUPE) };
  }
  function ecrire(sel, t) { var e = q(sel); if (e) e.textContent = t; }
  function detailGroupes(c) {
    var m = [];
    if (c.gd) m.push(pl(c.gd, 'groupe débutant', 'groupes débutants'));
    if (c.ga) m.push(pl(c.ga, 'groupe avancé', 'groupes avancés'));
    return m.join(' et ');
  }
  function resume(c) {
    return 'Plan de déploiement IA pour ' + fr(c.n) + ' mandataires\n'
      + '- Diagnostic Academia Parcours pour chaque mandataire\n'
      + '- ' + detailGroupes(c) + ' (' + MAX_GROUPE + ' mandataires au plus par session)\n'
      + '- ' + etat.h + ' h par mandataire, ' + FORMATS[etat.format][1] + '\n'
      + '- Outils maison remis à chacun, charte d’usage de l’IA commune au réseau\n'
      + 'Start Academia, organisme certifié Qualiopi. Devis établi après l’appel découverte.';
  }
  function afficher() {
    var c = calcul(), g = c.gd + c.ga, plus = etat.n >= 1000;
    ecrire('.plan-val-n', fr(c.n) + ' mandataires' + (plus ? ' et plus' : ''));
    ecrire('.plan-val-deb', pl(c.d, 'débutant', 'débutants') + ' · ' + pl(c.a, 'déjà utilisateur', 'déjà utilisateurs'));
    ecrire('.plan-val-h', etat.h + ' h par mandataire');
    ecrire('#pt-groupes', String(g));
    ecrire('#pt-groupes-l', g > 1 ? 'groupes de niveau' : 'groupe de niveau');
    ecrire('#pt-h', etat.h + ' h');
    ecrire('#pt-format', FORMATS[etat.format][0]);
    ecrire('#pe-1', 'Les ' + fr(c.n) + ' mandataires font leur diagnostic avec Academia Parcours : vous savez qui débute et qui est avancé.');
    ecrire('#pe-2', detailGroupes(c).replace(/^./, function (x) { return x.toUpperCase(); }) + ', ' + MAX_GROUPE + ' mandataires au plus par session.');
    ecrire('#pe-3', etat.h + ' h par mandataire, ' + FORMATS[etat.format][1] + '. Les heures comptent pour la loi ALUR.');
    cibler(c);
    return c;
  }

  cN.addEventListener('input', function () { etat.n = +cN.value; afficher(); });
  cD.addEventListener('input', function () { etat.deb = +cD.value; afficher(); });
  cH.addEventListener('input', function () { etat.h = +cH.value; afficher(); });
  boutons.forEach(function (b) {
    b.addEventListener('click', function () {
      etat.format = b.getAttribute('data-format');
      boutons.forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
      afficher();
    });
  });
  var copier = q('.plan-copier');
  if (copier && navigator.clipboard) {
    copier.hidden = false;
    copier.addEventListener('click', function () {
      navigator.clipboard.writeText(resume(calcul())).then(function () {
        copier.textContent = 'Plan copié'; setTimeout(function () { copier.textContent = 'Copier mon plan'; }, 2200);
      });
    });
  }
  var appel = q('.plan-appel');
  if (appel) appel.addEventListener('click', function () {
    if (window.va) window.va('event', { name: 'plan_reseau', data: { mandataires: etat.n >= 500 ? '500+' : etat.n >= 100 ? '100-499' : '<100', format: etat.format } });
  });

  /* ---------- Le réseau en relief (canvas) ---------- */
  var toile = q('.plan-toile'), ctx = toile && toile.getContext && toile.getContext('2d');
  var P = [], G = [], angle = -.5, visee = 0, incl = 0, zoom = 1, zoomCible = 1, L = 0, H = 0, visible = true, dessinDemande = false;
  var ANNEAUX = [[1.7, 6], [3.05, 10], [4.4, 16]];
  function cibler(c) {
    if (!ctx) return;
    var total = c.gd + c.ga, echelle = Math.max(1, Math.ceil(c.n / MAX_POINTS));
    ecrire('.plan-echelle', echelle > 1 ? '1 point = ' + echelle + ' mandataires' : '1 point = 1 mandataire');
    G = []; var cibles = [], i = 0, reste, g, a;
    for (g = 0; g < total; g++) {
      var anneau = 0, rang = g;
      while (anneau < ANNEAUX.length - 1 && rang >= ANNEAUX[anneau][1]) { rang -= ANNEAUX[anneau][1]; anneau++; }
      var dansAnneau = Math.min(ANNEAUX[anneau][1], total - (g - rang));
      a = (rang / dansAnneau) * Math.PI * 2 + anneau * .5;
      var type = g < c.gd ? 0 : 1;
      var gens = type === 0 ? Math.min(MAX_GROUPE, c.d - g * MAX_GROUPE) : Math.min(MAX_GROUPE, c.a - (g - c.gd) * MAX_GROUPE);
      G.push({ x: Math.cos(a) * ANNEAUX[anneau][0], y: Math.sin(a) * ANNEAUX[anneau][0], type: type, anneau: anneau });
      var m = Math.max(1, Math.round(gens / echelle));
      for (var j = 0; j < m; j++) {
        var r = .56 * Math.sqrt((j + .5) / m), t = j * 2.399963;
        cibles.push([G[g].x + Math.cos(t) * r, G[g].y + Math.sin(t) * r, type]);
      }
    }
    for (i = 0; i < cibles.length; i++) {
      if (!P[i]) P[i] = { x: 0, y: 0, tx: 0, ty: 0, type: 0 };
      P[i].tx = cibles[i][0]; P[i].ty = cibles[i][1]; P[i].type = cibles[i][2];
      if (calme) { P[i].x = P[i].tx; P[i].y = P[i].ty; }
    }
    P.length = cibles.length;
    var dernier = G.length ? G[G.length - 1].anneau : 0;
    zoomCible = [2.05, 1.5, 1.12][dernier];
    if (calme) zoom = zoomCible;
    demander();
  }
  function taille() {
    var r = toile.getBoundingClientRect(), d = Math.min(window.devicePixelRatio || 1, 2);
    L = r.width; H = r.height; toile.width = Math.round(L * d); toile.height = Math.round(H * d);
    ctx.setTransform(d, 0, 0, d, 0, 0); demander();
  }
  function proj(x, y) {
    var c = Math.cos(angle), s = Math.sin(angle), x1 = x * c - y * s, y1 = x * s + y * c;
    var p = 1 / (1 - y1 * .055), S = Math.min(L, H * 1.5) / 10.4 * zoom;
    return [L / 2 + x1 * S * p, H * .54 + y1 * (.5 + incl) * S * p, p, y1];
  }
  function dessiner() {
    dessinDemande = false;
    if (!ctx || !L) return;
    var bouge = false, i, a, b;
    if (!calme) {
      angle += .0016; // rotation lente
      angle += visee * .02; visee *= .9;
      if (Math.abs(zoom - zoomCible) > .002) { zoom += (zoomCible - zoom) * .07; }
      for (i = 0; i < P.length; i++) { P[i].x += (P[i].tx - P[i].x) * .09; P[i].y += (P[i].ty - P[i].y) * .09; }
      bouge = true;
    }
    ctx.clearRect(0, 0, L, H);
    // cercles concentriques au sol
    ctx.lineWidth = 1;
    [1.7, 3.05, 4.4, 5.6].forEach(function (r, k) {
      ctx.beginPath();
      for (var t = 0; t <= 64; t++) { var q2 = proj(Math.cos(t / 64 * 6.2832) * r, Math.sin(t / 64 * 6.2832) * r); t ? ctx.lineTo(q2[0], q2[1]) : ctx.moveTo(q2[0], q2[1]); }
      ctx.strokeStyle = 'rgba(185,205,255,' + (.2 - k * .035) + ')'; ctx.stroke();
    });
    var centre = proj(0, 0);
    // liens du centre vers chaque groupe
    G.forEach(function (g) {
      a = proj(g.x, g.y); ctx.beginPath(); ctx.moveTo(centre[0], centre[1]); ctx.lineTo(a[0], a[1]);
      ctx.strokeStyle = 'rgba(185,205,255,.3)'; ctx.stroke();
    });
    // points (mandataires), du fond vers l'avant
    var ordre = P.map(function (p) { b = proj(p.x, p.y); return [b[3], b[0], b[1], b[2], p.type]; }).sort(function (u, v) { return u[0] - v[0]; });
    for (i = 0; i < ordre.length; i++) {
      b = ordre[i]; ctx.beginPath(); ctx.arc(b[1], b[2], Math.max(1.2, 2.6 * b[3] * Math.sqrt(zoom)), 0, 6.2832);
      ctx.fillStyle = b[4] ? 'rgba(255,255,255,' + Math.min(1, .55 + b[3] * .4) + ')' : 'rgba(140,168,255,' + Math.min(1, .6 + b[3] * .4) + ')';
      ctx.fill();
    }
    // nœuds orange : une session par groupe
    G.forEach(function (g) {
      a = proj(g.x, g.y); var r = 4.5 * a[2] * Math.sqrt(zoom);
      ctx.beginPath(); ctx.arc(a[0], a[1], r * 2.6, 0, 6.2832); ctx.fillStyle = 'rgba(254,85,0,.2)'; ctx.fill();
      ctx.beginPath(); ctx.arc(a[0], a[1], r, 0, 6.2832); ctx.fillStyle = '#fe5500'; ctx.fill();
    });
    // centre : Start Academia
    ctx.beginPath(); ctx.arc(centre[0], centre[1], 13 * Math.sqrt(zoom), 0, 6.2832); ctx.fillStyle = 'rgba(255,255,255,.14)'; ctx.fill();
    ctx.beginPath(); ctx.arc(centre[0], centre[1], 6.5 * Math.sqrt(zoom), 0, 6.2832); ctx.fillStyle = '#fff'; ctx.fill();
    if (bouge && visible) demander();
  }
  function demander() { if (!dessinDemande) { dessinDemande = true; requestAnimationFrame(dessiner); } }
  if (ctx) {
    if ('ResizeObserver' in window) new ResizeObserver(taille).observe(toile); else window.addEventListener('resize', taille);
    if ('IntersectionObserver' in window) new IntersectionObserver(function (e) { visible = e[0].isIntersecting; if (visible) demander(); }).observe(toile);
    if (!calme) {
      var dernierX = null;
      toile.addEventListener('pointermove', function (e) {
        var r = toile.getBoundingClientRect();
        if (dernierX !== null) visee += (e.clientX - dernierX) / r.width * 1.6;
        dernierX = e.clientX; incl = ((e.clientY - r.top) / r.height - .5) * .16;
      });
      toile.addEventListener('pointerleave', function () { dernierX = null; });
    }
    taille();
  }
  racine.classList.add('actif');
  afficher();
})();
