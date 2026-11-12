/* Mur de logos de l'accueil : transforme la bande de logos (deux rangées à faire glisser au doigt)
   en deux rangées qui défilent seules, en sens opposés. Sans script ou en mouvement réduit,
   la bande reste telle quelle. Les copies servant à la boucle sont masquées aux lecteurs d'écran. */
(function () {
  var mur = document.querySelector('.partenaires-v2 .mur');
  if (!mur || !('IntersectionObserver' in window)) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  function monter() {
    var logos = Array.prototype.slice.call(mur.children);
    var moitie = Math.ceil(logos.length / 2);
    var cadre = document.createElement('div');
    cadre.className = 'mur-defile';
    [logos.slice(0, moitie), logos.slice(moitie)].forEach(function (lot, i) {
      var piste = document.createElement('ul');
      piste.className = 'mur-piste' + (i ? ' inverse' : '');
      lot.forEach(function (li) {
        var img = li.querySelector('img');
        if (img) img.loading = 'eager';
        piste.appendChild(li);
      });
      lot.forEach(function (li) {
        var copie = li.cloneNode(true);
        copie.setAttribute('aria-hidden', 'true');
        piste.appendChild(copie);
      });
      cadre.appendChild(piste);
    });
    mur.replaceWith(cadre);
  }

  var veille = new IntersectionObserver(function (entrees) {
    if (entrees[0].isIntersecting) { veille.disconnect(); monter(); }
  }, { rootMargin: '600px' });
  veille.observe(mur);
})();
