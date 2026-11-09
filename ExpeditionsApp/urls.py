from django.urls import path
from .views import home, afficher, listExpeitions, detailExpedition, suprimerExpedition, ExpeditionListview, ExpeditionDetailview, ExpeditionCreateview, ExpeditionUpdateview

urlpatterns = [
    path('home/', home, name='home'),
    path('afficher/<str:name>/', afficher, name='afficher'),
    path('list/', listExpeitions, name='list'),
    path('detail/<int:pk>/', detailExpedition, name='detail'),
    path('supprimer/<int:pk>/', suprimerExpedition, name='supprimer'),
    path('listviews/', ExpeditionListview.as_view(), name='Listview'),
    path('detailviews/', ExpeditionDetailview.as_view(), name='detailview'),
    path('Createviews/', ExpeditionCreateview.as_view(), name='createexpedition'),
    path('modifier/<int:pk>/', ExpeditionUpdateview.as_view(), name='modifier'),
]