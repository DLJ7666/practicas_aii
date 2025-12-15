from django.db import models

class Anime(models.Model):
    anime_id = models.IntegerField(primary_key=True)
    titulo = models.CharField(max_length=255)
    generos = models.CharField(max_length=255)
    formato = models.CharField(max_length=50)
    episodios = models.IntegerField()

    def __str__(self):
        return self.titulo

class Puntuacion(models.Model):
    id_usuario = models.IntegerField()
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE)
    puntuacion = models.IntegerField()

    def __str__(self):
        return f"User {self.id_usuario} -> {self.anime.titulo}: {self.puntuacion}"