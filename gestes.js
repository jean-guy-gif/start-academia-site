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
})();
