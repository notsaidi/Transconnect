from django.urls import path
from .views import home, afficher, listExpeitions,detailExpedition

urlpatterns = [
    path('home/', home, name='home'),
    path('afficher/<str:name>/', afficher, name='afficher'),
    path('list/', listExpeitions, name='list'),
    path('detail/<int:pk>/', detailExpedition, name='detail'),
]