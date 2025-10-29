from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.apps import apps

"""
Command: python manage.py seed_profesores

Este comando poblará la base de datos con:
- Estados de Cuenta
- Tipos de Usuario
- Tipos de Profesor
- Escuela
- Cuentas de Usuario
- Usuarios
- Profesores
- Cursos
- Ambientes
- Horarios

Si los registros ya existen, no se duplirán (get_or_create).
"""

class Command(BaseCommand):
    help = "Carga datos iniciales de profesores y horarios en la BD"

    def handle(self, *args, **kwargs):
        EstadoCuenta = apps.get_model('app', 'EstadoCuenta')
        TipoUsuario = apps.get_model('app', 'TipoUsuario')
        TipoProfesor = apps.get_model('app', 'TipoProfesor')
        Escuela = apps.get_model('app', 'Escuela')
        CuentaUsuario = apps.get_model('app', 'CuentaUsuario')
        Usuario = apps.get_model('app', 'Usuario')
        Profesor = apps.get_model('app', 'Profesor')
        Curso = apps.get_model('app', 'Curso')
        Ambiente = apps.get_model('app', 'Ambiente')
        Horario = apps.get_model('app', 'Horario')

        now = timezone.now()

        # --- Estados Cuenta ---
        activa, _ = EstadoCuenta.objects.get_or_create(nombre="Activa", defaults={"descripcion": "Cuenta activa"})
        EstadoCuenta.objects.get_or_create(nombre="Inactiva", defaults={"descripcion": "Cuenta inactiva"})

        # --- Tipos ---
        tipo_profesor, _ = TipoUsuario.objects.get_or_create(nombre="Profesor", defaults={"descripcion": "Usuario con rol profesor", "activo": True})
        titular, _ = TipoProfesor.objects.get_or_create(nombre="Titular", defaults={"descripcion": "Profesor titular"})

        # --- Escuela ---
        escuela, _ = Escuela.objects.get_or_create(codigo="CS", defaults={
            "nombre": "Ciencia de la Computación",
            "facultad": "Facultad de Ingeniería de Producción y Servicios",
            "activo": True
        })

        # --- Cuentas de Usuario ---
        cuenta_y, _ = CuentaUsuario.objects.get_or_create(email="yyarira@unsa.edu.pe", defaults={
            "password": make_password("12345678"),
            "estado": activa,
            "fecha_creacion": now,
            "fecha_modificacion": now,
        })

        cuenta_m, _ = CuentaUsuario.objects.get_or_create(email="mquispecr@unsa.edu.pe", defaults={
            "password": make_password("87654321"),
            "estado": activa,
            "fecha_creacion": now,
            "fecha_modificacion": now,
        })

        # --- Usuarios ---
        y_user, _ = Usuario.objects.get_or_create(cuenta=cuenta_y, defaults={
            "tipo_usuario": tipo_profesor,
            "codigo": "yyarira@unsa.edu.pe",
            "nombres": "Yessenia Deysi",
            "apellidos": "Yari Ramos",
            "activo": True
        })

        m_user, _ = Usuario.objects.get_or_create(cuenta=cuenta_m, defaults={
            "tipo_usuario": tipo_profesor,
            "codigo": "mquispecr@unsa.edu.pe",
            "nombres": "Marcela",
            "apellidos": "Quispe Cruz",
            "activo": True
        })

        # --- Profesores ---
        prof_y, _ = Profesor.objects.get_or_create(usuario=y_user, defaults={
            "tipo_profesor": titular,
            "dni": "11223344",
            "especialidad": "Trabajo Interdisciplinar"
        })

        prof_m, _ = Profesor.objects.get_or_create(usuario=m_user, defaults={
            "tipo_profesor": titular,
            "dni": "99887766",
            "especialidad": "Algoritmos y Teoría"
        })

        # --- Ambientes ---
        aula203, _ = Ambiente.objects.get_or_create(codigo="AULA203", defaults={"nombre": "AULA 203", "capacidad": 60, "piso": 2, "edificio": "Principal", "activo": True})
        aula202, _ = Ambiente.objects.get_or_create(codigo="AULA202", defaults={"nombre": "AULA 202", "capacidad": 60, "piso": 2, "edificio": "Principal", "activo": True})
        lab02, _ = Ambiente.objects.get_or_create(codigo="LAB02", defaults={"nombre": "LAB 02", "capacidad": 30, "piso": 1, "edificio": "Laboratorios", "activo": True})

        # --- Cursos ---
        ti2, _ = Curso.objects.get_or_create(codigo="TI2", defaults={
            "nombre": "Trabajo Interdisciplinar II",
            "creditos": 3,
            "semestre": "2025-I",
            "profesor_titular": prof_y,
            "activo": True
        })

        ada, _ = Curso.objects.get_or_create(codigo="ADA", defaults={
            "nombre": "Análisis y Diseño de Algoritmos",
            "creditos": 4,
            "semestre": "2025-I",
            "profesor_titular": prof_m,
            "activo": True
        })

        tc, _ = Curso.objects.get_or_create(codigo="TC", defaults={
            "nombre": "Teoría de la Computación",
            "creditos": 3,
            "semestre": "2025-I",
            "profesor_titular": prof_m,
            "activo": True
        })

        # --- Horarios --- (opción A: grupos manejados como tipo_sesion)
        horarios = [
            (ti2, aula203, "Miércoles", "07:00", "08:40", "Grupo A"),
            (ti2, aula203, "Jueves", "10:40", "12:20", "Grupo B"),

            (ada, aula203, "Lunes", "15:50", "17:30", "Teoría - Grupo A"),
            (ada, lab02, "Martes", "07:00", "08:40", "Laboratorio - Grupo A"),
            (ada, aula203, "Viernes", "07:00", "08:40", "Práctica - Grupo A"),

            (tc, aula202, "Viernes", "17:40", "19:20", "Teoría - Grupo B"),
            (tc, aula202, "Jueves", "14:00", "15:40", "Práctica - Grupo B"),
            (tc, aula202, "Lunes", "07:50", "09:40", "Teoría - Grupo A"),
            (tc, aula202, "Lunes", "10:40", "12:20", "Práctica - Grupo A"),
        ]

        for curso, amb, dia, ini, fin, tipo in horarios:
            Horario.objects.get_or_create(
                curso=curso,
                ambiente=amb,
                dia_semana=dia,
                hora_inicio=f"{ini}:00",
                hora_fin=f"{fin}:00",
                defaults={"tipo_sesion": tipo, "activo": True}
            )

        self.stdout.write(self.style.SUCCESS("Datos de profesores y horarios cargados correctamente!"))
