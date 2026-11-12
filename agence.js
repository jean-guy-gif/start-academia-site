/* Page directeurs : « Le rythme de votre agence ». Le directeur compose son équipe et choisit la
   fréquence de ses entretiens ; la page dessine l'agence en relief et écrit son mois de pilotage
   et son plan de formation par poste.
   Chiffres : 15 min de pilotage le lundi (livret managers 2025, à confirmer), réunion de 45 min
   au plus (livret Module 2 Animer, oct. 2026), 5 min pour préparer un entretien individuel
   (Jean-Guy, 12/11/2026). Aucun gain de temps calculé. */
(function () {
  var racine = document.querySelector('.agence');
  if (!racine) return;
  var calme = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var etat = { conseillers: 6, assistantes: 1, managers: 1, freq: 1 };
  var FREQ = { 4: 'chaque semaine', 2: 'tous les quinze jours', 1: 'chaque mois' };
  function q(s) { return racine.querySelector(s); }
  function el(tag, cls, txt) { var n = document.createElement(tag); if (cls) n.className = cls; if (txt != null) n.textContent = txt; return n; }
  function pl(n, s, p) { return n + ' ' + (n > 1 ? p : s); }
  function duree(m) { if (m < 60) return m + ' min'; var h = Math.floor(m / 60), r = m % 60; return h + ' h' + (r ? ' ' + (r < 10 ? '0' : '') + r : ''); }
  function ecrire(sel, t) { var e = q(sel); if (e) e.textContent = t; }

  [].forEach.call(racine.querySelectorAll('.agence-poste[data-poste]'), function (p) {
    var cle = p.getAttribute('data-poste'), max = +p.getAttribute('data-max'), val = p.querySelector('output');
    var b = p.querySelectorAll('button');
    function pas(d) { etat[cle] = Math.max(0, Math.min(max, etat[cle] + d)); val.textContent = etat[cle]; afficher(); }
    b[0].addEventListener('click', function () { pas(-1); }); b[1].addEventListener('click', function () { pas(1); });
  });
  var freqs = [].slice.call(racine.querySelectorAll('.agence-freq button'));
  freqs.forEach(function (b) {
    b.addEventListener('click', function () {
      etat.freq = +b.getAttribute('data-freq'); freqs.forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); }); afficher();
    });
  });

  function calcul() {
    var suivis = etat.conseillers + etat.assistantes + etat.managers;
    return { equipe: suivis + 1, suivis: suivis, entretiens: suivis * etat.freq, prepa: suivis * etat.freq * 5 };
  }
  function plan(c) {
    var l = [];
    l.push(['Vous' + (etat.managers ? ' et ' + (etat.managers > 1 ? 'vos ' + etat.managers + ' managers' : 'votre manager') : ''), 'Piloter l’activité avec Academia Pilotage, préparer les entretiens avec Academia Parcours, poser la charte d’usage de l’IA de l’agence.', '/formation-ia-directeur-agence-immobiliere/#titre-final']);
    if (etat.conseillers) l.push([pl(etat.conseillers, 'conseiller', 'conseillers'), 'La formation IA immobilier, en version débutant ou avancée, sur leurs propres dossiers : prospection, estimation, mandat, acquéreurs.', '/formation-ia-immobilier/']);
    if (etat.assistantes) l.push([pl(etat.assistantes, 'assistante', 'assistantes'), 'L’organisation et l’administratif avec l’IA : comptes rendus, synthèses de documents, tâches répétitives.', '/formations/']);
    return l;
  }
  function resume(c) {
    return 'Le rythme de mon agence (' + pl(c.equipe, 'personne', 'personnes') + ')\n'
      + '- Lundi : 15 min de pilotage\n- Réunion d’équipe : 45 min au plus\n'
      + '- Entretiens individuels ' + FREQ[etat.freq] + ' : ' + c.entretiens + ' par mois, préparés en ' + duree(c.prepa).replace(/ /g, ' ') + '\n'
      + plan(c).map(function (p) { return '- ' + p[0].replace(/ /g, ' ') + ' : ' + p[1]; }).join('\n') + '\nStart Academia, formation IA pour directeurs d’agence.';
  }
  function afficher() {
    var c = calcul();
    ecrire('#ag-equipe', String(c.equipe)); ecrire('#ag-equipe-l', c.equipe > 1 ? 'personnes dans l’agence' : 'personne dans l’agence');
    ecrire('#ag-entretiens', String(c.entretiens)); ecrire('#ag-entretiens-l', (c.entretiens > 1 ? 'entretiens' : 'entretien') + ' par mois');
    ecrire('#ag-prepa', c.entretiens ? duree(c.prepa) : '–');
    ecrire('#ag-e3', c.suivis ? 'Un entretien ' + FREQ[etat.freq] + ' avec chacun, soit ' + pl(c.entretiens, 'entretien', 'entretiens') + ' par mois. Cinq minutes de préparation chacun, à partir des indicateurs du conseiller : ' + duree(c.prepa) + ' par mois.' : 'Ajoutez un collaborateur pour voir le rythme de vos entretiens.');
    var ul = q('#ag-plan'); ul.textContent = '';
    plan(c).forEach(function (p) { var li = el('li'), a = el('a', null, p[0]); a.href = p[2]; li.appendChild(a); li.appendChild(el('span', null, p[1])); ul.appendChild(li); });
    demander();
    return c;
  }
  var copier = q('.plan-copier');
  if (copier && navigator.clipboard) {
    copier.hidden = false;
    copier.addEventListener('click', function () { navigator.clipboard.writeText(resume(calcul())).then(function () { copier.textContent = 'Plan copié'; setTimeout(function () { copier.textContent = 'Copier mon plan'; }, 2200); }); });
  }
  var appel = q('.agence-appel');
  if (appel) appel.addEventListener('click', function () {
    var n = calcul().equipe;
    if (window.va) window.va('event', { name: 'plan_agence', data: { equipe: n >= 20 ? '20+' : n >= 8 ? '8-19' : '<8', entretiens: FREQ[etat.freq] } });
  });

  /* ---------- L'agence en relief : un bloc par personne, la hauteur dit le poste ---------- */
  var toile = q('.agence-toile'), ctx = toile && toile.getContext && toile.getContext('2d');
  var L = 0, H = 0, demande = false, pousse = {};
  var TEINTES = { directeur: ['#ff8a4d', '#fe5500', '#c94400'], manager: ['#ffffff', '#dfe7ff', '#b9cdff'], conseiller: ['#b9cdff', '#6988ee', '#2f44ce'], assistante: ['#8ea2ff', '#4a5fd6', '#27379f'] };
  var HAUTEURS = { directeur: 3, manager: 2, conseiller: 1, assistante: 1 };
  function taille() { var r = toile.getBoundingClientRect(), d = Math.min(window.devicePixelRatio || 1, 2); L = r.width; H = r.height; toile.width = Math.round(L * d); toile.height = Math.round(H * d); ctx.setTransform(d, 0, 0, d, 0, 0); demander(); }
  function cube(x, y, s, c) {
    var w = s * .866, h = s * .5;
    ctx.strokeStyle = 'rgba(11,16,51,.3)'; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(x, y - s); ctx.lineTo(x + w, y - s + h); ctx.lineTo(x, y - s + 2 * h); ctx.lineTo(x - w, y - s + h); ctx.closePath(); ctx.fillStyle = c[0]; ctx.fill(); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(x - w, y - s + h); ctx.lineTo(x, y - s + 2 * h); ctx.lineTo(x, y + 2 * h); ctx.lineTo(x - w, y + h); ctx.closePath(); ctx.fillStyle = c[1]; ctx.fill(); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(x + w, y - s + h); ctx.lineTo(x, y - s + 2 * h); ctx.lineTo(x, y + 2 * h); ctx.lineTo(x + w, y + h); ctx.closePath(); ctx.fillStyle = c[2]; ctx.fill(); ctx.stroke();
  }
  function dessiner() {
    demande = false;
    if (!ctx || !L) return;
    var gens = ['directeur'], i, bouge = false;
    for (i = 0; i < etat.managers; i++) gens.push('manager');
    for (i = 0; i < etat.conseillers; i++) gens.push('conseiller');
    for (i = 0; i < etat.assistantes; i++) gens.push('assistante');
    var cote = Math.max(2, Math.ceil(Math.sqrt(gens.length)));
    var pas = 1.45, s = Math.min(L / (cote * pas * 1.9 + 1), H / (cote * pas * .98 + 4.5));
    var w = s * .866, h = s * .5, cx = L / 2, haut = H * .5 - (cote - 1) * pas * h + s;
    ctx.clearRect(0, 0, L, H);
    // sol : trame de points
    ctx.fillStyle = 'rgba(185,205,255,.35)';
    for (var a = -1; a <= cote; a++) for (var b = -1; b <= cote; b++) { ctx.beginPath(); ctx.arc(cx + (a - b) * pas * w, haut + (a + b) * pas * h + 2 * h, 1.3, 0, 6.2832); ctx.fill(); }
    var cases = gens.map(function (g, n) { return { g: g, i: n % cote, j: Math.floor(n / cote), n: n }; }).sort(function (u, v) { return (u.i + u.j) - (v.i + v.j) || u.i - v.i; });
    cases.forEach(function (c) {
      var cible = HAUTEURS[c.g], cle = c.n + c.g, v = pousse[cle];
      if (v == null) v = calme ? cible : 0;
      if (v < cible) { v = Math.min(cible, v + .12); bouge = true; }
      pousse[cle] = v;
      var x = cx + (c.i - c.j) * pas * w, y = haut + (c.i + c.j) * pas * h, k;
      for (k = 0; k < Math.ceil(v); k++) cube(x, y - k * s, s, TEINTES[c.g]);
    });
    Object.keys(pousse).forEach(function (k) { if (!cases.some(function (c) { return c.n + c.g === k; })) delete pousse[k]; });
    if (bouge) demander();
  }
  function demander() { if (ctx && !demande) { demande = true; requestAnimationFrame(dessiner); } }
  if (ctx) { if ('ResizeObserver' in window) new ResizeObserver(taille).observe(toile); else window.addEventListener('resize', taille); taille(); }
  racine.classList.add('actif');
  afficher();
})();
