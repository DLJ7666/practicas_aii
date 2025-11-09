from bs4 import BeautifulSoup
import urllib.request
import tkinter as tk
from tkinter import messagebox
import re, os, shutil
from datetime import datetime
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, DATETIME, KEYWORD, ID
from whoosh.qparser import QueryParser, MultifieldParser, OrGroup

indexdir = "practicas\\practicas_aii\\whoosh\\3\\indexdir"
enlace="https://www.elseptimoarte.net/estrenos/2024/"
meses = {
    "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
    "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
    "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12"
    }

def extraer_peliculas(num_pags):
    #devuelve una lista de tuplas. Cada tupla tiene la información requerida de una pelicula
    lista_peliculas = []
        
    for i in range(1,num_pags+1):
        lista_pagina = extraer_pelicula(enlace+str(i))
        lista_peliculas.extend(lista_pagina)
    return lista_peliculas

def extraer_pelicula(url):
    
    lista =[]
    
    f = urllib.request.urlopen(url)
    s = BeautifulSoup(f, "html.parser")
    lista_link_peliculas = s.find("ul", class_="elements")
    if lista_link_peliculas: # por si no hay cuatro pÃ¡ginas
        lista_link_peliculas = s.find("ul", class_="elements").find_all("li")
    else:
        lista_link_peliculas = []
    for link_pelicula in lista_link_peliculas:
        url_detalle = link_pelicula.a['href']
        f = urllib.request.urlopen("https://www.elseptimoarte.net/"+url_detalle)
        s = BeautifulSoup(f, "html.parser")
        aux = s.find("main", class_="informativo").find_all("section",class_="highlight")
        datos = aux[0].div.dl
        titulo_original = datos.find("dt",string="Título original").find_next_sibling("dd").string.strip()
        #si no tiene título se pone el título original
        if (datos.find("dt",string="Título")):
            titulo = datos.find("dt",string="Título").find_next_sibling("dd").string.strip()
        else:
            titulo = titulo_original
        if(datos.find("dt",string="País")):
            pais = "".join(datos.find("dt",string="País").find_next_sibling("dd").stripped_strings)
        else:
            pais="Desconocido"
        fecha = datetime.strptime(datos.find("dt",string="Estreno en España").find_next_sibling("dd").string.strip(), '%d/%m/%Y')
        
        sinopsis = aux[1].div.text.strip()
        
        generos_director = s.find("div",id="datos_pelicula")
        generos = "".join(generos_director.find("p",class_="categorias").stripped_strings)
        director = "".join(generos_director.find("p",class_="director").stripped_strings)
        lista.append((titulo,titulo_original,pais,fecha,director,generos,sinopsis,url_detalle))
        
    return lista

def almacenar_datos(num_pags):
    
    #define el esquema de la información
    schem = Schema(titulo=TEXT(stored=True,phrase=False), titulo_original=TEXT(stored=True,phrase=False), pais=KEYWORD(stored=True,commas=True,lowercase=True), fecha=DATETIME(stored=True), director=KEYWORD(stored=True,commas=True,lowercase=True), generos=KEYWORD(stored=True,commas=True,lowercase=True), sinopsis=TEXT(stored=True,phrase=False), url=ID(stored=True,unique=True))
    
    #eliminamos el directorio del índice, si existe
    if os.path.exists(indexdir):
        shutil.rmtree(indexdir)
    os.mkdir(indexdir)
    
    #creamos el índice
    ix = create_in(indexdir, schema=schem)
    #creamos un writer para poder añadir documentos al indice
    writer = ix.writer()
    i=0
    lista=extraer_peliculas(num_pags)
    for pelicula in lista:
        #añade cada pelicula de la lista al índice
        writer.add_document(titulo=str(pelicula[0]), titulo_original=str(pelicula[1]), pais=str(pelicula[2]), fecha=pelicula[3], director=str(pelicula[4]), generos=str(pelicula[5]), sinopsis=str(pelicula[6]), url=str(pelicula[7]))    
        i+=1
    writer.commit()
    messagebox.showinfo("Fin de indexado", "Se han indexado "+str(i)+ " películas")

