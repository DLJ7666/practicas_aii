import sqlite3
import tkinter as tk
import urllib.request
from tkinter import messagebox

from bs4 import BeautifulSoup

enlace="http://resultados.as.com/resultados/futbol/primera/2023_2024/calendario/"

def extraer_jornadas(enlace):
    lista = []
    f = urllib.request.urlopen(enlace)
    s = BeautifulSoup(f, 'html.parser')
    jornadas = s.find_all('div', class_='cont-modulo resultados')
    num_jornada = 0
    for jornada in jornadas:
        num_jornada += 1
        body = jornada.find('tbody')
        partidos = body.find_all('tr')
        for partido in partidos:
            equipo_local = partido.find('td', class_=['col-equipo-local']).get_text(strip=True)
            equipo_visitante = partido.find('td', class_=['col-equipo-visitante']).get_text(strip=True)
            resultado = partido.find('td', class_=['col-resultado'])
            goles = resultado.get_text(strip=True).split('-')
            enlace_partido = resultado.find('a')['href']
            lista.append({
                'jornada': num_jornada,
                'equipo_local': equipo_local,
                'equipo_visitante': equipo_visitante,
                'goles': {
                    'local': int(goles[0]) if len(goles) > 0 else 0,
                    'visitante': int(goles[1]) if len(goles) > 1 else 0
                },
                'enlace': enlace_partido
            })
    return lista

def almacenar_bd():
    conn = sqlite3.connect('1\\jornadas.db')
    conn.text_factory = str
    conn.execute("DROP TABLE IF EXISTS PARTIDOS")
    conn.execute('''CREATE TABLE PARTIDOS
                 (JORNADA INT NOT NULL,
                 EQUIPO_LOCAL TEXT NOT NULL,
                 EQUIPO_VISITANTE TEXT NOT NULL,
                 GOL_LOCAL INT NOT NULL,
                 GOL_VISITANTE INT NOT NULL,
                 ENLACE TEXT NOT NULL
                )''')
    for i in extraer_jornadas(enlace):
        conn.execute("""INSERT INTO PARTIDOS VALUES (?,?,?,?,?,?)""",
                     (i['jornada'], i['equipo_local'], i['equipo_visitante'], i['goles']['local'], i['goles']['visitante'], i['enlace']))
    conn.commit()
    cursor = conn.execute("SELECT COUNT(*) FROM PARTIDOS")
    messagebox.showinfo("Base Datos",
                        "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " partidos.")
    conn.close()
    
def cargar():
    respuesta = messagebox.askyesno("Cargar datos", "¿Desea cargar los datos de las jornadas?" +
                                     "\nEsta operación puede ser lenta.")
    if respuesta:
        almacenar_bd()

def listar_jornadas(jornadas):
    v = tk.Toplevel()
    v.geometry("800x600")  # Establecer un tamaño mínimo para la ventana
    sc = tk.Scrollbar(v)
    sc.pack(side=tk.RIGHT, fill=tk.Y)
    lb = tk.Listbox(v, yscrollcommand=sc.set, width=80, font=("Courier", 10))  # Ancho de 80 caracteres y fuente monoespaciada
    for jornada in jornadas:
        lb.insert(tk.END, jornada[0])
        for partido in jornada[1:]:
            lb.insert(tk.END, partido)
        lb.insert(tk.END, "\n" + " "*70 + "\n")  # Espaciador más limpio
    lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)  # expand=True para que se expanda
    sc.config(command=lb.yview)

def parsear_jornada(cursor, jornada):
    res = []
    res.append("Jornada " + str(jornada) + ":")
    for fila in cursor:
        s = f"  {fila[1]} {fila[2]} - {fila[4]} {fila[3]}"
        res.append(s)
    return res
        
def listar_todas():
    conn = sqlite3.connect('1\\jornadas.db')
    jornada = 1
    jornadas = []
    while jornada <= 38:
        cursor = conn.execute("SELECT JORNADA, EQUIPO_LOCAL, GOL_LOCAL, EQUIPO_VISITANTE, GOL_VISITANTE FROM PARTIDOS WHERE JORNADA=?", (jornada,))
        conn.close
        jornadas.append(parsear_jornada(cursor, jornada))
        jornada += 1
    listar_jornadas(jornadas)

