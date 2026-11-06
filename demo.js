// Démo de l'accueil : une adresse → un rendez-vous vendeur préparé avec les données publiques.
// Sources : Base Adresse Nationale (IGN, data.geopf.fr) et DVF (DGFiP, API Cerema). Aucune donnée conservée.
(() => {
  const form = document.querySelector('.recherche');
  if (!form) return;
  const champ = form.querySelector('input');
  const bouton = form.querySelector('button');
  const liste = document.querySelector('#suggestions');
  const bulle = document.querySelector('.bulle-demo');
  const dossier = bulle.querySelector('.dossier');
  const CAL = 'https://calendar.app.google/7XsB8TrXs1KSkHs4A';
  const nb = new Intl.NumberFormat('fr-FR');
  const eur = new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 0 });
  const mois = new Intl.DateTimeFormat('fr-FR', { month: 'short', year: 'numeric' });
  const anneeMin = new Date().getFullYear() - 3;
  const sansDVF = ['57', '67', '68', '976'];
  const echappe = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const json = (url) => fetch(url).then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); });
  const geocode = (q, n, auto) => json(`https://data.geopf.fr/geocodage/search?q=${encodeURIComponent(q)}&limit=${n}${auto ? '&autocomplete=1' : ''}`).then((j) => j.features || []);
  const mediane = (t) => { if (!t.length) return null; const s = [...t].sort((a, b) => a - b), m = s.length >> 1; return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; };

  // ----- Suggestions d'adresses -----
  let choix = [], actif = -1, minuteur;
  const fermer = () => { liste.hidden = true; champ.setAttribute('aria-expanded', 'false'); actif = -1; };
  const surligner = (i) => {
    actif = i;
    [...liste.children].forEach((li, k) => li.setAttribute('aria-selected', k === i));
    champ.setAttribute('aria-activedescendant', i >= 0 ? `sug-${i}` : '');
  };
  champ.addEventListener('input', () => {
    clearTimeout(minuteur);
    const q = champ.value.trim();
    if (q.length < 4) return fermer();
    minuteur = setTimeout(async () => {
      try { choix = await geocode(q, 5, true); } catch { choix = []; }
      if (!choix.length) return fermer();
      liste.innerHTML = choix.map((f, i) => `<li id="sug-${i}" role="option" aria-selected="false">${echappe(f.properties.label)}</li>`).join('');
      liste.hidden = false; champ.setAttribute('aria-expanded', 'true'); actif = -1;
    }, 250);
  });
  champ.addEventListener('keydown', (e) => {
    if (liste.hidden) return;
    if (e.key === 'ArrowDown') { e.preventDefault(); surligner(Math.min(choix.length - 1, actif + 1)); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); surligner(Math.max(0, actif - 1)); }
    else if (e.key === 'Escape') fermer();
    else if (e.key === 'Enter' && actif >= 0) { e.preventDefault(); champ.value = choix[actif].properties.label; fermer(); lancer(choix[actif]); }
  });
  liste.addEventListener('mousedown', (e) => {
    const li = e.target.closest('li'); if (!li) return;
    e.preventDefault(); const f = choix[+li.id.slice(4)];
    champ.value = f.properties.label; fermer(); lancer(f);
  });
  champ.addEventListener('blur', () => setTimeout(fermer, 150));
  form.addEventListener('submit', (e) => { e.preventDefault(); fermer(); lancer(); });

  // ----- Ventes DVF autour du point -----
  const ventesAutour = async (lon, lat, rayon) => {
    const dLat = rayon / 111320, dLon = rayon / (111320 * Math.cos(lat * Math.PI / 180));
    const bbox = [lon - dLon, lat - dLat, lon + dLon, lat + dLat].map((n) => n.toFixed(5)).join(',');
    let url = `https://apidf-preprod.cerema.fr/dvf_opendata/geomutations/?in_bbox=${bbox}&anneemut_min=${anneeMin}&page_size=500`;
    const tout = [];
    for (let page = 0; url && page < 3; page++) { const j = await json(url); tout.push(...j.features.map((f) => f.properties)); url = j.next; }
    return tout.filter((v) => v.libnatmut === 'Vente' && /^(UN APPARTEMENT|UNE MAISON)$/.test(v.libtypbien) && +v.valeurfonc > 1000);
  };

  // ----- Affichage -----
  const etape = (titre, contenu) => `<li><h3>${titre}</h3><div>${contenu}</div></li>`;
  const ouvrir = () => { bulle.classList.add('ouverte'); dossier.hidden = false; const f = bulle.querySelector('.film'); if (f) f.pause(); };
  const attendre = (ms) => new Promise((r) => setTimeout(r, matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : ms));

  async function lancer(dejaTrouve) {
    const q = champ.value.trim();
    if (!dejaTrouve && q.length < 4) { champ.focus(); champ.setAttribute('aria-invalid', 'true'); return; }
    champ.removeAttribute('aria-invalid');
    bouton.disabled = true; bouton.textContent = 'Préparation…';
    const t0 = performance.now();
    ouvrir();
    dossier.innerHTML = '<p class="d-attente">Localisation de l\'adresse…</p>';
    if (matchMedia('(max-width: 1000px)').matches) bulle.scrollIntoView({ behavior: 'smooth', block: 'start' });
    try {
      const f = dejaTrouve || (await geocode(q, 1))[0];
      if (!f) throw new Error('introuvable');
      const p = f.properties, [lon, lat] = f.geometry.coordinates;
      const dep = (p.citycode || '').startsWith('97') ? p.citycode.slice(0, 3) : (p.citycode || '').slice(0, 2);
      const items = [etape('Adresse localisée', `${echappe(p.label)}`)];
      const rendre = (fin) => { dossier.innerHTML = `<p class="d-tete">Rendez-vous vendeur</p><h2>${echappe(p.name || p.label)}</h2><p class="d-ville">${echappe(p.postcode || '')} ${echappe(p.city || '')}</p><ol class="d-etapes">${items.join('')}</ol>${fin || '<p class="d-attente">Analyse du secteur…</p>'}`; };
      rendre();

      let ventes = [], rayon = 300, erreurDVF = false;
      if (!sansDVF.includes(dep)) {
        try { ventes = await ventesAutour(lon, lat, rayon); if (ventes.length < 8) { rayon = 700; ventes = await ventesAutour(lon, lat, rayon); } }
        catch { erreurDVF = true; }
      }
      await attendre(250);

      const apparts = ventes.filter((v) => v.libtypbien === 'UN APPARTEMENT');
      const maisons = ventes.filter((v) => v.libtypbien === 'UNE MAISON');
      if (sansDVF.includes(dep)) items.push(etape('Ventes du secteur', 'Les ventes ne sont pas publiées dans ce département. En formation, on travaille avec vos propres sources.'));
      else if (erreurDVF) items.push(etape('Ventes du secteur', 'Les données de ventes sont momentanément indisponibles. Réessayez dans un instant.'));
      else if (!ventes.length) items.push(etape('Ventes du secteur', `Aucune vente de maison ou d'appartement publiée depuis ${anneeMin} dans un rayon de ${rayon} m.`));
      else {
        items.push(etape('Ventes du secteur', `<strong>${nb.format(ventes.length)} ventes</strong> depuis ${anneeMin} dans un rayon de ${rayon} m&nbsp;: ${nb.format(apparts.length)} appartements, ${nb.format(maisons.length)} maisons.`));
        rendre(); await attendre(300);
        const m2 = (t) => { const x = t.filter((v) => +v.sbati >= 9 && +v.nbcomm === 1).map((v) => +v.valeurfonc / +v.sbati).filter((x) => x > 300 && x < 40000); return x.length >= 5 ? mediane(x) : null; };
        const ma = m2(apparts), mm = m2(maisons);
        const reperes = [ma && `Appartements&nbsp;: <strong>${eur.format(Math.round(ma / 10) * 10)}&nbsp;€/m²</strong> médian`, mm && `Maisons&nbsp;: <strong>${eur.format(Math.round(mm / 10) * 10)}&nbsp;€/m²</strong> médian`].filter(Boolean);
        if (reperes.length) items.push(etape('Repères de prix du secteur', reperes.join('<br>') + '<span class="d-note">Repères de marché, pas une estimation du bien.</span>'));
        const dernieres = [...ventes].sort((a, b) => b.datemut.localeCompare(a.datemut)).slice(0, 3);
        items.push(etape('Dernières ventes', `<table><caption class="cache-texte">Les trois dernières ventes du secteur</caption><thead><tr><th scope="col">Date</th><th scope="col">Bien</th><th scope="col">Surface</th><th scope="col">Prix</th></tr></thead><tbody>${dernieres.map((v) => `<tr><td>${mois.format(new Date(v.datemut))}</td><td>${v.libtypbien === 'UNE MAISON' ? 'Maison' : 'Appartement'}</td><td>${+v.sbati ? nb.format(Math.round(+v.sbati)) + '&nbsp;m²' : '–'}</td><td>${eur.format(+v.valeurfonc)}&nbsp;€</td></tr>`).join('')}</tbody></table>`));
        rendre(); await attendre(300);
        const args = [
          ventes.length >= 20
            ? `Secteur actif, ${nb.format(ventes.length)} ventes en ${new Date().getFullYear() - anneeMin} ans&nbsp;: les acquéreurs comparent, un bien préparé et suivi par une seule agence se démarque.`
            : `Peu de ventes dans le secteur&nbsp;: chaque acquéreur compte, un seul interlocuteur évite que le bien soit vu partout à des prix différents.`,
          `Le vendeur a un prix en tête&nbsp;: vous arrivez avec les ventes réelles du quartier pour en parler.`,
        ];
        items.push(etape('Arguments pour l\'exclusivité', `<ul>${args.map((a) => `<li>${a}</li>`).join('')}</ul>`));
      }
      items.push(etape('Questions à poser au vendeur', '<ul><li>Qu\'est-ce qui vous amène à vendre, et pour quand&nbsp;?</li><li>Qu\'est-ce qui compte le plus pour vous&nbsp;: le prix, le délai ou la tranquillité&nbsp;?</li><li>Avez-vous déjà rencontré d\'autres agences&nbsp;?</li></ul>'));
      document.querySelector('.apres-demo').hidden = false;
      document.querySelector('.ou').hidden = true;
      const s = ((performance.now() - t0) / 1000).toFixed(1).replace('.', ',');
      rendre(`<p class="d-temps">Préparé en ${s}&nbsp;secondes avec les données publiques.</p>
        <div class="d-suite"><p>En formation, vos agents vont bien plus loin avant chaque premier rendez-vous&nbsp;: dossier d'adresse complet, profil du vendeur, argumentaire, avec nos outils et l'IA.</p>
        <a class="action" href="${CAL}" rel="noopener">Réserver mon appel découverte<svg aria-hidden="true"><use href="#fleche"/></svg></a>
        <button type="button" class="d-autre">Essayer une autre adresse</button></div>
        <p class="d-source">Sources&nbsp;: Base Adresse Nationale (IGN) et demandes de valeurs foncières (DGFiP, via le Cerema). Démonstration&nbsp;: aucune estimation du bien, aucune donnée conservée.</p>`);
    } catch (e) {
      dossier.innerHTML = `<p class="d-tete">Rendez-vous vendeur</p><h2>Adresse introuvable</h2><p class="d-ville">Vérifiez le numéro, la rue et la ville, ou choisissez une adresse dans la liste proposée.</p><div class="d-suite"><button type="button" class="d-autre">Essayer une autre adresse</button></div>`;
    } finally {
      bouton.disabled = false; bouton.textContent = 'Préparer le rendez-vous';
      const autre = dossier.querySelector('.d-autre');
      if (autre) autre.addEventListener('click', () => { bulle.classList.remove('ouverte'); dossier.hidden = true; champ.select(); champ.focus(); });
      dossier.focus({ preventScroll: true });
    }
  }
})();

