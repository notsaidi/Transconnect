from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from VehiculesApp.models import Vehicule
from VehiculesApp.forms import VehiculeForm


def listVehicules(request):
    vehicules = Vehicule.objects.all()
    return render(request, 'Vehicules/list.html', {'list': vehicules})


def detailVehicule(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk)
    return render(request, 'Vehicules/detail.html', {'vehicule': vehicule})


@login_required
def supprimerVehicule(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk)
    if request.method == 'POST':
        vehicule.delete()
        return redirect('vehicules_list')
    return render(request, 'Vehicules/supprimer_confirm.html', {'vehicule': vehicule})


class VehiculeListview(ListView):
    model = Vehicule
    context_object_name = 'list'
    template_name = 'Vehicules/list.html'


class VehiculeDetailview(DetailView):
    model = Vehicule
    context_object_name = 'vehicule'
    template_name = 'Vehicules/detail.html'


class VehiculeCreateview(LoginRequiredMixin, CreateView):
    model = Vehicule
    form_class = VehiculeForm
    template_name = 'Vehicules/forms.html'
    success_url = '/Vehicule/list/'


class VehiculeUpdateview(LoginRequiredMixin, UpdateView):
    model = Vehicule
    form_class = VehiculeForm
    template_name = 'Vehicules/forms.html'
    success_url = '/Vehicule/list/'
