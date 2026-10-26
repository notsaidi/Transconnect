from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from VehiculesApp.models import Vehicule
from .models import Entreprise, Utilisateur


class VehiculeInline(admin.TabularInline):
    model = Vehicule
    extra = 0
    fields = ('immatriculation', 'type_vehicule', 'capacite_kg', 'disponible')


@admin.register(Entreprise)
class EntrepriseAdmin(admin.ModelAdmin):
    list_display = ('raison_sociale', 'type_entreprise', 'matricule_fiscal', 'gerant', 'created_at')
    list_filter = ('type_entreprise', 'created_at')
    search_fields = ('raison_sociale', 'matricule_fiscal')
    inlines = [VehiculeInline]
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

    fieldsets = (
        ("Informations de l'entreprise", {
            'fields': ('raison_sociale', 'matricule_fiscal', 'type_entreprise', 'gerant')
        }),
        ("Coordonnées", {
            'fields': ('adresse',)
        }),
        ("Traçabilité temporelle", {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ('username', 'user_id', 'email', 'role', 'telephone', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'user_id')
    readonly_fields = ('user_id', 'created_at', 'updated_at')
    ordering = ('-created_at',)

    fieldsets = UserAdmin.fieldsets + (
        ('Informations TransConnect', {
            'fields': ('user_id', 'role', 'telephone')
        }),
        ('Traçabilité temporelle', {
            'fields': ('created_at', 'updated_at')
        }),
    )