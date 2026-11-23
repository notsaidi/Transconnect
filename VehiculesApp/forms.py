from django import forms
from VehiculesApp.models import Vehicule


class VehiculeForm(forms.ModelForm):
    class Meta:
        model = Vehicule
        fields = [
            'immatriculation',
            'capacite_kg',
            'type_vehicule',
            'disponible',
            'entreprise',
        ]
