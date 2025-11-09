import os
import re
import shutil
import tkinter as tk
import urllib.request
from tkinter import messagebox
from datetime import datetime
from bs4 import BeautifulSoup
from whoosh.fields import DATETIME, KEYWORD, NUMERIC, TEXT, Schema
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.query import Every

indexdir = "practicas\\practicas_aii\\whoosh\\4\\indexdir"
enlace="https://www.recetasgratis.net/Recetas-de-Aperitivos-tapas-listado_receta-1_"
meses = {
    "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
    "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
    "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12"
    }

def extraer_urls(num_pags):
    lista=[]
    
    for num_paginas in range(1,num_pags+1):
        url = enlace+str(num_paginas)+".html"
        f = urllib.request.urlopen(url)
        s = BeautifulSoup(f, "html.parser")
        lista_una_pagina = s.find_all("a", class_="titulo titulo--resultado")
        lista.extend([a["href"] for a in lista_una_pagina])

    return lista

def extraer_datos_receta(url):
    f = urllib.request.urlopen(url)
    s = BeautifulSoup(f, "html.parser")
    titulo = s.find("h1", class_="titulo titulo--articulo").string.strip()
    num_comensales = s.find("span", class_="property comensales")
    if num_comensales == None:
        num_comensales = int(s.find("span", class_="property unidades").string.strip().split()[0])
    else:
        num_comensales = int(num_comensales.string.strip().split()[0])
    autor = s.find("div", class_ ="nombre_autor").find("a", rel="nofollow").string.strip() 
    fecha = s.find("span", class_="date_publish").string.strip()
    fecha_list = fecha.split()
    if len(fecha_list) > 3:
        fecha_list = fecha_list[-3:]
    dia, mes_texto, anyo = fecha_list
    mes = meses[mes_texto.lower()]
    fecha_formateada = datetime(int(anyo), int(mes), int(dia))

    caracteristicas = []
    caracteristicas_div = s.find("div", class_="properties inline")
    for line in caracteristicas_div.children:
        if line.name != "span":
            line = "".join(re.split(r'<[^<>]*>', str(line))).strip()
            chars = line.split(",")
            for c in chars:
                c = c.strip()
                if c != None and c != "":
                    caracteristicas.append(c)

    intro_div = s.find("div", class_="intro")
    introduccion = ""
    if intro_div is not None:
        p = intro_div.find("p")
        if p is not None:
            introduccion = p.get_text(separator=" ", strip=True)

    return (titulo, num_comensales, autor, str(fecha_formateada.date()), ", ".join(caracteristicas), introduccion)

def extraer_lista_recetas(num_pags):
    lista_recetas = []
    lista_enlaces = extraer_urls(num_pags)
    for enlace in lista_enlaces:
        datos = extraer_datos_receta(enlace)
        lista_recetas.append(datos)
    return lista_recetas

def almacenar_esquema(num_pags):
    lista_recetas = extraer_lista_recetas(num_pags)
    esquema = Schema(titulo=TEXT(stored=True),
                     num_comensales=NUMERIC(stored=True, numtype=int),
                     autor=TEXT(stored=True),
                     fecha=DATETIME(stored=True),
                     caracteristicas=KEYWORD(stored=True, commas=True, lowercase=True),
                     introduccion=TEXT(stored=True))
    if os.path.exists(indexdir):
        shutil.rmtree(indexdir)
    os.mkdir(indexdir)
    ix = create_in(indexdir, esquema)
    writer = ix.writer()
    i=0
    for receta in lista_recetas:
        writer.add_document(titulo=str(receta[0]), num_comensales=int(str(receta[1])),
                            autor=str(receta[2]), fecha=receta[3],
                            caracteristicas=str(receta[4]), introduccion=str(receta[5]))
        i+=1
    writer.commit()
    messagebox.showinfo("Indexación completa", f"Se han indexado {i} recetas.")

def cargar():
    def cargar_datos(event):
        num_pags = int(text.get())
        almacenar_esquema(num_pags)

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

def listar_recetas(recetas):
    v = tk.Toplevel()
    v.title("LISTADO DE RECETAS")
    sc = tk.Scrollbar(v)
    sc.pack(side=tk.RIGHT, fill=tk.Y)
    lb = tk.Listbox(v, width=150, yscrollcommand=sc.set)
    for r in recetas:
        s = r["titulo"]
        lb.insert(tk.END, s)
        lb.insert(tk.END, "-" * 120)
        s = ("     COMENSALES: " + str(r["num_comensales"]) +
             " | AUTOR: " + str(r["autor"]) +
             " | FECHA ACT.: " + str(r["fecha"]) +
             " | CARACTERÍSTICAS: " + (r["caracteristicas"] if r["caracteristicas"] else "—"))
        lb.insert(tk.END, s)
        lb.insert(tk.END, "\n")
    lb.pack(side=tk.LEFT, fill=tk.BOTH)
    sc.config(command=lb.yview)

