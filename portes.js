/* Accueil : trois portes en 3D. Pousser une porte règle la page sur le profil du visiteur
   (promesse, démo, outils mis en avant, carte « Pour qui », appel final). Le choix est gardé
   dans le navigateur (localStorage) et n'est pas transmis. Sans script, les portes restent
   de simples liens vers les pages de parcours. */
(function () {
  var scene = document.querySelector('.portes-scene');
  if (!scene) return;
  var CLE = 'sa-profil', CLE_NIVEAU = 'sa-niveau';
  var CAL = 'https://meet.brevo.com/jean-guy-ourmieres/appel-decouverte';
  var calme = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var PROFILS = {
    agence: {
      nom: 'agence', puce: 'Parcours agence', image: '/img/agence.webp', page: '/formation-ia-directeur-agence-immobiliere/',
      titre: 'Votre équipe, formée dans votre agence.',
      points: ['Formation dans votre agence, sur vos dossiers', 'Coaching et audit de direction', 'Des outils partagés par toute l’équipe'],
      financement: 'Financement par votre OPCO',
      promesse: 'Des formateurs de terrain qui rendent votre équipe plus rapide à chaque étape de la transaction, avec l’IA et nos outils maison.',
      demo: 'Vos agents peuvent préparer ça, et bien plus, avant chaque premier rendez-vous.',
      final: 'Parlons de votre agence.', badge: 'Pour votre agence', outils: ['Academia Pilotage', 'Academia Parcours'], carte: 0
    },
    reseau: {
      nom: 'réseau', puce: 'Parcours réseau', image: '/img/formation.webp', page: '/formation-ia-reseau-mandataires/',
      titre: 'L’IA déployée dans tout votre réseau.',
      points: ['Un programme adapté à votre réseau', 'En présentiel ou à distance', 'Des outils accessibles à chaque mandataire'],
      financement: 'Partenariat réseau ou financement individuel',
      promesse: 'Des formateurs de terrain qui déploient l’IA auprès de vos mandataires, à chaque étape de la transaction, avec nos outils maison.',
      demo: 'Vos mandataires peuvent préparer ça, et bien plus, avant chaque premier rendez-vous.',
      final: 'Parlons de votre réseau.', badge: 'Pour votre réseau', outils: ['Academia Parcours', 'Academia Secteur'], carte: 1
    },
    conseiller: {
      nom: 'conseiller', puce: 'Parcours conseiller', image: '/img/visite.webp', page: '/formation-ia-immobilier/',
      titre: 'Du temps gagné à chaque étape de la vente.',
      points: ['Version débutant ou avancée', 'Heures comptabilisées pour la loi ALUR', 'Dossier de financement monté avec vous'],
      financement: 'Financement par l’AGEFICE, le FIF PL…',
      promesse: 'Des formateurs de terrain qui vous font gagner du temps à chaque étape de la transaction, avec l’IA et nos outils maison.',
      demo: 'Vous pouvez préparer ça, et bien plus, avant chaque premier rendez-vous.',
      final: 'Parlons de votre activité.', badge: 'Pour vous', outils: ['Academia Secteur', 'Academia ACM'], carte: 2
    }
  };
  var NIVEAUX = {
    debutant: 'Version débutant : on part de zéro, pas à pas, sur vos propres dossiers.',
    avance: 'Version avancée : on passe directement aux cas complexes et à nos outils maison.'
  };
  function lire(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function ecrire(k, v) { try { v === null ? localStorage.removeItem(k) : localStorage.setItem(k, v); } catch (e) {} }
  function el(tag, cls, txt) { var n = document.createElement(tag); if (cls) n.className = cls; if (txt != null) n.textContent = txt; return n; }
  function suivre(nom, data) { if (window.va) window.va('event', { name: nom, data: data }); }

  var couloir = scene.querySelector('.portes-couloir');
  var parcours = scene.querySelector('.parcours');
  var portes = [].slice.call(scene.querySelectorAll('.porte'));

  // Éléments de la page réglés sur le profil, avec leur texte d'origine
  var cibles = {
    promesse: document.querySelector('.voyage-titre .promesse'),
    demo: document.querySelector('.apres-demo p'),
    final: document.getElementById('titre-final')
  };
  var origine = {};
  Object.keys(cibles).forEach(function (k) { if (cibles[k]) origine[k] = cibles[k].textContent; });
  var atelier = document.querySelector('.outil') && document.querySelector('.outil').parentNode;
  var ordreOutils = atelier ? [].slice.call(atelier.children) : [];
  var cartes = [].slice.call(document.querySelectorAll('.carte-cible'));
  var barre = document.querySelector('.entete .barre');
  var puce = null;

  function nomOutil(a) { var h = a.querySelector('h3'); return h ? h.textContent.trim() : ''; }
  function reglerOutils(p) {
    if (!atelier) return;
    ordreOutils.forEach(function (a) { var b = a.querySelector('.outil-pourvous'); if (b) b.remove(); atelier.appendChild(a); });
    if (p) {
      p.outils.slice().reverse().forEach(function (nom) {
        var a = ordreOutils.filter(function (o) { return nomOutil(o).indexOf(nom) === 0; })[0];
        if (!a) return;
        var t = a.querySelector('.o-texte') || a;
        t.insertBefore(el('p', 'outil-pourvous', p.badge), t.firstChild);
        atelier.insertBefore(a, atelier.firstChild);
      });
    }
    [].slice.call(atelier.querySelectorAll('.outil.vedette')).forEach(function (a, i) { a.classList.toggle('inverse', i % 2 === 1); });
  }
  function reglerPage(id) {
    var p = id ? PROFILS[id] : null;
    if (p) document.documentElement.setAttribute('data-profil', id); else document.documentElement.removeAttribute('data-profil');
    Object.keys(cibles).forEach(function (k) { if (cibles[k]) cibles[k].textContent = p ? p[k] : origine[k]; });
    cartes.forEach(function (c, i) { c.classList.toggle('choisie', !!p && i === p.carte); c.classList.toggle('attenuee', !!p && i !== p.carte); });
    reglerOutils(p);
    if (puce) { puce.remove(); puce = null; }
    if (p && barre) {
      puce = el('button', 'profil-puce'); puce.type = 'button';
      puce.appendChild(el('span', 'pp-nom', p.puce)); puce.appendChild(el('span', 'pp-changer', 'changer'));
      puce.addEventListener('click', function () { changer(true); });
      var cta = barre.querySelector('.action'); if (cta) cta.parentNode.insertBefore(puce, cta); else barre.appendChild(puce);
    }
  }

  function montrerParcours(id, anime) {
    var p = PROFILS[id];
    parcours.textContent = '';
    var vue = el('div', 'parcours-vue'); var img = new Image(); img.src = p.image; img.alt = ''; vue.appendChild(img);
    var corps = el('div', 'parcours-corps');
    corps.appendChild(el('p', 'parcours-sur', 'Vous êtes entré. La page est réglée sur votre profil.'));
    var h = el('h3', 'parcours-titre', p.titre); h.tabIndex = -1; corps.appendChild(h);
    var ul = el('ul', 'parcours-points'); p.points.forEach(function (t) { ul.appendChild(el('li', null, t)); }); corps.appendChild(ul);
    corps.appendChild(el('p', 'parcours-financement', p.financement));
    var niv = el('div', 'parcours-niveau'); niv.setAttribute('role', 'group'); niv.setAttribute('aria-label', 'Votre niveau en IA');
    niv.appendChild(el('span', 'pn-question', 'Votre niveau en IA ?'));
    var reponse = el('p', 'pn-reponse'); reponse.setAttribute('aria-live', 'polite');
    [['debutant', 'Je débute'], ['avance', 'Je l’utilise déjà']].forEach(function (n) {
      var b = el('button', 'pn-choix', n[1]); b.type = 'button'; b.setAttribute('aria-pressed', 'false');
      b.addEventListener('click', function () {
        [].forEach.call(niv.querySelectorAll('.pn-choix'), function (x) { x.setAttribute('aria-pressed', String(x === b)); });
        reponse.textContent = NIVEAUX[n[0]]; ecrire(CLE_NIVEAU, n[0]); suivre('niveau', { profil: id, niveau: n[0] });
      });
      niv.appendChild(b);
      if (lire(CLE_NIVEAU) === n[0]) { b.setAttribute('aria-pressed', 'true'); reponse.textContent = NIVEAUX[n[0]]; }
    });
    corps.appendChild(niv); corps.appendChild(reponse);
    var actions = el('div', 'parcours-actions');
    var appel = el('a', 'action', 'Réserver mon appel découverte'); appel.href = CAL; appel.rel = 'noopener';
    appel.insertAdjacentHTML('beforeend', '<svg aria-hidden="true"><use href="#fleche"/></svg>');
    var detail = el('a', 'parcours-detail', 'Le détail du parcours ' + p.nom); detail.href = p.page; detail.setAttribute('data-suivi', 'parcours-' + id);
    var autre = el('button', 'parcours-changer', 'Changer de porte'); autre.type = 'button'; autre.addEventListener('click', function () { changer(false); });
    actions.appendChild(appel); actions.appendChild(detail); actions.appendChild(autre); corps.appendChild(actions);
    parcours.appendChild(vue); parcours.appendChild(corps);
    couloir.hidden = true; parcours.hidden = false; scene.setAttribute('data-etat', 'parcours');
    if (anime) { parcours.classList.add('entre'); h.focus({ preventScroll: true }); setTimeout(function () { parcours.classList.remove('entre'); }, 1200); }
  }

  function changer(defiler) {
    ecrire(CLE, null); reglerPage(null);
    portes.forEach(function (x) { x.classList.remove('ouverte', 'ecartee'); });
    parcours.hidden = true; couloir.hidden = false; scene.setAttribute('data-etat', 'choix');
    if (defiler) document.getElementById('portes').scrollIntoView({ behavior: calme ? 'auto' : 'smooth', block: 'center' });
  }

  portes.forEach(function (a) {
    a.addEventListener('click', function (e) {
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.button) return; // ouverture dans un nouvel onglet : lien normal
      e.preventDefault();
      var id = a.getAttribute('data-profil');
      ecrire(CLE, id); suivre('profil', { profil: id });
      portes.forEach(function (x) { x.classList.toggle('ouverte', x === a); x.classList.toggle('ecartee', x !== a); });
      setTimeout(function () { try { reglerPage(id); } catch (err) {} montrerParcours(id, true); }, calme ? 0 : 850);
    });
  });

  // Légère inclinaison du couloir sous la souris (profondeur)
  if (!calme && window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
    scene.addEventListener('pointermove', function (e) {
      var r = scene.getBoundingClientRect();
      couloir.style.setProperty('--ry', ((e.clientX - r.left) / r.width - .5) * 7 + 'deg');
      couloir.style.setProperty('--rx', (.5 - (e.clientY - r.top) / r.height) * 4 + 'deg');
    });
    scene.addEventListener('pointerleave', function () { couloir.style.setProperty('--ry', '0deg'); couloir.style.setProperty('--rx', '0deg'); });
  }

  // Première apparition : les portes s'entrouvrent pour montrer qu'on peut les pousser
  if (!calme && 'IntersectionObserver' in window) {
    var obs = new IntersectionObserver(function (es) {
      if (es[0].isIntersecting) { scene.classList.add('vue'); obs.disconnect(); }
    }, { threshold: .4 });
    obs.observe(couloir);
  }

  var memo = lire(CLE);
  if (memo && PROFILS[memo]) { try { reglerPage(memo); } catch (err) {} montrerParcours(memo, false); }
})();
