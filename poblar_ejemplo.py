from datetime import date, time
from app.models.usuario.models import Usuario, Profesor, Escuela
from app.models.asistencia.models import Ubicacion
from app.models.curso.models import Curso
from app.models.horario.models import Horario

PERIODO = "2025-B"

# === Profesora ===
email = "yyarira@unsa.edu.pe"
usuario = Usuario.objects.get(email=email)
profesor = usuario.profesor

# === Asegurar Escuela ===
escuela = Escuela.objects.first()
if not escuela:
    escuela = Escuela.objects.create(
        codigo="CCOMP",
        nombre="Ciencia de la Computación",
        facultad="FIST"
    )

# === Asegurar ambientes ===
aula201 = Ubicacion.objects.get_or_create(
    codigo="A201",
    defaults={"nombre": "Aula 201", "tipo": "AULA"}
)[0]

lab1 = Ubicacion.objects.get_or_create(
    codigo="L1",
    defaults={"nombre": "Laboratorio 1", "tipo": "LABORATORIO", "tiene_computadoras": True}
)[0]

# === Cursos ===
cursos_data = [
    ("1703238", "Estructuras de Datos Avanzados"),
    ("1703240", "Trabajo Interdisciplinar II"),
    ("1705272", "Trabajo de Investigación"),
]

cursos = {}
for codigo, nombre in cursos_data:
    curso, _ = Curso.objects.get_or_create(
        codigo=codigo,
        defaults={
            "nombre": nombre,
            "creditos": 4,
            "horas_teoria": 2,
            "horas_practica": 2,
            "escuela": escuela,
        }
    )
    cursos[codigo] = curso

# === Horarios ===
horarios = [
    (cursos["1703238"], profesor, aula201, 1, time(8,50), time(10,30)),
    (cursos["1703238"], profesor, aula201, 3, time(8,50), time(10,30)),
    (cursos["1703238"], profesor, lab1, 4, time(10,40), time(12,20)),
    (cursos["1703240"], profesor, aula201, 5, time(7,50), time(9,40)),
]

for cur, prof, ub, dia, hi, hf in horarios:
    Horario.objects.update_or_create(
        curso=cur,
        profesor=prof,
        ubicacion=ub,
        dia_semana=dia,
        hora_inicio=hi,
        hora_fin=hf,
        periodo_academico=PERIODO,
        defaults={
            "fecha_inicio": date(2025, 8, 1),
            "fecha_fin": date(2025, 12, 15),
            "tipo_clase": "TEORIA",
            "is_active": True
        }
    )

print("Datos creados correctamente sin errores")
