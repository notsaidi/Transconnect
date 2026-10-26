import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from EntreprisesApp.models import Entreprise, Utilisateur
from ExpeditionsApp.models import Expedition
from OffresApp.models import Offre
from VehiculesApp.models import Vehicule


class Command(BaseCommand):
    help = "Initialise le jeu de données de démonstration pour le workshop Admin (EXP-26-00001 et EXP-26-00002)"

    def handle(self, *args, **options):
        # 1. Nettoyage ciblé des données de démo existantes
        Expedition.objects.filter(reference__in=['EXP-26-00001', 'EXP-26-00002']).delete()
        Entreprise.objects.filter(matricule_fiscal__in=['1234567AAM001', '2345678BAM002', '3456789CAM003']).delete()
        Utilisateur.objects.filter(username__in=['demo_chargeur', 'demo_transp1', 'demo_transp2']).delete()

        # 2. Utilisateurs et Entreprises
        user_ch = Utilisateur.objects.create(
            username='demo_chargeur',
            email='demo_chargeur@gmail.com',
            role='chargeur'
        )
        chargeur = Entreprise.objects.create(
            raison_sociale='Atlas Distribution SARL',
            matricule_fiscal='1234567AAM001',
            adresse='Zone Industrielle Megrine, 2033 Ben Arous',
            type_entreprise='chargeur',
            gerant=user_ch
        )

        user_tr1 = Utilisateur.objects.create(
            username='demo_transp1',
            email='demo_transp1@gmail.com',
            role='transporteur'
        )
        transp1 = Entreprise.objects.create(
            raison_sociale='Express Fret Tunisie',
            matricule_fiscal='2345678BAM002',
            adresse='Route de Gabès Km 4, 3000 Sfax Tunisie',
            type_entreprise='transporteur',
            gerant=user_tr1
        )

        user_tr2 = Utilisateur.objects.create(
            username='demo_transp2',
            email='demo_transp2@gmail.com',
            role='transporteur'
        )
        transp2 = Entreprise.objects.create(
            raison_sociale='Maghreb Trans Rapide',
            matricule_fiscal='3456789CAM003',
            adresse='Avenue Habib Bourguiba, 4000 Sousse Tunisie',
            type_entreprise='transporteur',
            gerant=user_tr2
        )

        # 3. Flotte de véhicules
        v1, _ = Vehicule.objects.get_or_create(
            immatriculation='180-TUN-1234',
            defaults={
                'type_vehicule': Vehicule.TypeVehicule.CAMION_PORTEUR,
                'capacite_kg': 12000,
                'disponible': True,
                'entreprise': transp1
            }
        )
        v2, _ = Vehicule.objects.get_or_create(
            immatriculation='210-TUN-5678',
            defaults={
                'type_vehicule': Vehicule.TypeVehicule.SEMI_REMORQUE,
                'capacite_kg': 25000,
                'disponible': True,
                'entreprise': transp2
            }
        )

        # 4. Expédition 1
        exp1 = Expedition(
            reference='EXP-26-00001',
            entreprise=chargeur,
            ville_depart='Tunis',
            ville_arrivee='Sousse',
            poids_kg=Decimal('3500.00'),
            statut=Expedition.Statut.PUBLIEE,
            date_souhaitee=timezone.now().date() + datetime.timedelta(days=2),
            description='Lots de pièces industrielles conditionnées'
        )
        exp1.full_clean()
        super(Expedition, exp1).save()

        # Offres sur Expédition 1
        Offre.objects.create(
            expedition=exp1,
            transporteur=transp1,
            vehicule=v1,
            prix=Decimal('750.00'),
            delai_jours=2,
            statut=Offre.Statut.PROPOSEE
        )
        Offre.objects.create(
            expedition=exp1,
            transporteur=transp2,
            vehicule=v2,
            prix=Decimal('690.00'),
            delai_jours=1,
            statut=Offre.Statut.PROPOSEE
        )

        # 5. Expédition 2
        exp2 = Expedition(
            reference='EXP-26-00002',
            entreprise=chargeur,
            ville_depart='Sfax',
            ville_arrivee='Bizerte',
            poids_kg=Decimal('5000.00'),
            statut=Expedition.Statut.PUBLIEE,
            date_souhaitee=timezone.now().date() + datetime.timedelta(days=5),
            description='Palettes de composants électroniques'
        )
        exp2.full_clean()
        super(Expedition, exp2).save()

        # Offres sur Expédition 2
        Offre.objects.create(
            expedition=exp2,
            transporteur=transp1,
            vehicule=v1,
            prix=Decimal('1100.00'),
            delai_jours=3,
            statut=Offre.Statut.PROPOSEE
        )
        Offre.objects.create(
            expedition=exp2,
            transporteur=transp2,
            vehicule=v2,
            prix=Decimal('1050.00'),
            delai_jours=2,
            statut=Offre.Statut.PROPOSEE
        )

        self.stdout.write(self.style.SUCCESS("Création de deux expéditions : EXP-26-00001 et EXP-26-00002."))
