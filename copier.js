/* Blocs de prompt des pages pilotes : zones [À PERSONNALISER] mises en évidence et bouton « Copier ». */
(function () {
  document.querySelectorAll('.b-prompt pre.prompt-bloc').forEach(function (pre) {
    var texte = pre.textContent;
    pre.innerHTML = pre.innerHTML.replace(/\[[^\]\n]+\]/g, '<mark>$&</mark>');
    if (!navigator.clipboard) return;
    var b = document.createElement('button');
    b.type = 'button'; b.className = 'prompt-copier'; b.textContent = 'Copier le prompt';
    b.addEventListener('click', function () {
      navigator.clipboard.writeText(texte).then(function () {
        b.textContent = 'Prompt copié'; b.classList.add('ok');
        if (window.va) window.va('event', { name: 'clic', data: { cible: 'copier-prompt', page: location.pathname } });
        setTimeout(function () { b.textContent = 'Copier le prompt'; b.classList.remove('ok'); }, 2200);
      });
    });
    pre.parentNode.insertBefore(b, pre);
  });
})();