// Film d'ouverture : version légère sur téléphone, rien si l'utilisateur limite les animations ou ses données.
(() => {
  const film = document.querySelector('.film');
  const bouton = document.querySelector('.film-pause');
  if (!film) return;
  const calme = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const eco = navigator.connection && navigator.connection.saveData;
  if (calme || eco) return;
  film.src = matchMedia('(max-width: 1000px)').matches ? '/img/hero-720.mp4' : '/img/hero-1280.mp4';
  // Le film démarre quand la bulle est visible (sur téléphone, elle est sous le formulaire).
  const vue = new IntersectionObserver(([e]) => {
    if (!e.isIntersecting) return;
    vue.disconnect();
    film.play().then(() => { bouton.hidden = false; }).catch(() => {});
  }, { threshold: .35 });
  vue.observe(film);
  bouton.addEventListener('click', () => {
    if (film.paused) { film.play(); bouton.textContent = 'Pause'; bouton.setAttribute('aria-pressed', 'false'); }
    else { film.pause(); bouton.textContent = 'Lecture'; bouton.setAttribute('aria-pressed', 'true'); }
  });
  film.addEventListener('ended', () => { bouton.textContent = 'Revoir'; bouton.setAttribute('aria-pressed', 'true'); });
})();

// La bulle suit légèrement la souris, comme une fenêtre regardée de biais (ordinateur uniquement).
(() => {
  const bulle = document.querySelector('.bulle-demo');
  if (!bulle) return;
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  if (!matchMedia('(hover: hover) and (pointer: fine)').matches) return;
  const fond = bulle.querySelector('video, img');
  let cx = 0, cy = 0, x = 0, y = 0, boucle = 0;
  const pas = () => {
    const ouverte = bulle.classList.contains('ouverte');
    const tx = ouverte ? 0 : cx, ty = ouverte ? 0 : cy;
    x += (tx - x) * .08; y += (ty - y) * .08;
    bulle.style.transform = `perspective(1400px) rotateX(${(-y * 5).toFixed(2)}deg) rotateY(${(x * 7).toFixed(2)}deg)`;
    if (fond) fond.style.translate = `${(-x * 16).toFixed(1)}px ${(-y * 12).toFixed(1)}px`;
    boucle = Math.abs(tx - x) + Math.abs(ty - y) > .002 ? requestAnimationFrame(pas) : 0;
  };
  addEventListener('pointermove', (e) => {
    const r = bulle.getBoundingClientRect();
    if (r.bottom < 0 || r.top > innerHeight) return;
    cx = Math.max(-1, Math.min(1, (e.clientX - (r.left + r.width / 2)) / (r.width / 2 + 200)));
    cy = Math.max(-1, Math.min(1, (e.clientY - (r.top + r.height / 2)) / (r.height / 2 + 200)));
    if (!boucle) boucle = requestAnimationFrame(pas);
  }, { passive: true });
  document.documentElement.addEventListener('pointerleave', () => { cx = cy = 0; if (!boucle) boucle = requestAnimationFrame(pas); });
})();
