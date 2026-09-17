# Document de cadrage — Dashboard Spotify

## Message clé

> Le genre musical permet d'observer des différences de popularité, mais les caractéristiques audio prises individuellement n'expliquent qu'une partie limitée du succès d'un titre.

## Audience cible

Équipe marketing musicale (labels / plateformes) cherchant à identifier sur quels leviers (genre, profil audio) s'appuyer pour orienter la mise en avant de titres.

## KPIs retenus

| KPI | Vanity ou Actionable ? | Justification |
|---|---|---|
| **Popularité moyenne** (des titres filtrés) | Actionable | Sert de référence contextuelle : permet de comparer un genre, une tranche de tempo ou un sous-ensemble de titres à la moyenne globale, et donc de juger si un segment mérite d'être priorisé. |
| **% de titres populaires (popularité > 50)** | Actionable | Donne une mesure de rendement plutôt qu'un volume brut : indique la probabilité qu'un titre du segment sélectionné perce, ce qui guide directement une décision de mise en avant. |
| **Genre en tête / genre analysé** | Actionable | Identifie concrètement le genre sur lequel concentrer les efforts marketing selon les filtres actifs, plutôt qu'un simple comptage de titres (qui serait une vanity metric). |

*(Écarté volontairement : le nombre total de titres du dataset, qui serait une vanity metric — il ne dit rien sur la popularité ni sur une action à mener.)*

## Structure prévue

- **Zone filtres** (sidebar) : genre musical, popularité minimum, type de contenu (explicite), tempo (BPM), recherche titre/artiste, sélection de genres à comparer.
- **Zone KPIs** (haut de page) : les 3 indicateurs ci-dessus, recalculés dynamiquement selon les filtres.
- **Zone détail** (onglets) :
  1. *Vue générale* — distribution de la popularité (histogramme) + interprétation.
  2. *Comparer les genres* — classement des genres par popularité moyenne (Top 10 automatique ou comparaison manuelle).
  3. *Caractéristiques audio* — relation entre une caractéristique audio choisie et la popularité (nuage de points + corrélation).
  4. *Explorer les titres* — tableau triable des titres filtrés, avec export CSV.
