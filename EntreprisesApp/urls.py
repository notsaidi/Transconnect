from django.urls import path
from .views import (
    listEntreprises, detailEntreprise, supprimerEntreprise,
    EntrepriseListview, EntrepriseDetailview, EntrepriseCreateview, EntrepriseUpdateview,
    inscription, profile_view, profile_modifier, profile_supprimer
)

urlpatterns = [
    # User accounts & profile
    path('inscription/', inscription, name='inscription'),
    path('profil/', profile_view, name='user_profile'),
    path('profil/modifier/', profile_modifier, name='user_modifier'),
    path('profil/supprimer/', profile_supprimer, name='user_supprimer'),

    # Entreprise CRUD
    path('list/', listEntreprises, name='entreprises_list'),
    path('detail/<int:pk>/', detailEntreprise, name='entreprise_detail'),
    path('supprimer/<int:pk>/', supprimerEntreprise, name='entreprise_supprimer'),
    path('ajouter/', EntrepriseCreateview.as_view(), name='entreprise_ajouter'),
    path('modifier/<int:pk>/', EntrepriseUpdateview.as_view(), name='entreprise_modifier'),
]
