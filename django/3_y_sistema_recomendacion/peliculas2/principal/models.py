from django.db import models

# Modelo para Ocupación
class Ocupacion(models.Model):
    nombre = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name_plural = "Ocupaciones"


# Modelo para Categoría
class Categoria(models.Model):
    id_categoria = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=50)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name_plural = "Categorías"


# Modelo para Usuario
class Usuario(models.Model):
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]
    
    id_usuario = models.IntegerField(primary_key=True)
    edad = models.IntegerField()
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    ocupacion = models.ForeignKey(Ocupacion, on_delete=models.CASCADE)
    codigo_postal = models.CharField(max_length=10)
    
    def __str__(self):
        return f"Usuario {self.id_usuario}"
    
    class Meta:
        verbose_name_plural = "Usuarios"


# Modelo para Película
class Pelicula(models.Model):
    id_pelicula = models.IntegerField(primary_key=True)
    titulo = models.CharField(max_length=200)
    fecha_estreno = models.DateField(null=True, blank=True)
    imdb_url = models.URLField(max_length=300)
    categorias = models.ManyToManyField(Categoria)
    
    def __str__(self):
        return self.titulo
    
    class Meta:
        verbose_name_plural = "Películas"


# Modelo para Puntuación
class Puntuacion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    pelicula = models.ForeignKey(Pelicula, on_delete=models.CASCADE)
    puntuacion = models.IntegerField()
    
    def __str__(self):
        return f"{self.usuario} - {self.pelicula}: {self.puntuacion}"
    
    class Meta:
        verbose_name_plural = "Puntuaciones"
        unique_together = ('usuario', 'pelicula')