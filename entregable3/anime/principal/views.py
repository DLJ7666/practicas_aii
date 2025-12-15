from django.shortcuts import render
from principal.models import Anime, Puntuacion
from django.conf import settings
from principal.populate import populate

def home(request):
    return render(request, 'index.html', {'STATIC_URL':settings.STATIC_URL})

def load_db(request):
    return render(request, 'confirma_carga.html')


def populate_db(request):
    info_animes, info_puntuaciones = populate()
    return render(request, 'carga.html', {'STATIC_URL':settings.STATIC_URL,
                    'info_animes': info_animes, 'info_puntuaciones': info_puntuaciones})
 
def animes_by_format(request):
    lista_formatos = Anime.objects.values_list('formato', flat=True).distinct().order_by('formato')
    
    animes = None
    total = 0
    formato_seleccionado = None

    if request.method == 'POST':
        formato_seleccionado = request.POST.get('formato')
        
        if formato_seleccionado:
            animes = Anime.objects.filter(formato=formato_seleccionado).order_by('-episodios')
            total = animes.count()

    return render(request, 'animes_por_formato.html', {
        'formatos': lista_formatos,      
        'animes': animes,                
        'total': total,                  
        'seleccionado': formato_seleccionado
    })