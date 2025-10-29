from principal.models import Bebida
from django.shortcuts import render

def lista_bebidas(request):
    bebidas = Bebida.objects.all()
    return render(request, 'lista_bebidas.html', {'lista': bebidas})