def cargar():
    def cargar_datos(event):
        num_pags = int(text.get())
        almacenar_datos(num_pags)

    respuesta = messagebox.askyesno(title="Confirmar",
                message="Esta seguro que quiere recargar los datos. " \
                "\nEsta operación puede ser lenta.")
    if respuesta:
        ventana = tk.Toplevel()
        label = tk.Label(ventana,text="Introduzca el número de páginas a cargar:")
        label.pack()
        text = tk.Entry(ventana)
        text.bind("<Return>", cargar_datos)
        text.pack(side=tk.LEFT)

def buscar_titulo_sinopsis():
    def mostrar_lista(event):
        #abrimos el índice
        ix=open_dir(indexdir)
        #creamos un searcher en el índice
        with ix.searcher() as searcher:
            #se crea la consulta: buscamos en los campos "titulo" o "sinopsis" alguna de las palabras que hay en el Entry "en"
            #se usa la opción OrGroup para que use el operador OR por defecto entre palabras, en lugar de AND
            query = MultifieldParser(["titulo","sinopsis"], ix.schema, group=OrGroup).parse(str(en.get()))
            #llamamos a la función search del searcher, pasándole como parámetro la consulta creada
            results = searcher.search(query) #sólo devuelve los 10 primeros
            #recorremos los resultados obtenidos(es una lista de diccionarios) y mostramos lo solicitado
            v = tk.Toplevel()
            v.title("Listado de Peliculas")
            v.geometry('800x150')
            sc = tk.Scrollbar(v)
            sc.pack(side=tk.RIGHT, fill=tk.Y)
            lb = tk.Listbox(v, yscrollcommand=sc.set)
            lb.pack(side=tk.BOTTOM, fill = tk.BOTH)
            sc.config(command = lb.yview)
            #Importante: el diccionario solo contiene los campos que han sido almacenados(stored=True) en el Schema
            for r in results:
                lb.insert(tk.END,r['titulo'])
                lb.insert(tk.END,r['titulo_original'])
                lb.insert(tk.END,r['director'])
                lb.insert(tk.END,'')
    
    v = tk.Toplevel()
    v.title("Busqueda por Título o Sinopsis")
    l = tk.Label(v, text="Introduzca las palabras a buscar:")
    l.pack(side=tk.LEFT)
    en = tk.Entry(v)
    en.bind("<Return>", mostrar_lista)
    en.pack(side=tk.LEFT)

def buscar_generos():
    def mostrar_lista(event):
        ix=open_dir(indexdir)
        with ix.searcher() as searcher:
            #lista de todos los géneros disponibles en el campo de géneros
            lista_generos = [i.decode('utf-8') for i in searcher.lexicon('generos')]
            # en la entrada ponemos todo en minúsculas
            entrada = str(en.get().lower())
            #si la entrada no está en la lista de géneros disponibles, da un error e informa de los géneros disponibles     
            if entrada not in lista_generos:
                messagebox.showinfo("Error", "El criterio de búsqueda no es un género existente\nLos géneros existentes son: " + ",".join(lista_generos))
                return
            
            query = QueryParser("generos", ix.schema).parse('"'+entrada+'"')
            results = searcher.search(query, limit=20) #sólo devuelve los 20 primeros
            v = tk.Toplevel()
            v.title("Listado de Películas")
            v.geometry('800x150')
            sc = tk.Scrollbar(v)
            sc.pack(side=tk.RIGHT, fill=tk.Y)
            lb = tk.Listbox(v, yscrollcommand=sc.set)
            lb.pack(side=tk.BOTTOM, fill = tk.BOTH)
            sc.config(command = lb.yview)
            for r in results:
                lb.insert(tk.END,r['titulo'])
                lb.insert(tk.END,r['titulo_original'])
                lb.insert(tk.END,r['pais'])
                lb.insert(tk.END,'')
    
    v = tk.Toplevel()
    v.title("Busqueda por Género")
    l = tk.Label(v, text="Introduzca género a buscar:")
    l.pack(side=tk.LEFT)
    en = tk.Entry(v)
    en.bind("<Return>", mostrar_lista)
    en.pack(side=tk.LEFT)

