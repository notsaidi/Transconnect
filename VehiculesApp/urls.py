from django.urls import path
from .views import (
    listVehicules, detailVehicule, supprimerVehicule,
    VehiculeListview, VehiculeDetailview, VehiculeCreateview, VehiculeUpdateview
)

urlpatterns = [
    path('list/', listVehicules, name='vehicules_list'),
    path('detail/<int:pk>/', detailVehicule, name='vehicule_detail'),
    path('supprimer/<int:pk>/', supprimerVehicule, name='vehicule_supprimer'),
    path('ajouter/', VehiculeCreateview.as_view(), name='vehicule_ajouter'),
    path('modifier/<int:pk>/', VehiculeUpdateview.as_view(), name='vehicule_modifier'),
]
