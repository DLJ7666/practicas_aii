#encoding:utf-8
from main.models import Usuario, Puntuacion, Pelicula
from main.populateDB import populate
from main.forms import  UsuarioBusquedaForm, PeliculaBusquedaForm
from django.shortcuts import render, get_object_or_404
from django.http.response import HttpResponseRedirect
from django.conf import settings
from main.recommendations import  transformPrefs, calculateSimilarItems, getRecommendations, getRecommendedItems, topMatches
import shelve

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from gevent.libev.corecext import NONE

# Funcion que carga en el diccionario Prefs todas las puntuaciones de usuarios a peliculas. Tambien carga el diccionario inverso
# Serializa los resultados en dataRS.dat
def loadDict():
    Prefs={}   # matriz de usuarios y puntuaciones a cada a items
    shelf = shelve.open("dataRS.dat")
    ratings = Puntuacion.objects.all()
    for ra in ratings:
        user = int(ra.idUsuario.idUsuario)
        itemid = int(ra.idPelicula.idPelicula)
        rating = float(ra.puntuacion)
        Prefs.setdefault(user, {})
        Prefs[user][itemid] = rating
    shelf['Prefs']=Prefs
    shelf['ItemsPrefs']=transformPrefs(Prefs)
    shelf['SimItems']=calculateSimilarItems(Prefs, n=10)
    shelf.close()


#Funcion de acceso restringido que carga los datos en la BD  
@login_required(login_url='/ingresar')
def populateDatabase(request):
    populate()
    logout(request)  # se hace logout para obligar a login cada vez que se vaya a poblar la BD
    return HttpResponseRedirect('/index.html')


def loadRS(request):
    loadDict()
    return HttpResponseRedirect('/index.html')


def recomendar_peliculas_usuario_RSusuario(request):
    formulario = UsuarioBusquedaForm()
    items = None
    usuario = None
    
    if request.method=='POST':
        formulario = UsuarioBusquedaForm(request.POST)
        
        if formulario.is_valid():
            idUsuario=formulario.cleaned_data['idUsuario']
            usuario = get_object_or_404(Usuario, pk=idUsuario)
            shelf = shelve.open("dataRS.dat")
            Prefs = shelf['Prefs']
            shelf.close()
            rankings = getRecommendations(Prefs,int(idUsuario))
            recomendadas= rankings[:2]
            peliculas = []
            puntuaciones = []
            for re in recomendadas:
                peliculas.append(Pelicula.objects.get(pk=re[1]))
                puntuaciones.append(re[0])
            items= zip(peliculas,puntuaciones)
    
    return render(request, 'recomendar_peliculas_usuarios.html', {'formulario':formulario, 'items':items, 'usuario':usuario, 'STATIC_URL':settings.STATIC_URL})


def recomendar_peliculas_usuario_RSitems(request):
    formulario = UsuarioBusquedaForm()
    items = None
    usuario = None
    
    if request.method=='POST':
        formulario = UsuarioBusquedaForm(request.POST)
        
        if formulario.is_valid():
            idUsuario=formulario.cleaned_data['idUsuario']
            usuario = get_object_or_404(Usuario, pk=idUsuario)
            shelf = shelve.open("dataRS.dat")
            Prefs = shelf['Prefs']
            SimItems = shelf['SimItems']
            shelf.close()
            rankings = getRecommendedItems(Prefs, SimItems, int(idUsuario))
            recomendadas= rankings[:3]
            peliculas = []
            puntuaciones = []
            for re in recomendadas:
                peliculas.append(Pelicula.objects.get(pk=re[1]))
                puntuaciones.append(re[0])
            items= zip(peliculas,puntuaciones)
    
    return render(request, 'recomendar_peliculas_usuarios.html', {'formulario':formulario, 'items':items, 'usuario':usuario, 'STATIC_URL':settings.STATIC_URL})


def recomendar_usuarios_pelicula(request):
    formulario = PeliculaBusquedaForm()
    items = None
    pelicula = None
    
    if request.method=='POST':
        form = PeliculaBusquedaForm(request.POST)
        if form.is_valid():
            idPelicula = form.cleaned_data['idPelicula']
            pelicula = get_object_or_404(Pelicula, pk=idPelicula)
            shelf = shelve.open("dataRS.dat")
            Prefs = shelf['ItemsPrefs']
            shelf.close()
            rankings = getRecommendations(Prefs,int(idPelicula))
            recomendadas = rankings[:3]
            usuarios = []
            puntuaciones = []
            for re in recomendadas:
                usuarios.append(Usuario.objects.get(pk=re[1]))
                puntuaciones.append(re[0])
            items= zip(usuarios,puntuaciones)
            
    return render(request, 'recomendar_usuarios_peliculas.html', {'formulario':formulario, 'items':items, 'pelicula':pelicula, 'STATIC_URL':settings.STATIC_URL})


def mostrar_peliculas_parecidas(request):
    formulario = PeliculaBusquedaForm()
    pelicula = None
    items = None
    
    if request.method=='POST':
        formulario = PeliculaBusquedaForm(request.POST)
        
        if formulario.is_valid():
            idPelicula = formulario.cleaned_data['idPelicula']
            pelicula = get_object_or_404(Pelicula, pk=idPelicula)
            shelf = shelve.open("dataRS.dat")
            ItemsPrefs = shelf['ItemsPrefs']
            shelf.close()
            parecidas = topMatches(ItemsPrefs, int(idPelicula),n=3)
            peliculas = []
            similaridad = []
            for re in parecidas:
                peliculas.append(Pelicula.objects.get(pk=re[1]))
                similaridad.append(re[0])
            items= zip(peliculas,similaridad)
    
    return render(request, 'peliculas_similares.html', {'formulario':formulario, 'pelicula': pelicula, 'items': items, 'STATIC_URL':settings.STATIC_URL})



def mostrar_puntuaciones_usuario(request):
    formulario = UsuarioBusquedaForm()
    puntuaciones = None
    idusuario = None
    
    if request.method=='POST':
        formulario = UsuarioBusquedaForm(request.POST)
        
        if formulario.is_valid():
            idusuario = formulario.cleaned_data['idUsuario']
            puntuaciones = Puntuacion.objects.filter(idUsuario = Usuario.objects.get(pk=idusuario))
            
    return render(request, 'puntuaciones_usuario.html', {'formulario':formulario, 'puntuaciones':puntuaciones, 'idusuario':idusuario, 'STATIC_URL':settings.STATIC_URL})


def index(request):
    return render(request, 'index.html',{'STATIC_URL':settings.STATIC_URL})


def ingresar(request):
    formulario = AuthenticationForm()
    if request.method=='POST':
        formulario = AuthenticationForm(request.POST)
        usuario=request.POST['username']
        clave=request.POST['password']
        acceso=authenticate(username=usuario,password=clave)
        if acceso is not None:
            if acceso.is_active:
                login(request, acceso)
                return (HttpResponseRedirect('/populate'))
            else:
                return render(request, 'mensaje_error.html',{'error':"USUARIO NO ACTIVO",'STATIC_URL':settings.STATIC_URL})
        else:
            return render(request, 'mensaje_error.html',{'error':"USUARIO O CONTRASEÑA INCORRECTOS",'STATIC_URL':settings.STATIC_URL})
                     
    return render(request, 'ingresar.html', {'formulario':formulario, 'STATIC_URL':settings.STATIC_URL})


