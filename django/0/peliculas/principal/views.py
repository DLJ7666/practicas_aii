#encoding:utf-8
from principal.models import Genero, Pelicula
from principal.forms import BusquedaPorFechaForm, BusquedaPorGeneroForm
from principal.populateDB import populateDB
from django.shortcuts import render, redirect

#carga los datos desde la web en la BD
def carga(request):
 
    if request.method=='POST':
        if 'Aceptar' in request.POST:      
            num_peliculas, num_directores, num_generos, num_paises = populateDB()
            mensaje="Se han almacenado: " + str(num_peliculas) +" peliculas, " + str(num_directores) +" directores, " + str(num_generos) +" generos, " + str(num_paises) +" paises"
            return render(request, 'cargaBD.html', {'mensaje':mensaje})
        else:
            return redirect("/")
           
    return render(request, 'confirmacion.html')

#muestra el número de películas que hay en la BD
def inicio(request):
    num_peliculas=Pelicula.objects.all().count()
    return render(request,'inicio.html', {'num_peliculas':num_peliculas})

#muestra un listado con los datos de las películas (título, título original, país, director, géneros y fecha de estreno)
def lista_peliculas(request):
    peliculas=Pelicula.objects.all()
    return render(request,'peliculas.html', {'peliculas':peliculas})

#muestra la lista de películas agrupadas por paises
def lista_peliculasporpais(request):
    peliculas=Pelicula.objects.all().order_by('pais')
    return render(request,'peliculasporpais.html', {'peliculas':peliculas})

#muestra un formulario con un modelchoicefield con la lista de géneros que hay en la BD. Cuando se seleccione
#un género muestra los datos de todas las películas de ese género
def buscar_peliculasporgenero(request):
    formulario = BusquedaPorGeneroForm()
    peliculas = None
    
    if request.method=='POST':
        formulario = BusquedaPorGeneroForm(request.POST)      
        if formulario.is_valid():
            genero=Genero.objects.get(id=formulario.cleaned_data['genero'].id)
            peliculas = genero.pelicula_set.all()
            
    return render(request, 'peliculasbusquedaporgenero.html', {'formulario':formulario, 'peliculas':peliculas})

#muestra un formulario con un datefield. Cuando se escriba una fecha muestra los datos de todas las
#las películas con una fecha de estreno posterior a ella
def buscar_peliculasporfecha(request):
    formulario = BusquedaPorFechaForm()
    peliculas = None
    
    if request.method=='POST':
        formulario = BusquedaPorFechaForm(request.POST)      
        if formulario.is_valid():
            peliculas = Pelicula.objects.filter(fechaEstreno__gte=formulario.cleaned_data['fecha'])
            
    return render(request, 'peliculasbusquedaporfecha.html', {'formulario':formulario, 'peliculas':peliculas})
