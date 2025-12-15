"""
URL configuration for peliculas2 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from principal import views as principal_views
from recomendacion import views as recomendacion_views
from django.contrib.admin.views.decorators import staff_member_required


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', principal_views.index, name='inicio'),
    path('index.html/', principal_views.index),
    path('cargar/', staff_member_required(principal_views.recargar_datos), name='cargar'),
    path('ocupaciones_usuarios/',principal_views.mostrar_ocupaciones, name='ocupaciones_usuarios'),
    path('puntuaciones_usuario/',principal_views.mostrar_puntuaciones_usuario, name='puntuaciones_usuario'),
    path('mejores_peliculas/<int:pag>',principal_views.mostrar_mejores_peliculas, name='mejores_peliculas'),
    path('busqueda_peliculas/',principal_views.mostrar_peliculas_year),
    # path('ingresar/', principal_views.ingresar),
    path('loadRS/', recomendacion_views.loadRS),
    path('recomendar_peliculas_usuarios/', recomendacion_views.recomendar_peliculas_usuario_RSusuario, name='recomendar_peliculas_usuarios'),
    path('recomendar_peliculas_usuarios_items/', recomendacion_views.recomendar_peliculas_usuario_RSitems, name='recomendar_peliculas_usuarios_items'),
    path('recomendar_usuarios_peliculas/', recomendacion_views.recomendar_usuarios_pelicula, name='recomendar_usuarios_pelicula'),
    path('peliculas_similares/', recomendacion_views.mostrar_peliculas_parecidas, name='peliculas_similares'),
]
