"""Bloc HTML du simulateur de financement (page /financement-formation-immobilier/).
Les années et taux affichés sont remplis par simulateur.js depuis sa CONFIG."""

CAL = 'https://calendar.app.google/7XsB8TrXs1KSkHs4A'

def radio(nom, options):
    return ''.join(f'<label class="simu-choix"><input type="radio" name="{nom}" value="{v}"{" checked" if i == 0 else ""}><span>{t}</span></label>'
                   for i, (v, t) in enumerate(options))

def montant(id_, label, aide, err, suffixe='€', placeholder='', aide_html=True):
    return f'''<div class="simu-champ">
            <label for="{id_}">{label}</label>
            <div class="simu-saisie"><input id="{id_}" type="text" inputmode="decimal" autocomplete="off" placeholder="{placeholder}" aria-describedby="{id_}-aide {err}"><span aria-hidden="true">{suffixe}</span></div>
            <p class="simu-aide" id="{id_}-aide">{aide}</p>
            <p class="simu-erreur" id="{err}" hidden>Saisissez un montant valide, positif ou nul (ex. 1 250,50).</p>
          </div>'''

def resultat(k, titre_plafond, titre_deja, titre_reste):
    return f'''<aside class="simu-resultat" aria-labelledby="{k}-etiquette">
          <p class="simu-etiquette" id="{k}-etiquette">Estimation</p>
          <p class="simu-montant" id="{k}-reste" aria-live="polite">—</p>
          <p class="simu-legende">{titre_reste}</p>
          <dl class="simu-detail">
            <div><dt>{titre_plafond}</dt><dd id="{k}-plafond">—</dd></div>
            <div><dt>{titre_deja}</dt><dd id="{k}-deja">—</dd></div>
          </dl>
          <p class="simu-message" id="{k}-message" aria-live="polite"></p>
          <button type="button" class="simu-copier" id="{k}-copier" disabled>Copier mon estimation</button>
          <p class="simu-reserve">Simulation indicative calculée selon les critères de financement <span data-annee></span>. Le montant réellement mobilisable dépend de votre éligibilité, de vos cotisations, des formations sélectionnées et de l'accord de votre organisme financeur.</p>
          <div class="simu-suite" hidden>
            <a class="action" href="{CAL}" rel="noopener">Faites vérifier votre financement par Start Academia<svg aria-hidden="true"><use href="#fleche"/></svg></a>
            <p>Notre équipe vous accompagne dans la vérification de votre éligibilité et le montage de votre dossier de financement.</p>
          </div>
        </aside>'''

