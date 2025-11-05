import tkinter as tk
from tkinter import messagebox
from bs4 import BeautifulSoup
import re
import urllib.request
from whoosh.fields import Schema, TEXT, ID, NUMERIC, KEYWORD
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser
import os, shutil

indexdir = "practicas\\practicas_aii\\whoosh\\2\\indexdir"
enlace="https://zacatrus.es/juegos-de-mesa.html?p="

def extraer_urls(num_pags):
    lista=[]
    
    for num_paginas in range(1,num_pags+1):
        url = enlace+str(num_paginas)
        f = urllib.request.urlopen(url)
        s = BeautifulSoup(f, "html.parser")
        lista_una_pagina = s.find_all("a", class_="product photo product-item-photo")
        lista.extend([a["href"] for a in lista_una_pagina])

    return lista

def extraer_datos_juego(url):
    f = urllib.request.urlopen(url)
    s = BeautifulSoup(f, "html.parser")
    nombre = s.find("span", class_="base", itemprop="name").string.strip()
    precio = s.find("meta", itemprop="price")["content"].strip()
    tematicas = s.find("div", {"data-th": "Temática"})
    if tematicas == None:
        tematicas = "No especificada"
    else:
        tematicas = tematicas.string.strip()
    complejidad = s.find("div", {"data-th": "Complejidad"})
    if complejidad == None:
        complejidad = "No especificada"
    else:
        complejidad = complejidad.string.strip()

    numero_jugadores = s.find("div", {"data-th": "Núm. jugadores"})
    if numero_jugadores != None and numero_jugadores.string != "":
        numero_jugadores = numero_jugadores.string.strip()

    detalles = s.find("div", {"data-content-type": "text", "data-appearance": "default",
                              "data-element": "main"})
    d = ""
    if detalles is not None:
        for det in detalles.find_all("p"):
            d += "".join(re.split(r'<[^<>]*>', str(det)))
    return (nombre, float(precio), tematicas, complejidad, numero_jugadores, d)

def extraer_lista_juegos(num_pags):
    lista_juegos = []
    lista_enlaces = extraer_urls(num_pags)
    for enlace in lista_enlaces:
        datos = extraer_datos_juego(enlace)
        lista_juegos.append(datos)
    return lista_juegos

def almacenar_datos(num_pags):

    lista_juegos = extraer_lista_juegos(num_pags)
    esquema = Schema(titulo=TEXT(stored=True),
                     precio=NUMERIC(stored=True, numtype=float),
                     tematicas=KEYWORD(stored=True, commas=True, lowercase=True),
                     complejidad=ID(stored=True),
                     numero_jugadores=KEYWORD(stored=True, commas=True),
                     detalles=TEXT(stored=True))

    if os.path.exists(indexdir):
        shutil.rmtree(indexdir)
    os.mkdir(indexdir)

    ix = create_in(indexdir, schema=esquema)
    writer = ix.writer()
    i=0
    for juego in lista_juegos:
        writer.add_document(titulo=str(juego[0]), precio=float(str(juego[1])), tematicas=str(juego[2]),
                            complejidad=str(juego[3]), numero_jugadores=str(juego[4]),
                            detalles=str(juego[5]))
        i += 1

    writer.commit()
    messagebox.showinfo("Indexación completa", f"Se han indexado {i} juegos.")

def cargar():
    def cargar_datos(event):
        num_pags = int(text.get())
        almacenar_datos(num_pags)

    respuesta = messagebox.askyesno(title="Confirmar",
                message="Esta seguro que quiere recargar los datos. " \
                "\nEsta operación puede ser lenta")
    if respuesta:
        ventana = tk.Toplevel()
        label = tk.Label(ventana,text="Introduzca el número de páginas a cargar:")
        label.pack()
        text = tk.Entry(ventana)
        text.bind("<Return>", cargar_datos)
        text.pack(side=tk.LEFT)

