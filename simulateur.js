// Simulateur de financement Start Academia (AGEFICE / OPCO EP branche Immobilier).
// Reprend les règles de la version 3 validée. Tous les montants, taux et années sont
// centralisés dans CONFIG : à mettre à jour à chaque campagne, rien n'est reconduit automatiquement.
(() => {
  'use strict';

  const CONFIG = {
    anneeBareme: 2026,                 // barèmes appliqués
    // Le chiffre d'affaires de référence est toujours celui de l'année N-1.
    get anneeCA() { return this.anneeBareme - 1; },
    agefice: {
      seuilCFP: 7,                     // CFP >= 7 € → plafond haut ; 0 < CFP < 7 € → plafond bas
      plafondBas: 600,
      plafondHaut: 3000,
      zoneIncertitude: [6.75, 7.25],   // CFP calculée depuis le CA trop proche du seuil
      cfpTropFaible: 0.25              // en dessous, le prélèvement réel peut être nul après arrondis
    },
    tauxCFP: {                         // micro-entrepreneurs uniquement
      bnc: { taux: 0.002, libelle: '0,20 %' },
      bic: { taux: 0.001, libelle: '0,10 %' }
    },
    opcoEP: {
      paliers: [{ max: 10, plafond: 2500 }, { max: 50, plafond: 4500 }]
      // au-delà de 50 salariés : 100 % de la cotisation conventionnelle, pas de forfait
    }
  };

  const racine = document.getElementById('simulateur');
  if (!racine) return;
  const $ = id => document.getElementById(id);
  const euro = n => new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR', minimumFractionDigits: Number.isInteger(n) ? 0 : 2, maximumFractionDigits: 2 }).format(n);
  const an = CONFIG.anneeBareme, anCA = CONFIG.anneeCA;

  // Remplit les années affichées dans le texte
  racine.querySelectorAll('[data-annee]').forEach(e => { e.textContent = an; });
  racine.querySelectorAll('[data-annee-ca]').forEach(e => { e.textContent = anCA; });
  $('simu-opt-bnc').textContent = `Micro-BNC — Agent commercial immobilier : CFP ${CONFIG.tauxCFP.bnc.libelle}`;
  $('simu-opt-bic').textContent = `Micro-entreprise — Activité commerciale : CFP ${CONFIG.tauxCFP.bic.libelle}`;

  // Pas de reconduction automatique : si l'année en cours dépasse l'année des barèmes, on n'estime rien.
  const perime = new Date().getFullYear() > an;
  if (perime) { $('simu-perime').hidden = false; racine.classList.add('simu-inactif'); }

  // ---------- Outils de saisie ----------
  const lireMontant = v => {
    const s = String(v).replace(/[\s  ]/g, '').replace(',', '.');
    if (!s) return null;
    if (!/^\d+(\.\d{1,2})?$/.test(s)) return NaN;
    const n = Number(s);
    return Number.isFinite(n) && n >= 0 ? n : NaN;
  };
  const lireEntier = v => {
    const s = String(v).replace(/[\s  ]/g, '');
    if (!s) return null;
    return /^\d+$/.test(s) ? Number(s) : NaN;
  };
  const coche = nom => racine.querySelector(`input[name="${nom}"]:checked`).value;
  const montrer = (id, oui) => { $(id).hidden = !oui; };
  const erreur = (champ, id, oui) => { montrer(id, oui); $(champ).setAttribute('aria-invalid', String(oui)); };

  const plafondAgefice = cfp => cfp <= 0 ? 0 : cfp < CONFIG.agefice.seuilCFP ? CONFIG.agefice.plafondBas : CONFIG.agefice.plafondHaut;
  const plafondOpco = n => { if (n === 0) return 0; for (const p of CONFIG.opcoEP.paliers) if (n <= p.max) return p.plafond; return null; };
  const cfpDepuisCA = (ca, regime) => Math.round((ca * CONFIG.tauxCFP[regime].taux + Number.EPSILON) * 100) / 100;

  function afficher(k, { reste = '—', plafond = '—', deja = '—', message, resume = '', etiquette }) {
    $(k + '-reste').textContent = reste;
    $(k + '-plafond').textContent = plafond;
    $(k + '-deja').textContent = deja;
    $(k + '-message').textContent = message;
    if (etiquette) $(k + '-etiquette').textContent = etiquette;
    const b = $(k + '-copier');
    b.disabled = !resume; b.dataset.resume = resume; b.textContent = 'Copier mon estimation';
    racine.querySelector(`#${k}-panneau .simu-suite`).hidden = !resume;
  }

  // ---------- Parcours AGEFICE ----------
  function majAgefice() {
    const mode = coche('simu-mode'), regime = $('simu-regime').value, faf = coche('simu-faf');
    const parCA = mode === 'ca', micro = regime !== 'autre';
    montrer('simu-groupe-ca', parCA); montrer('simu-groupe-cfp', !parCA);
    montrer('simu-champ-ca', micro); montrer('simu-hors-micro', !micro);
    montrer('simu-cfp-calculee', false);
    const aDeja = coche('simu-age-deja') === 'oui';
    montrer('simu-champ-age-deja', aDeja);
    const deja = aDeja ? lireMontant($('simu-age-montant').value) : 0;
    const ca = lireMontant($('simu-ca').value), cfpAtt = lireMontant($('simu-cfp').value);
    erreur('simu-age-montant', 'simu-err-age', aDeja && Number.isNaN(deja));
    erreur('simu-ca', 'simu-err-ca', parCA && micro && Number.isNaN(ca));
    erreur('simu-cfp', 'simu-err-cfp', !parCA && Number.isNaN(cfpAtt));
    const vide = message => afficher('age', { message, etiquette: 'Estimation AGEFICE' });

    if (perime) return vide(`Les barèmes ${new Date().getFullYear()} ne sont pas encore intégrés à ce simulateur.`);
    if (faf === 'non') return vide('Votre attestation indique un autre fonds : les plafonds AGEFICE ne s’appliquent pas. Consultez les critères du fonds indiqué, par exemple ceux du FIF PL, présentés plus bas sur cette page.');
    if (parCA && !micro) return vide('Hors micro-entreprise, la contribution ne se calcule pas à partir du chiffre d’affaires : choisissez « Mon attestation CFP ».');
    if (deja === null || Number.isNaN(deja)) return vide('Indiquez le montant de vos formations déjà financées.');
    if (parCA && (ca === null || Number.isNaN(ca))) return vide(`Indiquez votre chiffre d’affaires ${anCA} déclaré à l’URSSAF.`);
    if (!parCA && (cfpAtt === null || Number.isNaN(cfpAtt))) return vide('Indiquez le montant de CFP inscrit sur votre attestation URSSAF.');

    const cfp = parCA ? cfpDepuisCA(ca, regime) : cfpAtt;
    const reserve = faf === 'inconnu' ? 'Sous réserve de rattachement à l’AGEFICE' : null;
    if (parCA) {
      $('simu-cfp-calculee').textContent = `CFP théorique : ${euro(cfp)} (${euro(ca)} × ${CONFIG.tauxCFP[regime].libelle}). Seul le montant réellement versé, inscrit sur votre attestation URSSAF, fait foi.`;
      montrer('simu-cfp-calculee', true);
    }
    if (parCA && cfp > 0 && cfp <= CONFIG.agefice.cfpTropFaible) return vide('CFP très faible : le montant réellement prélevé peut être nul après arrondis. Aucune estimation fiable sans votre attestation URSSAF.');

    const [zMin, zMax] = CONFIG.agefice.zoneIncertitude, { plafondBas: bas, plafondHaut: haut } = CONFIG.agefice;
    if (parCA && cfp >= zMin && cfp <= zMax) {
      const r1 = Math.max(0, bas - deja), r2 = Math.max(0, haut - deja);
      return afficher('age', {
        reste: `${euro(r1)} à ${euro(r2)}`, plafond: `${euro(bas)} à ${euro(haut)}`, deja: euro(deja),
        etiquette: reserve || 'Estimation à confirmer',
        message: `CFP calculée : ${euro(cfp)}, très proche du seuil de ${euro(CONFIG.agefice.seuilCFP)}. Le plafond applicable dépend du montant réellement versé : vérifiez-le sur votre attestation URSSAF.`,
        resume: `Start Academia – estimation AGEFICE ${an} (à confirmer)\nCFP théorique (CA ${anCA}) : ${euro(cfp)}\nPlafond envisageable : ${euro(bas)} à ${euro(haut)}\nDéjà mobilisé : ${euro(deja)}\nBudget potentiellement restant : ${euro(r1)} à ${euro(r2)}\nÀ confirmer sur l’attestation URSSAF${reserve ? ' – ' + reserve.toLowerCase() : ''}.`
      });
    }

    const plafond = plafondAgefice(cfp), reste = Math.max(0, plafond - deja);
    let message;
    if (plafond === 0) message = 'Contribution nulle : aucun plafond AGEFICE ne s’applique. À vérifier sur votre attestation URSSAF.';
    else if (deja > plafond) message = 'Le montant déjà financé dépasse le plafond annuel : vérifiez l’année et les montants saisis.';
    else message = (parCA ? `CFP théorique : ${euro(cfp)}. ` : `CFP attestée : ${euro(cfp)}. `) + 'Le financement réellement accordé dépend des critères de la formation et de l’accord de l’AGEFICE.';
    afficher('age', {
      reste: euro(reste), plafond: euro(plafond), deja: euro(deja), message,
      etiquette: reserve || (parCA ? 'Estimation à partir du chiffre d’affaires' : 'Budget théorique selon votre attestation'),
      resume: plafond === 0 ? '' : `Start Academia – estimation AGEFICE ${an}\n${parCA ? `CFP théorique calculée sur le CA ${anCA}` : 'CFP inscrite sur l’attestation URSSAF'} : ${euro(cfp)}\nPlafond annuel théorique : ${euro(plafond)}\nDéjà mobilisé : ${euro(deja)}\nBudget potentiellement restant : ${euro(reste)}\n${reserve ? reserve + '. ' : ''}Sous réserve des critères et de l’accord du financeur.`
    });
  }

  // ---------- Parcours OPCO EP ----------
  function majOpco() {
    const n = lireEntier($('simu-effectif').value);
    const aDeja = coche('simu-opco-deja') === 'oui';
    montrer('simu-champ-opco-deja', aDeja);
    const deja = aDeja ? lireMontant($('simu-opco-montant').value) : 0;
    erreur('simu-effectif', 'simu-err-effectif', Number.isNaN(n));
    erreur('simu-opco-montant', 'simu-err-opco', aDeja && Number.isNaN(deja));
    const vide = message => afficher('opco', { message, etiquette: 'OPCO EP · branche Immobilier' });
    if (perime) return vide(`Les barèmes ${new Date().getFullYear()} ne sont pas encore intégrés à ce simulateur.`);
    if (n === null || Number.isNaN(n)) return vide('Indiquez le nombre de salariés de votre entreprise (nombre entier).');
    if (deja === null || Number.isNaN(deja)) return vide('Indiquez le montant HT déjà financé ou réservé.');
    if (n === 0) return vide('Sans salarié, ce dispositif ne finance pas de formation. Si vous êtes indépendant, utilisez l’onglet AGEFICE.');
    const plafond = plafondOpco(n);
    if (plafond === null) return vide('Au-delà de 50 salariés, le financement correspond à la cotisation conventionnelle de l’entreprise : il ne se calcule pas avec le seul effectif. Contactez l’OPCO EP.');
    const reste = Math.max(0, plafond - deja);
    afficher('opco', {
      reste: euro(reste) + ' HT', plafond: euro(plafond) + ' HT', deja: euro(deja) + ' HT', etiquette: 'Budget collectif OPCO EP',
      message: deja > plafond ? 'Le montant déjà mobilisé dépasse le plafond annuel : vérifiez vos données.' : 'Budget pour toute l’entreprise, pas par salarié. L’accord de l’OPCO, ses règles de financement et la disponibilité des fonds restent déterminants.',
      resume: `Start Academia – estimation OPCO EP Immobilier ${an}\nEffectif : ${n} salarié${n > 1 ? 's' : ''}\nBudget collectif annuel théorique : ${euro(plafond)} HT\nDéjà mobilisé : ${euro(deja)} HT\nBudget collectif potentiellement restant : ${euro(reste)} HT\nBudget collectif, sous réserve de l’accord de l’OPCO EP et des fonds disponibles.`
    });
  }

  // ---------- Onglets (clavier : flèches, Début, Fin) ----------
  const onglets = ['age', 'opco'];
  function activer(k, focus) {
    for (const o of onglets) {
      const on = o === k;
      $(o + '-panneau').hidden = !on;
      $(o + '-onglet').setAttribute('aria-selected', String(on));
      $(o + '-onglet').tabIndex = on ? 0 : -1;
    }
    if (focus) $(k + '-onglet').focus();
  }
  onglets.forEach(o => $(o + '-onglet').addEventListener('click', () => activer(o, false)));
  racine.querySelector('[role="tablist"]').addEventListener('keydown', e => {
    if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(e.key)) return;
    e.preventDefault();
    const cur = $('age-onglet').getAttribute('aria-selected') === 'true' ? 'age' : 'opco';
    activer(e.key === 'Home' ? 'age' : e.key === 'End' ? 'opco' : cur === 'age' ? 'opco' : 'age', true);
  });

  ['simu-ca', 'simu-cfp', 'simu-age-montant'].forEach(id => $(id).addEventListener('input', majAgefice));
  $('simu-regime').addEventListener('change', majAgefice);
  ['simu-mode', 'simu-faf', 'simu-age-deja'].forEach(n => racine.querySelectorAll(`input[name="${n}"]`).forEach(x => x.addEventListener('change', majAgefice)));
  ['simu-effectif', 'simu-opco-montant'].forEach(id => $(id).addEventListener('input', majOpco));
  racine.querySelectorAll('input[name="simu-opco-deja"]').forEach(x => x.addEventListener('change', majOpco));
  onglets.forEach(k => $(k + '-copier').addEventListener('click', async function () {
    if (!this.dataset.resume) return;
    try { await navigator.clipboard.writeText(this.dataset.resume); this.textContent = 'Estimation copiée'; }
    catch { this.textContent = 'Copie indisponible'; }
  }));

  window.__simulateur = { CONFIG, lireMontant, lireEntier, plafondAgefice, plafondOpco, cfpDepuisCA };
  majAgefice(); majOpco();
})();
