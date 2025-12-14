#encoding:utf-8
from main.models import Vino, Uva
from main.forms import  VinosPorAnyo, VinosPorUvas
from main.populateDB import populate
from django.shortcuts import render



def populateDatabase(request):
    (p,d,u,v) = populate()
    informacion="Datos cargados correctamente\n" + "Paises: " + str(p) + " ; " + "Denominaciones: " + str(d) + " ; " + "Tipos de Uvas: " + str(u) + " ; " + "Vinos: " + str(v)
    return render(request, 'carga.html', {'inf':informacion})


def mostrar_vinos_por_denominaciones(request):
    vinos= Vino.objects.all().order_by('denominacion')
    return render(request, 'denominacion_vinos.html',{'vinos':vinos})

def buscar_vinos_por_anyo(request):
    formulario = VinosPorAnyo()
    vinos = None
    anyo =""
    
    if request.method=='POST':
        formulario = VinosPorAnyo(request.POST)
        
        if formulario.is_valid():
            anyo = formulario.cleaned_data['anyo']
            vinos = Vino.objects.filter(nombre__contains=anyo)
            
    return render(request, 'busqueda_vinos_anyo.html', {'formulario':formulario, 'vinos':vinos, 'anyo':anyo})

def buscar_vinos_por_uva(request):
    formulario = VinosPorUvas()
    vinos = None
    
    if request.method=='POST':
        formulario = VinosPorUvas(request.POST)      
        if formulario.is_valid():
            uva = Uva.objects.get(idUva=formulario.cleaned_data['uva'].idUva)
            vinos = uva.vino_set.all()
            
    return render(request, 'busqueda_vinos_uva.html', {'formulario':formulario, 'vinos':vinos})

def index(request):
    return render(request, 'index.html')



