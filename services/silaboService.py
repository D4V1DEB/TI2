#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.utils import timezone
from app.models.curso.models import Silabo, Curso, Contenido
from app.models.usuario.models import Profesor
from app.models.asistencia.models import Asistencia
from app.models.horario.models import Horario
from django.db.models import Q, Count


class SilaboService:
    """
    Servicio para gestionar sílabos y contenido del curso
    """
    
    def __init__(self):
        pass

    def verificarSilabosPendientes(self, profesor_usuario_id):
        """
        Verifica si el profesor tiene sílabos pendientes de subir
        para cursos asignados que aún no han iniciado su primera clase
        
        Args:
            profesor_usuario_id: ID del usuario del profesor (codigo del usuario)
            
        Returns:
            lista de cursos con sílabos pendientes
        """
        try:
            # Obtener el profesor
            from app.models.usuario.models import Usuario
            usuario = Usuario.objects.get(codigo=profesor_usuario_id)
            profesor = usuario.profesor
            
            # Obtener horarios del profesor que aún no han tenido clases
            horarios = Horario.objects.filter(
                profesor=profesor,
                is_active=True
            ).select_related('curso')
            
            cursos_pendientes = []
            
            for horario in horarios:
                # Verificar si tiene asistencias registradas (clases dictadas)
                tiene_clases = Asistencia.objects.filter(
                    curso=horario.curso,
                    registrado_por=profesor
                ).exists()
                
                # Verificar si el sílabo está subido
                silabo = Silabo.objects.filter(
                    curso=horario.curso,
                    profesor=profesor,
                    subido=True
                ).first()
                
                # Si no tiene clases dictadas y no tiene sílabo subido
                if not tiene_clases and not silabo:
                    cursos_pendientes.append({
                        'curso': horario.curso,
                        'horario': horario
                    })
            
            return cursos_pendientes
            
        except Exception as e:
            raise Exception(f"Error al verificar sílabos pendientes: {str(e)}")

    def subirSilabo(self, curso_codigo, profesor_usuario_id, archivo_pdf, periodo_academico, 
                    sumilla='', competencias='', metodologia='', sistema_evaluacion='', bibliografia=''):
        """
        Sube el sílabo de un curso
        
        Args:
            curso_codigo: Código del curso
            profesor_usuario_id: Código del usuario del profesor
            archivo_pdf: Archivo PDF del sílabo
            periodo_academico: Periodo académico (ej: 2024-1)
            sumilla: Sumilla del curso
            competencias: Competencias del curso
            metodologia: Metodología del curso
            sistema_evaluacion: Sistema de evaluación
            bibliografia: Bibliografía
            
        Returns:
            Objeto Silabo creado o actualizado
        """
        try:
            from app.models.usuario.models import Usuario
            
            curso = Curso.objects.get(codigo=curso_codigo)
            usuario = Usuario.objects.get(codigo=profesor_usuario_id)
            profesor = usuario.profesor
            
            # Buscar si ya existe un sílabo
            codigo_silabo = f"{curso_codigo}_{periodo_academico}"
            silabo, created = Silabo.objects.update_or_create(
                codigo=codigo_silabo,
                defaults={
                    'curso': curso,
                    'periodo_academico': periodo_academico,
                    'sumilla': sumilla,
                    'competencias': competencias,
                    'metodologia': metodologia,
                    'sistema_evaluacion': sistema_evaluacion,
                    'bibliografia': bibliografia,
                    'archivo_pdf': archivo_pdf,
                    'profesor': profesor,
                    'subido': True,
                    'fecha_subida': timezone.now(),
                    'is_active': True
                }
            )
            
            return silabo
            
        except Curso.DoesNotExist:
            raise Exception(f"Curso {curso_codigo} no encontrado")
        except Usuario.DoesNotExist:
            raise Exception(f"Usuario {profesor_usuario_id} no encontrado")
        except Exception as e:
            raise Exception(f"Error al subir sílabo: {str(e)}")

    def obtenerSilabo(self, curso_codigo, periodo_academico=None):
        """
        Obtiene el sílabo de un curso
        
        Args:
            curso_codigo: Código del curso
            periodo_academico: Periodo académico (opcional)
            
        Returns:
            Objeto Silabo
        """
        try:
            query = Q(curso__codigo=curso_codigo, subido=True, is_active=True)
            
            if periodo_academico:
                query &= Q(periodo_academico=periodo_academico)
            
            silabo = Silabo.objects.filter(query).select_related('curso', 'profesor').first()
            
            return silabo
            
        except Exception as e:
            raise Exception(f"Error al obtener sílabo: {str(e)}")

    def calcularAvanceCurso(self, curso_codigo, periodo_academico=None):
        """
        Calcula el avance del curso basado en las clases dictadas
        
        Args:
            curso_codigo: Código del curso
            periodo_academico: Periodo académico (opcional)
            
        Returns:
            Diccionario con información del avance
        """
        try:
            # Obtener todas las asistencias únicas por fecha (clases dictadas)
            clases_dictadas = Asistencia.objects.filter(
                curso__codigo=curso_codigo
            ).values('fecha', 'hora_clase', 'tema_clase', 'registrado_por__usuario__nombres', 
                     'registrado_por__usuario__apellidos').distinct().order_by('fecha', 'hora_clase')
            
            # Obtener el sílabo
            silabo = self.obtenerSilabo(curso_codigo, periodo_academico)
            
            # Obtener contenidos del sílabo
            contenidos = []
            if silabo:
                contenidos = Contenido.objects.filter(
                    silabo=silabo,
                    tipo='UNIDAD'
                ).order_by('orden', 'numero')
            
            return {
                'curso_codigo': curso_codigo,
                'silabo': silabo,
                'total_clases_dictadas': len(clases_dictadas),
                'clases': clases_dictadas,
                'contenidos_programados': contenidos,
                'total_contenidos': len(contenidos)
            }
            
        except Exception as e:
            raise Exception(f"Error al calcular avance del curso: {str(e)}")

    def gestionarContenido(self, silabo_codigo, tipo, numero, titulo, descripcion='', 
                          duracion_semanas=1, contenido_padre_id=None, orden=0):
        """
        Gestiona el contenido del sílabo (crear/actualizar unidades, temas, subtemas)
        
        Args:
            silabo_codigo: Código del sílabo
            tipo: Tipo de contenido (UNIDAD, TEMA, SUBTEMA)
            numero: Número de la unidad/tema
            titulo: Título del contenido
            descripcion: Descripción del contenido
            duracion_semanas: Duración en semanas
            contenido_padre_id: ID del contenido padre (para jerarquía)
            orden: Orden del contenido
            
        Returns:
            Objeto Contenido creado
        """
        try:
            silabo = Silabo.objects.get(codigo=silabo_codigo)
            
            contenido_data = {
                'silabo': silabo,
                'tipo': tipo,
                'numero': numero,
                'titulo': titulo,
                'descripcion': descripcion,
                'duracion_semanas': duracion_semanas,
                'orden': orden
            }
            
            if contenido_padre_id:
                contenido_data['contenido_padre_id'] = contenido_padre_id
            
            contenido = Contenido.objects.create(**contenido_data)
            
            return contenido
            
        except Silabo.DoesNotExist:
            raise Exception(f"Sílabo {silabo_codigo} no encontrado")
        except Exception as e:
            raise Exception(f"Error al gestionar contenido: {str(e)}")

    def validarFechaExam(self, fecha_examen, curso_codigo):
        """
        Valida que la fecha de examen sea válida según el avance del curso
        
        Args:
            fecha_examen: Fecha del examen
            curso_codigo: Código del curso
            
        Returns:
            Boolean indicando si es válida
        """
        # Esta función puede implementarse según las reglas de negocio
        # Por ahora retorna True
        return True

