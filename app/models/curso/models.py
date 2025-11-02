"""
Modelos de Django para el módulo de Cursos
"""
from django.db import models
from app.models.usuario.models import Escuela, Profesor


class Curso(models.Model):
    """Curso académico"""
    codigo = models.CharField(max_length=20, unique=True, primary_key=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    creditos = models.IntegerField(default=3)
    horas_teoria = models.IntegerField(default=2)
    horas_practica = models.IntegerField(default=2)
    horas_laboratorio = models.IntegerField(default=0)
    semestre_recomendado = models.IntegerField(default=1)
    
    escuela = models.ForeignKey(
        Escuela,
        on_delete=models.PROTECT,
        related_name='cursos'
    )
    
    # Prerequisitos (cursos que se deben aprobar antes)
    prerequisitos = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='cursos_siguientes',
        blank=True
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'curso'
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        ordering = ['codigo']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    def total_horas(self):
        """Calcula el total de horas del curso"""
        return self.horas_teoria + self.horas_practica + self.horas_laboratorio


class Silabo(models.Model):
    """Sílabo de un curso"""
    codigo = models.CharField(max_length=20, unique=True, primary_key=True)
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name='silabos'
    )
    periodo_academico = models.CharField(max_length=20)  # Ej: 2024-1
    
    # Información del sílabo
    sumilla = models.TextField()
    competencias = models.TextField(blank=True, null=True)
    metodologia = models.TextField(blank=True, null=True)
    sistema_evaluacion = models.TextField(blank=True, null=True)
    bibliografia = models.TextField(blank=True, null=True)
    
    # Archivos
    archivo_pdf = models.FileField(
        upload_to='silabos/',
        blank=True,
        null=True
    )
    
    profesor = models.ForeignKey(
        Profesor,
        on_delete=models.SET_NULL,
        null=True,
        related_name='silabos'
    )
    
    fecha_aprobacion = models.DateField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'silabo'
        verbose_name = 'Sílabo'
        verbose_name_plural = 'Sílabos'
        unique_together = ['curso', 'periodo_academico']
    
    def __str__(self):
        return f"Sílabo {self.curso.codigo} - {self.periodo_academico}"


class Contenido(models.Model):
    """Contenido temático de un sílabo"""
    TIPO_CONTENIDO = [
        ('UNIDAD', 'Unidad'),
        ('TEMA', 'Tema'),
        ('SUBTEMA', 'Subtema'),
    ]
    
    silabo = models.ForeignKey(
        Silabo,
        on_delete=models.CASCADE,
        related_name='contenidos'
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CONTENIDO)
    numero = models.IntegerField()  # Número de unidad/tema
    titulo = models.CharField(max_length=300)
    descripcion = models.TextField(blank=True, null=True)
    duracion_semanas = models.IntegerField(default=1)
    
    # Referencia al contenido padre (para jerarquía)
    contenido_padre = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcontenidos'
    )
    
    orden = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'contenido'
        verbose_name = 'Contenido'
        verbose_name_plural = 'Contenidos'
        ordering = ['silabo', 'orden', 'numero']
        unique_together = ['silabo', 'tipo', 'numero']
    
    def __str__(self):
        return f"{self.get_tipo_display()} {self.numero}: {self.titulo}"
