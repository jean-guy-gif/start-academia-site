/* Comptage des clics (Vercel Web Analytics, sans cookie).
   - tout lien portant data-suivi="nom" envoie l'événement « clic » avec ce nom ;
   - tout lien vers la réservation Brevo envoie « appel_decouverte ».
   Deux propriétés au plus par événement (limite de l'offre Pro). */
(function () {
  window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a');
    if (!a) return;
    var page = location.pathname;
    if (a.dataset.suivi) window.va('event', { name: 'clic', data: { cible: a.dataset.suivi, page: page } });
    else if (a.href.indexOf('meet.brevo.com') !== -1) window.va('event', { name: 'appel_decouverte', data: { page: page } });
  }, { capture: true });
})();
