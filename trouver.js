/* Catalogue : trois questions, une formation au premier plan. Sans script, le bloc reste masqué
   et le catalogue complet se lit tel quel. */
(function () {
  var bloc = document.querySelector('.trouver'); if (!bloc) return;
  var cartes = [].slice.call(document.querySelectorAll('.carte-f'));
  var sortie = bloc.querySelector('.trouver-resultat');
  var appel = (document.querySelector('.final .action') || {}).href || '/#contact';
  var NOMS = {}; [].forEach.call(bloc.querySelectorAll('input[name="t-etape"]'), function (r) { NOMS[r.value] = r.parentNode.textContent; });
  var envoye = '';
  function lire(c) { try { return localStorage.getItem(c); } catch (e) { return null; } }
  function val(n) { var r = bloc.querySelector('input[name="' + n + '"]:checked'); return r ? r.value : ''; }
  function el(tag, cls, txt) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt) e.textContent = txt; return e; }
  function fiche(c) {
    var lien = c.querySelector('.cf-fiche'), img = c.querySelector('.cf-visuel img'), ch = c.querySelector('.cf-chiffres');
    return { id: c.id, titre: c.querySelector('h3').textContent, heures: parseFloat(c.getAttribute('data-heures')) || 0,
      duree: c.querySelector('.cf-duree').textContent, prix: c.querySelector('.cf-prix').textContent, url: lien ? lien.getAttribute('href') : '#' + c.id,
      img: img ? img.getAttribute('src') : '', chiffres: ch ? ch.innerHTML : '', niveau: c.getAttribute('data-niveau'),
      profils: (c.getAttribute('data-profils') || '').split(' '), appr: parseInt(c.getAttribute('data-appr'), 10) || 0, immo: c.getAttribute('data-immo') === '1' ? 1 : 0, carte: c };
  }
  function ouvrir(f) {
    var b = document.querySelector('.cf-chaine button[data-etape=""]'); if (b) b.click();
    var d = f.carte.querySelector('details'); if (d) d.open = true;
    f.carte.classList.add('ciblee'); f.carte.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  function maj() {
    var profil = val('t-profil'), etape = val('t-etape'), niveau = val('t-niveau');
    if (!profil || !etape || !niveau) return;
    var liste = cartes.filter(function (c) { return c.getAttribute('data-etapes').split(' ').indexOf(etape) >= 0; }).map(fiche);
    liste.forEach(function (f) { f.p = f.profils.indexOf(profil) >= 0 ? 1 : 0; f.n = f.niveau === niveau ? 1 : 0; });
    liste.sort(function (a, b) { return (b.immo - a.immo) || (b.p - a.p) || (b.n - a.n) || (b.appr - a.appr) || (niveau === 'avance' ? b.heures - a.heures : a.heures - b.heures); });
    sortie.innerHTML = '';
    if (liste.length) {
      var f = liste[0], h = el('article', 'trouver-une');
      if (f.img) { var i = el('img'); i.src = f.img; i.alt = ''; i.loading = 'lazy'; h.appendChild(i); }
      var c = el('div', 'tu-corps');
      c.appendChild(el('p', 'tu-etape', NOMS[etape] + ' · ' + f.duree + ' · ' + f.prix));
      c.appendChild(el('h3', '', f.titre));
      if (f.chiffres) { var ch = el('div', 'cf-chiffres'); ch.innerHTML = f.chiffres; c.appendChild(ch); }
      var a = el('a', 'tu-fiche', f.url.charAt(0) === '#' ? 'Voir le programme' : 'Voir la fiche complète'); a.href = f.url;
      if (f.url.charAt(0) === '#') a.addEventListener('click', function (e) { e.preventDefault(); ouvrir(f); });
      c.appendChild(a); h.appendChild(c); sortie.appendChild(h);
      if (liste.length > 1) {
        var ul = el('ul', 'trouver-autres');
        liste.slice(1, 3).forEach(function (g) {
          var li = el('li'), b = el('button', '', g.titre); b.type = 'button';
          b.appendChild(el('span', '', g.duree + ' · ' + g.prix));
          b.addEventListener('click', function () { ouvrir(g); }); li.appendChild(b); ul.appendChild(li);
        });
        sortie.appendChild(ul);
      }
    }
    var note = niveau === 'avance' ? 'Vous utilisez déjà l’IA : nos formations se règlent sur votre niveau, et le contenu se cale à l’appel découverte. ' : '';
    if (profil === 'reseau') note += 'Pour un réseau, le plan de déploiement se construit à part. ';
    var p = el('p', 'trouver-mesure', note + (liste.length ? 'Aucune ne colle exactement ? ' : 'Aucune formation du catalogue sur cette étape pour l’instant. '));
    var l = el('a', '', 'On construit votre parcours'); l.href = appel; l.rel = 'noopener'; l.setAttribute('data-suivi', 'trouver-appel'); p.appendChild(l);
    if (profil === 'reseau') { p.appendChild(document.createTextNode(' · ')); var r = el('a', '', 'Voir le plan réseau'); r.href = '/formation-ia-reseau-mandataires/'; p.appendChild(r); }
    sortie.appendChild(p);
    bloc.classList.add('trouve');
    var cle = etape + '/' + niveau;
    if (cle !== envoye) { envoye = cle; if (window.va) window.va('event', { name: 'trouver_formation', data: { etape: etape, niveau: niveau } }); }
  }
  var pr = lire('sa-profil'), nv = lire('sa-niveau'), x;
  if (pr && (x = bloc.querySelector('input[name="t-profil"][value="' + pr + '"]'))) x.checked = true;
  if (nv && (x = bloc.querySelector('input[name="t-niveau"][value="' + nv + '"]'))) x.checked = true;
  bloc.addEventListener('change', maj);
  bloc.hidden = false; maj();
})();
