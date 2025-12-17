import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.hashers import make_password
from app.models.usuario.models import (
    Usuario, Profesor, Estudiante, Escuela, TipoUsuario, 
    EstadoCuenta, TipoProfesor
)
from app.models.curso.models import Curso
from app.models.horario.models import Horario
from app.models.asistencia.models import Ubicacion
from app.models.matricula.models import Matricula

Matricula.objects.filter(
    periodo_academico='2025-B', 
    curso__codigo__in=['1703240', '1705267']
).delete()

class Command(BaseCommand):
    help = 'Poblar datos para Trabajo Interdisciplinar II y III (sin tocar EDA)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Iniciando carga de TI2 y TI3...'))

        with transaction.atomic():
            # 1. Crear Datos Maestros (Si no existen)
            self.crear_datos_maestros()
            
            # 2. Crear Ubicaciones (Asegurar que existan)
            self.crear_ubicaciones()
            
            # 3. Obtener/Crear Profesora
            profesor = self.crear_profesora()
            
            # 4. Crear solo cursos TI2 y TI3
            cursos = self.crear_cursos()
            
            # 5. Crear Horarios (SOLO para TI2 y TI3, respetando EDA)
            self.crear_horarios(profesor, cursos)
            
            # 6. Matricular estudiantes en TI2 y TI3
            self.crear_estudiantes(cursos)

        self.stdout.write(self.style.SUCCESS('¡Datos de TI2 y TI3 agregados exitosamente sin afectar EDA!'))

    def crear_datos_maestros(self):
        self.escuela, _ = Escuela.objects.get_or_create(
            codigo='EPCC',
            defaults={'nombre': 'Ciencia de la Computación', 'facultad': 'Ingeniería de Producción y Servicios'}
        )
        
        tipos = ['ADMIN', 'PROFESOR', 'ESTUDIANTE', 'SECRETARIA']
        for t in tipos:
            TipoUsuario.objects.get_or_create(codigo=t, defaults={'nombre': t.capitalize()})
            
        EstadoCuenta.objects.get_or_create(codigo='ACTIVO', defaults={'nombre': 'Activo'})
        
        self.tipo_profe_tp, _ = TipoProfesor.objects.get_or_create(
            codigo='TP',
            defaults={'nombre': 'Tiempo Parcial'}
        )

    def crear_ubicaciones(self):
        self.aula_203, _ = Ubicacion.objects.get_or_create(
            codigo='AULA-203',
            defaults={'nombre': 'AULA 203', 'tipo': 'AULA', 'capacidad': 40}
        )
        self.aula_301, _ = Ubicacion.objects.get_or_create(
            codigo='AULA-301',
            defaults={'nombre': 'AULA 301', 'tipo': 'AULA', 'capacidad': 40}
        )

    def crear_profesora(self):
        datos_user = {
            'codigo': '24105017',
            'nombres': 'Yessenia Deysi',
            'apellidos': 'Yari Ramos',
            'email': 'yyarira@unsa.edu.pe',
            'dni': '24105017',
            'tipo_usuario_id': 'PROFESOR',
            'estado_cuenta_id': 'ACTIVO',
            'password': '24105017123'
        }

        usuario = Usuario.objects.filter(dni=datos_user['dni']).first()
        if not usuario:
            usuario, created = Usuario.objects.get_or_create(
                codigo=datos_user['codigo'],
                defaults={k: v for k, v in datos_user.items() if k != 'password'}
            )
            if created:
                usuario.set_password(datos_user['password'])
                usuario.save()

        profesor, _ = Profesor.objects.get_or_create(
            usuario=usuario,
            defaults={
                'tipo_profesor': self.tipo_profe_tp,
                'escuela': self.escuela,
                'especialidad': 'Computación Gráfica',
                'grado_academico': 'Magister'
            }
        )
        return profesor

    def crear_cursos(self):
        # SOLO definimos TI2 y TI3
        lista_cursos = [
            {'codigo': '1703240', 'nombre': 'TRABAJO INTERDISCIPLINAR II', 'creditos': 3, 'semestre': 6},
            {'codigo': '1705267', 'nombre': 'TRABAJO INTERDISCIPLINAR III', 'creditos': 2, 'semestre': 10},
        ]
        
        objs_cursos = {}
        for c in lista_cursos:
            curso, _ = Curso.objects.get_or_create(
                codigo=c['codigo'],
                defaults={
                    'nombre': c['nombre'],
                    'creditos': c['creditos'],
                    'semestre_recomendado': c['semestre'],
                    'escuela': self.escuela,
                    'tiene_grupo_b': True if c['codigo'] == '1703240' else False
                }
            )
            objs_cursos[c['codigo']] = curso
        return objs_cursos

    def crear_horarios(self, profesor, cursos):
        # CAMBIO IMPORTANTE: Solo borramos horarios de TI2 y TI3 para este profesor y periodo.
        # Esto PRESERVA los horarios de EDA u otros cursos.
        codigos_a_actualizar = ['1703240', '1705267'] # TI2 y TI3
        
        Horario.objects.filter(
            profesor=profesor, 
            periodo_academico='2025-B',
            curso__codigo__in=codigos_a_actualizar
        ).delete()

        # Horarios nuevos para TI2 y TI3
        horarios_data = [
            # Curso 1703240: TI II
            (cursos['1703240'], 3, '07:00', '08:40', self.aula_203, 'TEORIA', 'A'),
            (cursos['1703240'], 4, '10:40', '12:20', self.aula_203, 'TEORIA', 'B'),
            
            # Curso 1705267: TI III
            (cursos['1705267'], 1, '14:00', '15:40', self.aula_301, 'TEORIA', 'A'),
            (cursos['1705267'], 1, '17:40', '18:30', self.aula_301, 'PRACTICA', 'A'),
        ]

        fecha_ini = datetime.date(2025, 8, 18)
        fecha_fin = datetime.date(2025, 12, 15)

        for item in horarios_data:
            Horario.objects.create(
                curso=item[0],
                profesor=profesor,
                ubicacion=item[4],
                dia_semana=item[1],
                hora_inicio=item[2],
                hora_fin=item[3],
                tipo_clase=item[5],
                grupo=item[6],
                periodo_academico='2025-B',
                fecha_inicio=fecha_ini,
                fecha_fin=fecha_fin,
                is_active=True
            )

    def registrar_estudiante(self, data, cursos_a_matricular):
        # 1. Crear el Usuario y Estudiante (Esto estaba bien)
        usuario, created = Usuario.objects.get_or_create(
            codigo=data['cui'],
            defaults={
                'nombres': data['nombres'],
                'apellidos': data['apellidos'],
                'email': data['email'],
                'dni': data['cui'],
                'tipo_usuario_id': 'ESTUDIANTE',
                'estado_cuenta_id': 'ACTIVO'
            }
        )
        if created:
            usuario.set_password(f"{data['cui']}123")
            usuario.save()

        estudiante, _ = Estudiante.objects.get_or_create(
            usuario=usuario,
            defaults={
                'escuela': self.escuela,
                'codigo_estudiante': data['cui'],
                'fecha_ingreso': datetime.date(2023, 3, 1)
            }
        )

        # 2. CORRECCIÓN: Matricular usando el modelo Matricula y asignando el Grupo
        for curso_obj, grupo_asignado in cursos_a_matricular:
            # Usamos update_or_create para asegurar que el grupo sea el correcto
            # si el estudiante ya existía.
            Matricula.objects.update_or_create(
                estudiante=estudiante,
                curso=curso_obj,
                periodo_academico='2025-B',
                defaults={
                    'estado': 'MATRICULADO',
                    'grupo': grupo_asignado, # IMPORTANTE: Aquí asignamos 'A' o 'B'
                    'es_segunda_matricula': False
                }
            )
            self.stdout.write(f"Matriculado: {data['cui']} en {curso_obj.codigo} Grupo {grupo_asignado}")

    def crear_estudiantes(self, cursos):
        # Lista 1: Alumnos de TI2 (Ignoramos su curso EDA aquí)
        lista_1_raw = [
            ("20233590", "DIEGO DANIEL ABENSUR ROMERO", "dabensurr@unsa.edu.pe"),
            ("20232284", "DIOGO ANDRE ALCAZAR MEDINA", "dalcazarm@unsa.edu.pe"),
            ("20230573", "JOSE JAVIER ALVA CORNEJO", "jalvac@unsa.edu.pe"),
            ("20213145", "JHOSEP ANGEL CACSIRE SANCHEZ", "jcacsires@unsa.edu.pe"),
            ("20231537", "SERGIO ELISEO CALCINA MUCHICA", "scalcinam@unsa.edu.pe"),
            ("20233598", "JOSE LUIS CALIZAYA QUISPE", "jcalizayaq@unsa.edu.pe"),
            ("20222178", "ALEX ENRIQUE CANAPATANA VARGAS", "acanapatanav@unsa.edu.pe"),
            ("20222145", "PIERO ADRIANO CARDENAS VILLAGOMEZ", "pcardenasv@unsa.edu.pe"),
            # --- Corte Grupo B ---
            ("20222179", "JOSE RODRIGO CARI ALMIRON", "jcaria@unsa.edu.pe"),
            ("20233582", "JOAQUIN ANDRE CASTELO CHOQUE", "jcasteloc@unsa.edu.pe"),
            ("20221737", "FERNANDO JESUS CHAVEZ MEDINA", "fchavezm@unsa.edu.pe"),
            ("20230579", "RIKI SANTHER COLOMA YUJRA", "rcolomay@unsa.edu.pe"),
            ("20233589", "ANTHONY RICHAR CONDORIOS CHAMBI", "acondoriosc@unsa.edu.pe"),
            ("20232279", "MAURICIO ANDRES CORNEJO ALVAREZ", "mcornejoa@unsa.edu.pe"),
            ("20200364", "KATHIA YERARDINE CUEVAS APAZA", "kcuevasa@unsa.edu.pe"),
            ("20232276", "ESDRAS AMADO DIAZ VASQUEZ", "ediazv@unsa.edu.pe"),
        ]

        # Lista 3: Alumnos de TI3
        lista_3_raw = [
            ("20230580", "IVAN ALEXANDER LOPEZ ZEGARRA", "ilopezz@unsa.edu.pe"),
            ("20231535", "ARTHUR PATRICK MEZA PAREJA", "amezap@unsa.edu.pe"),
            ("20233581", "RONI EZEQUIEL MONTANEZ PACCO", "rmontanezp@unsa.edu.pe"),
            ("20222143", "GIOMAR DANNY MUNOZ CURI", "gmunozc@unsa.edu.pe"),
            ("20210680", "NEILL ELVERTH OLAZABAL CHAVEZ", "nolazabalc@unsa.edu.pe"),
            ("20230584", "MISAEL JESUS PALOMINO RIVADENEYRA", "mpalominor@unsa.edu.pe"),
            ("20024030", "JOSE CARLOS PAREDES MALAGA", "jparedesm@unsa.edu.pe"),
            ("20231540", "LEONARDO ADRIANO PAXI HUAYHUA", "lpaxih@unsa.edu.pe"),
            ("20231533", "JAFET JOEL POCO CHIRE", "jpococ@unsa.edu.pe"),
            ("20162924", "JUAN CARLOS POSTIGO CABANA", "jpostigoc@unsa.edu.pe"),
            ("20230571", "MARCELO ADRIAN QUINA DELGADO", "mquinad@unsa.edu.pe"),
            ("20233594", "JESUS SALVADOR QUINTEROS CONDORI", "jquinterosc@unsa.edu.pe"),
        ]

        # Procesar TI2 (Lista 1)
        mitad = len(lista_1_raw) // 2
        for i, (cui, nombre, email) in enumerate(lista_1_raw):
            partes = nombre.split()
            mis_nombres = " ".join(partes[:-2])
            mis_apellidos = " ".join(partes[-2:])
            grupo_trabajo = 'A' if i < mitad else 'B'
            
            # Solo matriculamos en TI2
            self.registrar_estudiante({
                'cui': cui, 'nombres': mis_nombres, 'apellidos': mis_apellidos, 'email': email
            }, [(cursos['1703240'], grupo_trabajo)])

        # Procesar TI3 (Lista 3)
        for cui, nombre, email in lista_3_raw:
            partes = nombre.split()
            mis_nombres = " ".join(partes[:-2])
            mis_apellidos = " ".join(partes[-2:])
            
            self.registrar_estudiante({
                'cui': cui, 'nombres': mis_nombres, 'apellidos': mis_apellidos, 'email': email
            }, [(cursos['1705267'], 'A')])