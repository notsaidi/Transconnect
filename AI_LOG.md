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

## Entrée [2026-10-04] — Modélisation et Résolution des Dépendances

- **Outil IA utilisé** : Assistant IA
- **Prompt** : 
  > "Valider et corriger les relations ForeignKey et la syntaxe entre les applications EntreprisesApp, VehiculesApp, ExpeditionsApp et OffresApp."

- **Sortie obtenue (résumé)** :
  > Détection et correction des erreurs d'indentation dans les `TextChoices`, correction des chaînes ForeignKey pour pointer vers les bonnes applications (`ExpeditionsApp.Expedition`, `VehiculesApp.Vehicule`, `EntreprisesApp.Entreprise`), et ajout des arguments `max_digits` et `decimal_places` sur les `DecimalField`.

- **Écarts identifiés vs cahier des charges** :
  - Mauvaise cible de ForeignKey (`EntreprisesApp.Expedition` au lieu de `ExpeditionsApp.Expedition`).
  - Indentation non alignée dans les classes d'énumération `Statut`.

- **Correction apportée et justification** :
  - Référencement explicite au format `"<NomApplication>.<NomModele>"` pour découpler et fiabiliser les relations inter-applications.
  - Normalisation de l'indentation à 4 espaces pour respecter les standards PEP 8 et la syntaxe Python.
