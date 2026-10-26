from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from OffresApp.models import Offre
from .models import Expedition


class EnRetardFilter(admin.SimpleListFilter):
    title = 'en retard'
    parameter_name = 'en_retard'

    def lookups(self, request, model_admin):
        return [('oui', 'Oui'), ('non', 'Non')]

    def queryset(self, request, queryset):
        if self.value() == 'oui':
            return queryset.filter(
                statut=Expedition.Statut.PUBLIEE,
                date_souhaitee__lt=timezone.now().date()
            )
        if self.value() == 'non':
            return queryset.exclude(
                statut=Expedition.Statut.PUBLIEE,
                date_souhaitee__lt=timezone.now().date()
            )
        return queryset


class OffreInline(admin.StackedInline):
    model = Offre
    extra = 0
    fk_name = 'expedition'
    readonly_fields = ('transporteur', 'vehicule', 'prix', 'delai_jours', 'statut')
    show_change_link = True
    can_delete = False


@admin.action(description="Clôturer les expéditions sélectionnées")
def cloturer_expeditions(modeladmin, request, queryset):
    candidats = queryset.filter(statut=Expedition.Statut.EN_COURS)
    nb_traites = 0
    for expedition in candidats:
        expedition.statut = Expedition.Statut.LIVREE
        expedition.full_clean()
        expedition.save()
        nb_traites += 1

    if nb_traites:
        modeladmin.message_user(
            request,
            f"{nb_traites} expédition(s) en cours clôturée(s) avec succès."
        )
    else:
        modeladmin.message_user(
            request,
            "Aucune expédition au statut 'en cours' n'a été sélectionnée.",
            level='warning'
        )


@admin.register(Expedition)
class ExpeditionAdmin(admin.ModelAdmin):
    list_display = (
        'reference',
        'entreprise',
        'ville_depart',
        'ville_arrivee',
        'statut_badge',
        'date_souhaitee',
    )
    list_filter = ('statut', 'ville_depart', EnRetardFilter)
    search_fields = ('reference', 'entreprise__raison_sociale')
    list_editable = ('date_souhaitee',)
    ordering = ('-created_at',)
    date_hierarchy = 'date_souhaitee'
    list_per_page = 25
    inlines = [OffreInline]
    actions = [cloturer_expeditions]
    readonly_fields = ('reference', 'created_at', 'updated_at')

    fieldsets = (
        ("Identification & Statut", {
            'fields': ('reference', 'entreprise', 'statut')
        }),
        ("Trajet & Planification", {
            'fields': ('ville_depart', 'ville_arrivee', 'date_souhaitee')
        }),
        ("Cargaison", {
            'fields': ('poids_kg', 'description')
        }),
        ("Traçabilité temporelle", {
            'fields': ('created_at', 'updated_at')
        }),
    )

    @admin.display(description='Statut')
    def statut_badge(self, obj):
        couleurs = {
            'publiee': '#0275d8',
            'attribuee': '#f0ad4e',
            'en_cours': '#6f42c1',
            'livree': '#5cb85c',
            'annulee': '#d9534f',
        }
        return format_html(
            '<span style="color:white;background:{};padding:3px 8px;border-radius:4px;font-weight:600;">{}</span>',
            couleurs.get(obj.statut, '#777777'),
            obj.get_statut_display(),
        )