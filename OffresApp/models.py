from django.db import models

# Create your models here.
# pyrefly: ignore [parse-error]
class Offre(models.Model):
    class Statut(models.TextChoices):
        PROPOSEE = 'proposee', 'Proposée'
        ACCEPTEE = 'acceptee', 'Acceptée'
        REFUSEE = 'refusee', 'Refusée'
        RETIREE = 'retiree', 'Retirée'

    prix = models.DecimalField(max_digits=10, decimal_places=2)
    delai_jours = models.PositiveIntegerField()
    date_proposition = models.DateField(auto_now_add=True)
    statut = models.CharField(max_length=10, choices=Statut.choices, default=Statut.PROPOSEE)
    expedition = models.ForeignKey("ExpeditionsApp.Expedition", on_delete=models.CASCADE, related_name="offres")
    vehicule = models.ForeignKey("VehiculesApp.Vehicule", on_delete=models.CASCADE, related_name="offres")
    transporteur = models.ForeignKey("EntreprisesApp.Entreprise", on_delete=models.CASCADE, related_name="offres")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)