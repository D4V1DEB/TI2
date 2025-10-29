from django.db import models
from .curso import Curso

class Silabo(models.Model):
    """Modelo para almacenar el archivo PDF del sílabo de un curso."""

    curso = models.OneToOneField(
        Curso,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='silabo'
    )

    archivo_pdf = models.FileField(
        upload_to='silabos/',
        verbose_name='Archivo PDF del sílabo',
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'silabo'
        verbose_name = 'Sílabo'
        verbose_name_plural = 'Sílabos'

    def __str__(self):
        return f"Sílabo de {self.curso.nombre}"

