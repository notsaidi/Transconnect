from decimal import Decimal
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from ExpeditionsApp.models import Expedition
from VehiculesApp.models import Vehicule


class Offre(models.Model):
    class Statut(models.TextChoices):
        PROPOSEE = 'proposee', 'Proposée'
        ACCEPTEE = 'acceptee', 'Acceptée'
        REFUSEE = 'refusee', 'Refusée'
        RETIREE = 'retiree', 'Retirée'

    prix = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0.01'), message="Le prix doit être strictement supérieur à 0.")
        ]
    )
    delai_jours = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1, message="Le délai doit être supérieur ou égal à 1 jour.")
        ]
    )
    date_proposition = models.DateField(auto_now_add=True)
    statut = models.CharField(
        max_length=10,
        choices=Statut.choices,
        default=Statut.PROPOSEE
    )
    expedition = models.ForeignKey(
        "ExpeditionsApp.Expedition",
        on_delete=models.CASCADE,
        related_name="offres"
    )
    vehicule = models.ForeignKey(
        "VehiculesApp.Vehicule",
        on_delete=models.CASCADE,
        related_name="offres"
    )
    transporteur = models.ForeignKey(
        "EntreprisesApp.Entreprise",
        on_delete=models.CASCADE,
        related_name="offres"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()

        # Règle 1 : Une offre ne peut être créée que par une entreprise dont type_entreprise = transporteur
        if self.transporteur_id and self.transporteur.type_entreprise != 'transporteur':
            raise ValidationError({
                'transporteur': "Une offre ne peut être créée que par une entreprise dont le type est transporteur."
            })

        # Règle 2 : Le véhicule associé à une offre doit appartenir à la même entreprise que le transporteur de l'offre
        if self.vehicule_id and self.transporteur_id:
            if self.vehicule.entreprise_id != self.transporteur_id:
                raise ValidationError({
                    'vehicule': "Le véhicule associé à une offre doit appartenir au transporteur qui propose l'offre."
                })

        # Règle 3 : Une expédition ne peut recevoir de nouvelles offres que si son statut est 'publiee'
        is_new = self._state.adding or not self.pk
        if is_new and self.expedition_id:
            if self.expedition.statut != Expedition.Statut.PUBLIEE:
                raise ValidationError({
                    'expedition': "Une expédition ne peut recevoir de nouvelles offres que si son statut est 'publiee'."
                })

        # Règle 4 : Une entreprise ne peut pas avoir deux offres au statut proposee actives simultanément sur la même expédition
        if self.transporteur_id and self.expedition_id and self.statut == self.Statut.PROPOSEE:
            qs = Offre.objects.filter(
                expedition=self.expedition,
                transporteur=self.transporteur,
                statut=self.Statut.PROPOSEE
            )
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError(
                    "Une entreprise ne peut pas avoir deux offres au statut 'proposée' actives simultanément sur la même expédition."
                )

        # Règle 6 : Un véhicule dont disponible = False ne peut pas être proposé sur une nouvelle offre
        if is_new and self.vehicule_id:
            if not self.vehicule.disponible:
                raise ValidationError({
                    'vehicule': "Un véhicule indisponible (disponible = False) ne peut pas être proposé sur une nouvelle offre."
                })

        # Règle 7 : L'attribut type_vehicule conditionne la compatibilité avec le poids d'une expédition
        if self.vehicule_id and self.expedition_id and self.expedition.poids_kg is not None:
            poids = Decimal(str(self.expedition.poids_kg))
            limites_poids = {
                Vehicule.TypeVehicule.CAMIONNETTE: Decimal('1500'),
                Vehicule.TypeVehicule.FOURGON: Decimal('3500'),
                Vehicule.TypeVehicule.CAMION_PORTEUR: Decimal('19000'),
                Vehicule.TypeVehicule.SEMI_REMORQUE: Decimal('26000'),
            }
            limite_max = limites_poids.get(self.vehicule.type_vehicule)
            if limite_max is not None and poids > limite_max:
                raise ValidationError({
                    'vehicule': (
                        f"Le type de véhicule '{self.vehicule.get_type_vehicule_display()}' "
                        f"ne peut pas transporter une expédition de {poids} kg "
                        f"(capacité indicative maximale : {limite_max} kg)."
                    )
                })
            if self.vehicule.capacite_kg and poids > Decimal(str(self.vehicule.capacite_kg)):
                raise ValidationError({
                    'vehicule': (
                        f"Le poids de l'expédition ({poids} kg) dépasse la capacité maximale "
                        f"du véhicule ({self.vehicule.capacite_kg} kg)."
                    )
                })

    def save(self, *args, **kwargs):
        self.full_clean()

        # Règle 5 : Cascade à l'acceptation
        is_becoming_accepted = False
        if self.statut == self.Statut.ACCEPTEE:
            if not self.pk:
                is_becoming_accepted = True
            else:
                old_statut = Offre.objects.filter(pk=self.pk).values_list('statut', flat=True).first()
                if old_statut != self.Statut.ACCEPTEE:
                    is_becoming_accepted = True

        with transaction.atomic():
            super().save(*args, **kwargs)

            if is_becoming_accepted:
                # 1. L'expédition associée passe automatiquement à « attribuee »
                if self.expedition.statut != Expedition.Statut.ATTRIBUEE:
                    self.expedition.statut = Expedition.Statut.ATTRIBUEE
                    self.expedition.save(update_fields=['statut', 'updated_at'])

                # 2. Toutes les autres offres « proposee » sur cette même expédition passent à « refusee »
                Offre.objects.filter(
                    expedition=self.expedition,
                    statut=self.Statut.PROPOSEE
                ).exclude(pk=self.pk).update(statut=self.Statut.REFUSEE)

    def __str__(self):
        return f"Offre #{self.id} - {self.prix} TND sur {self.expedition.reference} ({self.get_statut_display()})"