# Journal de Traçabilité de l'Usage de l'IA (AI_LOG.md)

## Entrée [2026-10-04] — Exercice IV : Bug Hunt (Entité Offre)

- **Outil IA utilisé** : Assistant IA
- **Prompt** : 
  > "Générer le modèle Django `Offre` pour l'application TransConnect selon le cahier des charges."

- **Sortie obtenue (code avec anomalies)** :
  ```python
  class Offre(models.Model):
      prix = models.CharField(max_length=10)
      delai_jours = models.IntegerField()
      statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='proposee')
      date_proposition = models.DateField(auto_now=True)
      expedition = models.ForeignKey(Expedition, on_delete=models.CASCADE)
      transporteur = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
      vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, null=True)

      def save(self, *args, **kwargs):
          super().save(*args, **kwargs)
  ```

- **Écarts identifiés vs cahier des charges (4 Anomalies)** :
  1. **Type du champ `prix` erroné** : Le champ `prix` a été déclaré en `CharField(max_length=10)` au lieu d'un `DecimalField`. Un prix nécessite des calculs arithmétiques et des contraintes de précision monétaire.
  2. **Type du champ `delai_jours` imprécis** : Le champ `delai_jours` est en `IntegerField()` au lieu de `PositiveIntegerField()`. Un délai de livraison en jours ne peut pas être négatif.
  3. **Option d'horodatage erronée sur `date_proposition`** : Le paramètre `auto_now=True` met à jour la date à chaque modification de l'objet, alors que la date de proposition initiale doit être figée à la création (`auto_now_add=True`).
  4. **Absence des champs de traçabilité temporelle obligatoires** : La consigne (Section III) exige que tous les modèles possèdent les attributs `created_at` et `updated_at`. Ils étaient absents du modèle initial.

- **Corrections apportées et justifications** :
  ```python
  from django.db import models

  class Offre(models.Model):
      class Statut(models.TextChoices):
          PROPOSEE = 'proposee', 'Proposée'
          ACCEPTEE = 'acceptee', 'Acceptée'
          REFUSEE = 'refusee', 'Refusée'
          RETIREE = 'retiree', 'Retirée'

      # Correction 1 : DecimalField pour manipuler des valeurs monétaires précises
      prix = models.DecimalField(max_digits=10, decimal_places=2)

      # Correction 2 : PositiveIntegerField pour interdire les délais négatifs
      delai_jours = models.PositiveIntegerField()

      # Correction 3 : auto_now_add=True pour figer la date de création de l'offre
      date_proposition = models.DateField(auto_now_add=True)

      statut = models.CharField(max_length=10, choices=Statut.choices, default=Statut.PROPOSEE)
      expedition = models.ForeignKey("ExpeditionsApp.Expedition", on_delete=models.CASCADE, related_name="offres")
      vehicule = models.ForeignKey("VehiculesApp.Vehicule", on_delete=models.CASCADE, related_name="offres")
      transporteur = models.ForeignKey("EntreprisesApp.Entreprise", on_delete=models.CASCADE, related_name="offres")

      # Correction 4 : Ajout des champs obligatoires created_at et updated_at
      created_at = models.DateTimeField(auto_now_add=True)
      updated_at = models.DateTimeField(auto_now=True)
  ```

---

## Entrée [2026-10-26] — Atelier Administration TransConnect & Dashboard d'Intégrité

- **Outil IA utilisé** : Antigravity (Google DeepMind)
- **Objectif** : Transformer l'interface d'administration Django en cockpit opérationnel métier et implémenter un tableau de bord d'intégrité des données (`/admin/health-check/`).

### 1. Travaux réalisés
1. **Personnalisation complète des 4 `admin.py`** :
   - `ExpeditionsApp` : classe `ExpeditionAdmin`, filtre dynamique `EnRetardFilter` (`SimpleListFilter`), `OffreInline` (`StackedInline` avec liens directs), action groupée `cloturer_expeditions` avec `full_clean() + save()`, et badge visuel de statut.
   - `OffresApp` : classe `OffreAdmin`, autocomplétion des clés étrangères (`autocomplete_fields`), `get_readonly_fields()` dynamique (verrouillant `prix` et `delai_jours` après acceptation), pastille colorée de statut et action `exporter_offres_csv`.
   - `EntreprisesApp` : classe `EntrepriseAdmin` intégrant `VehiculeInline` (`TabularInline`), `search_fields` pour supporter l'autocomplétion, et `UtilisateurAdmin` étendant `UserAdmin`.
   - `VehiculesApp` : classe `VehiculeAdmin` avec `list_editable = ('disponible',)` et `search_fields`.
2. **Branding du site d'administration** :
   - Personnalisation de `site_header`, `site_title`, et `index_title` dans `config/urls.py`.
   - Surcharge du template `admin/base_site.html` avec identité visuelle TransConnect et bouton direct vers le contrôle d'intégrité.
3. **Manipulation guidée (Section VII)** :
   - Création de la commande de gestion `EntreprisesApp/management/commands/seed_demo.py` initialisant `EXP-26-00001` et `EXP-26-00002`.
   - Vérification de l'effet d'un `Offre.objects.filter(...).update(statut='acceptee')` sur `EXP-26-00001` (désynchronisation : expédition restée `publiee`, véhicule non réservé, autre offre non refusée).
   - Vérification du contre-exemple sur `EXP-26-00002` via l'ORM avec `full_clean() + save()` déclenchant la cascade métier.
4. **Tableau de bord de contrôle d'intégrité (Section VIII)** :
   - Route `/admin/health-check/` enregistrée via surcharge de `get_urls()` sur le site admin.
   - Implémentation des 5 contrôles d'intégrité métier par requêtes ORM optimisées (`annotate`, `aggregate`, `Count`, `filter`, sans boucle Python).

### 2. Réflexion critique sur l'usage de l'IA (Section VIII)
- **Observation sur les requêtes générées par l'IA** :
  Les assistants IA ont une tendance naturelle à proposer des requêtes de mise à jour groupée directes du type `.update()` ou `.bulk_create()` dès qu'il est question de traiter plusieurs objets, guidés par un réflexe de performance SQL.
- **Le piège identifié** :
  Ces opérations SQL directes contournent entièrement les méthodes `clean()` et `save()` des modèles Django. Dans une architecture orientée règles métier (comme la cascade d'acceptation d'offres de TransConnect), ce raccourci engendre silencieusement des incohérences graves en base de données.
- **Enseignement méthodologique** :
  Pour les actions modifiant des données sensibles, il est indispensable de forcer une itération avec `full_clean() + save()`. Réciproquement, pour l'audit et la détection d'anomalies, l'IA doit être contrainte d'utiliser les outils d'agrégation ORM (`annotate`, `Count`) plutôt que de charger des listes d'objets en mémoire dans des boucles Python.
