from django.contrib import admin
from django.urls import path
from main import views as main_views

urlpatterns = [
    path('',main_views.index),
    path('populate/', main_views.populateDatabase),
    path('denominacion_vinos/',main_views.mostrar_vinos_por_denominaciones),
    path('vinos_anyo/',main_views.buscar_vinos_por_anyo),
    path('vinos_uva/',main_views.buscar_vinos_por_uva),
    path('admin/',admin.site.urls),

    ]
