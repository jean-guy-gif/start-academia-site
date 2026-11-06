// Ouverture de l'accueil, façon Vesper : la bulle à côté du titre grandit jusqu'à remplir l'écran,
// puis le film avance (ou recule) au rythme de la molette, avec un chapitre de texte par séquence.
(() => {
  const voyage = document.querySelector('.voyage');
  const film = voyage && voyage.querySelector('.film-defile');
  if (!film) return;
  const scene = voyage.querySelector('.scene');
  const titre = voyage.querySelector('.voyage-titre');
  const fin = voyage.querySelector('.voyage-fin');
  const chapitres = [...voyage.querySelectorAll('.chapitre')];
  const index = [...voyage.querySelectorAll('.index-ch li')];
  const etroit = matchMedia('(max-width: 1000px)').matches;
  // moments du film (en secondes) où commence chaque chapitre : mer, port, entrée de l'agence, formation
  const DEBUTS = [0, 8.5, 18, 21.8];

  if (matchMedia('(prefers-reduced-motion: reduce)').matches) {
    film.poster = '/img/hero-fin.webp';
    return;
  }
  // Trois versions : téléphone (carré 1080), ordinateur (1920), grand écran ou Retina (2560).
  // Même règle que les balises preload de index.html, pour ne télécharger qu'un seul fichier.
  const grand = matchMedia('(min-resolution: 1.41dppx), (min-width: 2200px)').matches;
  film.src = etroit ? '/img/scrub-1080.mp4' : grand ? '/img/scrub-2560.mp4' : '/img/scrub-1920.mp4';
  const debloquer = () => film.play().then(() => film.pause()).catch(() => {});
  film.addEventListener('loadedmetadata', debloquer, { once: true });
  addEventListener('touchstart', debloquer, { once: true, passive: true });

  const borne = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const phase = (p, a, b) => borne((p - a) / (b - a));
  const doux = (x) => x * x * (3 - 2 * x);
  let cible = 0, actuel = 0, chActif = -2, visible = true;

  const maj = () => {
    const r = voyage.getBoundingClientRect();
    const p = borne(-r.top / (r.height - innerHeight));
    // 1. la bulle s'ouvre (0 → 16 % du défilement)
    const o = doux(phase(p, 0, 0.16));
    if (etroit) {
      scene.style.setProperty('--rx', (46 + o * 40) + '%');
      scene.style.setProperty('--ry', (21 + o * 70) + '%');
      scene.style.setProperty('--cy', (77 - o * 27) + '%');
    } else {
      scene.style.setProperty('--rx', (27 + o * 59) + '%');
      scene.style.setProperty('--ry', (40 + o * 51) + '%');
      scene.style.setProperty('--cx', (72 - o * 22) + '%');
    }
    scene.style.setProperty('--z', (1.12 - o * 0.12).toFixed(3));
    scene.style.setProperty('--t', (1 - phase(p, 0.01, 0.09)).toFixed(3));
    titre.classList.toggle('cache', p > 0.06);
    scene.style.setProperty('--v', phase(p, 0.1, 0.17).toFixed(3));
    // 2. le film avance de 8 % à 94 % du défilement
    if (film.duration) cible = phase(p, 0.08, 0.94) * (film.duration - 0.05);
    // 3. un chapitre par séquence du film, puis l'appel à l'action
    const f = phase(p, 0.93, 0.98);
    scene.style.setProperty('--f', f.toFixed(3));
    fin.classList.toggle('visible', f > 0.5);
    let ch = -1;
    if (p > 0.15 && f < 0.3) { ch = 0; DEBUTS.forEach((d, k) => { if (cible >= d) ch = k; }); }
    if (ch !== chActif) {
      chapitres.forEach((c, k) => c.classList.toggle('actif', k === ch));
      index.forEach((li, k) => li.classList.toggle('actif', k === ch));
      chActif = ch;
    }
  };
  const boucle = () => {
    if (visible) {
      maj();
      actuel += (cible - actuel) * 0.18;
      if (film.readyState >= 2 && !film.seeking && Math.abs(film.currentTime - actuel) > 1 / 30) film.currentTime = actuel;
    }
    requestAnimationFrame(boucle);
  };
  new IntersectionObserver(([e]) => { visible = e.isIntersecting; }).observe(voyage);
  requestAnimationFrame(boucle);
})();
