from django.db import models

class Genero(models.Model):
    nombre = models.CharField(max_length=30, verbose_name='Género')

    def __str__(self):
        return self.nombre
    
class Director(models.Model):
    nombre = models.CharField(max_length=30,verbose_name='Director')

    def __str__(self):
        return self.nombre
    
class Pais(models.Model):
    nombre = models.CharField(max_length=30,verbose_name='País')

    def __str__(self):
        return self.nombre

class Pelicula(models.Model):
    titulo = models.TextField(verbose_name='Título')
    tituloOriginal = models.TextField(verbose_name='Título Original')
    fechaEstreno = models.DateField(verbose_name='Fecha de Estreno')
    pais = models.ForeignKey(Pais,on_delete=models.SET_NULL, null=True)
    director = models.ForeignKey(Director,on_delete=models.SET_NULL, null=True)
    generos = models.ManyToManyField(Genero)

    def __str__(self):
        return self.titulo