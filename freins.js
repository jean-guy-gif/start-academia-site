/* Page mandat exclusif : les cinq freins du vendeur à retourner.
   Sans script, chaque frein et sa preuve se lisent l'un sous l'autre. */
(function () {
  var bloc = document.querySelector('.b-freins');
  if (!bloc) return;
  var cartes = [].slice.call(bloc.querySelectorAll('.frein'));
  var temps = bloc.querySelectorAll('.freins-frise li');
  var compte = bloc.querySelector('.freins-compte');
  var fin = bloc.querySelector('.freins-fin');
  var zone = null, envoye = false;
  [].forEach.call(document.querySelectorAll('.b-prompt pre.prompt-bloc mark'), function (m) {
    if (m.textContent === '[FREINS DU VENDEUR]') zone = m;
  });

  function maj() {
    var n = 0, noms = [];
    cartes.forEach(function (c, i) {
      var r = c.classList.contains('retournee');
      if (r) { n++; noms.push(c.getAttribute('data-frein')); }
      if (temps[i]) temps[i].classList.toggle('pose', r);
    });
    if (compte) compte.innerHTML = '<strong>' + n + '<span> / ' + cartes.length + '</span></strong> ' + (n > 1 ? 'preuves posées' : 'preuve posée') + ' sur la table';
    if (fin) fin.hidden = n < cartes.length;
    if (zone) { zone.textContent = noms.length ? noms.join(', ') : '[FREINS DU VENDEUR]'; zone.classList.toggle('rempli', noms.length > 0); }
    if (n === cartes.length && !envoye) {
      envoye = true;
      if (window.va) window.va('event', { name: 'freins_mandat', data: { page: location.pathname } });
    }
  }

  cartes.forEach(function (c, i) {
    var recto = c.querySelector('.frein-recto'), verso = c.querySelector('.frein-verso');
    var dit = c.querySelector('.frein-dit');
    var b = document.createElement('button');
    b.type = 'button'; b.className = 'frein-bouton';
    verso.id = verso.id || 'frein-preuve-' + (i + 1);
    b.setAttribute('aria-controls', verso.id);
    b.setAttribute('aria-expanded', 'false');
    b.innerHTML = '<span class="frein-geste">Retourner</span>';
    b.setAttribute('aria-label', 'Retourner le frein ' + (dit ? dit.textContent : i + 1));
    verso.setAttribute('aria-hidden', 'true');
    b.addEventListener('click', function () {
      var r = c.classList.toggle('retournee');
      b.setAttribute('aria-expanded', r ? 'true' : 'false');
      b.firstChild.textContent = r ? 'Revoir le frein' : 'Retourner';
      verso.setAttribute('aria-hidden', r ? 'false' : 'true');
      recto.setAttribute('aria-hidden', r ? 'true' : 'false');
      maj();
    });
    c.appendChild(b);
  });
  bloc.classList.add('freins-actifs');
  maj();
})();
