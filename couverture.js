/* Simulateur de financement : ce que le budget estimé couvre pour une durée de formation.
   Ne touche pas aux règles de calcul : lit le budget affiché par simulateur.js. */
(function () {
  var racine = document.getElementById('simulateur'); if (!racine) return;
  var TAUX = 42, MIN = 4, MAX = 72;
  var voulu = parseInt((location.search.match(/[?&]heures=(\d+)/) || [])[1], 10);
  if (voulu > MAX) MAX = Math.min(voulu, 200);
  var heures = voulu >= MIN ? Math.min(voulu, MAX) : 16, envoye = false, blocs = [];
  function euros(n) { return Math.round(n).toLocaleString('fr-FR') + ' €'; }
  function montants(txt) {
    return (txt || '').split(' à ').map(function (m) { var s = m.replace(/[^0-9,]/g, '').replace(',', '.'); return s ? parseFloat(s) : NaN; }).filter(function (n) { return !isNaN(n); });
  }
  function el(tag, cls, txt) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt) e.textContent = txt; return e; }
  function maj() {
    var cout = heures * TAUX;
    blocs.forEach(function (b) {
      b.curseur.value = heures;
      b.duree.textContent = heures + ' h';
      var m = montants(b.source.textContent);
      if (!m.length) {
        b.scene.hidden = true;
        b.texte.textContent = 'Complétez l’estimation pour voir ce que votre budget couvre sur ' + heures + ' heures (à partir de ' + euros(cout) + ').';
        return;
      }
      var budget = m[0], bas = m.length > 1, couvert = Math.min(budget, cout), reste = cout - couvert;
      b.scene.hidden = false;
      b.barre.style.setProperty('--part', Math.max(reste > 0 ? 4 : 100, couvert / cout * 100) + '%');
      b.barre.classList.toggle('plein', reste <= 0);
      b.chiffre.innerHTML = reste <= 0 ? '<strong>Couvert</strong> ' + heures + ' h à partir de ' + euros(cout) : '<strong>' + Math.floor(budget / TAUX) + ' h<span> / ' + heures + ' h</span></strong> couvertes par votre budget estimé';
      b.texte.textContent = (bas ? 'Dans l’hypothèse basse, votre ' : 'Votre ') + 'budget estimé de ' + euros(budget) + (reste <= 0
        ? ' couvre ces ' + heures + ' heures' + (budget - cout >= TAUX * MIN ? ', et il resterait environ ' + euros(budget - cout) + ' pour une autre formation.' : '.')
        : ' couvre environ ' + Math.floor(budget / TAUX) + ' heures sur ' + heures + '. Resterait environ ' + euros(reste) + ' à votre charge.');
    });
  }
  ['age', 'opco'].forEach(function (k) {
    var source = document.getElementById(k + '-reste'), panneau = document.querySelector('#' + k + '-panneau .simu-resultat');
    if (!source || !panneau) return;
    var b = { source: source }, bloc = el('div', 'couverture'), id = 'couv-' + k;
    var l = el('label', 'couv-label', 'Durée de formation visée '); l.htmlFor = id; b.duree = el('strong', '', ''); l.appendChild(b.duree);
    b.curseur = el('input'); b.curseur.type = 'range'; b.curseur.id = id; b.curseur.min = MIN; b.curseur.max = MAX; b.curseur.step = 1;
    b.curseur.addEventListener('input', function () {
      heures = parseInt(b.curseur.value, 10); maj();
      if (!envoye) { envoye = true; if (window.va) window.va('event', { name: 'couverture_financement', data: { page: location.pathname } }); }
    });
    b.scene = el('div', 'couv-scene'); b.barre = el('div', 'offre-barre'); b.barre.setAttribute('aria-hidden', 'true');
    b.barre.appendChild(el('i', 'offre-pleine')); b.barre.appendChild(el('i', 'offre-vide'));
    b.chiffre = el('p', 'couv-chiffre'); b.scene.appendChild(b.barre); b.scene.appendChild(b.chiffre);
    b.texte = el('p', 'couv-texte'); b.texte.setAttribute('aria-live', 'polite');
    var note = el('p', 'couv-note', 'Tarif à partir de ' + TAUX + ' € de l’heure, devis après l’appel découverte. L’accord et le montant dépendent de votre financeur.');
    [l, b.curseur, b.scene, b.texte, note].forEach(function (x) { bloc.appendChild(x); });
    var suite = panneau.querySelector('.simu-suite');
    if (suite) panneau.insertBefore(bloc, suite); else panneau.appendChild(bloc);
    blocs.push(b);
    if (window.MutationObserver) new MutationObserver(maj).observe(source, { childList: true, characterData: true, subtree: true });
  });
  maj();
})();
