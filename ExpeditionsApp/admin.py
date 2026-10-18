from django.contrib import admin
from .models import Expedition

# Register your models here.


class ExpeditionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'ville_depart', 'ville_arrivee', 'poids_kg', 'date_souhaitee', 'statut')


admin.site.register(Expedition, ExpeditionAdmin)