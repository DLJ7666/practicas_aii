import sqlite3
import tkinter as tk
import urllib.request
from datetime import datetime
from tkinter import messagebox

from bs4 import BeautifulSoup

enlace="https://www.sevilla.org/ayuntamiento/alcaldia/comunicacion/calendario/agenda-actividades"
base_datos = "actividades.db"

def almacenar_bd():
    conn = sqlite3.connect(base_datos)
    conn.text_factory = str
    conn.execute("DROP TABLE IF EXISTS ACTIVIDADES")
    conn.execute('''CREATE TABLE ACTIVIDADES
                 (TITULO TEXT NOT NULL,
                 DESCRIPCION TEXT,
                 LUGAR TEXT NOT NULL,
                 FECHA_INICIO DATE NOT NULL,
                 FECHA_FIN DATE,
                 HORA_INICIO TIME,
                 HORA_FIN TIME
                )''')
    for i in extraer_datos(enlace):
        conn.execute("""INSERT INTO ACTIVIDADES VALUES (?,?,?,?,?,?,?)""",
                     (i['titulo'], i['descripcion'], i['lugar'], str(i['fecha_inicio']),
                      str(i['fecha_fin']), str(i['hora_inicio']), str(i['hora_fin'])))
    conn.commit()
    cursor = conn.execute("SELECT COUNT(*) FROM ACTIVIDADES")
    messagebox.showinfo("Base Datos",
                        "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " actividades.")
    conn.close()

def extraer_datos(enlace):
    res = []
    pagina = urllib.request.urlopen(enlace)
    s = BeautifulSoup(pagina, 'html.parser')
    actividades = s.find_all("div", {"class": "cal_info clearfix"})
    for actividad in actividades:
        titulo = actividad.find("span", {"class": "summary"}).string.strip()
        descripcion = actividad.find("p", {"class": "description"})
        if descripcion is not None:
            descripcion = descripcion.string.strip()
        url_lugar = actividad.find('a')['href']
        lugar = extraer_lugar(url_lugar)
        fechahora_inicio = actividad.find("abbr", {"class": "dtstart"})['title']
        fechahora_inicio = parsear_fechahora(fechahora_inicio)
        fecha_inicio = fechahora_inicio[0]
        hora_inicio = fechahora_inicio[1]
        fechahora_fin = actividad.find("abbr", {"class": "dtend"})
        fecha_fin = None
        hora_fin = None
        if fechahora_fin is not None:
            fechahora_fin = fechahora_fin['title']
            fechahora_fin = parsear_fechahora(fechahora_fin)
            fecha_fin = fechahora_fin[0]
            hora_fin = fechahora_fin[1]
        res.append({
            "titulo": titulo,
            "descripcion": descripcion,
            "lugar": lugar,
            "fecha_inicio": fecha_inicio,
            "hora_inicio": hora_inicio,
            "fecha_fin": fecha_fin,
            "hora_fin": hora_fin
        })
    return res

def extraer_lugar(enlace):
    lugar = None
    response = urllib.request.urlopen(enlace)
    soup = BeautifulSoup(response, 'html.parser')
    lugar = soup.find("span", {"itemprop": "location"})
    if lugar is not None:
        lugar = lugar.string.strip()
    return lugar

def parsear_fechahora(fechahora):
    fechahora_obj = datetime.fromisoformat(fechahora)
    fecha = fechahora_obj.date()
    hora = fechahora_obj.time()
    return fecha, hora

def cargar_datos():
    respuesta = tk.messagebox.askyesno(title="Confirmar",
                                       message="Se va a proceder a cargar los datos en la base de datos. Esto puede tardar unos minutos. ¿Desea continuar?")
    if respuesta:
        almacenar_bd()

def listar_todos():
    conn = sqlite3.connect(base_datos)
    conn.text_factory = str
    cursor = conn.execute("SELECT * FROM ACTIVIDADES ORDER BY FECHA_INICIO, HORA_INICIO")
    conn.close
    listar_actividades(cursor)

def listar_actividades(cursor):
    v = tk.Toplevel()
    sc = tk.Scrollbar(v)
    sc.pack(side=tk.RIGHT, fill=tk.Y)
    lb = tk.Listbox(v, width=150, yscrollcommand=sc.set)
    for row in cursor:
        title = row[0]
        desc = row[1] if row[1] is not None else ""
        lugar = row[2]
        fecha_inicio = row[3] if row[3] is not None else ""
        fecha_fin = row[4] if row[4] is not None else ""
        hora_inicio = row[5] if row[5] is not None else ""
        hora_fin = row[6] if row[6] is not None else ""
        lb.insert(tk.END, f'ACTIVIDAD: {title}')
        lb.insert(tk.END, "------------------------------------------------------------------------")
        s = f"     TITULO: {title} | DESCRIPCION: {desc} | LUGAR: {lugar} | FECHA INICIO: {fecha_inicio} | HORA INICIO: {hora_inicio} | FECHA FIN: {fecha_fin} | HORA FIN: {hora_fin}"
        lb.insert(tk.END, s)
        lb.insert(tk.END, "\n\n")
    lb.pack(side=tk.LEFT, fill=tk.BOTH)
    sc.config(command=lb.yview)

def listar_proximas():
    conn = sqlite3.connect(base_datos)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    today = datetime.now().date()
    cur.execute(
            "SELECT * FROM ACTIVIDADES WHERE FECHA_INICIO >= ? ORDER BY FECHA_INICIO, HORA_INICIO LIMIT 5",
            (today,)
        )
    rows = cur.fetchall()
    conn.close()

    v = tk.Toplevel()
    v.title("Próximas actividades")
    sc = tk.Scrollbar(v)
    sc.pack(side=tk.RIGHT, fill=tk.Y)
    lb = tk.Listbox(v, width=150, yscrollcommand=sc.set)
    if not rows:
        lb.insert(tk.END, "No hay actividades próximas.")
    else:
        for r in rows:
            titulo = r['TITULO']
            descripcion = r['DESCRIPCION'] if r['DESCRIPCION'] is not None else ""
            lugar = r['LUGAR']
            fecha_inicio = r['FECHA_INICIO'] if r['FECHA_INICIO'] is not None else ""
            hora_inicio = r['HORA_INICIO'] if r['HORA_INICIO'] is not None else ""
            fecha_fin = r['FECHA_FIN'] if r['FECHA_FIN'] is not None else ""
            hora_fin = r['HORA_FIN'] if r['HORA_FIN'] is not None else ""

            lb.insert(tk.END, f"TITULO: {titulo}")
            lb.insert(tk.END, f"  DESCRIPCION: {descripcion}")
            lb.insert(tk.END, f"  LUGAR: {lugar}")
            lb.insert(tk.END, f"  FECHA INICIO: {fecha_inicio}    HORA INICIO: {hora_inicio}")
            lb.insert(tk.END, f"  FECHA FIN: {fecha_fin}    HORA FIN: {hora_fin}")
            lb.insert(tk.END, "------------------------------------------------------------------------")

    lb.pack(side=tk.LEFT, fill=tk.BOTH)
    sc.config(command=lb.yview)

def buscar_por_lugar():
    def listar(event):
            conn = sqlite3.connect(base_datos)
            conn.text_factory = str
            cursor = conn.execute("SELECT * FROM ACTIVIDADES WHERE LUGAR LIKE ?", ('%' + lugar_spin.get() + '%',))
            conn.close
            listar_actividades(cursor)
    conn = sqlite3.connect(base_datos)
    conn.text_factory = str
    cursor = conn.execute("SELECT DISTINCT LUGAR FROM ACTIVIDADES ORDER BY LUGAR")
    lugares = [u[0] for u in cursor]
    ventana = tk.Toplevel()
    tk.Label(ventana, text="Seleccione el lugar deseado:")
    lugar_spin = tk.Spinbox(ventana, values=lugares, width=50)
    lugar_spin.pack(side=tk.LEFT)
    lugar_spin.bind("<Return>", listar)
    conn.close()
    
def buscar_por_fecha():
    def listar(event):
            conn = sqlite3.connect(base_datos)
            conn.text_factory = str
            cursor = conn.execute("SELECT * FROM ACTIVIDADES WHERE FECHA_INICIO = ? OR (FECHA_FIN IS NOT NULL AND ? BETWEEN FECHA_INICIO AND FECHA_FIN) ORDER BY HORA_INICIO",
                                  (datetime.strptime(fecha.get(), "%d-%m-%Y").date(), datetime.strptime(fecha.get(), "%d-%m-%Y").date()))
            conn.close
            listar_actividades(cursor)
    ventana = tk.Toplevel()
    label = tk.Label(ventana, text="Indique la fecha deseada en formato DD-MM-YYYY:")
    label.pack(side=tk.LEFT)
    fecha = tk.Entry(ventana)
    fecha.pack(side=tk.LEFT)
    fecha.bind("<Return>", listar)

def listar_matinales():
    conn = sqlite3.connect(base_datos)
    conn.text_factory = str
    cursor = conn.execute("SELECT * FROM ACTIVIDADES WHERE HORA_INICIO < ? OR HORA_INICIO IS NULL ORDER BY FECHA_INICIO, HORA_INICIO", ("12:00:00",))
    rows = cursor.fetchall()
    conn.close
    if not rows:
        v = tk.Toplevel()
        v.title("Actividades matinales")
        lb = tk.Listbox(v, width=150)
        lb.insert(tk.END, "No hay actividades matinales.")
        lb.pack()
        return
    listar_actividades(rows)

def ventana_principal():
    raiz = tk.Tk()

    menu = tk.Menu(raiz)

    #DATOS
    menudatos = tk.Menu(menu, tearoff=0)
    menudatos.add_command(label="Cargar", command=cargar_datos)
    menudatos.add_separator()
    menudatos.add_command(label="Salir", command=raiz.quit)
    menu.add_cascade(label="Datos", menu=menudatos)

    # LISTAR
    menulistar = tk.Menu(menu, tearoff=0)
    menulistar.add_command(label="Todas las actividades", command=listar_todos)
    menulistar.add_command(label="Próximas actividades", command=listar_proximas)
    menu.add_cascade(label="Listar", menu=menulistar)

    #BUSCAR
    menubuscar = tk.Menu(menu, tearoff=0)
    menubuscar.add_command(label="Actividades por lugar", command=buscar_por_lugar)
    menubuscar.add_command(label="Actividades por fecha", command=buscar_por_fecha)
    menubuscar.add_command(label="Actividades matinales", command=listar_matinales)
    menu.add_cascade(label="Buscar", menu=menubuscar)

    raiz.config(menu=menu)

    raiz.mainloop()

if __name__ == "__main__":
    ventana_principal()