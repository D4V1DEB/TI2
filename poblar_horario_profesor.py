from datetime import date, timedelta, time
from app.models.usuario.models import Profesor
from app.models.curso.models import Curso
from app.models.horario.models import Horario
from app.models.asistencia.models import Ubicacion

PERIODO = "2025-B"

p = Profesor.objects.get(correo="yyarira@unsa.edu.pe")

a201 = Ubicacion.objects.get(codigo="A201")
a202 = Ubicacion.objects.get(codigo="A202")
lab1 = Ubicacion.objects.get(codigo="L1")

c1 = Curso.objects.get(codigo="1703238")  # Estructuras Datos
c2 = Curso.objects.get(codigo="1703240")  # Trabajo Interdisciplinar II
c3 = Curso.objects.get(codigo="1705272")  # Trabajo Investigación

inicio = date.today()
fin = inicio + timedelta(days=120)

horarios_data = [
    (c1, a201, 1, time(8, 50), time(10, 30), "A"),
    (c2, lab1, 3, time(10, 40), time(12, 20), "A"),
    (c3, a202, 5, time(17, 40), time(19, 20), "B"),
]

for c, u, d, hi, hf, g in horarios_data:
    Horario.objects.update_or_create(
        profesor=p,
        curso=c,
        ubicacion=u,
        dia_semana=d,
        hora_inicio=hi,
        hora_fin=hf,
        tipo_clase="TEORIA",
        periodo_academico=PERIODO,
        defaults={
            "fecha_inicio": inicio,
            "fecha_fin": fin,
            "grupo": g,
        }
    )

print("Horarios de prueba creados correctamente")
