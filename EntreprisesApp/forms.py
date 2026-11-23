from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from EntreprisesApp.models import Entreprise, Utilisateur


class UtilisateurRegistrationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=[
            ('chargeur', 'Chargeur'),
            ('transporteur', 'Transporteur'),
        ],
        label="Rôle"
    )

    class Meta:
        model = Utilisateur
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'telephone',
            'role',
        ]
        help_texts = {
            'email': "L'adresse email doit obligatoirement se terminer par @gmail.com",
        }

    def clean(self):
        """
        Validation stricte par ordre de priorité champ par champ :
        1. username
        2. email (@gmail.com et unicité)
        3. first_name
        4. last_name
        5. telephone
        6. role
        7. password1 & password2 (conformité & correspondance)
        """
        cleaned_data = super().clean()

        # Priorité 1 : Nom d'utilisateur
        username = cleaned_data.get('username')
        if not username:
            raise ValidationError({'username': "Le nom d'utilisateur est obligatoire."})

        # Priorité 2 : Email (@gmail.com et unicité)
        email = cleaned_data.get('email')
        if not email:
            raise ValidationError({'email': "L'adresse email est obligatoire."})
        if not email.endswith('@gmail.com'):
            raise ValidationError({'email': "Seuls les emails appartenant au domaine gmail.com sont acceptés."})
        if Utilisateur.objects.filter(email__iexact=email).exists():
            raise ValidationError({'email': "Cette adresse email est déjà associée à un compte."})

        # Priorité 3 : Prénom
        first_name = cleaned_data.get('first_name')
        if not first_name:
            raise ValidationError({'first_name': "Le prénom est obligatoire."})

        # Priorité 4 : Nom de famille
        last_name = cleaned_data.get('last_name')
        if not last_name:
            raise ValidationError({'last_name': "Le nom de famille est obligatoire."})

        # Priorité 5 : Numéro de téléphone
        telephone = cleaned_data.get('telephone')
        if telephone:
            if not telephone.isdigit() or len(telephone) < 8:
                raise ValidationError({'telephone': "Le numéro de téléphone doit contenir au moins 8 chiffres."})

        # Priorité 6 : Rôle
        role = cleaned_data.get('role')
        if not role:
            raise ValidationError({'role': "Le choix du rôle est obligatoire."})
        if role not in ['chargeur', 'transporteur']:
            raise ValidationError({'role': "Rôle invalide. Choisissez 'chargeur' ou 'transporteur'."})

        # Priorité 7 : Mots de passe
        pass1 = cleaned_data.get('password1')
        pass2 = cleaned_data.get('password2')
        if pass1 and pass2 and pass1 != pass2:
            raise ValidationError({'password2': "Les deux mots de passe ne correspondent pas."})

        return cleaned_data


class UtilisateurProfileForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=[
            ('chargeur', 'Chargeur'),
            ('transporteur', 'Transporteur'),
        ],
        label="Rôle"
    )

    class Meta:
        model = Utilisateur
        fields = [
            'first_name',
            'last_name',
            'email',
            'telephone',
            'role',
        ]
        help_texts = {
            'email': "L'adresse email doit obligatoirement se terminer par @gmail.com",
        }

    def clean(self):
        """
        Validation stricte ordonnée champ par champ pour la mise à jour du profil :
        1. email
        2. first_name
        3. last_name
        4. telephone
        5. role
        """
        cleaned_data = super().clean()

        # Priorité 1 : Email
        email = cleaned_data.get('email')
        if not email:
            raise ValidationError({'email': "L'adresse email est obligatoire."})
        if not email.endswith('@gmail.com'):
            raise ValidationError({'email': "Seuls les emails appartenant au domaine gmail.com sont acceptés."})
        if self.instance and self.instance.pk:
            if Utilisateur.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
                raise ValidationError({'email': "Cette adresse email est déjà utilisée par un autre compte."})

        # Priorité 2 : Prénom
        first_name = cleaned_data.get('first_name')
        if not first_name:
            raise ValidationError({'first_name': "Le prénom est obligatoire."})

        # Priorité 3 : Nom de famille
        last_name = cleaned_data.get('last_name')
        if not last_name:
            raise ValidationError({'last_name': "Le nom de famille est obligatoire."})

        # Priorité 4 : Numéro de téléphone
        telephone = cleaned_data.get('telephone')
        if telephone:
            if not telephone.isdigit() or len(telephone) < 8:
                raise ValidationError({'telephone': "Le numéro de téléphone doit contenir au moins 8 chiffres."})

        # Priorité 5 : Rôle
        role = cleaned_data.get('role')
        if not role:
            raise ValidationError({'role': "Le choix du rôle est obligatoire."})
        if role not in ['chargeur', 'transporteur']:
            raise ValidationError({'role': "Rôle invalide. Choisissez 'chargeur' ou 'transporteur'."})

        return cleaned_data


class EntrepriseForm(forms.ModelForm):
    class Meta:
        model = Entreprise
        fields = [
            'raison_sociale',
            'matricule_fiscal',
            'adresse',
            'type_entreprise',
            'gerant',
        ]
