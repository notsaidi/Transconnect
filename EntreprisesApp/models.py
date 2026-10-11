from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from django.utils import timezone


def validate_email(value):
    if not value:
        raise ValidationError("L'adresse email est obligatoire.")
    if not value.endswith('@gmail.com'):
        raise ValidationError("Seuls les emails appartenant au domaine gmail.com sont acceptés.")


matricule_fiscal_validator = RegexValidator(
    regex=(
        r'^\d{7}[/ -]?[A-Za-z][/ -]?'
        r'[ABDNPEabdnpe][/ -]?[MPCNEmpcne][/ -]?\d{3}'
        r'$'
    ),
    message="Format du matricule fiscal non conforme."
)


class Utilisateur(AbstractUser):
    user_id = models.CharField(max_length=8, primary_key=True, editable=False, blank=True)
    email = models.EmailField(unique=True, validators=[validate_email])
    telephone = models.CharField(max_length=15, null=True, blank=True)
    role = models.CharField(
        max_length=20,
        choices=[
            ('chargeur', 'Chargeur'),
            ('transporteur', 'Transporteur'),
            ('administrateur', 'Administrateur')
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def _generate_user_id(cls):
        annee = timezone.now().strftime('%y')
        prefix = f"{annee}user"
        dernier = cls.objects.filter(user_id__startswith=prefix).order_by('-user_id').first()
        if dernier:
            try:
                compteur = int(dernier.user_id[6:]) + 1
            except (ValueError, IndexError):
                compteur = 0
        else:
            compteur = 0

        if compteur > 99:
            raise ValidationError("Le nombre maximal d'utilisateurs pour cette année (99) est atteint.")

        return f"{prefix}{compteur:02d}"

    def clean(self):
        super().clean()
        validate_email(self.email)

    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user_id = self._generate_user_id()
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.user_id})"


class Entreprise(models.Model):
    raison_sociale = models.CharField(max_length=200)
    matricule_fiscal = models.CharField(
        max_length=17,
        unique=True,
        validators=[matricule_fiscal_validator]
    )
    adresse = models.TextField(
        validators=[
            MinLengthValidator(20, message="L'adresse doit contenir au moins 20 caractères.")
        ]
    )
    type_entreprise = models.CharField(
        max_length=100,
        choices=[
            ('chargeur', 'Chargeur'),
            ('transporteur', 'Transporteur'),
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    gerant = models.OneToOneField(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='entreprise'
    )

    def clean(self):
        super().clean()
        matricule_fiscal_validator(self.matricule_fiscal)
        if self.adresse and len(self.adresse.strip()) < 20:
            raise ValidationError({'adresse': "L'adresse doit contenir au moins 20 caractères."})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.raison_sociale