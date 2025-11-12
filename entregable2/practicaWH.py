import os
import re
import shutil
import tkinter as tk
import urllib.request
from datetime import datetime
from tkinter import messagebox

from bs4 import BeautifulSoup
from whoosh.fields import DATETIME, ID, TEXT, Schema
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser
from whoosh.query import Every, And, Or

indexdir = "indexdir"
enlace="https://www.sensacine.com/noticias/?page="
meses = {
    "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
    "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
    "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12"
    }

def extraer_datos_noticias(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    f = urllib.request.urlopen(req)
    s = BeautifulSoup(f, "html.parser")
    noticias = s.find_all("div", {"class": "news-card"})
    lista_noticias = []
    for noticia in noticias:
        categoria = noticia.find("div", class_="meta-category").get_text(strip=True).split("-")[1].strip()
        titulo = noticia.find("a", class_="meta-title-link").text.strip() if noticia.find("a", class_="meta-title-link") else None
        enlace = noticia.find("a", class_= "meta-title-link")['href'].strip() if noticia.find("a", class_="meta-title-link") else None
        descripcion = noticia.find("div", class_="meta-body").text.strip() if noticia.find("div", class_="meta-body") else None
        fecha = s.find("div", class_="meta-date").text.strip()
        fecha_list = fecha.split(" de ")
        if len(fecha_list) > 3:
            fecha_list = fecha_list[-3:]
        dia, mes_texto, anyo = fecha_list
        dia = dia[-2:].strip()
        mes = meses[mes_texto.lower()]
        fecha_formateada = datetime(int(anyo), int(mes), int(dia))

        lista_noticias.append((categoria, titulo, enlace, descripcion, str(fecha_formateada.date())))

    return lista_noticias

def extraer_lista_noticias(num_pags):
    lista_noticias = []
    
    for num_paginas in range(1,num_pags+1):
        url = enlace + str(num_paginas)
        lista_noticias.extend(extraer_datos_noticias(url))

    return lista_noticias

def almacenar_esquema(num_pags):
    lista_noticias = extraer_lista_noticias(num_pags)
    esquema = Schema(titulo=TEXT(stored=True),
                    categoria=ID(stored=True),
                    enlace=TEXT(stored=True),
                    descripcion=TEXT(stored=True),
                    fecha=DATETIME(stored=True))
    if os.path.exists(indexdir):
        confirmacion = messagebox.askyesno(title="Confirmar",
                message="El índice ya existe. ¿Desea sobrescribirlo?")
        if not confirmacion:
            messagebox.showinfo("Operación cancelada", "No se ha modificado el índice.")
            return
        else:
            shutil.rmtree(indexdir)

    os.mkdir(indexdir)
    ix = create_in(indexdir, esquema)
    writer = ix.writer()
    i=0
    for noticia in lista_noticias:
        writer.add_document(categoria=str(noticia[0]), titulo=str(noticia[1]),
                            enlace=str(noticia[2]), descripcion=str(noticia[3]),
                            fecha=noticia[4])
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

def listar_titulos_fechas(noticias):
    lista_titulos_fechas = []
    for noticia in noticias:
        lista_titulos_fechas.append((noticia['titulo'], noticia['fecha']))
    return lista_titulos_fechas

def listar_noticias(noticias):
    v = tk.Toplevel()
    v.title("Listado de noticias")
    sc = tk.Scrollbar(v)
    sc.pack(side=tk.RIGHT, fill=tk.Y)
    lb = tk.Listbox(v, width=150, yscrollcommand=sc.set)
    for noticia in noticias:
        s1 = f"CATEGORÍA: {noticia['categoria']}"
        s2 = f"TÍTULO: {noticia['titulo']}"
        s3 = f"ENLACE: {noticia['enlace']}"
        s4 = f"FECHA: {noticia['fecha']}"
        lb.insert(tk.END, s1)
        lb.insert(tk.END, s2)
        lb.insert(tk.END, s3)
        lb.insert(tk.END, s4)
        lb.insert(tk.END, "-" * 120)
    lb.pack(side=tk.LEFT, fill=tk.BOTH)
    sc.config(command=lb.yview)
    
def listar_titulos_fechas(noticias):
    lista_titulos_fechas = []
    for noticia in noticias:
        lista_titulos_fechas.append((noticia['titulo'], noticia['fecha']))
    return lista_titulos_fechas

def listar_todas():
    ix = open_dir(indexdir)
    with ix.searcher() as searcher:
        query = Every()
        noticias = searcher.search(query, limit=None)
        resultados = listar_titulos_fechas(noticias)
    v = tk.Toplevel()
    v.title("Listado de noticias")
    sc = tk.Scrollbar(v)
    sc.pack(side=tk.RIGHT, fill=tk.Y)
    lb = tk.Listbox(v, width=150, yscrollcommand=sc.set)
    for titulo, fecha in resultados:
        s = f"TÍTULO: {titulo} | FECHA: {fecha}"
        lb.insert(tk.END, s)
        lb.insert(tk.END, "-" * 120)
    lb.pack(side=tk.LEFT, fill=tk.BOTH)
    sc.config(command=lb.yview)

def buscar_por_descripcion():
    ix = open_dir(indexdir)

    v_busq = tk.Toplevel()
    v_busq.title("Búsqueda por descripción")

    label = tk.Label(v_busq, text="Introduzca una frase a buscar en la descripción:")
    label.pack(padx=10, pady=5)

    entry = tk.Entry(v_busq, width=80)
    entry.pack(side=tk.LEFT, padx=10, pady=5)
    entry.focus_set()

    def realizar_busqueda(event=None):
        frase = entry.get().strip()
        if not frase:
            messagebox.showwarning("Advertencia", "Debe introducir una frase de búsqueda.")
            return

        with ix.searcher() as searcher:
            parser = QueryParser("descripcion", ix.schema)
            query_str = f'"{frase}"'
            
            try:
                query = parser.parse(query_str)
                results = searcher.search(query, limit=10)
            except Exception as e:
                messagebox.showerror("Error de Búsqueda", f"Error al parsear la consulta: {e}")
                return

            if results:

                listar_noticias(results)
            else:
                messagebox.showinfo("Búsqueda", "No se han encontrado noticias que contengan esa frase en la descripción.")
    entry.bind("<Return>", realizar_busqueda)

    boton = tk.Button(v_busq, text="Buscar", command=realizar_busqueda)
    boton.pack(side=tk.LEFT, padx=5, pady=5)

def buscar_por_categoria_y_titulo():
    
    ix = open_dir(indexdir)

    def mostrar_lista():
        categoria_sel = spinbox_cat.get().strip()
        palabras_titulo = entry_titulo.get().strip()
        
        if not categoria_sel or not palabras_titulo:
            messagebox.showwarning("Advertencia", "Debe seleccionar una categoría e introducir palabras en el título.")
            return

        with ix.searcher() as searcher:
            categoria_q = QueryParser("categoria", ix.schema).parse(f'"{categoria_sel}"')
            
            palabras_list = palabras_titulo.split()
            query_titulo = []
            for palabra in palabras_list:
                query_titulo.append(QueryParser("titulo", ix.schema).parse(palabra))
            titulo_q = Or(query_titulo)
            
            query_str = And([categoria_q, titulo_q])
            
            try:
                
                results = searcher.search(query_str, limit=None)
                
                if results:
                    listar_noticias(results)
                else:
                    messagebox.showinfo("Búsqueda", "No se encontraron noticias con esos criterios.")
                    
            except Exception as e:
                messagebox.showerror("Error de Búsqueda", f"Ocurrió un error al ejecutar la consulta: {e}")

    v = tk.Toplevel()
    v.title("Categoría y Título")
    with ix.searcher() as searcher:
        lista_categorias = sorted([i.decode('utf-8') for i in searcher.lexicon('categoria')])

    label_cat = tk.Label(v, text="Categoría:")
    label_cat.pack(side=tk.LEFT)
    spinbox_cat = tk.Spinbox(v, values=lista_categorias, state="readonly")
    spinbox_cat.pack(side=tk.LEFT, padx=5)

    label_titulo = tk.Label(v, text="Palabras en Título:")
    label_titulo.pack(side=tk.LEFT)
    entry_titulo = tk.Entry(v, width=50)
    entry_titulo.pack(side=tk.LEFT, padx=5)

    btn_buscar = tk.Button(v, text="Buscar", command=mostrar_lista)
    btn_buscar.pack(side=tk.LEFT, padx=5)
    
def buscar_por_titulo_y_descripcion():
    ix = open_dir(indexdir)
    def realizar_busqueda():
        frase_titulo = entry_titulo.get().strip()
        palabras_desc = entry_desc.get().strip()
        
        if not frase_titulo or not palabras_desc:
            messagebox.showwarning("Advertencia", "Debe rellenar ambos campos.")
            return

        with ix.searcher() as searcher:
            try:
               
                q_titulo = QueryParser("titulo", ix.schema).parse(frase_titulo)
                q_desc = QueryParser("descripcion", ix.schema).parse(palabras_desc)
                query_str = And([q_titulo, q_desc])
                
                results = searcher.search(query_str, limit=None)
                
                if results:
                    listar_noticias(results)
                else:
                    messagebox.showinfo("Búsqueda", "No se encontraron noticias con esos criterios.")
                    
            except Exception as e:
                messagebox.showerror("Error de Búsqueda", f"Ocurrió un error al ejecutar la consulta: {e}")

    v = tk.Toplevel()
    v.title("Título y Descripción")
    
    frame_titulo = tk.Frame(v)
    label_titulo = tk.Label(frame_titulo, text="Frase en Título:")
    label_titulo.pack(side=tk.LEFT)
    entry_titulo = tk.Entry(frame_titulo, width=50)
    entry_titulo.pack(side=tk.LEFT, padx=5)
    frame_titulo.pack(pady=5, padx=5)

    frame_desc = tk.Frame(v)
    label_desc = tk.Label(frame_desc, text="Palabras en Descripción:")
    label_desc.pack(side=tk.LEFT)
    entry_desc = tk.Entry(frame_desc, width=50)
    entry_desc.pack(side=tk.LEFT, padx=5)
    frame_desc.pack(pady=5, padx=5)

    btn_buscar = tk.Button(v, text="Buscar", command=realizar_busqueda)
    btn_buscar.pack(pady=10)


def buscar_por_fecha():
    ix = open_dir(indexdir)

    def realizar_busqueda(event=None):
        rango_str = entry_fecha.get().strip()
        if not rango_str:
            messagebox.showwarning("Advertencia", "Debe introducir un rango de fechas.")
            return
            
        regex = r"(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})\s+hasta\s+(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})$"
        match = re.match(regex, rango_str, re.IGNORECASE)
        
        if not match:
            messagebox.showerror("Error de Formato",
                                 "El formato debe ser:\n"
                                 "'D de MES de AAAA hasta D de MES de AAAA'\n"
                                 "Ej: 5 de Noviembre de 2025 hasta 6 de Noviembre de 2025")
            return

        try:
            dia_i_str, mes_i_str, anio_i_str = match.group(1), match.group(2), match.group(3)
            dia_f_str, mes_f_str, anio_f_str = match.group(4), match.group(5), match.group(6)
            mes_i_num = meses.get(mes_i_str.lower())
            mes_f_num = meses.get(mes_f_str.lower())
            if not mes_i_num or not mes_f_num:
                messagebox.showerror("Error de Formato", f"Mes no reconocido: '{mes_i_str}' o '{mes_f_str}'")
                return
            fecha_i = datetime(int(anio_i_str), int(mes_i_num), int(dia_i_str))
            fecha_f = datetime(int(anio_f_str), int(mes_f_num), int(dia_f_str))

        except ValueError as e:
            messagebox.showerror("Error de Fecha", f"Fecha inválida: {e}")
            return
        except Exception as e:
            messagebox.showerror("Error", f"Error desconocido al parsear la fecha: {e}")
            return

        with ix.searcher() as searcher:
            try:
                fecha_i_whoosh = fecha_i.strftime('%Y%m%d')
                fecha_f_whoosh = fecha_f.strftime('%Y%m%d')

                query_str = f"[{fecha_i_whoosh} TO {fecha_f_whoosh}]"
                
                parser = QueryParser("fecha", ix.schema)
                query = parser.parse(query_str)
                
                results = searcher.search(query, limit=None)
                
                if results:
                    listar_noticias(results)
                else:
                    messagebox.showinfo("Búsqueda", "No se encontraron noticias en ese rango de fechas.")
                    
            except Exception as e:
                messagebox.showerror("Error de Búsqueda", f"Ocurrió un error al ejecutar la consulta: {e}")

    v = tk.Toplevel()
    v.title("Búsqueda por Fecha")
    
    label_formato = tk.Label(v, text="Formato: '5 de Noviembre de 2025 hasta 6 de Noviembre de 2025'")
    label_formato.pack(pady=5, padx=10)
    
    entry_fecha = tk.Entry(v, width=70)
    entry_fecha.pack(pady=5, padx=10)
    entry_fecha.focus_set()
    
    entry_fecha.bind("<Return>", realizar_busqueda)
    
    btn_buscar = tk.Button(v, text="Buscar", command=realizar_busqueda)
    btn_buscar.pack(pady=10)


def eliminar_por_descripcion():
    def modificar(event):
        ix=open_dir(indexdir)
        with ix.searcher() as searcher:
            query_descripcion = QueryParser("descripcion", ix.schema).parse("None")
            query_titulo = QueryParser("titulo", ix.schema).parse('%' + str(text.get()) + '%')
            results = searcher.search(And([query_descripcion, query_titulo]), limit=None)
            if len(results) > 0:
                v = tk.Toplevel()
                v.title("Listado de Noticias a Borrar")
                v.geometry('800x150')
                sc = tk.Scrollbar(v)
                sc.pack(side=tk.RIGHT, fill=tk.Y)
                lb = tk.Listbox(v, yscrollcommand=sc.set)
                lb.pack(side=tk.BOTTOM, fill = tk.BOTH)
                sc.config(command = lb.yview)
                for r in results:
                    lb.insert(tk.END,r['titulo'])
                    lb.insert(tk.END,'')
                respuesta = messagebox.askyesno(title="Confirmar",message="Esta seguro que quiere eliminar estas noticias?")
                if respuesta:
                    writer = ix.writer()
                    writer.delete_by_query(And([query_descripcion, query_titulo]))
                    writer.commit()
            else:
                messagebox.showinfo("AVISO", "No hay ninguna noticia con esas palabras en el título")
    ventana = tk.Toplevel()
    ventana.title("Eliminar noticias sin descripción")
    label = tk.Label(ventana,text="Introduzca el texto a buscar en el título:")
    label.pack()
    text = tk.Entry(ventana, width=90)
    text.pack(side=tk.LEFT)
    text.bind("<Return>", modificar)

def buscar_por_titulo_y_fecha():
    
    ix = open_dir(indexdir)

    def realizar_busqueda():
        frase_titulo = entry_titulo.get().strip()
        fecha_str = entry_fecha.get().strip()
        
        if not frase_titulo or not fecha_str:
            messagebox.showwarning("Advertencia", "Debe rellenar ambos campos.")
            return

        try:
            fecha_obj = datetime.strptime(fecha_str, '%d%m%Y')
        except ValueError:
            messagebox.showerror("Error de Formato",
                                 "Formato de fecha incorrecto. Debe ser DDMMAAAA (ej: 05112025).")
            return

        with ix.searcher() as searcher:
            try:
                parser_titulo = QueryParser("titulo", ix.schema)
                query_titulo = parser_titulo.parse(f'"{frase_titulo}"')
                
                fecha_whoosh_str = fecha_obj.strftime("%Y%m%d")
                parser_fecha = QueryParser("fecha", ix.schema)
                query_fecha = parser_fecha.parse(fecha_whoosh_str)
                
                query_fecha.boost = 2.0
                
                query_final = And([query_titulo, query_fecha])

                results = searcher.search(query_final, limit=5)
                
                if results:
                    listar_noticias(results)
                else:
                    messagebox.showinfo("Búsqueda", "No se encontraron noticias con esa frase y esa fecha.")
                    
            except Exception as e:
                messagebox.showerror("Error de Búsqueda", f"Ocurrió un error al ejecutar la consulta: {e}")

    v = tk.Toplevel()
    v.title("Título y Fecha")
    
    frame_titulo = tk.Frame(v)
    label_titulo = tk.Label(frame_titulo, text="Frase en Título:")
    label_titulo.pack(side=tk.LEFT, padx=5)
    entry_titulo = tk.Entry(frame_titulo, width=40)
    entry_titulo.pack(side=tk.LEFT, padx=5)
    frame_titulo.pack(pady=5, padx=5)

    frame_fecha = tk.Frame(v)
    label_fecha = tk.Label(frame_fecha, text="Fecha (DDMMAAAA):")
    label_fecha.pack(side=tk.LEFT, padx=5)
    entry_fecha = tk.Entry(frame_fecha, width=40)
    entry_fecha.pack(side=tk.LEFT, padx=5)
    frame_fecha.pack(pady=5, padx=5)

    btn_buscar = tk.Button(v, text="Buscar", command=realizar_busqueda)
    btn_buscar.pack(pady=10)

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
    menubuscar.add_command(label="Descripcion", command=buscar_por_descripcion)
    menubuscar.add_command(label="Categoria y Título", command=buscar_por_categoria_y_titulo)
    menubuscar.add_command(label="Título o descripción", command=buscar_por_titulo_y_descripcion)
    menubuscar.add_command(label="Fecha", command=buscar_por_fecha)
    menubuscar.add_command(label="Eliminar por Descripción", command=eliminar_por_descripcion)
    menubuscar.add_command(label="Título y fecha", command=buscar_por_titulo_y_fecha)
    menu.add_cascade(label="Buscar", menu=menubuscar)
    raiz.config(menu=menu)

    raiz.mainloop()

if __name__ == "__main__":
    ventana_principal()