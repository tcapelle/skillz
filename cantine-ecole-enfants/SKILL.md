---
name: cantine-ecole-enfants
description: "Gérer les réservations périscolaires et de restauration scolaire sur l'Espace Famille / Espace Citoyens de Chambéry. Utiliser cette skill dès que l'utilisateur mentionne : réservations cantine, périscolaire, accueil matin/midi/soir, restauration scolaire, Espace Famille Chambéry, espace-citoyens.net, ou demande de gérer les inscriptions d'Alba ou Hector. Couvre la navigation sur le site, le remplissage du calendrier de réservation, l'application de périodicités, la soumission des demandes et le suivi des démarches."
---

# Gérer les réservations — Espace Famille Chambéry

## Informations du compte

- **Site** : https://www.espace-citoyens.net/chambery/espace-citoyens/
- **Compte** : Perrine CARROY
- **Enfants** : Alba (idDynamic=4), Hector (idDynamic=3)
- **Identifiants** : stockés dans les variables d'environnement `ESPACE_CITOYENS_LOGIN` et `ESPACE_CITOYENS_PASSWORD` (configurées dans `~/.claude/settings.json` → `env`). Le login est l'identifiant "Mon espace perso" (pas l'email).

## URL directes des réservations

Toutes les URL sont à préfixer de `https://www.espace-citoyens.net/chambery/espace-citoyens`

| Enfant | Service                  | Chemin                                                     |
|--------|--------------------------|------------------------------------------------------------|
| Alba   | Accueil matin/midi/soir  | /DemandeEnfance/NouvelleDemandeReservation/4/316074/95/1163 |
| Alba   | Restauration Scolaire    | /DemandeEnfance/NouvelleDemandeReservation/4/316073/152/41  |
| Hector | Accueil matin/midi/soir  | /DemandeEnfance/NouvelleDemandeReservation/3/316072/95/1163 |
| Hector | Restauration Scolaire    | /DemandeEnfance/NouvelleDemandeReservation/3/316071/152/41  |

## Workflow — 100% JavaScript

Toute l'interaction se fait via `navigate` + `javascript_tool` + `screenshot`. Ne jamais utiliser `find`, `read_page`, ou des clics par coordonnées. Les éléments du site sont stables et référençables directement.

Quand la demande concerne les deux enfants, toujours commencer par Alba et cocher la case "Effectuer la même demande pour Hector" — une seule démarche pour les deux.

### Step 1 — Navigate + vérifier connexion (login auto si nécessaire)

```
navigate → URL directe d'Alba (voir tableau ci-dessus)
screenshot → vérifier "Bonjour Madame CARROY" en haut à droite
```

Si la page de login apparaît (formulaire de connexion au lieu du tableau de bord) :

1. Lire les identifiants depuis les variables d'environnement :
   ```bash
   echo $ESPACE_CITOYENS_LOGIN
   echo $ESPACE_CITOYENS_PASSWORD
   ```

2. Cliquer sur "Mon espace perso" si nécessaire, puis remplir et soumettre le formulaire via `javascript_tool` :
   ```javascript
   // Sélecteurs à vérifier sur la page de login réelle — adapter si besoin
   document.querySelector('#txtLogin').value = '<login from env>';
   document.querySelector('#txtMotDePasse').value = '<password from env>';
   document.querySelector('#btnConnexion').click();
   ```
   **Note :** les sélecteurs `#txtLogin`, `#txtMotDePasse`, `#btnConnexion` sont des hypothèses basées sur les conventions du site. Si le login échoue, prendre un screenshot, inspecter les vrais sélecteurs via `javascript_tool` (`document.querySelectorAll('input')`) et mettre à jour cette section.

3. Attendre 3 secondes, puis `screenshot` → vérifier "Bonjour Madame CARROY".

4. Si connexion réussie, re-naviguer vers l'URL directe d'Alba (le login peut rediriger vers l'accueil).

Si le login échoue (mauvais mot de passe, captcha, 2FA) → demander à l'utilisateur de se connecter manuellement, attendre confirmation, puis re-naviguer.

### Step 2 — Cliquer "Commencer la démarche"

```javascript
[...document.querySelectorAll('a')].find(a => a.textContent.includes('Commencer')).click();
```

### Step 3 — Lire l'état actuel des cases

```javascript
const checkboxes = document.querySelectorAll('input[type="checkbox"]');
const result = [];
checkboxes.forEach(cb => {
  if (cb.name && cb.name.startsWith('c')) result.push({id: cb.id, checked: cb.checked});
});
JSON.stringify(result);
```

### Step 4 — Modifier les cases + cocher Hector

Adapter les paramètres, puis exécuter en un seul `javascript_tool` call :

```javascript
// === ADAPTER CES PARAMÈTRES ===
const serviceName = 'Repas ou PAI';
const datesToCheck = [];                          // dates YYYYMMDD à COCHER
const datesToUncheck = ['20260428', '20260430'];  // dates YYYYMMDD à DÉCOCHER
const applyToOtherChild = true;

// === EXÉCUTION ===
const r = {checked: [], unchecked: [], otherChild: false};

datesToCheck.forEach(d => {
  const cb = document.getElementById('c' + serviceName + d);
  if (cb && !cb.checked) { cb.click(); r.checked.push(d); }
});

datesToUncheck.forEach(d => {
  const cb = document.getElementById('c' + serviceName + d);
  if (cb && cb.checked) { cb.click(); r.unchecked.push(d); }
});

// IMPORTANT: .click() directement — ne PAS faire .checked=false puis .click() (double-toggle)

if (applyToOtherChild) {
  const all = document.querySelectorAll('input[type="checkbox"]');
  const last = all[all.length - 1]; // la case "autre enfant" est toujours la dernière
  if (last && !last.checked) { last.click(); r.otherChild = true; }
}

JSON.stringify(r);
```

**Notes sur les dates :**
- Le mercredi n'a pas de case (pas de cantine).
- Les vacances scolaires n'apparaissent pas dans le calendrier.
- Les jours hors délai sont bloqués.

### Step 5 — Passer au récapitulatif

```javascript
[...document.querySelectorAll('a')].find(a => a.textContent.includes('tape 2')).click();
```

### Step 6 — Vérifier, demander confirmation et valider

Le récapitulatif peut mettre quelques secondes à charger (modale "Merci de patienter..."). Attendre 3-5 secondes avant de prendre le screenshot.

```
wait 3-5 secondes
screenshot → vérifier le récapitulatif (jours + autre enfant)
```

**Avant de valider, toujours demander confirmation à l'utilisateur.** Résumer clairement l'action, par exemple :

> « Je vais désinscrire Hector et Alba de la cantine pour les jours suivants : lundi 28/04, mercredi 30/04. Dois-je valider ? »

Adapter le message selon le contexte (inscription/désinscription, enfants concernés, service, dates). Attendre la confirmation explicite de l'utilisateur avant de cliquer sur Valider.

Le bouton Valider est un `<button>`, pas un `<a>` :

```javascript
document.querySelector('button.btn-style3').click();
```

### Step 7 — Confirmation

```
screenshot → lire les numéros de demande et statuts
```

Donner un résumé clair à l'utilisateur : enfants, service, jours inscrits/désinscrits, numéros de demande.

## Séquence résumée

| # | Outil | Action |
|---|-------|--------|
| 1 | `navigate` | URL directe d'Alba |
| 2 | `screenshot` | Vérifier connexion — si login requis : remplir formulaire via `javascript_tool` avec identifiants env, puis re-naviguer |
| 3 | `javascript_tool` | `[...document.querySelectorAll('a')].find(a => a.textContent.includes('Commencer')).click()` |
| 4 | `javascript_tool` | Lire état des cases (optionnel) |
| 5 | `javascript_tool` | Modifier cases + cocher autre enfant |
| 6 | `screenshot` | Vérifier modifications (fond vert) |
| 7 | `javascript_tool` | Clic "Aller à l'étape 2" |
| 8 | `screenshot` | Vérifier récapitulatif |
| 9 | **confirmation** | Résumer l'action et demander confirmation à l'utilisateur |
| 10 | `javascript_tool` | `document.querySelector('button.btn-style3').click()` |
| 11 | `screenshot` | Lire confirmation → résumé utilisateur |

## Suivi des demandes

Demandes visibles dans "Mes démarches" : `/CompteCitoyen/MesDemandes`.

## Points d'attention

- Session expire après inactivité — cliquer "Prolonger ma session" si modale apparaît.
- Toujours utiliser la case "autre enfant" quand la modification concerne les deux.
- Toujours demander confirmation à l'utilisateur avant de valider (résumer enfants, service, dates).
- **Login auto** : les identifiants doivent être configurés dans `~/.claude/settings.json` → `"env"` (`ESPACE_CITOYENS_LOGIN` et `ESPACE_CITOYENS_PASSWORD`). Si absents, demander à l'utilisateur de les ajouter ou de se connecter manuellement.
- **Sélecteurs login** : les sélecteurs du formulaire (`#txtLogin`, `#txtMotDePasse`, `#btnConnexion`) sont des hypothèses initiales. Lors du premier login automatisé, vérifier et corriger si nécessaire, puis mettre à jour ce fichier.