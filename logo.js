// Logo animé de l'en-tête : le « A » tourne quand on fait défiler et revient toujours face à l'écran à l'arrêt,
// et le triangle orange (l'IA) s'échappe quand on fait défiler vite ou qu'on survole le logo.
(() => {
  const logo = document.querySelector('.entete .logo-anime');
  if (!logo || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const lien = logo.closest('a');
  logo.classList.add('arrive');
  logo.addEventListener('animationend', (e) => { if (e.target.classList.contains('la-t')) logo.classList.remove('arrive'); });
  let tour = 0, cibleTour = 0, ecart = 0, survol = 0, avant = scrollY, arret = 0, boucle = 0;
  const pas = () => {
    const dy = scrollY - avant; avant = scrollY;
    const vitesse = Math.abs(dy);
    cibleTour += dy * .5;                                   // il tourne dans le sens du défilement
    arret = vitesse ? 0 : arret + 1;
    if (arret > 10) {                                       // à l'arrêt : il finit son tour et se remet de face
      const sens = Math.sign(cibleTour - tour) || 1;
      cibleTour = (sens > 0 ? Math.ceil : Math.floor)(cibleTour / 360) * 360;
    }
    const cibleEcart = Math.max(survol, Math.min(1, vitesse / 40));
    tour += (cibleTour - tour) * .12;
    ecart += (cibleEcart - ecart) * (cibleEcart > ecart ? .3 : .08);
    logo.style.setProperty('--tour', tour.toFixed(1) + 'deg');
    logo.style.setProperty('--tx', (ecart * 5).toFixed(2) + 'px');
    logo.style.setProperty('--ty', (-ecart * 4).toFixed(2) + 'px');
    logo.style.setProperty('--tr', (ecart * 22).toFixed(1) + 'deg');
    logo.style.setProperty('--lueur', (ecart * 6).toFixed(1) + 'px');
    const calme = arret > 10 && cibleTour % 360 === 0 && Math.abs(cibleTour - tour) < .1 && Math.abs(cibleEcart - ecart) < .005 && vitesse === 0;
    boucle = calme ? 0 : requestAnimationFrame(pas);
  };
  const relance = () => { if (!boucle) boucle = requestAnimationFrame(pas); };
  addEventListener('scroll', relance, { passive: true });
  if (lien) {
    lien.addEventListener('pointerenter', () => { survol = 1; relance(); });
    lien.addEventListener('pointerleave', () => { survol = 0; relance(); });
  }
  relance();
})();
