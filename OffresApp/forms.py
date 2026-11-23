from django import forms
from OffresApp.models import Offre


class OffreForm(forms.ModelForm):
    class Meta:
        model = Offre
        fields = [
            'prix',
            'delai_jours',
            'statut',
            'expedition',
            'vehicule',
            'transporteur',
        ]