def listar_todas():
    ix = open_dir(indexdir)
    with ix.searcher() as searcher:
        results = searcher.search(Every(), limit=None)
        listar_recetas(results)

def buscar_por_titulo_o_introduccion():
    def mostrar_lista(event):
        ix=open_dir(indexdir)
        with ix.searcher() as searcher:
            query = MultifieldParser(["titulo","introduccion"], ix.schema).parse('"'+ str(en.get()) + '"')
            results = searcher.search(query,limit=3)
            listar_recetas(results)
    
    v = tk.Toplevel()
    v.title("Búsqueda por Título o Introducción")

    l1 = tk.Label(v, text="Escriba frase del título o introducción:")
    l1.pack(side=tk.LEFT)
    en = tk.Entry(v, width=75)
    en.bind("<Return>", mostrar_lista)
    en.pack(side=tk.LEFT)

def buscar_fecha():
    def mostrar_lista(event):
        ix=open_dir(indexdir)
        s = re.compile('(\d{2})/(\d{2})/(\d{4})\s+(\d{2})/(\d{2})/(\d{4})').match(str(en.get()))
        if s:
            fecha_i = s.group(3)+s.group(2)+s.group(1)
            fecha_f = s.group(6)+s.group(5)+s.group(4)
            with ix.searcher() as searcher:
                query = QueryParser("fecha", ix.schema).parse('['+fecha_i+' TO '+fecha_f+']')
                results = searcher.search(query,limit=None)
                listar_recetas(results)
        else:
            messagebox.showerror("ERROR", "formato de rango de fechas incorrecto DD/MM/AAAA DD/MM/AAAA")

    v = tk.Toplevel()
    v.title("Búsqueda por Fecha")
    l = tk.Label(v, text="Introduzca el rango de fechas (DD/MM/AAAA DD/MM/AAAA):")
    l.pack(side=tk.LEFT)
    en = tk.Entry(v, width=75)
    en.bind("<Return>", mostrar_lista)
    en.pack(side=tk.LEFT)

def buscar_caracteristicas_y_titulo():
    def mostrar_lista():
        with ix.searcher() as searcher:
            entrada = '"'+str(en.get())+'"' #se ponen comillas porque hay categorías con más de una palabra
            query = QueryParser("titulo", ix.schema).parse('caracteristicas:'+ entrada +' '+str(en1.get()))
            results = searcher.search(query,limit=10)
            listar_recetas(results)

    v = tk.Toplevel()
    v.title("Búsqueda por características y Título")
    l = tk.Label(v, text="Seleccione característica a buscar:")
    l.pack(side=tk.LEFT)

    ix = open_dir("Index")
    with ix.searcher() as searcher:
        # lista de todas las categorias disponibles en el campo de caracteristicas
        lista_caracteristicas = [i.decode('utf-8') for i in searcher.lexicon('caracteristicas')]

    en = tk.Spinbox(v, values=lista_caracteristicas, state="readonly")
    en.pack(side=tk.LEFT)

    l1 = tk.Label(v, text="Escriba palabras del título:")
    l1.pack(side=tk.LEFT)
    en1 = tk.Entry(v, width=75)
    en1.pack(side=tk.LEFT)

    b = tk.Button(v, text="Buscar", command=mostrar_lista)
    b.pack(side=tk.LEFT)

def ventana_principal():
    raiz = tk.Tk()

    menu = tk.Menu(raiz)

    #DATOS
    menudatos = tk.Menu(menu, tearoff=0)
    menudatos.add_command(label="Cargar", command=cargar)
    menudatos.add_command(label="Listar", command=listar_todas)
    menudatos.add_separator()
    menudatos.add_command(label="Salir", command=raiz.quit)
    menu.add_cascade(label="Datos", menu=menudatos)

    #BUSCAR
    menubuscar = tk.Menu(menu, tearoff=0)
    menubuscar.add_command(label="Título/Introducción", command=buscar_por_titulo_o_introduccion)
    menubuscar.add_command(label="Fecha", command=buscar_fecha)
    menubuscar.add_command(label="Características y Título", command=buscar_caracteristicas_y_titulo)
    menu.add_cascade(label="Buscar", menu=menubuscar)

    raiz.config(menu=menu)

    raiz.mainloop()

if __name__ == "__main__":
    ventana_principal()