from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from OffresApp.models import Offre
from OffresApp.forms import OffreForm


def listOffres(request):
    offres = Offre.objects.all()
    return render(request, 'Offres/list.html', {'list': offres})


def detailOffre(request, pk):
    offre = get_object_or_404(Offre, pk=pk)
    return render(request, 'Offres/detail.html', {'offre': offre})


@login_required
def supprimerOffre(request, pk):
    offre = get_object_or_404(Offre, pk=pk)
    if request.method == 'POST':
        offre.delete()
        return redirect('offres_list')
    return render(request, 'Offres/supprimer_confirm.html', {'offre': offre})


class OffreListview(ListView):
    model = Offre
    context_object_name = 'list'
    template_name = 'Offres/list.html'


class OffreDetailview(DetailView):
    model = Offre
    context_object_name = 'offre'
    template_name = 'Offres/detail.html'


class OffreCreateview(LoginRequiredMixin, CreateView):
    model = Offre
    form_class = OffreForm
    template_name = 'Offres/forms.html'
    success_url = '/Offre/list/'


class OffreUpdateview(LoginRequiredMixin, UpdateView):
    model = Offre
    form_class = OffreForm
    template_name = 'Offres/forms.html'
    success_url = '/Offre/list/'
