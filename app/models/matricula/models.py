"""
Modelos de Django para el módulo de Matrículas
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from app.models.usuario.models import Estudiante
from app.models.curso.models import Curso


class Matricula(models.Model):
    """Matrícula de un estudiante en un curso"""
    ESTADO_MATRICULA = [
        ('MATRICULADO', 'Matriculado'),
        ('RETIRADO', 'Retirado'),
        ('APROBADO', 'Aprobado'),
        ('DESAPROBADO', 'Desaprobado'),
        ('EN_PROCESO', 'En Proceso'),
    ]
    
    estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.CASCADE,
        related_name='matriculas'
    )
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name='matriculas'
    )
    periodo_academico = models.CharField(max_length=20)
    grupo = models.CharField(max_length=10, default='A')
    
    fecha_matricula = models.DateTimeField(auto_now_add=True)
    fecha_retiro = models.DateTimeField(null=True, blank=True)
    motivo_retiro = models.TextField(blank=True, null=True)
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_MATRICULA,
        default='MATRICULADO'
    )
    
    # Notas del curso
    nota_final = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)]
    )
    
    # Información adicional
    es_segunda_matricula = models.BooleanField(default=False)
    es_tercera_matricula = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'matricula'
        verbose_name = 'Matrícula'
        verbose_name_plural = 'Matrículas'
        unique_together = ['estudiante', 'curso', 'periodo_academico']
        ordering = ['-fecha_matricula']
    
    def __str__(self):
        return f"{self.estudiante} - {self.curso} ({self.periodo_academico})"
    
    def clean(self):
        """Validaciones personalizadas"""
        # Verificar prerequisitos
        if self.curso.prerequisitos.exists():
            cursos_prerequisitos = self.curso.prerequisitos.all()
            matriculas_aprobadas = Matricula.objects.filter(
                estudiante=self.estudiante,
                curso__in=cursos_prerequisitos,
                estado='APROBADO',
                nota_final__gte=10.5
            )
            
            if matriculas_aprobadas.count() < cursos_prerequisitos.count():
                cursos_faltantes = set(cursos_prerequisitos) - set(
                    [m.curso for m in matriculas_aprobadas]
                )
                raise ValidationError(
                    f'El estudiante no ha aprobado los prerequisitos: {", ".join([str(c) for c in cursos_faltantes])}'
                )
    
    def esta_aprobado(self):
        """Verifica si el estudiante aprobó el curso"""
        return self.nota_final and self.nota_final >= 10.5
    
    def calcular_nota_final(self):
        """Calcula la nota final basada en las evaluaciones"""
        from app.models.evaluacion.models import Nota
        
        notas = Nota.objects.filter(
            estudiante=self.estudiante,
            curso=self.curso
        )
        
        if not notas.exists():
            return None
        
        # Agrupar notas por tipo
        notas_por_tipo = {}
        for nota in notas:
            tipo = nota.tipo_nota.codigo
            if tipo not in notas_por_tipo:
                notas_por_tipo[tipo] = []
            notas_por_tipo[tipo].append(nota.valor)
        
        # Calcular promedio ponderado
        suma_ponderada = 0
        suma_pesos = 0
        
        for tipo, valores in notas_por_tipo.items():
            promedio_tipo = sum(valores) / len(valores)
            # Obtener el peso del tipo de nota
            from app.models.evaluacion.models import TipoNota
            tipo_nota = TipoNota.objects.get(codigo=tipo)
            peso = float(tipo_nota.peso_porcentual)
            
            suma_ponderada += promedio_tipo * peso
            suma_pesos += peso
        
        if suma_pesos > 0:
            self.nota_final = suma_ponderada / suma_pesos
            self.save()
            return self.nota_final
        
        return None
