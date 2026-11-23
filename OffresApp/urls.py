from django.urls import path
from .views import (
    listOffres, detailOffre, supprimerOffre,
    OffreListview, OffreDetailview, OffreCreateview, OffreUpdateview
)

urlpatterns = [
    path('list/', listOffres, name='offres_list'),
    path('detail/<int:pk>/', detailOffre, name='offre_detail'),
    path('supprimer/<int:pk>/', supprimerOffre, name='offre_supprimer'),
    path('ajouter/', OffreCreateview.as_view(), name='offre_ajouter'),
    path('modifier/<int:pk>/', OffreUpdateview.as_view(), name='offre_modifier'),
]
