from django.contrib import admin
from app.models.usuario.usuario import Usuario
from app.models.usuario.estudiante import Estudiante
from app.models.usuario.profesor import Profesor
from app.models.curso.curso import Curso
from app.models.asistencia.asistencia import Asistencia
from app.models.evaluacion.nota import Nota
from app.models.horario.horario import Horario
from app.models.matricula.matricula import Matricula

# Register your models here.
admin.site.register(Usuario)
admin.site.register(Estudiante)
admin.site.register(Profesor)
admin.site.register(Curso)
admin.site.register(Asistencia)
admin.site.register(Nota)
admin.site.register(Horario)
admin.site.register(Matricula)
