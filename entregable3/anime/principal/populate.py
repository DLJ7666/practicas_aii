from principal.models import Anime, Puntuacion
from datetime import datetime
import html
import csv

path = "data"

def populate():
    info_animes = populateAnime()
    info_puntuaciones = populatePuntuaciones()
    return info_animes, info_puntuaciones

def populatePuntuaciones():
    Puntuacion.objects.all().delete()
    
    lista = []
    
    diccionario_animes = {a.anime_id: a for a in Anime.objects.all()}
    
    fileobj = open(path + "\\ratings.csv", "r", encoding='utf-8')
    
    lines = fileobj.readlines()
    
    for line in lines[1:]:
        rip = str(line.strip()).split(';')
        
        if len(rip) != 3:
            continue
            
        user_id = int(rip[0])
        anime_id_csv = int(rip[1])
        rating = int(rip[2])
        
        if anime_id_csv in diccionario_animes:
            lista.append(Puntuacion(
                id_usuario=user_id,
                anime=diccionario_animes[anime_id_csv], 
                puntuacion=rating
            ))
            
    fileobj.close()
    
    Puntuacion.objects.bulk_create(lista, batch_size=1000)
    return len(lista)

def populateAnime():
    Anime.objects.all().delete()
    lista = []
    
    with open(path + "\\anime.csv", "r", encoding='utf-8') as fileobj:

        reader = csv.reader(fileobj, delimiter=';')
        
        next(reader, None)
    
        for row in reader:

            if len(row) < 5:
                continue
                
            titulo_limpio = html.unescape(row[1])
            
            episodios_str = row[4]
            if episodios_str == 'Unknown':
                episodios_int = 0
            else:
                try:
                    episodios_int = int(episodios_str)
                except ValueError:
                    episodios_int = 0

            lista.append(Anime(
                anime_id=int(row[0]),
                titulo=titulo_limpio,
                generos=row[2],
                formato=row[3],
                episodios=episodios_int
            ))
                
    Anime.objects.bulk_create(lista)
    return len(lista)