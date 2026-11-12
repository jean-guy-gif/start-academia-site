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
  var ul = bloc.querySelector('.freins'), d = function (a, defaut) { return ul.getAttribute('data-' + a) || defaut; };
  var NOM = d('zone', '[FREINS DU VENDEUR]'), UN = d('un', 'preuve posée'), PLUS = d('plusieurs', 'preuves posées'), SUITE = d('suite', 'sur la table'), EVT = d('evenement', 'freins_mandat');
  [].forEach.call(document.querySelectorAll('.b-prompt pre.prompt-bloc mark'), function (m) {
    if (m.textContent === NOM) zone = m;
  });

  function maj() {
    var n = 0, noms = [];
    cartes.forEach(function (c, i) {
      var r = c.classList.contains('retournee');
      if (r) { n++; noms.push(c.getAttribute('data-frein')); }
      if (temps[i]) temps[i].classList.toggle('pose', r);
    });
    if (compte) compte.innerHTML = '<strong>' + n + '<span> / ' + cartes.length + '</span></strong> ' + (n > 1 ? PLUS : UN) + ' ' + SUITE;
    if (fin) fin.hidden = n < cartes.length;
    if (zone) { zone.textContent = noms.length ? noms.join(', ') : NOM; zone.classList.toggle('rempli', noms.length > 0); }
    if (n === cartes.length && !envoye) {
      envoye = true;
      if (window.va) window.va('event', { name: EVT, data: { page: location.pathname } });
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
    b.setAttribute('aria-label', 'Retourner ' + (dit ? dit.textContent : 'la carte ' + (i + 1)));
    verso.setAttribute('aria-hidden', 'true');
    b.addEventListener('click', function () {
      var r = c.classList.toggle('retournee');
      b.setAttribute('aria-expanded', r ? 'true' : 'false');
      b.firstChild.textContent = r ? 'Revoir la phrase' : 'Retourner';
      verso.setAttribute('aria-hidden', r ? 'false' : 'true');
      recto.setAttribute('aria-hidden', r ? 'true' : 'false');
      maj();
    });
    c.appendChild(b);
  });
  bloc.classList.add('freins-actifs');
  maj();
})();
