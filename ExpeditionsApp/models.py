from django.db import models

# Create your models here.
# pyrefly: ignore [parse-error]
class Expedition(models.Model):
    class Statut(models.TextChoices):
        PUBLIEE = 'publiee', 'Publiée'
        ATTRIBUEE = 'attribuee', 'Attribuée'
        EN_COURS = 'en_cours', 'En cours'
        LIVREE = 'livree', 'Livrée'
        ANNULEE = 'annulee', 'Annulée'

    reference = models.CharField(max_length=20, unique=True)
    poids_kg = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=10, choices=Statut.choices, default=Statut.PUBLIEE)
    entreprise = models.ForeignKey("EntreprisesApp.Entreprise", on_delete=models.CASCADE, related_name="Expeditions")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
