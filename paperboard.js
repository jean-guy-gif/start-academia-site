// Le paperboard tactile du manifeste : une page par cran de défilement, la page précédente
// se tourne vers le haut comme une feuille de paperboard. Expose la progression (--p) pour le grand « A ».
(() => {
  const zone = document.querySelector('.defile-pb');
  if (!zone) return;
  const pages = [...zone.querySelectorAll('.pb-page')];
  const num = zone.querySelector('.pb-num b');
  const ecran = zone.querySelector('.pb-ecran');
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) { pages.forEach((p) => p.classList.add('vue')); return; }
  let actuelle = 0, attente = false;
  const maj = () => {
    attente = false;
    const r = zone.getBoundingClientRect();
    const p = Math.min(1, Math.max(0, -r.top / (r.height - innerHeight)));
    zone.style.setProperty('--p', p.toFixed(4));
    ecran.style.setProperty('--p', p.toFixed(4));
    const i = Math.min(pages.length - 1, Math.floor(p * pages.length * 0.999 + 0.0001));
    if (i === actuelle) return;
    pages.forEach((pg, k) => {
      pg.classList.toggle('vue', k === i);
      pg.classList.toggle('tournee', k < i);
    });
    actuelle = i; num.textContent = i + 1;
  };
  addEventListener('scroll', () => { if (!attente) { attente = true; requestAnimationFrame(maj); } }, { passive: true });
  maj();
})();
