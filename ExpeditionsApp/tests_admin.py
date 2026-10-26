import csv
import io
from decimal import Decimal
from django.contrib.admin.sites import AdminSite
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone
import datetime

from EntreprisesApp.models import Entreprise, Utilisateur
from EntreprisesApp.admin import EntrepriseAdmin, VehiculeInline
from VehiculesApp.models import Vehicule
from VehiculesApp.admin import VehiculeAdmin
from ExpeditionsApp.models import Expedition
from ExpeditionsApp.admin import ExpeditionAdmin, EnRetardFilter, cloturer_expeditions
from OffresApp.models import Offre
from OffresApp.admin import OffreAdmin, exporter_offres_csv


class MockSuperUser:
    def __init__(self):
        self.is_active = True
        self.is_staff = True
        self.is_superuser = True

    def has_perm(self, perm):
        return True


class AdminFeaturesTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.site = AdminSite()

        # Admin user
        self.admin_user = Utilisateur.objects.create_superuser(
            username='admin_test',
            email='admin@gmail.com',
            password='AdminPassword123!',
            role='administrateur'
        )

        # Chargeur
        self.user_chg = Utilisateur.objects.create(
            username='chg_test',
            email='chg_test@gmail.com',
            role='chargeur'
        )
        self.entreprise_chg = Entreprise.objects.create(
            raison_sociale='Atlas Fret SA',
            matricule_fiscal='1234567AAM001',
            adresse='123 Avenue Habib Bourguiba Tunis Tunisie',
            type_entreprise='chargeur',
            gerant=self.user_chg
        )

        # Transporteur
        self.user_trans = Utilisateur.objects.create(
            username='trans_test',
            email='trans_test@gmail.com',
            role='transporteur'
        )
        self.entreprise_trans = Entreprise.objects.create(
            raison_sociale='Maghreb Transports',
            matricule_fiscal='2345678BAM002',
            adresse='Route de Gabes km 3, Sfax Tunisie',
            type_entreprise='transporteur',
            gerant=self.user_trans
        )

        # Vehicule
        self.vehicule = Vehicule.objects.create(
            immatriculation='123-TUN-456',
            type_vehicule=Vehicule.TypeVehicule.CAMION_PORTEUR,
            capacite_kg=12000,
            disponible=True,
            entreprise=self.entreprise_trans
        )

        # Expeditions
        self.exp_en_cours = Expedition.objects.create(
            ville_depart='Tunis',
            ville_arrivee='Sousse',
            poids_kg=Decimal('2000.00'),
            statut=Expedition.Statut.EN_COURS,
            date_souhaitee=timezone.now().date() + datetime.timedelta(days=2),
            entreprise=self.entreprise_chg
        )
        self.exp_publiee = Expedition.objects.create(
            ville_depart='Sfax',
            ville_arrivee='Bizerte',
            poids_kg=Decimal('3000.00'),
            statut=Expedition.Statut.PUBLIEE,
            date_souhaitee=timezone.now().date() - datetime.timedelta(days=2),  # en retard
            entreprise=self.entreprise_chg
        )

        # Offres
        self.offre_prop = Offre.objects.create(
            expedition=self.exp_publiee,
            transporteur=self.entreprise_trans,
            vehicule=self.vehicule,
            prix=Decimal('450.00'),
            delai_jours=2,
            statut=Offre.Statut.PROPOSEE
        )

    def test_entreprise_admin_inlines_and_search(self):
        ea = EntrepriseAdmin(Entreprise, self.site)
        self.assertIn(VehiculeInline, ea.inlines)
        self.assertIn('raison_sociale', ea.search_fields)
        self.assertIn('matricule_fiscal', ea.search_fields)

    def test_vehicule_admin_list_editable_and_search(self):
        va = VehiculeAdmin(Vehicule, self.site)
        self.assertEqual(va.list_editable, ('disponible',))
        self.assertIn('immatriculation', va.search_fields)

    def test_action_cloturer_expeditions(self):
        ea = ExpeditionAdmin(Expedition, self.site)
        request = self.factory.get('/admin/expedition/')
        request.user = self.admin_user
        # Attacher le support des messages Django
        setattr(request, 'session', {})
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        qs = Expedition.objects.filter(pk__in=[self.exp_en_cours.pk, self.exp_publiee.pk])
        cloturer_expeditions(ea, request, qs)

        self.exp_en_cours.refresh_from_db()
        self.exp_publiee.refresh_from_db()

        # Seule celle en_cours doit être clôturée (passée à LIVREE)
        self.assertEqual(self.exp_en_cours.statut, Expedition.Statut.LIVREE)
        # Celle publiée doit rester intacte (PUBLIEE)
        self.assertEqual(self.exp_publiee.statut, Expedition.Statut.PUBLIEE)

    def test_en_retard_filter(self):
        ea = ExpeditionAdmin(Expedition, self.site)
        request = self.factory.get('/admin/expedition/')
        request.user = self.admin_user

        # Filtre oui
        filter_oui = EnRetardFilter(request, {'en_retard': ['oui']}, Expedition, ea)
        qs_retard = filter_oui.queryset(request, Expedition.objects.all())
        self.assertIn(self.exp_publiee, qs_retard)
        self.assertNotIn(self.exp_en_cours, qs_retard)

        # Filtre non
        filter_non = EnRetardFilter(request, {'en_retard': ['non']}, Expedition, ea)
        qs_pas_retard = filter_non.queryset(request, Expedition.objects.all())
        self.assertNotIn(self.exp_publiee, qs_pas_retard)

    def test_statut_badge_expedition_and_offre(self):
        ea = ExpeditionAdmin(Expedition, self.site)
        badge_exp = ea.statut_badge(self.exp_publiee)
        self.assertIn('<span style=', badge_exp)
        self.assertIn('Publiée', badge_exp)

        oa = OffreAdmin(Offre, self.site)
        badge_offre = oa.statut_colore(self.offre_prop)
        self.assertIn('<span style=', badge_offre)
        self.assertIn('Proposée', badge_offre)

    def test_offre_admin_readonly_fields_dynamic(self):
        oa = OffreAdmin(Offre, self.site)
        request = self.factory.get('/admin/offre/')
        request.user = self.admin_user

        # Offre proposée -> prix et delai_jours éditables
        fields_prop = oa.get_readonly_fields(request, self.offre_prop)
        self.assertNotIn('prix', fields_prop)
        self.assertNotIn('delai_jours', fields_prop)

        # Offre acceptée -> prix et delai_jours deviennent readonly
        self.offre_prop.statut = Offre.Statut.ACCEPTEE
        fields_acc = oa.get_readonly_fields(request, self.offre_prop)
        self.assertIn('prix', fields_acc)
        self.assertIn('delai_jours', fields_acc)

    def test_exporter_offres_csv_action(self):
        oa = OffreAdmin(Offre, self.site)
        request = self.factory.get('/admin/offre/')
        request.user = self.admin_user

        response = exporter_offres_csv(oa, request, Offre.objects.filter(pk=self.offre_prop.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
        content = response.content.decode('utf-8')
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        self.assertEqual(rows[0], ['reference_expedition', 'transporteur', 'prix', 'statut'])
        self.assertEqual(rows[1][0], self.exp_publiee.reference)
        self.assertEqual(rows[1][1], self.entreprise_trans.raison_sociale)

    def test_health_check_view_accessible_by_admin(self):
        self.client.force_login(self.admin_user)
        response = self.client.get('/admin/health-check/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tableau de bord de contrôle d'intégrité")
        self.assertContains(response, "Offres orphelines")
        self.assertContains(response, "Expéditions bloquées")
        self.assertContains(response, "Transporteurs sans flotte")
        self.assertContains(response, "Incohérence de disponibilité")
        self.assertContains(response, "Doublons de proposition")
