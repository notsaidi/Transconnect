from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
# Create your models here.

class Expedition(models.Model):
    class Statut(models.TextChoices):
        PUBLIEE = 'publiee', 'Publiée'
        ATTRIBUEE = 'attribuee', 'Attribuée'
        EN_COURS = 'en_cours', 'En cours'
        LIVREE = 'livree', 'Livrée'
        ANNULEE = 'annulee', 'Annulée'

    reference = models.CharField(max_length=20, unique=True)
    ville_depart = models.CharField(max_length=100)
    ville_arrivee = models.CharField(max_length=100)
    date_souhaitee = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    poids_kg = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=10, choices=Statut.choices, default=Statut.PUBLIEE)
    entreprise = models.ForeignKey(
        'EntreprisesApp.Entreprise',
        on_delete=models.CASCADE,
        related_name='expeditions'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if self.entreprise_id and self.entreprise.type_entreprise != 'chargeur':
            raise ValidationError("L'entreprise doit être de type chargeur")
    
    @classmethod
    def _generate_reference(cls):
        annee = timezone.now().strftime('%Y')

        dernier = cls.objects.filter(reference__startswith=f"EXP_{annee}_").order_by('-reference').first()


        compteur = int(dernier.reference[-5:]) + 1 if dernier else 1

        if compteur > 99999:
            raise ValidationError("Limite dépassée")

        return f"EXP_{annee}_{compteur:05d}"

        
        

    