def listar_juegos(juegos):
    v = tk.Toplevel()
    v.title("LISTADO DE JUEGOS")
    sc = tk.Scrollbar(v)
    sc.pack(side=tk.RIGHT, fill=tk.Y)
    lb = tk.Listbox(v, width=150, yscrollcommand=sc.set)
    for juego in juegos:
        s = 'JUEGO: ' + juego["titulo"]
        lb.insert(tk.END, s)
        lb.insert(tk.END, "------------------------------------------------------------------------")
        s = "     PRECIO: " + str(juego["precio"])+ " | TEMATICAS: " + str(juego["tematicas"]) + \
            " | COMPLEJIDAD: " + str(juego["complejidad"]) + \
            " | NUMERO JUGADORES: " + str(juego["numero_jugadores"])
        lb.insert(tk.END, s)
        lb.insert(tk.END,"\n\n")
    lb.pack(side=tk.LEFT, fill=tk.BOTH)
    sc.config(command=lb.yview)

def buscar_por_detalles():
    def buscar(event):
        ix = open_dir(indexdir)
        with ix.searcher() as searcher:
            entry = str(text.get().lower())
            query = QueryParser("detalles", ix.schema).parse('"' + entry + '"')
            results = searcher.search(query, limit=10)
            listar_juegos(results)

    ventana = tk.Toplevel()
    ventana.title("Búsqueda por detalles")
    label = tk.Label(ventana,text="Introduzca el texto a buscar en los detalles:")
    label.pack()
    text = tk.Entry(ventana, width=90)
    text.bind("<Return>", buscar)
    text.pack(side=tk.LEFT)

def buscar_por_tematica():
    def buscar(event):
        with ix.searcher() as searcher:
            entry = str(text.get().lower())
            query = QueryParser("tematicas", ix.schema).parse('"' + entry + '"')
            results = searcher.search(query, limit=None)
            listar_juegos(results)

    ventana = tk.Toplevel()
    ventana.title("Búsqueda por temática")
    label = tk.Label(ventana,text="Introduzca la temática:")
    label.pack()
    ix = open_dir(indexdir)
    with ix.searcher() as searcher:
        tematicas = [i.decode("utf-8") for i in searcher.lexicon("tematicas")]
    text = tk.Spinbox(ventana, values = tematicas, state= "readonly")
    text.bind("<Return>", buscar)
    text.pack(side=tk.LEFT)

def buscar_por_precio():
    def buscar(event):
        if not re.match('\d+\.\d+', text.get().strip()):
            messagebox.showerror("Error de entrada", "El precio debe ser un número con decimales (por ejemplo 19.99)")
            return
        ix = open_dir(indexdir)
        with ix.searcher() as searcher:
            query = QueryParser("precio", ix.schema).parse('[TO '+str(text.get().strip())+'}')
            results = searcher.search(query, limit=None)
            listar_juegos(results)

    ventana = tk.Toplevel()
    ventana.title("Búsqueda por precio")
    label = tk.Label(ventana,text="Introduzca el precio máximo:")
    label.pack(side=tk.LEFT)
    text = tk.Entry(ventana)
    text.bind("<Return>", buscar)
    text.pack(side=tk.LEFT)

def buscar_por_numero_jugadores():
    def mostrar_lista(event):
        if not re.match('\d+', en.get().strip()):
            messagebox.showinfo("ERROR", "Formato incorrecto (dd)")
            return
        ix=open_dir("Index")
        with ix.searcher() as searcher:
            query = QueryParser("jugadores", ix.schema).parse(str(en.get().strip()))
            results = searcher.search(query,limit=None)
            listar_juegos(results)
    
    ventana = tk.Toplevel()
    ventana.title("Búsqueda por Jugadores")
    label = tk.Label(ventana, text="Introduzca el número de jugadores:")
    label.pack(side=tk.LEFT)
    en = tk.Entry(ventana)
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
    menubuscar.add_command(label="Detalles", command=buscar_por_detalles)
    menubuscar.add_command(label="Temática", command=buscar_por_tematica)
    menubuscar.add_command(label="Precio", command=buscar_por_precio)
    menubuscar.add_command(label="Número de jugadores", command=buscar_por_numero_jugadores)
    menu.add_cascade(label="Buscar", menu=menubuscar)

    raiz.config(menu=menu)
 
    raiz.mainloop()

if __name__ == "__main__":
    ventana_principal()