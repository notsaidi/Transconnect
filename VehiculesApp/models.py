from django.db import models
from django.core.validators import MinValueValidator 

# Create your models here.
# pyrefly: ignore [parse-error]
class Vehicule(models.Model):
    class TypeVehicule(models.TextChoices):
        CAMIONNETTE = 'camionnette', 'Camionnette'
        FOURGON = 'fourgon', 'Fourgon'
        CAMION_PORTEUR = 'camion_porteur', 'Camion porteur'
        SEMI_REMORQUE = 'semi_remorque', 'Semi-remorque'

    immatriculation  = models.CharField(max_length=20 ,unique=True)
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
    disponibilite = models.BooleanField(default=True)
    entreprise = models.ForeignKey ("EntreprisesApp.Entreprise", on_delete=models.CASCADE,related_name="vehicules")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    
