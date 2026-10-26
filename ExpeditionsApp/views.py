from ExpeditionsApp.models import Expedition
from django.shortcuts import render
from django.http import HttpResponse




# Create your views here.


def home(request):
    return HttpResponse("Welcome to the Expedition App!")

def afficher(request, name):
    #return HttpResponse(f"hello, {name}!")
    return render(request,"Expeditions/afficher.html", {"name":name})

def listExpeitions(request):
    expeditions = Expedition.objects.all()
    return render(request, "Expeditions/list.html", {"list": expeditions}) 

def detailExpedition(request, pk):
    expedition = Expedition.objects.get(pk=pk)
    return render(request, "Expeditions/detail.html", {"expedition": expedition})