SIMULATEUR = f'''  <section class="bloc bloc-simu" id="simulateur-financement" aria-labelledby="titre-simu">
    <div class="simu-tete">
      <h2 id="titre-simu">Calculez votre budget formation en moins d'une minute</h2>
      <p>Indépendant ou employeur&nbsp;? Estimez les financements que vous pourriez mobiliser pour développer vos compétences ou celles de votre équipe.</p>
    </div>
    <div class="simu" id="simulateur">
      <p class="simu-perime" id="simu-perime" hidden>Ce simulateur utilise les barèmes <span data-annee></span>, qui ne sont plus en vigueur. Les nouveaux barèmes seront intégrés dès leur publication&nbsp;: en attendant, <a href="{CAL}" rel="noopener">contactez-nous</a> pour une estimation.</p>
      <div class="simu-onglets" role="tablist" aria-label="Votre situation">
        <button type="button" role="tab" id="age-onglet" aria-selected="true" aria-controls="age-panneau">Je suis indépendant <span>AGEFICE</span></button>
        <button type="button" role="tab" id="opco-onglet" aria-selected="false" aria-controls="opco-panneau" tabindex="-1">J'emploie des salariés <span>OPCO</span></button>
      </div>

      <div class="simu-panneau" role="tabpanel" id="age-panneau" aria-labelledby="age-onglet" tabindex="0">
        <div class="simu-questions">
          <fieldset class="simu-champ">
            <legend>Quelle information connaissez-vous&nbsp;?</legend>
            <div class="simu-choix-liste">{radio("simu-mode", [("ca", "Mon chiffre d’affaires déclaré à l’URSSAF"), ("cfp", "Mon attestation CFP")])}</div>
          </fieldset>
          <div id="simu-groupe-ca">
            <div class="simu-champ">
              <label for="simu-regime">Votre régime d'activité</label>
              <select id="simu-regime" class="simu-select">
                <option value="bnc" id="simu-opt-bnc">Micro-BNC — Agent commercial immobilier</option>
                <option value="bic" id="simu-opt-bic">Micro-entreprise — Activité commerciale</option>
                <option value="autre">Autre régime / hors micro-entreprise</option>
              </select>
              <p class="simu-aide">Le calcul à partir du chiffre d'affaires ne concerne que les micro-entrepreneurs. Le régime BNC ne prouve pas, à lui seul, le rattachement à l'AGEFICE.</p>
            </div>
            <div id="simu-champ-ca">
              {montant("simu-ca", 'Chiffre d’affaires encaissé et déclaré à l’URSSAF en <span data-annee-ca></span>', 'Indiquez uniquement le chiffre d’affaires encaissé et déclaré à l’URSSAF en <span data-annee-ca></span>, et non votre production commerciale immobilière.', "simu-err-ca", placeholder="Ex. 30 000")}
            </div>
            <p class="simu-note" id="simu-hors-micro" hidden>Hors micro-entreprise, une estimation fiable nécessite votre attestation CFP URSSAF. Choisissez « Mon attestation CFP » ci-dessus.</p>
            <p class="simu-note simu-note-calcul" id="simu-cfp-calculee" hidden aria-live="polite"></p>
          </div>
          <div id="simu-groupe-cfp" hidden>
            {montant("simu-cfp", 'Montant de la CFP inscrit sur votre attestation URSSAF', 'Attestation délivrée en <span data-annee></span>, relative à votre activité <span data-annee-ca></span>. Elle se télécharge dans votre espace URSSAF.', "simu-err-cfp", placeholder="Ex. 12,50")}
          </div>
          <fieldset class="simu-champ">
            <legend>Votre attestation URSSAF indique-t-elle AGEFICE&nbsp;?</legend>
            <div class="simu-choix-liste">{radio("simu-faf", [("inconnu", "Je ne sais pas"), ("oui", "Oui"), ("non", "Non / FIF PL")])}</div>
            <p class="simu-aide">Un indépendant de l'immobilier peut dépendre d'un autre fonds, notamment le FIF PL. Seule l'attestation URSSAF confirme le fonds compétent.</p>
          </fieldset>
          <fieldset class="simu-champ">
            <legend>Avez-vous déjà bénéficié d'un financement AGEFICE en <span data-annee></span>&nbsp;?</legend>
            <div class="simu-choix-liste">{radio("simu-age-deja", [("non", "Non"), ("oui", "Oui")])}</div>
          </fieldset>
          <div id="simu-champ-age-deja" hidden>
            {montant("simu-age-montant", 'Montant total de vos formations déjà financées ou réservées par l’AGEFICE en <span data-annee></span>', 'Total des prises en charge accordées ou en cours cette année.', "simu-err-age", placeholder="Ex. 850")}
          </div>
        </div>
        {resultat("age", "Plafond annuel théorique", "Financements déjà mobilisés", "Budget potentiellement restant")}
      </div>

      <div class="simu-panneau" role="tabpanel" id="opco-panneau" aria-labelledby="opco-onglet" tabindex="0" hidden>
        <div class="simu-questions">
          <p class="simu-note">Pour les entreprises de la branche Immobilier de l'OPCO EP (convention collective IDCC&nbsp;1527). Ces barèmes ne s'appliquent pas aux autres OPCO ni aux autres conventions collectives.</p>
          <div class="simu-champ">
            <label for="simu-effectif">Combien de salariés compte votre entreprise&nbsp;?</label>
            <div class="simu-saisie"><input id="simu-effectif" type="text" inputmode="numeric" autocomplete="off" placeholder="Ex. 8" aria-describedby="simu-effectif-aide simu-err-effectif"><span aria-hidden="true">salariés</span></div>
            <p class="simu-aide" id="simu-effectif-aide">Ce budget est collectif&nbsp;: il concerne l'ensemble des salariés de l'entreprise et non chaque salarié individuellement.</p>
            <p class="simu-erreur" id="simu-err-effectif" hidden>Saisissez un nombre entier de salariés, positif ou nul.</p>
          </div>
          <fieldset class="simu-champ">
            <legend>Votre entreprise a-t-elle déjà bénéficié de financements OPCO EP en <span data-annee></span>&nbsp;?</legend>
            <div class="simu-choix-liste">{radio("simu-opco-deja", [("non", "Non"), ("oui", "Oui")])}</div>
          </fieldset>
          <div id="simu-champ-opco-deja" hidden>
            {montant("simu-opco-montant", 'Quel montant HT a déjà été financé ou réservé en <span data-annee></span>&nbsp;?', 'Total des prises en charge déjà accordées à l’entreprise cette année.', "simu-err-opco", suffixe="€ HT", placeholder="Ex. 1 200")}
          </div>
        </div>
        {resultat("opco", "Budget collectif annuel théorique", "Montant HT déjà mobilisé", "Budget collectif potentiellement restant")}
      </div>

      <p class="simu-sources">Sources officielles&nbsp;: <a href="https://communication-agefice.fr/plafonds-financiers-annee-2026/" rel="noopener" target="_blank">AGEFICE, plafonds 2026</a> · <a href="https://communication-agefice.fr/les-ressortissants-de-lagefice/" rel="noopener" target="_blank">AGEFICE, ressortissants</a> · <a href="https://www.economie.gouv.fr/entreprises/gerer-sa-micro-entreprise/micro-entreprises-quel-est-le-montant-de-vos-cotisations-sociales" rel="noopener" target="_blank">CFP des micro-entrepreneurs</a> · <a href="https://www.opcoep.fr/criteres-de-financement?branche=187" rel="noopener" target="_blank">OPCO EP, branche Immobilier</a></p>
    </div>
    <script src="/simulateur.js" defer></script>
  </section>'''
