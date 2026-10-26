import datetime
from django.contrib import admin
from django.db.models import Count
from django.template.response import TemplateResponse
from django.utils import timezone
from EntreprisesApp.models import Entreprise
from ExpeditionsApp.models import Expedition
from OffresApp.models import Offre
from VehiculesApp.models import Vehicule


def health_check_view(request):
    """
    Vue d'audit et de contrôle d'intégrité de la plateforme TransConnect.
    Exécute 5 contrôles d'intégrité métier basés exclusivement sur des requêtes ORM (sans boucles Python).
    """
    now = timezone.now()
    sept_jours_avant = now - datetime.timedelta(days=7)

    # 1. Offres orphelines
    # Offres au statut 'proposee' ou 'acceptee' dont l'expédition associée
    # n'est plus ni 'publiee' ni 'attribuee' (ex: annulée ou livrée prématurément).
    offres_orphelines = Offre.objects.filter(
        statut__in=[Offre.Statut.PROPOSEE, Offre.Statut.ACCEPTEE]
    ).exclude(
        expedition__statut__in=[Expedition.Statut.PUBLIEE, Expedition.Statut.ATTRIBUEE]
    ).select_related('expedition', 'transporteur')

    # 2. Expéditions bloquées
    # Expéditions restées 'publiee' depuis plus de 7 jours sans passer à l'étape suivante.
    expeditions_bloquees = Expedition.objects.filter(
        statut=Expedition.Statut.PUBLIEE,
        created_at__lte=sept_jours_avant
    ).select_related('entreprise')

    # 3. Transporteurs sans flotte
    # Entreprises dont type_entreprise = 'transporteur' qui n'ont aucun véhicule enregistré.
    transporteurs_sans_flotte = (
        Entreprise.objects
        .filter(type_entreprise='transporteur')
        .annotate(nb_vehicules=Count('vehicules'))
        .filter(nb_vehicules=0)
        .select_related('gerant')
    )

    # 4. Incohérence de disponibilité
    # Véhicules marqués 'disponible = True' mais actuellement assignés à une offre 'acceptee'.
    vehicules_incoherents = (
        Vehicule.objects
        .filter(disponible=True, offres__statut=Offre.Statut.ACCEPTEE)
        .distinct()
        .select_related('entreprise')
    )

    # 5. Doublons de proposition
    # Transporteurs ayant plus d'une offre au statut 'proposee' sur la même expédition (violation Règle 4).
    doublons_propositions = (
        Offre.objects
        .filter(statut=Offre.Statut.PROPOSEE)
        .values('expedition_id', 'expedition__reference', 'transporteur_id', 'transporteur__raison_sociale')
        .annotate(nb_offres=Count('id'))
        .filter(nb_offres__gt=1)
    )

    controles = [
        {
            'id': 1,
            'titre': "Offres orphelines",
            'regle': "Règle métier 3 : Cohérence du statut des propositions liées au cycle de vie de l'expédition",
            'scenario': "Un opérateur exécute un '.update(statut='annulee')' sur des expéditions en base, laissant les offres dans un statut actif alors que l'expédition est close.",
            'count': offres_orphelines.count(),
            'items': offres_orphelines,
            'type': 'offres_orphelines'
        },
        {
            'id': 2,
            'titre': "Expéditions bloquées (> 7 jours)",
            'regle': "Gestion du flux opérationnel : toute expédition publiée doit recevoir des offres ou être relancée sous 7 jours",
            'scenario': "Expéditions créées par des chargeurs puis délaissées, ou script d'import massif d'anciennes demandes sans mécanisme d'archivage ou d'annulation automatique.",
            'count': expeditions_bloquees.count(),
            'items': expeditions_bloquees,
            'type': 'expeditions_bloquees'
        },
        {
            'id': 3,
            'titre': "Transporteurs sans flotte",
            'regle': "Règles métier 1 & 2 : Tout transporteur opérant sur la plateforme doit être doté d'au moins un véhicule",
            'scenario': "Inscription d'une entreprise transporteur par formulaire ou synchronisation API sans ajout immédiat de véhicules dans la flotte.",
            'count': transporteurs_sans_flotte.count(),
            'items': transporteurs_sans_flotte,
            'type': 'transporteurs_sans_flotte'
        },
        {
            'id': 4,
            'titre': "Incohérence de disponibilité des véhicules",
            'regle': "Règle métier 6 : Un véhicule affecté à une offre acceptée doit être marqué indisponible",
            'scenario': "Mise à jour en masse SQL ou via l'admin ('Vehicule.objects.update(disponible=True)') pour réinitialiser la flotte sans vérifier les missions attribuées en cours.",
            'count': vehicules_incoherents.count(),
            'items': vehicules_incoherents,
            'type': 'vehicules_incoherents'
        },
        {
            'id': 5,
            'titre': "Doublons de proposition (Violation Règle 4)",
            'regle': "Règle métier 4 : Une entreprise ne peut avoir deux offres au statut 'proposée' actives simultanément sur la même expédition",
            'scenario': "Utilisation de 'Offre.objects.bulk_create()' lors d'un import de devis partenaires, ce qui court-circuite la méthode 'clean()' du modèle.",
            'count': doublons_propositions.count(),
            'items': doublons_propositions,
            'type': 'doublons_propositions'
        },
    ]

    total_anomalies = sum(c['count'] for c in controles)
    controles_en_echec = sum(1 for c in controles if c['count'] > 0)
    controles_valides = len(controles) - controles_en_echec

    context = {
        **admin.site.each_context(request),
        'title': "Tableau de bord de contrôle d'intégrité",
        'subtitle': "Diagnostic & Détection d'anomalies ORM",
        'controles': controles,
        'total_anomalies': total_anomalies,
        'controles_valides': controles_valides,
        'controles_en_echec': controles_en_echec,
        'date_analyse': now,
    }

    return TemplateResponse(request, 'admin/health_check.html', context)
