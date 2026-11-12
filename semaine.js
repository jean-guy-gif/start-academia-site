/* Page « Formation IA immobilier » : le conseiller coche ses tâches et indique le temps qu'il y passe
   aujourd'hui ; la page empile sa semaine actuelle et la même semaine avec la méthode.
   Les temps « avec la méthode » viennent des livrets tactiques (temps en routine). Le temps « aujourd'hui »
   est celui du visiteur : le site n'affirme aucun temps « avant ». */
(function () {
  var racine = document.querySelector('.semaine');
  if (!racine) return;
  var calme = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var ETAPES = { prospection: ['Prospection', '/ia-prospection-immobiliere/'], vendeur: ['Vendeur', '/ia-estimation-immobiliere/'], mandat: ['Mandat', '/ia-mandat-exclusif/'], acquereurs: ['Acquéreurs', '/ia-decouverte-acquereur/'], visites: ['Visites', '/ia-visite-immobiliere/'] };
  function q(s) { return racine.querySelector(s); }
  function el(tag, cls, txt) { var n = document.createElement(tag); if (cls) n.className = cls; if (txt != null) n.textContent = txt; return n; }
  function duree(m) {
    m = Math.round(m); if (m < 60) return m + ' min';
    var h = Math.floor(m / 60), r = m % 60; return h + ' h' + (r ? ' ' + (r < 10 ? '0' : '') + r : '');
  }
  var taches = [].slice.call(racine.querySelectorAll('.tache')).map(function (li) {
    var c = li.querySelector('input');
    return { li: li, c: c, ia: +c.getAttribute('data-ia'), etape: c.getAttribute('data-etape'), unite: c.getAttribute('data-unite'), nom: li.querySelector('.tache-nom').textContent, fois: 1, auj: 0 };
  });

  function reglages(t) {
    var b = el('div', 'tache-reglages');
    var f = el('div', 'tache-fois'); f.appendChild(el('span', 'tr-label', 'Fois par semaine'));
    var moins = el('button', null, '−'), val = el('output', null, '1'), plus = el('button', null, '+');
    moins.type = plus.type = 'button'; moins.setAttribute('aria-label', 'Une fois de moins'); plus.setAttribute('aria-label', 'Une fois de plus');
    function fois(d) { t.fois = Math.max(1, Math.min(30, t.fois + d)); val.textContent = t.fois; calcul(); }
    moins.addEventListener('click', function () { fois(-1); }); plus.addEventListener('click', function () { fois(1); });
    f.appendChild(moins); f.appendChild(val); f.appendChild(plus);
    var a = el('div', 'tache-auj'); a.setAttribute('role', 'group');
    a.appendChild(el('span', 'tr-label', 'Aujourd’hui, ça vous prend à chaque fois'));
    var choix = el('div', 'tache-temps');
    [5, 10, 15, 30, 45, 60, 90, 120, 180].forEach(function (m) {
      var bt = el('button', null, duree(m)); bt.type = 'button'; bt.setAttribute('aria-pressed', 'false');
      bt.addEventListener('click', function () {
        t.auj = m; [].forEach.call(choix.children, function (x) { x.setAttribute('aria-pressed', String(x === bt)); });
        t.li.classList.remove('a-regler'); calcul();
      });
      choix.appendChild(bt);
    });
    a.appendChild(choix);
    b.appendChild(f); b.appendChild(a);
    return b;
  }
  taches.forEach(function (t) {
    t.c.addEventListener('change', function () {
      t.li.classList.toggle('cochee', t.c.checked); t.li.classList.toggle('a-regler', t.c.checked && !t.auj);
      if (t.c.checked && !t.reglages) { t.reglages = reglages(t); t.li.appendChild(t.reglages); }
      if (t.reglages) t.reglages.hidden = !t.c.checked;
      calcul();
    });
  });

  var totaux = { auj: 0, ia: 0 };
  function calcul() {
    var actives = taches.filter(function (t) { return t.c.checked; });
    var auj = 0, ia = 0, sansTemps = 0;
    actives.forEach(function (t) { if (!t.auj) { sansTemps++; return; } auj += t.fois * t.auj; ia += t.fois * t.ia; });
    var reglees = actives.length - sansTemps;
    totaux = { auj: auj, ia: ia };
    q('#sm-auj').textContent = duree(auj); q('#sm-ia').textContent = duree(ia);
    var gain = auj - ia, phrase = q('#sm-phrase');
    q('#sm-gain').textContent = reglees && gain > 0 ? duree(gain) : '–';
    var reste = sansTemps ? ' Il reste ' + (sansTemps > 1 ? sansTemps + ' tâches à régler' : 'une tâche à régler') + ' pour compléter votre semaine.' : '';
    if (!actives.length) phrase.textContent = 'Cochez une première tâche pour commencer.';
    else if (!reglees) phrase.textContent = 'Touchez le temps que chaque tâche cochée vous prend aujourd’hui : vos deux piles se construisent aussitôt.';
    else if (gain > 0) phrase.textContent = 'Avec la méthode, ces tâches vous prennent ' + duree(ia) + ' par semaine au lieu de ' + duree(auj) + '. Vous récupérez ' + duree(gain) + ' pour vos vendeurs et vos acquéreurs.' + reste;
    else phrase.textContent = 'Sur ces tâches, vous êtes déjà rapide. Le gain se trouve sans doute ailleurs dans votre semaine : parlons-en pendant l’appel.' + reste;
    var prog = q('#sm-programme'); prog.textContent = '';
    Object.keys(ETAPES).forEach(function (k) {
      var liste = actives.filter(function (t) { return t.etape === k; });
      if (!liste.length) return;
      var li = el('li'), a = el('a', null, ETAPES[k][0]); a.href = ETAPES[k][1]; a.setAttribute('data-suivi', 'semaine-' + k);
      li.appendChild(a); li.appendChild(el('span', null, liste.map(function (t) { return t.nom.charAt(0).toLowerCase() + t.nom.slice(1); }).join(', ') + '.'));
      prog.appendChild(li);
    });
    prog.hidden = !actives.length;
    demander();
    return actives;
  }
  function resume() {
    var actives = taches.filter(function (t) { return t.c.checked; });
    return 'Ma semaine, tâche par tâche\n' + actives.map(function (t) {
      return '- ' + t.nom + ' : ' + t.fois + ' fois par semaine, ' + (t.auj ? duree(t.auj) : '?') + ' aujourd’hui, ' + duree(t.ia) + ' avec la méthode';
    }).join('\n') + '\nTotal : ' + duree(totaux.auj) + ' aujourd’hui, ' + duree(totaux.ia) + ' avec la méthode.\nStart Academia, formation IA immobilier.';
  }
  var copier = q('.plan-copier');
  if (copier && navigator.clipboard) {
    copier.hidden = false;
    copier.addEventListener('click', function () {
      navigator.clipboard.writeText(resume().replace(/ /g, ' ')).then(function () { copier.textContent = 'Semaine copiée'; setTimeout(function () { copier.textContent = 'Copier ma semaine'; }, 2200); });
    });
  }
  var appel = q('.semaine-appel');
  if (appel) appel.addEventListener('click', function () {
    var n = taches.filter(function (t) { return t.c.checked; }).length, g = totaux.auj - totaux.ia;
    if (window.va) window.va('event', { name: 'ma_semaine', data: { taches: n, gain: g >= 300 ? '5h+' : g >= 120 ? '2-5h' : g > 0 ? '<2h' : 'aucun' } });
  });

  /* ---------- Les deux piles (canvas, vue isométrique) : un étage = une heure, quatre cubes d'un quart d'heure ---------- */
  var toile = q('.semaine-toile'), ctx = toile && toile.getContext && toile.getContext('2d');
  var L = 0, H = 0, vus = { auj: 0, ia: 0 }, demande = false;
  function taille() {
    var r = toile.getBoundingClientRect(), d = Math.min(window.devicePixelRatio || 1, 2);
    L = r.width; H = r.height; toile.width = Math.round(L * d); toile.height = Math.round(H * d); ctx.setTransform(d, 0, 0, d, 0, 0); demander();
  }
  function cube(x, y, s, haut, gauche, droite) {
    var w = s * .866, h = s * .5;
    ctx.strokeStyle = 'rgba(11,16,51,.28)'; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(x, y - s); ctx.lineTo(x + w, y - s + h); ctx.lineTo(x, y - s + 2 * h); ctx.lineTo(x - w, y - s + h); ctx.closePath(); ctx.fillStyle = haut; ctx.fill(); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(x - w, y - s + h); ctx.lineTo(x, y - s + 2 * h); ctx.lineTo(x, y + 2 * h - 0); ctx.lineTo(x - w, y + h); ctx.closePath(); ctx.fillStyle = gauche; ctx.fill(); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(x + w, y - s + h); ctx.lineTo(x, y - s + 2 * h); ctx.lineTo(x, y + 2 * h); ctx.lineTo(x + w, y + h); ctx.closePath(); ctx.fillStyle = droite; ctx.fill(); ctx.stroke();
  }
  function pile(cx, base, s, quarts, c) {
    var w = s * .866, h = s * .5, n, k, i, j, ordre = [[0, 0], [1, 0], [0, 1], [1, 1]];
    // socle
    ctx.beginPath(); ctx.moveTo(cx, base - 2 * h - 6); ctx.lineTo(cx + 2 * w + 10, base); ctx.lineTo(cx, base + 2 * h + 6); ctx.lineTo(cx - 2 * w - 10, base); ctx.closePath();
    ctx.strokeStyle = 'rgba(185,205,255,.3)'; ctx.lineWidth = 1; ctx.stroke();
    for (n = 0; n < quarts; n++) {
      k = Math.floor(n / 4); i = ordre[n % 4][0]; j = ordre[n % 4][1];
      cube(cx + (i - j) * w, base - h * 2 + (i + j) * h - k * s + h, s, c[0], c[1], c[2]);
    }
  }
  function dessiner() {
    demande = false;
    if (!ctx || !L) return;
    var cA = Math.round(totaux.auj / 15), cI = totaux.ia ? Math.max(1, Math.round(totaux.ia / 15)) : 0, bouge = false;
    ['auj', 'ia'].forEach(function (k) {
      var cible = k === 'auj' ? cA : cI;
      if (calme) vus[k] = cible;
      else if (vus[k] !== cible) { vus[k] += vus[k] < cible ? Math.max(1, Math.ceil((cible - vus[k]) / 8)) : -Math.max(1, Math.ceil((vus[k] - cible) / 8)); bouge = true; }
    });
    var etages = Math.max(4, Math.ceil(Math.max(vus.auj, vus.ia, cA) / 4));
    var s = Math.max(6, Math.min(L / 13, (H * .78) / (etages + 2)));
    var base = H - s * 1.5;
    ctx.clearRect(0, 0, L, H);
    pile(L * .3, base, s, vus.auj, ['#ff8a4d', '#fe5500', '#c94400']);
    pile(L * .7, base, s, vus.ia, ['#b9cdff', '#6988ee', '#2f44ce']);
    if (bouge) demander();
  }
  function demander() { if (ctx && !demande) { demande = true; requestAnimationFrame(dessiner); } }
  if (ctx) { if ('ResizeObserver' in window) new ResizeObserver(taille).observe(toile); else window.addEventListener('resize', taille); taille(); }
  racine.classList.add('actif');
  calcul();
})();
