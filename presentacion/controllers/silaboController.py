#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse, Http404
from services.silaboService import SilaboService
from datetime import datetime


class SilaboController:
    """
    Controlador para gestión de sílabos y contenido del curso
    """
    
    def __init__(self):
        self.silaboService = SilaboService()

    def verificarSilabosPendientes(self, request):
        """
        Verifica si el profesor tiene sílabos pendientes de subir
        Redirige a la vista de subida si hay pendientes
        """
        try:
            profesor = request.user.profesor
            cursos_pendientes = self.silaboService.verificarSilabosPendientes(profesor.codigo)
            
            if cursos_pendientes:
                return {
                    'tiene_pendientes': True,
                    'cursos': cursos_pendientes
                }
            
            return {
                'tiene_pendientes': False,
                'cursos': []
            }
            
        except Exception as e:
            return {
                'tiene_pendientes': False,
                'error': str(e)
            }

    def subirContenido(self, request, curso_codigo):
        """
        Vista para subir el sílabo del curso
        """
        try:
            if request.method == 'POST':
                archivo_pdf = request.FILES.get('archivo_pdf')
                periodo_academico = request.POST.get('periodo_academico', datetime.now().year)
                sumilla = request.POST.get('sumilla', '')
                competencias = request.POST.get('competencias', '')
                metodologia = request.POST.get('metodologia', '')
                sistema_evaluacion = request.POST.get('sistema_evaluacion', '')
                bibliografia = request.POST.get('bibliografia', '')
                
                profesor = request.user.profesor
                
                silabo = self.silaboService.subirSilabo(
                    curso_codigo=curso_codigo,
                    profesor_usuario_id=profesor.codigo,  # Nombre corregido
                    archivo_pdf=archivo_pdf,
                    periodo_academico=periodo_academico,
                    sumilla=sumilla,
                    competencias=competencias,
                    metodologia=metodologia,
                    sistema_evaluacion=sistema_evaluacion,
                    bibliografia=bibliografia
                )
                
                messages.success(request, '¡Sílabo subido exitosamente!')
                return redirect('profesor_dashboard')
            
            # GET: Mostrar formulario
            context = {
                'curso_codigo': curso_codigo,
                'periodo_actual': f"{datetime.now().year}-{1 if datetime.now().month <= 6 else 2}"
            }
            return render(request, 'profesor/subir_silabo.html', context)
            
        except Exception as e:
            messages.error(request, f'Error al subir sílabo: {str(e)}')
            return redirect('profesor_dashboard')

    def consultarAvance(self, request, curso_codigo):
        """
        Vista para consultar el avance del curso
        Disponible para estudiantes
        """
        try:
            periodo_academico = request.GET.get('periodo', None)
            avance = self.silaboService.calcularAvanceCurso(curso_codigo, periodo_academico)
            
            context = {
                'curso_codigo': curso_codigo,
                'avance': avance,
                'silabo': avance.get('silabo'),
                'clases_dictadas': avance.get('clases'),
                'total_clases': avance.get('total_clases_dictadas'),
                'contenidos': avance.get('contenidos_programados')
            }
            
            return render(request, 'estudiante/avance_curso.html', context)
            
        except Exception as e:
            messages.error(request, f'Error al consultar avance: {str(e)}')
            return redirect('estudiante_dashboard')

    def descargarSilabo(self, request, curso_codigo):
        """
        Permite descargar el PDF del sílabo
        """
        try:
            periodo_academico = request.GET.get('periodo', None)
            silabo = self.silaboService.obtenerSilabo(curso_codigo, periodo_academico)
            
            if not silabo or not silabo.archivo_pdf:
                raise Http404("Sílabo no encontrado")
            
            return FileResponse(
                silabo.archivo_pdf.open('rb'),
                as_attachment=True,
                filename=f'silabo_{curso_codigo}.pdf'
            )
            
        except Http404:
            raise
        except Exception as e:
            messages.error(request, f'Error al descargar sílabo: {str(e)}')
            return redirect('estudiante_dashboard')

    def registrarFechaExam(self, fecha, curso_codigo):
        """
        Valida la fecha de examen
        """
        try:
            es_valida = self.silaboService.validarFechaExam(fecha, curso_codigo)
            return {
                'success': True,
                'valida': es_valida
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


# Instancia global del controlador
silaboController = SilaboController()

