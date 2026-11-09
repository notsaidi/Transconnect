from ExpeditionsApp.models import Expedition
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from ExpeditionsApp.forms import ExpeditionForm


# Create your views here.


def home(request):
    return HttpResponse("Welcome to the Expedition App!")

def afficher(request, name):
    #return HttpResponse(f"hello, {name}!")
    return render(request, "Expeditions/afficher.html", {"name": name})

def listExpeitions(request):
    expeditions = Expedition.objects.filter(statut='publiee')
    return render(request, "Expeditions/list.html", {"list": expeditions})

def detailExpedition(request, pk):
    expedition = Expedition.objects.get(pk=pk)
    return render(request, "Expeditions/detail.html", {"expedition": expedition})


def suprimerExpedition(request, pk):
    expedition = get_object_or_404(Expedition, pk=pk)
    if request.method == 'POST':        # confirmed → delete
        expedition.delete()
        return redirect('list')
    return render(request, "Expeditions/supprimer_confirm.html", {"expedition": expedition})  # GET → show confirmation page

class ExpeditionListview(ListView):
    model = Expedition
    context_object_name = "list"
    template_name = "Expeditions/list.html"

    def get_queryset(self):
        return Expedition.objects.filter(statut='publiee')


class ExpeditionDetailview(DetailView):
    model = Expedition
    context_object_name = "expedition"
    template_name = "Expeditions/detail.html"

class ExpeditionCreateview(CreateView):
    model = Expedition
    form_class = ExpeditionForm
    template_name = "Expeditions/forms.html"
    success_url = "/Expedition/list/"


class ExpeditionUpdateview(UpdateView):
    model = Expedition
    form_class = ExpeditionForm
    template_name = "Expeditions/forms.html"
    success_url = "/Expedition/list/"


