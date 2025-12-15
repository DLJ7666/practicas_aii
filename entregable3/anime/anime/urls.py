"""
URL configuration for anime project.

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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', principal_views.home, name='home'),
    path('confirma_carga/', principal_views.load_db, name='confirma_carga'),
    path('cargar_bd/', principal_views.populate_db, name='cargar bd'),
    path('confirma_carga_recsys/', recomendacion_views.load_rs, name='confirma carga recsys'),
    path('cargar_recsys/', recomendacion_views.cargar_rs, name='cargar recsys'),
    path('animes_formato_emision/', principal_views.animes_by_format, name='animes por formato'),
    path('animes_populares/', recomendacion_views.popular_animes, name='animes populares'),
    path('recomendar_usuarios/', recomendacion_views.recommend_users, name='recomendar animes a usuario'),
]