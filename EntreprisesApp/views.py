from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from EntreprisesApp.models import Entreprise, Utilisateur
from EntreprisesApp.forms import EntrepriseForm, UtilisateurRegistrationForm, UtilisateurProfileForm


# ------------------- Authentication & Profile Views -------------------

def inscription(request):
    if request.user.is_authenticated:
        return redirect('root_home')
    if request.method == 'POST':
        form = UtilisateurRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('root_home')
    else:
        form = UtilisateurRegistrationForm()
    return render(request, 'Entreprises/inscription.html', {'form': form})


@login_required
def profile_view(request):
    return render(request, 'Entreprises/profile.html', {'user': request.user})


@login_required
def profile_modifier(request):
    if request.method == 'POST':
        form = UtilisateurProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('user_profile')
    else:
        form = UtilisateurProfileForm(instance=request.user)
    return render(request, 'Entreprises/profile_modifier.html', {'form': form})


@login_required
def profile_supprimer(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        return redirect('login')
    return render(request, 'Entreprises/profile_supprimer_confirm.html', {'user': request.user})


# ------------------- Entreprise CRUD Views -------------------

def listEntreprises(request):
    entreprises = Entreprise.objects.all()
    return render(request, 'Entreprises/list.html', {'list': entreprises})


def detailEntreprise(request, pk):
    entreprise = get_object_or_404(Entreprise, pk=pk)
    return render(request, 'Entreprises/detail.html', {'entreprise': entreprise})


@login_required
def supprimerEntreprise(request, pk):
    entreprise = get_object_or_404(Entreprise, pk=pk)
    # Seul le gérant ou un administrateur peut supprimer l'entreprise
    if not (request.user == entreprise.gerant or request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied("Vous n'êtes pas autorisé à supprimer cette entreprise.")
        
    if request.method == 'POST':
        entreprise.delete()
        return redirect('entreprises_list')
    return render(request, 'Entreprises/supprimer_confirm.html', {'entreprise': entreprise})


class EntrepriseListview(ListView):
    model = Entreprise
    context_object_name = 'list'
    template_name = 'Entreprises/list.html'


class EntrepriseDetailview(DetailView):
    model = Entreprise
    context_object_name = 'entreprise'
    template_name = 'Entreprises/detail.html'


class EntrepriseCreateview(LoginRequiredMixin, CreateView):
    model = Entreprise
    form_class = EntrepriseForm
    template_name = 'Entreprises/forms.html'
    success_url = '/Entreprise/list/'


class EntrepriseUpdateview(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Entreprise
    form_class = EntrepriseForm
    template_name = 'Entreprises/forms.html'
    success_url = '/Entreprise/list/'

    def test_func(self):
        """
        Règle de sécurité :
        - Un utilisateur ne peut pas modifier une entreprise de type 'chargeur' s'il n'en est pas le gérant (ou staff).
        - Plus généralement, seul le gérant de l'entreprise (ou un administrateur) peut modifier cette entreprise.
        """
        entreprise = self.get_object()
        user = self.request.user
        
        # Le staff / admin conserve l'accès
        if user.is_staff or user.is_superuser:
            return True
            
        # L'utilisateur ne peut modifier que sa propre entreprise dont il est le gérant
        return entreprise.gerant == user

