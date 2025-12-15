import shelve
from math import sqrt
from principal.models import Puntuacion, Anime
import os
from django.conf import settings

SHELVE_PATH = os.path.join(settings.BASE_DIR, 'recsys_data')

def load_recsys_data():
    """Carga los datos necesarios para el Sistema de Recomendación [cite: 13]"""
    prefs = {}
    
    ratings = Puntuacion.objects.all()
    for r in ratings:
        anime_id = r.anime.anime_id
        user_id = r.id_usuario
        
        prefs.setdefault(anime_id, {})
        prefs[anime_id][user_id] = float(r.puntuacion)
        
    sh = shelve.open(SHELVE_PATH)
    sh['prefs'] = prefs
    sh.close()

def euclidean_similarity(prefs, item1, item2):
    """Calcula similitud basada en distancia Euclidea """
    common = {}
    for user in prefs[item1]:
        if user in prefs[item2]:
            common[user] = 1

    if len(common) == 0: return 0

    sum_of_squares = sum([pow(prefs[item1][user] - prefs[item2][user], 2) 
                          for user in common])
    
    return 1 / (1 + sqrt(sum_of_squares))

def top_matches(prefs, item_person, n=3):
    """Devuelve los items más parecidos"""
    scores = [(euclidean_similarity(prefs, item_person, other), other) 
              for other in prefs if other != item_person]
    scores.sort()
    scores.reverse()
    return scores[0:n]

def get_recommendations_for_item(item_id):
    """
    Estrategia para 'Recomendar Usuarios' para un Anime[cite: 18]:
    Calculamos usuarios que NO han visto el anime y predecimos su puntuación
    basándonos en usuarios similares (User-Based) o items similares.
    Aquí usaremos una simplificación: buscaremos usuarios que hayan puntuado alto
    animes SIMILARES al dado.
    """
    sh = shelve.open(SHELVE_PATH)
    prefs = sh['prefs']
    sh.close()
    
    user_prefs = {}
    all_users = set()
    for anime, users in prefs.items():
        for u, r in users.items():
            user_prefs.setdefault(u, {})
            user_prefs[u][anime] = r
            all_users.add(u)
            
    sim_animes = top_matches(prefs, item_id, n=10) 
    
    user_scores = []
    
    for user in all_users:
        if user in prefs.get(item_id, {}): continue
        
        total_sim = 0
        weighted_sum = 0
        
        for sim, other_anime in sim_animes:
            if other_anime in user_prefs[user]:
                rating = user_prefs[user][other_anime]
                weighted_sum += rating * sim
                total_sim += sim
                
        if total_sim > 0:
            pred_score = weighted_sum / total_sim
            user_scores.append((pred_score, user))
            
    user_scores.sort(reverse=True)
    return user_scores[:5] 