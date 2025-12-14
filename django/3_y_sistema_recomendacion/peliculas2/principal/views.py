from django.shortcuts import render
from principal.models import Categoria, Pelicula, Usuario, Ocupacion, Puntuacion
from principal.forms import PeliculaBusquedaYearForm, UsuarioBusquedaForm
from datetime import datetime
from django.db import models
from django.http import HttpResponseRedirect
from django.conf import settings
from django.db.models import Avg, Count

def popular_bd():
    usuarios = []
    peliculas = []
    with open('data/u.genre', 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                nombre, id_categoria = line.strip().split('|')
                Categoria.objects.get_or_create(id_categoria=int(id_categoria), nombre=nombre)
    with open('data/u.occupation', 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                nombre = line.strip()
                Ocupacion.objects.get_or_create(nombre=nombre)
    with open('data/u.user', 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                id_usuario, edad, sexo, ocupacion_nombre, codigo_postal = line.strip().split('|')
                ocupacion = Ocupacion.objects.get(nombre=ocupacion_nombre)
                usuario, _ = Usuario.objects.get_or_create(
                    id_usuario=int(id_usuario),
                    edad=int(edad),
                    sexo=sexo,
                    ocupacion=ocupacion,
                    codigo_postal=codigo_postal
                )
                usuarios.append(usuario)
    with open('data/u.item', 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                partes = line.strip().split('|')
                id_pelicula = int(partes[0])
                titulo = partes[1]
                fecha_estreno = datetime.strptime(partes[2], '%d-%b-%Y') if partes[2] else None
                imdb_url = partes[4]
                pelicula, _ = Pelicula.objects.get_or_create(
                    id_pelicula=id_pelicula,
                    titulo=titulo,
                    fecha_estreno=fecha_estreno,
                    imdb_url=imdb_url
                )
                categorias_ids = [int(cat_id) for cat_id in partes[5:] if cat_id.isdigit()]
                for i in range(len(categorias_ids)):
                    categoria = Categoria.objects.get(id_categoria=i)
                    pelicula.categorias.add(categoria)
                peliculas.append(pelicula)
    with open('data/u.data', 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                id_usuario, id_pelicula, puntuacion_valor, _ = line.strip().split('\t')
                usuario = Usuario.objects.get(id_usuario=int(id_usuario))
                pelicula = Pelicula.objects.get(id_pelicula=int(id_pelicula))
                Puntuacion.objects.get_or_create(
                    usuario=usuario,
                    pelicula=pelicula,
                    puntuacion=int(puntuacion_valor)
                )
def recargar_datos(request):
    # Borrar tablas existentes
    Puntuacion.objects.all().delete()
    Usuario.objects.all().delete()
    Pelicula.objects.all().delete()
    Categoria.objects.all().delete()
    Ocupacion.objects.all().delete()
    
    # Popular la base de datos
    popular_bd()

    return HttpResponseRedirect("/")
    
def index(request):
    return render(request, 'index.html', {'STATIC_URL':settings.STATIC_URL})

def mostrar_ocupaciones(request):
    usuarios= Usuario.objects.all().order_by('ocupacion')
    return render(request, 'ocupacion_usuarios.html',{'usuarios':usuarios, 'STATIC_URL':settings.STATIC_URL})

def mostrar_mejores_peliculas(request,pag):
    if pag > 5:
        pag = 5
    else:
        if pag < 1:
            pag = 1
    #peliculas con más de 100 puntuaciones
    peliculas = Pelicula.objects.annotate(avg_rating=Avg('puntuacion__puntuacion'),num_rating=Count('puntuacion__puntuacion')).filter(num_rating__gt=100).order_by('-avg_rating')[(pag-1)*10:pag*10]
    return render(request, 'mejores_peliculas.html', {'peliculas':peliculas, 'pagina':pag, 'STATIC_URL':settings.STATIC_URL})

def mostrar_peliculas_year(request):
    formulario = PeliculaBusquedaYearForm()
    peliculas = None
    anyo = None
    
    if request.method=='POST':
        formulario = PeliculaBusquedaYearForm(request.POST)
        
        if formulario.is_valid():
            anyo=formulario.cleaned_data['year']
            peliculas = Pelicula.objects.filter(fecha_estreno__year=anyo)
    
    return render(request, 'busqueda_peliculas.html', {'formulario':formulario, 'peliculas':peliculas, 'anyo':anyo, 'STATIC_URL':settings.STATIC_URL})


def mostrar_puntuaciones_usuario(request):
    formulario = UsuarioBusquedaForm()
    puntuaciones = None
    idusuario = None
    
    if request.method=='POST':
        formulario = UsuarioBusquedaForm(request.POST)
        
        if formulario.is_valid():
            idusuario = formulario.cleaned_data['idUsuario']
            puntuaciones = Puntuacion.objects.filter(usuario_id = Usuario.objects.get(pk=idusuario))
            
    return render(request, 'puntuaciones_usuario.html', {'formulario':formulario, 'puntuaciones':puntuaciones, 'idusuario':idusuario, 'STATIC_URL':settings.STATIC_URL})