def buscar_jornada():
    ventana = tk.Toplevel()
    tk.Label(ventana, text="Número de jornada:").pack()
    texto = tk.Entry(ventana)
    texto.pack()
    texto.bind("<Return>", lambda event: listar_jornada(texto.get()))

def listar_jornada(jornada):
    conn = sqlite3.connect('1\\jornadas.db')
    cursor = conn.execute("SELECT JORNADA, EQUIPO_LOCAL, GOL_LOCAL, EQUIPO_VISITANTE, GOL_VISITANTE FROM PARTIDOS WHERE JORNADA=?", (jornada,))
    partidos = [parsear_jornada(cursor, jornada)]
    conn.close
    listar_jornadas(partidos)

def buscar_estadisticas_jornada():
    ventana = tk.Toplevel()
    tk.Label(ventana, text="Número de jornada:").pack()
    texto = tk.Entry(ventana)
    texto.pack()
    texto.bind("<Return>", lambda event: mostrar_estadisticas_jornada(texto.get()))

def mostrar_estadisticas_jornada(jornada):
    conn = sqlite3.connect('1\\jornadas.db')
    cursor = conn.execute("SELECT GOL_LOCAL, GOL_VISITANTE FROM PARTIDOS WHERE JORNADA=?", (jornada,))
    total_goles = 0
    victorias_local = 0
    victorias_visitante = 0
    for fila in cursor:
        goles_local = fila[0]
        goles_visitante = fila[1]
        goles_partido = goles_local + goles_visitante
        total_goles += goles_partido
        if goles_local > goles_visitante:
            victorias_local += 1
        elif goles_visitante > goles_local:
            victorias_visitante += 1
    conn.close()
    messagebox.showinfo("Estadísticas", f"Estadísticas de la jornada {jornada}:\n\n"
                                        f"Total de goles: {total_goles}\n"
                                        f"Victorias locales: {victorias_local}\n"
                                        f"Victorias visitantes: {victorias_visitante}\n"
                                        f"Empates: {10 - (victorias_local + victorias_visitante)}")
    
def extraer_goleadores(enlace):
    response = urllib.request.urlopen(enlace)
    soup = BeautifulSoup(response, 'html.parser')
    goleadores = {"Local": [], "Visitante": []}
    equipo_local = soup.find("div", class_=["is-local"])
    goleadores_local = equipo_local.find("div", class_=["scr-hdr__scorers"])
    for goleador in goleadores_local.children:
        if goleador == "red-card":
            continue
        goleadores["Local"].append(goleador.get_text(strip=True).replace(',', ''))
    equipo_visitante = soup.find("div", class_=["is-visitor"])
    goleadores_visitante = equipo_visitante.find("div", class_=["scr-hdr__scorers"])
    for goleador in goleadores_visitante.children:
        if goleador.class_ == "red-card":
            continue
        print(goleador.class_)
        goleadores["Visitante"].append(goleador.get_text(strip=True).replace(',', ''))

    return goleadores

def ventana_principal():
    root = tk.Tk()
    root.geometry("550x550")

    menubar = tk.Menu(root)

   
    menubar.add_command(label="Almacenar Resultados", command=cargar)
    menubar.add_separator()
    menubar.add_command(label="Listar Jornadas", command=listar_todas)
    menubar.add_separator()
    menubar.add_command(label="Buscar Jornada", command=buscar_jornada)
    menubar.add_separator()
    menubar.add_command(label="Estadísticas Jornadas", command=buscar_estadisticas_jornada)
    menubar.add_separator()
    menubar.add_command(label="Buscar Goles", command="")

    root.config(menu=menubar)
    root.mainloop()

print(extraer_goleadores(extraer_jornadas(enlace)[1]['enlace']))

# if __name__ == "__main__":
#     ventana_principal()