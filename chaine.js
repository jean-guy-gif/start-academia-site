/* Accueil, chaîne des 8 étapes : chaque visuel se coupe en deux, « Avant » en gris à gauche,
   « Avec l'IA » en couleur à droite. Le visiteur fait glisser la poignée ; le texte suit.
   Sans script, le visuel et le tableau Avant / Avec l'IA restent tels quels. */
(function () {
  var maillons = [].slice.call(document.querySelectorAll('.chaine .maillon'));
  if (!maillons.length) return;
  var calme = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var bureau = window.matchMedia('(min-width: 772px)');
  var montre = false;
  maillons.forEach(function (m) {
    var visuel = m.querySelector('.visuel'); if (!visuel) return;
    var avant = document.createElement('div'); avant.className = 'coupe-avant'; avant.setAttribute('aria-hidden', 'true');
    [].forEach.call(visuel.children, function (c) { avant.appendChild(c.cloneNode(true)); });
    visuel.appendChild(avant);
    var e1 = document.createElement('span'); e1.className = 'coupe-nom coupe-nom-avant'; e1.textContent = 'Avant';
    var e2 = document.createElement('span'); e2.className = 'coupe-nom coupe-nom-ia'; e2.textContent = 'Avec l’IA';
    var poignee = document.createElement('button'); poignee.type = 'button'; poignee.className = 'coupe-poignee';
    poignee.setAttribute('role', 'slider'); poignee.setAttribute('aria-label', 'Comparer avant et avec l’IA'); poignee.setAttribute('aria-valuemin', '0'); poignee.setAttribute('aria-valuemax', '100');
    poignee.innerHTML = '<span aria-hidden="true"></span>';
    visuel.appendChild(e1); visuel.appendChild(e2); visuel.appendChild(poignee);
    m.classList.add('coupe');
    function bornes() { return bureau.matches ? [50, 74] : [6, 94]; }
    function poser(v) {
      var b = bornes(); v = Math.max(b[0], Math.min(b[1], v));
      m.style.setProperty('--coupe', v + '%');
      var part = (v - b[0]) / (b[1] - b[0]); // 0 = tout « avec l'IA », 1 = tout « avant »
      m.setAttribute('data-cote', part > .72 ? 'avant' : part < .28 ? 'ia' : 'deux');
      poignee.setAttribute('aria-valuenow', String(Math.round((1 - part) * 100)));
      poignee.setAttribute('aria-valuetext', part > .72 ? 'Avant' : part < .28 ? 'Avec l’IA' : 'Avant et avec l’IA');
      m._coupe = v;
    }
    function depuis(e) { var r = visuel.getBoundingClientRect(); poser((e.clientX - r.left) / r.width * 100); }
    var tire = false;
    poignee.addEventListener('pointerdown', function (e) { tire = true; poignee.setPointerCapture(e.pointerId); m.classList.add('tire'); e.preventDefault(); });
    poignee.addEventListener('pointermove', function (e) { if (tire) depuis(e); });
    function fin() { if (tire) { tire = false; m.classList.remove('tire'); if (window.va) window.va('event', { name: 'clic', data: { cible: 'coupe-' + m.id, page: location.pathname } }); } }
    poignee.addEventListener('pointerup', fin); poignee.addEventListener('pointercancel', fin);
    poignee.addEventListener('keydown', function (e) {
      var pas = e.key === 'ArrowLeft' ? -6 : e.key === 'ArrowRight' ? 6 : 0;
      if (pas) { e.preventDefault(); poser(m._coupe + pas); }
    });
    m._poser = poser; m._bornes = bornes;
    poser(bureau.matches ? 62 : 50);
    bureau.addEventListener('change', function () { poser(bureau.matches ? 62 : 50); });
  });
  // Première étape vue : la poignée fait un aller-retour pour montrer qu'elle se tire
  function saluer(m) {
    if (montre || calme || !m._poser) return; montre = true;
    var b = m._bornes(), depart = m._coupe, t0 = null, duree = 1900;
    m.classList.add('tire');
    function pas(t) {
      if (t0 === null) t0 = t; var q = Math.min(1, (t - t0) / duree);
      var onde = Math.sin(q * Math.PI * 2) * (1 - q * .25);
      m._poser(depart + onde * (b[1] - b[0]) * .45);
      if (q < 1) requestAnimationFrame(pas); else { m._poser(depart); m.classList.remove('tire'); }
    }
    requestAnimationFrame(pas);
  }
  if ('IntersectionObserver' in window) {
    var obs = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { setTimeout(function () { saluer(maillons[0]); }, 700); obs.disconnect(); } }); }, { threshold: .5 });
    obs.observe(maillons[0].querySelector('.visuel'));
  }
})();
