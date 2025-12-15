import csv
import os
import shelve

from django.conf import settings
from django.db.models import Count
from django.shortcuts import redirect, render
from principal.models import Anime, Puntuacion
from recomendacion.recommendations import (get_recommendations_for_item,
                                           load_recsys_data, top_matches)


def load_rs(request):
    return render(request, 'confirma_carga_recsys.html')

def cargar_rs(request):
    load_recsys_data()
    return render(request, 'carga_recsys.html')

def popular_animes(request):
    popular = Puntuacion.objects.values('anime').annotate(
        num_votes=Count('puntuacion')
    ).order_by('-num_votes')[:3]
    
    results = []
    sh = shelve.open(os.path.join(settings.BASE_DIR, 'recsys_data'))
    prefs = sh.get('prefs', {})
    sh.close()

    for item in popular:
        anime = Anime.objects.get(pk=item['anime'])
        similares = []
        if prefs:
            matches = top_matches(prefs, anime.anime_id, n=3)
            for score, sim_id in matches:
                sim_anime = Anime.objects.get(pk=sim_id)
                similares.append({'titulo': sim_anime.titulo, 'similitud': round(score, 4)})
        
        results.append({
            'titulo': anime.titulo,
            'votos': item['num_votes'],
            'similares': similares
        })
        
    return render(request, 'animes_populares.html', {'results': results})

def recommend_users(request):
    anime = None
    recs = None
    error = None
    
    if request.method == 'POST':
        anime_id_str = request.POST.get('anime_id')
        if anime_id_str:
            try:
                anime_id = int(anime_id_str)
                if anime_id < 0:
                    error = "El ID del anime no puede ser negativo."
                else:
                    anime = Anime.objects.get(pk=anime_id)
                    recs = get_recommendations_for_item(anime_id)
                    recs = recs[:5]
            except ValueError:
                error = "El ID debe ser un número entero."
            except Anime.DoesNotExist:
                error = "No existe un anime con ese ID."
            except Exception as e:
                error = f"Error al obtener recomendaciones: {str(e)}"
        else:
            error = "Por favor, introduce un ID de anime."
            
    return render(request, 'recomendar_usuarios.html', {'anime': anime, 'recs': recs, 'error': error})

