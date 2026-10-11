from django.test import TestCase
from django.core.exceptions import ValidationError
from EntreprisesApp.models import Utilisateur, Entreprise
from VehiculesApp.models import Vehicule


class VehiculeModelTests(TestCase):
    def setUp(self):
        self.user_trans = Utilisateur.objects.create(
            username="gerant_trans",
            email="trans@gmail.com",
            role="transporteur"
        )
        self.entreprise_trans = Entreprise.objects.create(
            raison_sociale="Transport Express",
            matricule_fiscal="1234567AAM000",
            adresse="Avenue Habib Bourguiba Tunis Tunisie",
            type_entreprise="transporteur",
            gerant=self.user_trans
        )
        self.user_chg = Utilisateur.objects.create(
            username="gerant_chg",
            email="chg@gmail.com",
            role="chargeur"
        )
        self.entreprise_chg = Entreprise.objects.create(
            raison_sociale="Chargeur SA",
            matricule_fiscal="1234567BAM000",
            adresse="Avenue Habib Bourguiba Tunis Tunisie",
            type_entreprise="chargeur",
            gerant=self.user_chg
        )

    def test_vehicule_creation_succes(self):
        vehicule = Vehicule.objects.create(
            immatriculation="123TN4567",
            capacite_kg=1200,
            type_vehicule=Vehicule.TypeVehicule.CAMIONNETTE,
            entreprise=self.entreprise_trans
        )
        self.assertTrue(vehicule.disponible)
        self.assertEqual(vehicule.capacite_kg, 1200)

    def test_vehicule_entreprise_must_be_transporteur(self):
        vehicule = Vehicule(
            immatriculation="999TN9999",
            capacite_kg=2000,
            type_vehicule=Vehicule.TypeVehicule.FOURGON,
            entreprise=self.entreprise_chg
        )
        with self.assertRaises(ValidationError):
            vehicule.save()

    def test_vehicule_capacite_must_be_positive(self):
        vehicule = Vehicule(
            immatriculation="888TN8888",
            capacite_kg=0,
            type_vehicule=Vehicule.TypeVehicule.FOURGON,
            entreprise=self.entreprise_trans
        )
        with self.assertRaises(ValidationError):
            vehicule.save()
