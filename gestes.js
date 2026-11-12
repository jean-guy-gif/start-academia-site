/* Pages par étape : prospection (signaux de la rue), estimation (pièces du dossier), annonce (mentions).
   Sans script, chaque bloc se lit comme une liste. */
(function () {
  function zone(nom) {
    var z = null;
    [].forEach.call(document.querySelectorAll('.b-prompt pre.prompt-bloc mark'), function (m) { if (m.textContent === nom) z = m; });
    return z;
  }
  function remplir(z, nom, texte) { if (z) { z.textContent = texte || nom; z.classList.toggle('rempli', !!texte); } }
  function mesure(nom, donnees) { if (window.va) window.va('event', { name: nom, data: donnees }); }

  /* ---- Prospection : un signal dans la rue ---- */
  (function () {
    var bloc = document.querySelector('.b-signaux'); if (!bloc) return;
    var rue = bloc.querySelector('.signaux-rue'), liste = bloc.querySelector('.signaux-liste');
    var items = [].slice.call(bloc.querySelectorAll('.signal'));
    var z = zone('[SIGNAL DU JOUR]'), compte = false;
    var onglets = document.createElement('div'); onglets.className = 'signaux-choix';
    var balises = [], boutons = [];
    function choisir(i) {
      items.forEach(function (li, k) { li.hidden = k !== i; });
      balises.forEach(function (b, k) { b.classList.toggle('ici', k === i); });
      boutons.forEach(function (b, k) { b.setAttribute('aria-pressed', k === i ? 'true' : 'false'); });
      remplir(z, '[SIGNAL DU JOUR]', items[i].getAttribute('data-signal'));
      if (!compte) { compte = true; mesure('signal_rue', { page: location.pathname }); }
    }
    items.forEach(function (li, i) {
      var titre = li.querySelector('h3').textContent;
      var p = document.createElement('i'); p.className = 'balise';
      p.style.left = li.getAttribute('data-x') + '%'; p.style.top = li.getAttribute('data-y') + '%';
      rue.appendChild(p); balises.push(p);
      var b = document.createElement('button'); b.type = 'button'; b.textContent = titre; b.setAttribute('aria-pressed', 'false');
      b.addEventListener('click', function () { choisir(i); });
      onglets.appendChild(b); boutons.push(b);
      li.hidden = true;
    });
    var attente = document.createElement('p'); attente.className = 'signaux-attente'; attente.textContent = 'Cinq signaux dans la rue. Lequel avez-vous sous la main ?';
    liste.parentNode.insertBefore(onglets, liste);
    liste.appendChild(attente);
    bloc.classList.add('geste-actif');
    var premier = choisir; choisir = function (i) { attente.hidden = true; premier(i); };
  })();

  /* ---- Estimation : les pièces du dossier ---- */
  (function () {
    var bloc = document.querySelector('.b-dossier'); if (!bloc) return;
    var cases = [].slice.call(bloc.querySelectorAll('.avisv-pieces input'));
    var scene = bloc.querySelector('.avisv-scene'), pile = bloc.querySelector('.avisv-pile');
    var compte = bloc.querySelector('.avisv-compte'), verdict = bloc.querySelector('.avisv-verdict'), manques = bloc.querySelector('.avisv-manques');
    var z = zone('[PIÈCES DU DOSSIER]'), envoye = false;
    var feuillets = cases.map(function (c) {
      var f = document.createElement('span'); f.className = 'feuillet'; f.textContent = c.parentNode.querySelector('span').firstChild.textContent.trim();
      pile.appendChild(f); return f;
    });
    function maj() {
      var n = 0, noms = [];
      manques.innerHTML = '';
      cases.forEach(function (c, i) {
        feuillets[i].classList.toggle('pose', c.checked);
        if (c.checked) { feuillets[i].style.setProperty('--rang', n); n++; noms.push(c.getAttribute('data-piece')); }
        else { var li = document.createElement('li'); li.innerHTML = '<strong></strong> '; li.firstChild.textContent = feuillets[i].textContent + '.'; li.appendChild(document.createTextNode(c.getAttribute('data-manque'))); manques.appendChild(li); }
      });
      compte.innerHTML = '<strong>' + n + '<span> / ' + cases.length + '</span></strong> ' + (n > 1 ? 'pièces' : 'pièce') + ' dans votre dossier';
      verdict.textContent = n <= 2 ? 'Un chiffre presque seul. Le vendeur le comparera au sien.' : n <= 5 ? 'Un avis argumenté, encore attaquable sur ce qui manque.' : n < cases.length ? 'Un dossier solide. Il reste de quoi le rendre inattaquable.' : 'Un avis de valeur qui se défend sans vous.';
      remplir(z, '[PIÈCES DU DOSSIER]', noms.join(', '));
      if (n >= 3 && !envoye) { envoye = true; mesure('dossier_estimation', { page: location.pathname }); }
    }
    cases.forEach(function (c) { c.addEventListener('change', maj); });
    scene.hidden = false; bloc.classList.add('geste-actif'); maj();
  })();

  /* ---- Annonce : les mentions de votre cas ---- */
  (function () {
    var bloc = document.querySelector('.b-mentions'); if (!bloc) return;
    var lignes = [].slice.call(bloc.querySelectorAll('.mentions-liste li'));
    var verdict = bloc.querySelector('.mentions-verdict');
    var z = zone('[MENTIONS OBLIGATOIRES DE TON ANNONCE]'), envoye = false, touche = false;
    function val(nom) { var r = bloc.querySelector('input[name="' + nom + '"]:checked'); return r ? r.value : ''; }
    function maj() {
      var actifs = { copro: val('m-copro') === 'oui', acquereur: val('m-hono') === 'acquereur', fg: val('m-dpe') === 'fg', agentco: val('m-statut') === 'agentco' };
      var total = 0, ok = 0, noms = [];
      lignes.forEach(function (li) {
        var si = li.getAttribute('data-si'), c = li.querySelector('input');
        var visible = !si || actifs[si];
        li.hidden = !visible;
        if (!visible) return;
        total++; if (c.checked) ok++;
        noms.push(c.getAttribute('data-mention'));
      });
      var reste = total - ok;
      verdict.innerHTML = '<strong>' + ok + '<span> / ' + total + '</span></strong> ' + (reste === 0 ? 'Les mentions de votre cas sont toutes là.' : reste === 1 ? 'Il manque 1 mention avant de publier.' : 'Il manque ' + reste + ' mentions avant de publier.');
      bloc.querySelector('.mentions-fiche').classList.toggle('complete', reste === 0);
      remplir(z, '[MENTIONS OBLIGATOIRES DE TON ANNONCE]', touche ? noms.join(', ') : '');
      if (reste === 0 && !envoye) { envoye = true; mesure('mentions_annonce', { page: location.pathname }); }
    }
    bloc.addEventListener('change', function () { touche = true; maj(); });
    bloc.classList.add('geste-actif'); maj();
  })();

  /* ---- Visite : le compte rendu au vendeur ---- */
  (function () {
    var bloc = document.querySelector('.b-visite'); if (!bloc) return;
    var msg = bloc.querySelector('.visite-message'), objet = bloc.querySelector('.visite-objet'), corps = bloc.querySelector('.visite-corps');
    var zp = zone('[POINTS QUI ONT PLU]'), zf = zone('[POINTS QUI FREINENT]'), zs = zone('[SECONDE VISITE / RÉFLEXION / OFFRE POSSIBLE / PAS DE SUITE]');
    var envoye = false;
    var T = {
      fr: { et: ' et ', objet: 'Objet : retour sur la visite de ce jour', bonjour: 'Bonjour, je sors de la visite de votre bien.', plu: 'Ce qui a plu : ', pasPlu: 'Les visiteurs ne se sont pas exprimés sur les points forts.', frein: 'Ce qui freine : ', pasFrein: 'Aucun frein exprimé pendant la visite.',
        suite: { seconde: 'La suite : ils souhaitent revenir pour une seconde visite. Je vous propose une date dès qu’elle est fixée.', reflexion: 'La suite : ils prennent le temps de la réflexion. Je les rappelle dans deux jours et je vous tiens informé.', offre: 'La suite : une offre est envisagée. Je vous appelle dès que je l’ai par écrit.', rien: 'La suite : ils ne donnent pas suite. Leur retour reste utile, je le garde pour notre prochain point.' } },
      en: { et: ' and ', objet: 'Subject: feedback on today’s viewing', bonjour: 'Hello, I have just finished the viewing of your property.', plu: 'What they liked: ', pasPlu: 'The visitors did not comment on the strong points.', frein: 'What holds them back: ', pasFrein: 'No concern was raised during the viewing.',
        suite: { seconde: 'Next step: they would like to come back for a second viewing. I will suggest a date as soon as it is set.', reflexion: 'Next step: they are taking time to think it over. I will call them back in two days and keep you informed.', offre: 'Next step: an offer is being considered. I will call you as soon as I have it in writing.', rien: 'Next step: they will not take it further. Their feedback is still useful and I will keep it for our next review.' } }
    };
    var NOMS = { seconde: 'seconde visite', reflexion: 'réflexion', offre: 'offre possible', rien: 'pas de suite' };
    function liste(nom, langue) { return [].map.call(bloc.querySelectorAll('input[name="' + nom + '"]:checked'), function (c) { return c.getAttribute('data-' + langue); }); }
    function phrase(a, et) { return a.length < 2 ? a.join('') : a.slice(0, -1).join(', ') + et + a[a.length - 1]; }
    function maj() {
      var l = (bloc.querySelector('input[name="v-langue"]:checked') || {}).value || 'fr', t = T[l];
      var plu = liste('v-plu', l), fr = liste('v-frein', l), s = (bloc.querySelector('input[name="v-suite"]:checked') || {}).value;
      var lignes = [t.bonjour, plu.length ? t.plu + phrase(plu, t.et) + '.' : t.pasPlu, fr.length ? t.frein + phrase(fr, t.et) + '.' : t.pasFrein];
      if (s) lignes.push(t.suite[s]);
      objet.textContent = t.objet; corps.innerHTML = '';
      corps.setAttribute('lang', l);
      lignes.forEach(function (x) { var p = document.createElement('p'); p.textContent = x; corps.appendChild(p); });
      remplir(zp, '[POINTS QUI ONT PLU]', phrase(liste('v-plu', 'fr'), ' et '));
      remplir(zf, '[POINTS QUI FREINENT]', phrase(liste('v-frein', 'fr'), ' et '));
      remplir(zs, '[SECONDE VISITE / RÉFLEXION / OFFRE POSSIBLE / PAS DE SUITE]', s ? NOMS[s] : '');
      if (s && (plu.length || fr.length) && !envoye) { envoye = true; mesure('cr_visite', { page: location.pathname }); }
    }
    bloc.addEventListener('change', maj);
    msg.hidden = false; bloc.classList.add('geste-actif'); maj();
  })();

  /* ---- Négociation : l'écart entre le prix affiché et l'offre ---- */
  (function () {
    var bloc = document.querySelector('.b-offre'); if (!bloc) return;
    var cp = bloc.querySelector('#o-prix'), co = bloc.querySelector('#o-offre');
    var scene = bloc.querySelector('.offre-scene'), barre = bloc.querySelector('.offre-barre'), ecart = bloc.querySelector('.offre-ecart'), t1 = bloc.querySelector('.offre-t1');
    var base = t1.textContent, envoye = false;
    var zprix = zone('[PRIX]'), zmont = zone('[MONTANT]'), zec = zone('[ÉCART AVEC LE PRIX AFFICHÉ]'), zfin = zone('[COMPTANT / PRÊT AVEC ACCORD DE PRINCIPE / PRÊT SANS ACCORD]');
    function nombre(c) { var n = parseInt(c.value.replace(/[^0-9]/g, ''), 10); return isNaN(n) ? 0 : n; }
    function euros(n) { return n.toLocaleString('fr-FR') + ' €'; }
    function maj() {
      var p = nombre(cp), o = nombre(co), f = (bloc.querySelector('input[name="o-fin"]:checked') || {}).value || '';
      remplir(zprix, '[PRIX]', p ? euros(p) : ''); remplir(zmont, '[MONTANT]', o ? euros(o) : '');
      remplir(zfin, '[COMPTANT / PRÊT AVEC ACCORD DE PRINCIPE / PRÊT SANS ACCORD]', f);
      if (!p || !o) { scene.hidden = true; t1.textContent = base; remplir(zec, '[ÉCART AVEC LE PRIX AFFICHÉ]', ''); return; }
      var d = p - o, pct = Math.abs(d) / p * 100, txt = pct.toFixed(1).replace('.', ',') + ' %';
      var sens = d > 0 ? 'sous le prix affiché' : d < 0 ? 'au-dessus du prix affiché' : '';
      scene.hidden = false;
      barre.style.setProperty('--part', Math.max(4, Math.min(100, o / p * 100)) + '%');
      barre.classList.toggle('plein', d <= 0);
      ecart.innerHTML = d === 0 ? '<strong>Au prix</strong> l’offre est égale au prix affiché' : '<strong>' + (d > 0 ? '− ' : '+ ') + txt + '</strong> soit ' + euros(Math.abs(d)) + ' ' + sens;
      var resume = d === 0 ? 'au prix affiché' : euros(Math.abs(d)) + ' ' + sens + ' (' + txt + ')';
      t1.textContent = 'Une offre écrite à ' + euros(o) + ', ' + resume + (f ? ', financement : ' + f : '') + '. Vous la transmettez avec ses conditions et son délai, sans la commenter.';
      remplir(zec, '[ÉCART AVEC LE PRIX AFFICHÉ]', resume);
      if (!envoye) { envoye = true; mesure('ecart_offre', { page: location.pathname }); }
    }
    bloc.addEventListener('input', maj); bloc.addEventListener('change', maj);
    bloc.classList.add('geste-actif'); maj();
  })();

  /* ---- Loi ALUR : où en êtes-vous de vos 42 heures ---- */
  (function () {
    var bloc = document.querySelector('.b-alur'); if (!bloc) return;
    var TOTAL = 42, c = bloc.querySelector('#al-h'), hv = bloc.querySelector('#al-hv'), deo = bloc.querySelector('#al-deo'), dis = bloc.querySelector('#al-dis');
    var scene = bloc.querySelector('.alur-scene'), barre = bloc.querySelector('.offre-barre'), reste = bloc.querySelector('.alur-reste'), texte = bloc.querySelector('.alur-texte'), fin = bloc.querySelector('.alur-finance');
    var envoye = false;
    function maj() {
      var fait = parseInt(c.value, 10) || 0, r = TOTAL - fait, manque = [];
      if (!deo.checked) manque.push('2 h de déontologie');
      if (!dis.checked) manque.push('2 h de non-discrimination');
      var themes = manque.join(' et '), q = (bloc.querySelector('input[name="al-quand"]:checked') || {}).value;
      hv.textContent = fait + ' h';
      barre.style.setProperty('--part', Math.max(r > 0 ? 3 : 100, fait / TOTAL * 100) + '%');
      barre.classList.toggle('plein', r <= 0);
      var aFaire = r > 0 ? r : manque.length * 2;
      reste.innerHTML = aFaire === 0 ? '<strong>À jour</strong> vos 42 heures et les deux thèmes obligatoires sont faits' : '<strong>' + aFaire + ' h</strong> ' + (r > 0 ? 'restantes sur 42' : 'de thèmes obligatoires à ajouter');
      var t;
      if (aFaire === 0) t = 'Gardez vos attestations : elles vous seront demandées au renouvellement.';
      else if (r <= 0) t = 'Vos 42 heures sont faites, mais il manque ' + themes + '. Ces thèmes sont obligatoires sur la période.';
      else {
        t = 'Il vous reste ' + r + ' heures à suivre' + (themes ? ', dont ' + themes : '') + '.';
        if (q === '1') t += ' À planifier dans l’année, sans attendre le dernier trimestre.';
        else if (q) t += q === '3' ? ' Vous pouvez les étaler d\u2019ici le renouvellement.' : ' À répartir sur les deux prochaines années.';
      }
      texte.textContent = t;
      fin.hidden = aFaire < 4;
      fin.textContent = 'Voir mon financement pour ces ' + aFaire + ' heures';
      fin.setAttribute('href', '/financement-formation-immobilier/?heures=' + aFaire + '#simulateur');
    }
    bloc.addEventListener('input', function () { maj(); if (!envoye) { envoye = true; mesure('heures_alur', { page: location.pathname }); } });
    scene.hidden = false; bloc.classList.add('geste-actif'); maj();
  })();
})();
