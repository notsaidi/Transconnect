from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils import timezone


class Expedition(models.Model):
    class Statut(models.TextChoices):
        PUBLIEE = 'publiee', 'Publiée'
        ATTRIBUEE = 'attribuee', 'Attribuée'
        EN_COURS = 'en_cours', 'En cours'
        LIVREE = 'livree', 'Livrée'
        ANNULEE = 'annulee', 'Annulée'

    reference = models.CharField(max_length=20, unique=True, blank=True)
    ville_depart = models.CharField(max_length=100, default='')
    ville_arrivee = models.CharField(max_length=100, default='')
    date_souhaitee = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True, default='')
    poids_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0.01'), message="Le poids doit être strictement supérieur à 0.")
        ]
    )
    statut = models.CharField(
        max_length=10,
        choices=Statut.choices,
        default=Statut.PUBLIEE
    )
    entreprise = models.ForeignKey(
        'EntreprisesApp.Entreprise',
        on_delete=models.CASCADE,
        related_name='expeditions'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def _generate_reference(cls):
        annee = timezone.now().strftime('%y')
        prefix = f"EXP-{annee}-"
        dernier = cls.objects.filter(reference__startswith=prefix).order_by('-reference').first()
        if dernier:
            try:
                compteur = int(dernier.reference.split('-')[-1]) + 1
            except (ValueError, IndexError):
                compteur = 1
        else:
            compteur = 1

        if compteur > 99999:
            raise ValidationError("Limite séquentielle annuelle d'expéditions atteinte (99999).")

        return f"{prefix}{compteur:05d}"

    def clean(self):
        super().clean()
        if not self.ville_depart:
            raise ValidationError({'ville_depart': "La ville de départ est obligatoire."})
        if not self.ville_arrivee:
            raise ValidationError({'ville_arrivee': "La ville d'arrivée est obligatoire."})
        if self.poids_kg is not None and self.poids_kg <= Decimal('0'):
            raise ValidationError({'poids_kg': "Le poids doit être strictement supérieur à 0."})
        if self.entreprise_id and self.entreprise.type_entreprise != 'chargeur':
            raise ValidationError({'entreprise': "L'entreprise associée à l'expédition doit être de type chargeur."})

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self._generate_reference()
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference} ({self.ville_depart} -> {self.ville_arrivee})"
