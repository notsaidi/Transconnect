from django.contrib import admin
from django.urls import path, include
from config.admin_views import health_check_view
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

# 1. Image de marque et branding de l'espace admin (Section II & Bloc 5)
admin.site.site_header = "TransConnect Administration"
admin.site.site_title = "TransConnect Admin"
admin.site.index_title = "Pilotage des opérations TransConnect"


# 2. Surcharge de get_urls() sur le site admin pour le tableau de bord d'intégrité (Section VIII)
_original_get_urls = admin.site.get_urls


def custom_get_urls():
    custom_urls = [
        path('health-check/', admin.site.admin_view(health_check_view), name='health_check'),
    ]
    return custom_urls + _original_get_urls()


admin.site.get_urls = custom_get_urls

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='root_home'),
    path('admin/', admin.site.urls),
    path('Expedition/', include('ExpeditionsApp.urls')),
    path('Vehicule/', include('VehiculesApp.urls')),
    path('Offre/', include('OffresApp.urls')),
    path('Entreprise/', include('EntreprisesApp.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='Entreprises/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
