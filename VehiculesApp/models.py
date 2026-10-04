from django.db import models

# Create your models here.
# pyrefly: ignore [parse-error]
class Vehicule(models.Model):
    immatriculation  = models.CharField(max_length=20 ,unique=True)
    capacite_kg  = models.PositiveIntegerField()
    entreprise = models.ForeignKey ("EntreprisesApp.Entreprise", on_delete=models.CASCADE,related_name="vehicules")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    
