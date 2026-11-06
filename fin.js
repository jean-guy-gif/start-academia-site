// Fin de l'accueil : les blocs apparaissent en glissant, les chiffres des résultats défilent jusqu'à leur valeur.
(() => {
  const calme = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const blocs = document.querySelectorAll('.outil, .carte-cible, .alur-v2, .bloc-b, .eq-photo, .membre-v2, .info, .carte-qualiopi, .faq-liste details');
  if (calme || !('IntersectionObserver' in window)) return;
  const vue = new IntersectionObserver((entrees) => {
    entrees.forEach((e) => {
      if (!e.isIntersecting) return;
      e.target.classList.add('vu'); vue.unobserve(e.target);
      const n = e.target.querySelector('[data-compte]');
      if (n) {
        const fin = +n.dataset.compte, t0 = performance.now(), duree = 1400;
        const pas = (t) => { const k = Math.min(1, (t - t0) / duree); n.textContent = Math.round(fin * (1 - Math.pow(1 - k, 3))); if (k < 1) requestAnimationFrame(pas); };
        requestAnimationFrame(pas);
      }
    });
  }, { threshold: .18 });
  blocs.forEach((b, i) => { b.classList.add('revele'); b.style.transitionDelay = (i % 3) * 90 + 'ms'; vue.observe(b); });
})();
