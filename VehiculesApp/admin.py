from django.contrib import admin
from .models import Vehicule


@admin.register(Vehicule)
class VehiculeAdmin(admin.ModelAdmin):
    list_display = ('immatriculation', 'type_vehicule', 'entreprise', 'capacite_kg', 'disponible')
    list_filter = ('type_vehicule', 'disponible', 'entreprise')
    search_fields = ('immatriculation', 'entreprise__raison_sociale')
    list_editable = ('disponible',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ("Informations d'identification", {
            'fields': ('immatriculation', 'type_vehicule', 'entreprise')
        }),
        ('Caractéristiques techniques & Disponibilité', {
            'fields': ('capacite_kg', 'disponible')
        }),
        ('Traçabilité temporelle', {
            'fields': ('created_at', 'updated_at')
        }),
    )