#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models
from app.models.usuario.profesor import Profesor
from app.models.curso.curso import Curso
from datetime import datetime


class SolicitudProfesor(models.Model):
    """Modelo para solicitudes de justificación o clase remota del profesor"""
    
    TIPO_SOLICITUD = [
        ('JUSTIFICACION', 'Justificación de Inasistencia'),
        ('CLASE_REMOTA', 'Permiso Clase Virtual/Remota'),
    ]
    
    ESTADO_SOLICITUD = [
        ('PENDIENTE', 'Pendiente'),
        ('APROBADA', 'Aprobada'),
        ('RECHAZADA', 'Rechazada'),
    ]
    
    profesor = models.ForeignKey(Profesor, on_delete=models.CASCADE, related_name='solicitudes')
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='solicitudes_profesor')
    tipo = models.CharField(max_length=20, choices=TIPO_SOLICITUD)
    motivo = models.TextField()
    fecha_clase = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADO_SOLICITUD, default='PENDIENTE')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_respuesta = models.DateTimeField(null=True, blank=True)
    respuesta_secretaria = models.TextField(blank=True, default='')
    
    class Meta:
        db_table = 'solicitud_profesor'
        verbose_name = 'Solicitud Profesor'
        verbose_name_plural = 'Solicitudes Profesores'
        ordering = ['-fecha_solicitud']
    
    def __str__(self):
        return f"{self.profesor.dni} - {self.get_tipo_display()} - {self.estado}"

    def aprobar(self, respuesta=''):
        """Aprobar solicitud"""
        self.estado = 'APROBADA'
        self.respuesta_secretaria = respuesta
        self.fecha_respuesta = datetime.now()
        self.save()

    def rechazar(self, respuesta=''):
        """Rechazar solicitud"""
        self.estado = 'RECHAZADA'
        self.respuesta_secretaria = respuesta
        self.fecha_respuesta = datetime.now()
        self.save()
