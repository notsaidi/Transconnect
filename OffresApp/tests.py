from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from EntreprisesApp.models import Utilisateur, Entreprise
from VehiculesApp.models import Vehicule
from ExpeditionsApp.models import Expedition
from OffresApp.models import Offre


class OffreModelTests(TestCase):
    def setUp(self):
        # Chargeur
        self.user_chg = Utilisateur.objects.create(
            username="gerant_chg",
            email="chg@gmail.com",
            role="chargeur"
        )
        self.entreprise_chg = Entreprise.objects.create(
            raison_sociale="Chargeur SA",
            matricule_fiscal="1234567AAM000",
            adresse="Avenue Habib Bourguiba Tunis Tunisie",
            type_entreprise="chargeur",
            gerant=self.user_chg
        )

        # Transporteur 1
        self.user_trans1 = Utilisateur.objects.create(
            username="gerant_trans1",
            email="trans1@gmail.com",
            role="transporteur"
        )
        self.entreprise_trans1 = Entreprise.objects.create(
            raison_sociale="TransLog 1",
            matricule_fiscal="1234567BAM000",
            adresse="Avenue Habib Bourguiba Tunis Tunisie",
            type_entreprise="transporteur",
            gerant=self.user_trans1
        )

        # Transporteur 2
        self.user_trans2 = Utilisateur.objects.create(
            username="gerant_trans2",
            email="trans2@gmail.com",
            role="transporteur"
        )
        self.entreprise_trans2 = Entreprise.objects.create(
            raison_sociale="TransLog 2",
            matricule_fiscal="1234567CAM000",
            adresse="Avenue Habib Bourguiba Tunis Tunisie",
            type_entreprise="transporteur",
            gerant=self.user_trans2
        )

        # Vehicules
        self.vehicule_t1 = Vehicule.objects.create(
            immatriculation="100TN1000",
            capacite_kg=1200,
            type_vehicule=Vehicule.TypeVehicule.CAMIONNETTE,
            disponible=True,
            entreprise=self.entreprise_trans1
        )
        self.vehicule_t2 = Vehicule.objects.create(
            immatriculation="200TN2000",
            capacite_kg=3000,
            type_vehicule=Vehicule.TypeVehicule.FOURGON,
            disponible=True,
            entreprise=self.entreprise_trans2
        )

        # Expedition
        self.expedition = Expedition.objects.create(
            ville_depart="Tunis",
            ville_arrivee="Sousse",
            poids_kg=Decimal('1000.00'),
            statut=Expedition.Statut.PUBLIEE,
            entreprise=self.entreprise_chg
        )

    def test_regle_1_offre_creee_uniquement_par_transporteur(self):
        offre = Offre(
            prix=Decimal('500.00'),
            delai_jours=2,
            expedition=self.expedition,
            vehicule=self.vehicule_t1,
            transporteur=self.entreprise_chg  # Erreur : chargeur au lieu de transporteur
        )
        with self.assertRaises(ValidationError):
            offre.save()

    def test_regle_2_vehicule_doit_appartenir_au_transporteur(self):
        offre = Offre(
            prix=Decimal('500.00'),
            delai_jours=2,
            expedition=self.expedition,
            vehicule=self.vehicule_t2,  # Appartient au transporteur 2
            transporteur=self.entreprise_trans1  # Offre faite par transporteur 1
        )
        with self.assertRaises(ValidationError):
            offre.save()

    def test_regle_3_expedition_doit_etre_publiee(self):
        self.expedition.statut = Expedition.Statut.ANNULEE
        self.expedition.save()

        offre = Offre(
            prix=Decimal('500.00'),
            delai_jours=2,
            expedition=self.expedition,
            vehicule=self.vehicule_t1,
            transporteur=self.entreprise_trans1
        )
        with self.assertRaises(ValidationError):
            offre.save()

    def test_regle_4_pas_deux_offres_proposees_actives_pour_meme_transporteur(self):
        # 1ère offre
        Offre.objects.create(
            prix=Decimal('500.00'),
            delai_jours=2,
            expedition=self.expedition,
            vehicule=self.vehicule_t1,
            transporteur=self.entreprise_trans1,
            statut=Offre.Statut.PROPOSEE
        )

        # 2ème offre par le même transporteur sur la même expédition
        offre2 = Offre(
            prix=Decimal('450.00'),
            delai_jours=1,
            expedition=self.expedition,
            vehicule=self.vehicule_t1,
            transporteur=self.entreprise_trans1,
            statut=Offre.Statut.PROPOSEE
        )
        with self.assertRaises(ValidationError):
            offre2.save()

    def test_regle_5_cascade_a_l_acceptation(self):
        offre1 = Offre.objects.create(
            prix=Decimal('500.00'),
            delai_jours=2,
            expedition=self.expedition,
            vehicule=self.vehicule_t1,
            transporteur=self.entreprise_trans1,
            statut=Offre.Statut.PROPOSEE
        )
        offre2 = Offre.objects.create(
            prix=Decimal('600.00'),
            delai_jours=3,
            expedition=self.expedition,
            vehicule=self.vehicule_t2,
            transporteur=self.entreprise_trans2,
            statut=Offre.Statut.PROPOSEE
        )

        # Accepter offre1
        offre1.statut = Offre.Statut.ACCEPTEE
        offre1.save()

        # Recharger depuis la base
        self.expedition.refresh_from_db()
        offre2.refresh_from_db()

        self.assertEqual(self.expedition.statut, Expedition.Statut.ATTRIBUEE)
        self.assertEqual(offre2.statut, Offre.Statut.REFUSEE)

    def test_regle_6_vehicule_indisponible_non_proposable(self):
        self.vehicule_t1.disponible = False
        self.vehicule_t1.save()

        offre = Offre(
            prix=Decimal('500.00'),
            delai_jours=2,
            expedition=self.expedition,
            vehicule=self.vehicule_t1,
            transporteur=self.entreprise_trans1
        )
        with self.assertRaises(ValidationError):
            offre.save()

    def test_regle_7_compatibilite_type_vehicule_et_poids(self):
        # Expedition lourde de 2000 kg (> 1500 kg pour camionnette)
        exp_lourde = Expedition.objects.create(
            ville_depart="Tunis",
            ville_arrivee="Sfax",
            poids_kg=Decimal('2000.00'),
            statut=Expedition.Statut.PUBLIEE,
            entreprise=self.entreprise_chg
        )
        # Camionnette ne peut pas prendre 2000 kg
        offre_incompatible = Offre(
            prix=Decimal('700.00'),
            delai_jours=2,
            expedition=exp_lourde,
            vehicule=self.vehicule_t1,  # camionnette (max 1500 kg)
            transporteur=self.entreprise_trans1
        )
        with self.assertRaises(ValidationError):
            offre_incompatible.save()

        # Mais le fourgon de trans2 (max 3500 kg, capa 3000 kg) peut le prendre
        offre_compatible = Offre.objects.create(
            prix=Decimal('700.00'),
            delai_jours=2,
            expedition=exp_lourde,
            vehicule=self.vehicule_t2,
            transporteur=self.entreprise_trans2
        )
        self.assertIsNotNone(offre_compatible.pk)

    def test_prix_et_delai_validateurs(self):
        # Prix nul
        offre_prix_nul = Offre(
            prix=Decimal('0.00'),
            delai_jours=2,
            expedition=self.expedition,
            vehicule=self.vehicule_t1,
            transporteur=self.entreprise_trans1
        )
        with self.assertRaises(ValidationError):
            offre_prix_nul.save()

        # Delai 0
        offre_delai_nul = Offre(
            prix=Decimal('100.00'),
            delai_jours=0,
            expedition=self.expedition,
            vehicule=self.vehicule_t1,
            transporteur=self.entreprise_trans1
        )
        with self.assertRaises(ValidationError):
            offre_delai_nul.save()
