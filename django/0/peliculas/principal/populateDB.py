#encoding:utf-8
from principal.models import Genero, Director, Pais, Pelicula

from bs4 import BeautifulSoup
import urllib.request
from datetime import datetime

#función auxiliar que hace scraping en la web y carga los datos en la base datos
def populateDB():
    
    #borramos todas las tablas de la BD
    Director.objects.all().delete()
    Pais.objects.all().delete()
    Genero.objects.all().delete()
    Pelicula.objects.all().delete()
    
    #extraemos los datos de la web con BS
    for pag in range(1,3):
        f = urllib.request.urlopen("https://www.elseptimoarte.net/estrenos/"+str(pag))
        s = BeautifulSoup(f, "html.parser")
        lista_link_peliculas = s.find("ul", class_="elements").find_all("li")
        for link_pelicula in lista_link_peliculas:
            f = urllib.request.urlopen("https://www.elseptimoarte.net/"+link_pelicula.a['href'])
            s = BeautifulSoup(f, "html.parser")
            aux = s.find("main", class_="informativo").find_all("section",class_="highlight")
            datos = aux[0].div.dl
            titulo_original = datos.find("dt",string="Título original").find_next_sibling("dd").string.strip()
            #si no tiene título se pone el título original
            if (datos.find("dt",string="Título")):
                titulo = datos.find("dt",string="Título").find_next_sibling("dd").string.strip()
            else:
                titulo = titulo_original
            paises = "".join(datos.find("dt",string="País").find_next_sibling("dd").stripped_strings)
            pais = paises.split(sep=",")[0]  #sólo se pide el primer país
            fecha = datetime.strptime(datos.find("dt",string="Estreno en España").find_next_sibling("dd").string.strip(), '%d/%m/%Y')
            
            generos_director = s.find("div",id="datos_pelicula")
            generos = "".join(generos_director.find("p",class_="categorias").stripped_strings)
            generos = generos.split(sep=",")
            directores = "".join(generos_director.find("p",class_="director").stripped_strings)
            director = directores.split(sep=",")[0]  #sólo se pide el primer director 
            
            #almacenamos en la BD
            director_obj = Director.objects.get_or_create(nombre=director)[0]
            pais_obj = Pais.objects.get_or_create(nombre=pais)[0]
            lista_generos_obj = []
            for genero in generos:
                genero_obj = Genero.objects.get_or_create(nombre=genero)[0]
                lista_generos_obj.append(genero_obj)
            p = Pelicula.objects.create(titulo = titulo, tituloOriginal = titulo_original,
                                    fechaEstreno = fecha,
                                    pais = pais_obj,
                                    director = director_obj)
            #añadimos la lista de géneros a la película
            p.generos.set(lista_generos_obj)

    return ((Pelicula.objects.count(), Director.objects.count(), Genero.objects.count(), Pais.objects.count()))
