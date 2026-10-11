from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator


class Vehicule(models.Model):
    class TypeVehicule(models.TextChoices):
        CAMIONNETTE = 'camionnette', 'Camionnette'
        FOURGON = 'fourgon', 'Fourgon'
        CAMION_PORTEUR = 'camion_porteur', 'Camion porteur'
        SEMI_REMORQUE = 'semi_remorque', 'Semi-remorque'

    immatriculation = models.CharField(max_length=20, unique=True)
    capacite_kg = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1, message="La capacité doit être une valeur supérieure à 0.")
        ]
    )
    type_vehicule = models.CharField(
        max_length=20,
        choices=TypeVehicule.choices,
        default=TypeVehicule.CAMIONNETTE
    )
    disponible = models.BooleanField(default=True)
    entreprise = models.ForeignKey(
        "EntreprisesApp.Entreprise",
        on_delete=models.CASCADE,
        related_name="vehicules"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if self.capacite_kg is not None and self.capacite_kg <= 0:
            raise ValidationError({'capacite_kg': "La capacité doit être strictement supérieure à 0."})
        if self.entreprise_id and self.entreprise.type_entreprise != 'transporteur':
            raise ValidationError({'entreprise': "L'entreprise associée au véhicule doit être de type transporteur."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.immatriculation} - {self.get_type_vehicule_display()} ({self.entreprise.raison_sociale})"
