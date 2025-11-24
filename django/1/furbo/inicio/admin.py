from django.contrib import admin
from inicio.models import Temporada, Equipo, Jornada, Partido

admin.site.register(Partido)
admin.site.register(Equipo)
admin.site.register(Jornada)
admin.site.register(Temporada)