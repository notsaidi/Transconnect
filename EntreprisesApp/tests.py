from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from EntreprisesApp.models import Utilisateur, Entreprise


class UtilisateurModelTests(TestCase):
    def test_user_id_generation_format(self):
        user1 = Utilisateur.objects.create(
            username="user1",
            email="user1@gmail.com",
            role="chargeur"
        )
        current_year = timezone.now().strftime('%y')
        self.assertEqual(user1.user_id, f"{current_year}user00")

        user2 = Utilisateur.objects.create(
            username="user2",
            email="user2@gmail.com",
            role="transporteur"
        )
        self.assertEqual(user2.user_id, f"{current_year}user01")

    def test_email_must_be_gmail(self):
        user = Utilisateur(
            username="invalid_email_user",
            email="user@yahoo.com",
            role="chargeur"
        )
        with self.assertRaises(ValidationError):
            user.save()


class EntrepriseModelTests(TestCase):
    def setUp(self):
        self.user = Utilisateur.objects.create(
            username="gerant1",
            email="gerant1@gmail.com",
            role="chargeur"
        )

    def test_matricule_fiscal_valid(self):
        ent = Entreprise(
            raison_sociale="Societe Logistique",
            matricule_fiscal="1234567AAM000",
            adresse="123 Avenue Habib Bourguiba Tunis Tunisie",
            type_entreprise="chargeur",
            gerant=self.user
        )
        ent.save()
        self.assertIsNotNone(ent.pk)

    def test_matricule_fiscal_invalid(self):
        ent = Entreprise(
            raison_sociale="Societe Invalide",
            matricule_fiscal="1234INVALID",
            adresse="123 Avenue Habib Bourguiba Tunis Tunisie",
            type_entreprise="chargeur",
            gerant=self.user
        )
        with self.assertRaises(ValidationError):
            ent.save()

    def test_adresse_minimum_length(self):
        ent = Entreprise(
            raison_sociale="Societe Adresse Courte",
            matricule_fiscal="1234567BAM000",
            adresse="Trop court",
            type_entreprise="chargeur",
            gerant=self.user
        )
        with self.assertRaises(ValidationError):
            ent.save()
