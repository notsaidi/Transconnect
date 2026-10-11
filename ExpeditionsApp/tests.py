from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from EntreprisesApp.models import Utilisateur, Entreprise
from ExpeditionsApp.models import Expedition


class ExpeditionModelTests(TestCase):
    def setUp(self):
        self.user_chg = Utilisateur.objects.create(
            username="gerant_chg",
            email="chargeur@gmail.com",
            role="chargeur"
        )
        self.entreprise_chg = Entreprise.objects.create(
            raison_sociale="Chargeur SA",
            matricule_fiscal="1234567AAM000",
            adresse="Avenue Habib Bourguiba Tunis Tunisie",
            type_entreprise="chargeur",
            gerant=self.user_chg
        )
        self.user_trans = Utilisateur.objects.create(
            username="gerant_trans",
            email="trans@gmail.com",
            role="transporteur"
        )
        self.entreprise_trans = Entreprise.objects.create(
            raison_sociale="Transporteur SA",
            matricule_fiscal="1234567BAM000",
            adresse="Avenue Habib Bourguiba Tunis Tunisie",
            type_entreprise="transporteur",
            gerant=self.user_trans
        )

    def test_expedition_reference_generation(self):
        exp1 = Expedition.objects.create(
            ville_depart="Tunis",
            ville_arrivee="Sousse",
            poids_kg=Decimal('500.00'),
            entreprise=self.entreprise_chg
        )
        year_code = timezone.now().strftime('%y')
        self.assertEqual(exp1.reference, f"EXP-{year_code}-00001")

        exp2 = Expedition.objects.create(
            ville_depart="Sfax",
            ville_arrivee="Gabes",
            poids_kg=Decimal('1000.00'),
            entreprise=self.entreprise_chg
        )
        self.assertEqual(exp2.reference, f"EXP-{year_code}-00002")

    def test_expedition_entreprise_must_be_chargeur(self):
        exp = Expedition(
            ville_depart="Tunis",
            ville_arrivee="Bizerte",
            poids_kg=Decimal('500.00'),
            entreprise=self.entreprise_trans
        )
        with self.assertRaises(ValidationError):
            exp.save()

    def test_expedition_poids_must_be_positive(self):
        exp = Expedition(
            ville_depart="Tunis",
            ville_arrivee="Nabeul",
            poids_kg=Decimal('0.00'),
            entreprise=self.entreprise_chg
        )
        with self.assertRaises(ValidationError):
            exp.save()
