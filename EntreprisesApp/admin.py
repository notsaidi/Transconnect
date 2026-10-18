from django.contrib import admin
from .models import Entreprise
from .models import Utilisateur
# Register your models here.
admin.site.register(Entreprise)
admin.site.register(Utilisateur)