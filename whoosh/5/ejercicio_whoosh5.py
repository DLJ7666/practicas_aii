import os
import re
import shutil
import tkinter as tk
import urllib.request
from tkinter import messagebox
from datetime import datetime
from bs4 import BeautifulSoup
from whoosh.fields import DATETIME, ID, TEXT, Schema
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser
from whoosh.query import Every

indexdir = "practicas\\practicas_aii\\whoosh\\5\\indexdir"
enlace="https://muzikalia.com/category/noticia/page/1"
meses = {
    "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
    "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
    "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12"
    }

def extraer_datos_noticias(url):
    f = urllib.request.urlopen(url)
    s = BeautifulSoup(f, "html.parser")
    noticias = s.find_all("article")
    lista_noticias = []
    for noticia in noticias:
        titulo = noticia.find("header").text.strip()
        fecha = noticia.find("time")["datetime"]
        autor = noticia.find("a", class_="url fn n").text.strip()
        resumen = noticia.find("div", class_="cm-entry-summary").find("p").text.strip()
        enlace = noticia.find("a", class_="cm-entry-button")['href'].strip()
        lista_noticias.append((titulo, datetime.fromisoformat(fecha), autor, resumen, enlace))

    return lista_noticias

def extraer_lista_noticias(num_pags):
    lista_noticias = []
    
    for num_paginas in range(1,num_pags+1):
        url = "https://muzikalia.com/category/noticia/page/" + str(num_paginas)
        lista_noticias.extend(extraer_datos_noticias(url))

    return lista_noticias

def almacenar_esquema(num_pags):
    lista_noticias = extraer_lista_noticias(num_pags)
    esquema = Schema(titulo=TEXT(stored=True),
                    fecha=DATETIME(stored=True),
                    autor=ID(stored=True),
                    resumen=TEXT(stored=True),
                    enlace=TEXT(stored=True))
    if os.path.exists(indexdir):
        shutil.rmtree(indexdir)
    os.mkdir(indexdir)

    ix = create_in(indexdir, esquema)
    writer = ix.writer()
    i=0
    for noticia in lista_noticias:
        writer.add_document(titulo=str(noticia[0]), fecha=noticia[1],
                            autor=str(noticia[2]), resumen=str(noticia[3]),
                            enlace=str(noticia[4]))
        i+=1
    writer.commit()
    messagebox.showinfo("Indexación completa", f"Se han indexado {i} noticias.")


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

def listar_noticias(noticias):
    v = tk.Toplevel()
    v.title("Listado de noticias")
    sc = tk.Scrollbar(v)
    sc.pack(side=tk.RIGHT, fill=tk.Y)
    lb = tk.Listbox(v, width=150, yscrollcommand=sc.set)
    for n in noticias:
        s = n["titulo"]
        lb.insert(tk.END, s)
        lb.insert(tk.END, "-" * 120)
        s = ("  AUTOR: " + str(n["autor"]) + 
            " | FECHA: " + str(n["fecha"]) +
            " | RESUMEN: " + str(n["resumen"]) +
            " | ENLACE: " + str(n["resumen"]))
        lb.insert(tk.END, s)
        lb.insert(tk.END, "\n")
    lb.pack(side=tk.LEFT, fill=tk.BOTH)
    sc.config(command=lb.yview)
        
def listar_todas():
    ix = open_dir(indexdir)
    with ix.searcher() as searcher:
        results = searcher.search(Every(), limit=None)
        listar_noticias(results)
    

def buscar_por_autor():
    def buscar():
        with ix.searcher() as searcher:
            entry = text.get()
            print(entry)
            query = QueryParser("autor", schema=ix.schema).parse(entry)
            results = searcher.search(query, limit=None)
            listar_noticias(results)
            
    def listar_autores():
        with ix.searcher() as searcher:
            results = searcher.search(Every("autor"), limit=None)
            autores = set()
            for r in results:
                autores.add(r["autor"])
            return sorted(autores)

    ix = open_dir(indexdir)
    autores = listar_autores()
    ventana = tk.Toplevel()
    ventana.title("Búsqueda por autor")
    text = tk.Spinbox(ventana,values=autores, text="Introduzca el autor a buscar:")
    text.pack(side=tk.LEFT)
    button = tk.Button(ventana, text="Buscar", command=buscar)
    button.pack(side=tk.LEFT)

def eliminar_por_resumen():
    resultados_a_eliminar = []
    def buscar(event):
        with ix.searcher() as searcher:
            entry = text.get()
            query = QueryParser("resumen", schema=ix.schema).parse(entry)
            results = searcher.search(query, limit=None)
            if len(results) > 0:
                resultados_a_eliminar = results
            listar_titulos(results)

    def listar_titulos(resultados):
        v = tk.Toplevel()
        v.title("Listado de títulos a eliminar")
        sc = tk.Scrollbar(v)
        sc.pack(side=tk.RIGHT, fill=tk.Y)
        lb = tk.Listbox(v, width=150, yscrollcommand=sc.set)
        for r in resultados:
            lb.insert(tk.END, r["titulo"])
            lb.insert(tk.END, "-" * 120)
        lb.pack(side=tk.LEFT, fill=tk.BOTH)
        sc.config(command=lb.yview)
        tk.Button(v, text="Confirmar", command=eliminar).pack(side=tk.BOTTOM)

    def eliminar():
        with ix.writer() as writer:
            for r in resultados_a_eliminar:
                writer.delete_by_term('titulo', r['titulo'])
        messagebox.showinfo("Eliminación completa", f"Se han eliminado {len(resultados_a_eliminar)} noticias.")

    ix = open_dir(indexdir)
    ventana = tk.Toplevel()
    ventana.title("Eliminar por resumen")
    label = tk.Label(ventana,text="Introduzca el texto a buscar en el resumen:")
    label.pack()
    text = tk.Entry(ventana, width=90)
    text.pack(side=tk.LEFT)
    text.bind("<Return>", buscar)

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
    menubuscar.add_command(label="Autor", command=buscar_por_autor)
    menubuscar.add_command(label="Eliminar por resumen", command=eliminar_por_resumen)
    menu.add_cascade(label="Buscar", menu=menubuscar)
    raiz.config(menu=menu)

    raiz.mainloop()

if __name__ == "__main__":
    ventana_principal()