def modificar_fecha():
    def modificar():
        #comprobamos el formato de la entrada
        if(not re.match("\d{8}",en1.get())):
            messagebox.showinfo("Error", "Formato del rango de fecha incorrecto")
            return
        ix=open_dir(indexdir)
        lista=[]    # lista de las películas a modificar, usamos el campo url (unique) para updates
        with ix.searcher() as searcher:
            query = QueryParser("titulo", ix.schema).parse(str(en.get()))
            results = searcher.search(query, limit=None)
            v = tk.Toplevel()
            v.title("Listado de Películas a Modificar")
            v.geometry('800x150')
            sc = tk.Scrollbar(v)
            sc.pack(side=tk.RIGHT, fill=tk.Y)
            lb = tk.Listbox(v, yscrollcommand=sc.set)
            lb.pack(side=tk.BOTTOM, fill = tk.BOTH)
            sc.config(command = lb.yview)
            for r in results:
                lb.insert(tk.END,r['titulo'])
                lb.insert(tk.END,r['fecha'])
                lb.insert(tk.END,'')
                lista.append(r) #cargamos la lista con los resultados de la búsqueda
        # actualizamos con la nueva fecha de estreno todas las películas de la lista
        respuesta = messagebox.askyesno(title="Confirmar",message="Esta seguro que quiere modificar las fechas de estrenos de estas peliculas?")
        if respuesta:
            writer = ix.writer()
            for r in lista:
                writer.update_document(url=r['url'], fecha=datetime.strptime(str(en1.get()),'%Y%m%d'), titulo=r['titulo'], titulo_original=r['titulo_original'], pais=r['pais'], director=r['director'], generos=r['generos'], sinopsis=r['sinopsis'])
            writer.commit()
    
    v = tk.Toplevel()
    v.title("Modificar Fecha Estreno")
    l = tk.Label(v, text="Introduzca Título Película:")
    l.pack(side=tk.LEFT)
    en = tk.Entry(v)
    en.pack(side=tk.LEFT)
    l1 = tk.Label(v, text="Introduzca Fecha Estreno AAAAMMDD:")
    l1.pack(side=tk.LEFT)
    en1 = tk.Entry(v)
    en1.pack(side=tk.LEFT)
    bt = tk.Button(v, text='Modificar', command=modificar)
    bt.pack(side=tk.LEFT)

def buscar_fecha():
    def mostrar_lista(event):
        #comprobamos el formato de la entrada
        if(not re.match("\d{8}\s+\d{8}",en.get())):
            messagebox.showinfo("Error", "Formato del rango de fecha incorrecto")
            return
        ix=open_dir(indexdir)
        with ix.searcher() as searcher:
            
            aux = en.get().split()
            rango_fecha = '['+ aux[0] + ' TO ' + aux[1] +']'
            query = QueryParser("fecha", ix.schema).parse(rango_fecha)
            results = searcher.search(query,limit=None) #devuelve todos los resultados
            v = tk.Toplevel()
            v.title("Listado de Películas")
            v.geometry('800x150')
            sc = tk.Scrollbar(v)
            sc.pack(side=tk.RIGHT, fill=tk.Y)
            lb = tk.Listbox(v, yscrollcommand=sc.set)
            lb.pack(side=tk.BOTTOM, fill = tk.BOTH)
            sc.config(command = lb.yview)
            for r in results:
                lb.insert(tk.END,r['titulo'])
                lb.insert(tk.END,r['fecha'])
                lb.insert(tk.END,'')
    
    v = tk.Toplevel()
    v.title("Busqueda por Fecha")
    l = tk.Label(v, text="Introduzca rango de fechas AAAAMMDD AAAAMMDD:")
    l.pack(side=tk.LEFT)
    en = tk.Entry(v)
    en.bind("<Return>", mostrar_lista)
    en.pack(side=tk.LEFT)

def ventana_principal():
    raiz = tk.Tk()

    menu = tk.Menu(raiz)

    #DATOS
    menudatos = tk.Menu(menu, tearoff=0)
    menudatos.add_command(label="Cargar", command=cargar)
    menudatos.add_separator()
    menudatos.add_command(label="Salir", command=raiz.quit)
    menu.add_cascade(label="Datos", menu=menudatos)

    #BUSCAR
    menubuscar = tk.Menu(menu, tearoff=0)
    menubuscar.add_command(label="Título o sinopsis", command=buscar_titulo_sinopsis)
    menubuscar.add_command(label="Géneros", command=buscar_generos)
    menubuscar.add_command(label="Fecha de estreno", command=buscar_fecha)
    menubuscar.add_command(label="Modificar fecha de estreno", command=modificar_fecha)
    menu.add_cascade(label="Buscar", menu=menubuscar)
    raiz.config(menu=menu)

    raiz.mainloop()

if __name__ == "__main__":
    ventana_principal()