from django.db import models


class Partido(models.Model):
    equipo_local = models.ForeignKey('Equipo', on_delete=models.CASCADE, related_name='partidos_local')
    equipo_visitante = models.ForeignKey('Equipo', on_delete=models.CASCADE, related_name='partidos_visitante')
    goles_local = models.IntegerField(default=0)
    goles_visitante = models.IntegerField(default=0)
    jornada = models.ForeignKey('Jornada', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.equipo_local} vs {self.equipo_visitante}, Jornada {self.jornada.numero}"
    
class Equipo(models.Model):
    nombre = models.CharField(max_length=100)
    anyo_fundacion = models.IntegerField(null=True, blank=True)
    estadio = models.CharField(max_length=100)
    aforo = models.IntegerField(null=True, blank=True)
    direccion = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.nombre
    
class Jornada(models.Model):
    numero = models.IntegerField()
    temporada = models.ForeignKey('Temporada', on_delete=models.CASCADE)
    fecha = models.CharField(max_length=100) # Cambiado para almacenar el rango de fechas como texto

    def __str__(self):
        return f"Jornada {self.numero} ({self.fecha}) - Temporada {self.temporada.anyo}"
    
class Temporada(models.Model):
    anyo = models.IntegerField()

    def __str__(self):
        return f"Temporada {self.anyo}-{self.anyo + 1}"
