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
from app.models.matricula_curso.models import MatriculaCurso

class Command(BaseCommand):
    help = 'Poblar datos para la profesora Yessenia Yari y sus estudiantes'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Iniciando poblado de datos...'))

        with transaction.atomic():
            # 1. Crear Datos Maestros (Si no existen)
            self.crear_datos_maestros()
            
            # 2. Crear Ubicaciones
            self.crear_ubicaciones()
            
            # 3. Crear Profesora
            profesor = self.crear_profesora()
            
            # 4. Crear Cursos
            cursos = self.crear_cursos()
            
            # 5. Crear Horarios
            self.crear_horarios(profesor, cursos)
            
            # 6. Crear Estudiantes y Matricularlos
            self.crear_estudiantes(cursos)

        self.stdout.write(self.style.SUCCESS('¡Datos poblados exitosamente!'))

    def crear_datos_maestros(self):
        # Escuela
        self.escuela, _ = Escuela.objects.get_or_create(
            codigo='EPCC',
            defaults={'nombre': 'Ciencia de la Computación', 'facultad': 'Ingeniería de Producción y Servicios'}
        )
        
        # Tipos de Usuario
        tipos = ['ADMIN', 'PROFESOR', 'ESTUDIANTE', 'SECRETARIA']
        for t in tipos:
            TipoUsuario.objects.get_or_create(codigo=t, defaults={'nombre': t.capitalize()})
            
        # Estados de Cuenta
        EstadoCuenta.objects.get_or_create(codigo='ACTIVO', defaults={'nombre': 'Activo'})
        
        # Tipo Profesor
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
        self.lab_01, _ = Ubicacion.objects.get_or_create(
            codigo='LAB-01',
            defaults={'nombre': 'LABORATORIO 01', 'tipo': 'LABORATORIO', 'capacidad': 25}
        )

    def crear_profesora(self):
        # Datos del usuario base
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
            # Solo si no existe el DNI, intentamos crear o buscar por código
            usuario, created = Usuario.objects.get_or_create(
                codigo=datos_user['codigo'],
                defaults={k: v for k, v in datos_user.items() if k != 'password'}
            )
            if created:
                usuario.set_password(datos_user['password'])
                usuario.save()
        else:
            self.stdout.write(self.style.WARNING(f"Usuario con DNI {datos_user['dni']} ya existe. Se usará el registro existente."))

        # Datos específicos del profesor
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
        lista_cursos = [
            {'codigo': '1703240', 'nombre': 'TRABAJO INTERDISCIPLINAR II', 'creditos': 3, 'semestre': 6},
            {'codigo': '1703238', 'nombre': 'ESTRUCTURAS DE DATOS AVANZADOS', 'creditos': 4, 'semestre': 6},
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
        # Limpiar horarios existentes para este profesor y periodo para evitar duplicados al re-correr
        Horario.objects.filter(profesor=profesor, periodo_academico='2025-B').delete()

        # Formato: (CursoObj, Dia, HoraInicio, HoraFin, Aula, Tipo, Grupo)
        # Dias: 1=Lunes, 2=Martes, 3=Miercoles, 4=Jueves...
        horarios_data = [
            # Curso 1703240: TRABAJO INTERDISCIPLINAR II
            (cursos['1703240'], 3, '07:00', '08:40', self.aula_203, 'TEORIA', 'A'),
            (cursos['1703240'], 4, '10:40', '12:20', self.aula_203, 'TEORIA', 'B'),
            
            # Curso 1703238: ESTRUCTURAS DE DATOS AVANZADOS (Todo Grupo A)
            (cursos['1703238'], 1, '10:40', '12:20', self.aula_203, 'TEORIA', 'A'),
            (cursos['1703238'], 3, '08:50', '10:30', self.lab_01, 'PRACTICA', 'A'), # Lab cuenta como práctica
            (cursos['1703238'], 4, '08:50', '10:30', self.aula_203, 'TEORIA', 'A'),

            # Curso 1705267: TRABAJO INTERDISCIPLINAR III (Todo Grupo A)
            (cursos['1705267'], 1, '14:00', '15:40', self.aula_301, 'TEORIA', 'A'),
            (cursos['1705267'], 1, '17:40', '18:30', self.aula_301, 'PRACTICA', 'A'),
        ]

        fecha_ini = datetime.date(2025, 8, 18) # Fechas simuladas para 2025-B
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
        """
        Crea estudiante y lo matricula. 
        cursos_a_matricular es una lista de tuplas: (CursoObj, Grupo)
        """
        usuario, created = Usuario.objects.get_or_create(
            codigo=data['cui'],
            defaults={
                'nombres': data['nombres'],
                'apellidos': data['apellidos'], # Asumo que el nombre viene completo y lo separaremos simple
                'email': data['email'],
                'dni': data['cui'], # Usamos CUI como DNI temporalmente si no hay dato
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
                'fecha_ingreso': datetime.date(2023, 3, 1) # Default 2023
            }
        )

        for curso_obj, grupo in cursos_a_matricular:
            # Crear matrícula (Modelo MatriculaCurso no tiene campo grupo explícito en tu modelo provisto, 
            # pero asumiremos que la relación lógica existe. Si tu modelo MatriculaCurso tiene 'grupo', agrégalo)
            # Nota: Basado en tus archivos, MatriculaCurso no tiene 'grupo', el grupo se define por el horario.
            # Sin embargo, crearemos la matricula simple.
            
            MatriculaCurso.objects.get_or_create(
                estudiante=estudiante,
                curso=curso_obj,
                periodo_academico='2025-B',
                defaults={'estado': 'MATRICULADO'}
            )
            # Nota: Si tu sistema maneja grupos en la matrícula, deberías añadirlo aquí. 
            # Como tu modelo 'MatriculaCurso' no tiene campo 'grupo', el sistema probablemente 
            # asume el grupo o lo maneja en otra tabla. Por ahora solo registramos la inscripción.

    def procesar_nombre(self, nombre_completo):
        # Utilidad simple para separar apellidos y nombres (heurística básica)
        partes = nombre_completo.split()
        if len(partes) >= 3:
            return " ".join(partes[:2]), " ".join(partes[2:]) # 2 apellidos, resto nombres
        return partes[0], " ".join(partes[1:])

    def crear_estudiantes(self, cursos):
        # --- LISTA 1: Llevan 1703240 (A/B) y 1703238 (A) ---
        lista_1_raw = [
            ("20233590", "DIEGO DANIEL ABENSUR ROMERO", "dabensurr@unsa.edu.pe"),
            ("20232284", "DIOGO ANDRE ALCAZAR MEDINA", "dalcazarm@unsa.edu.pe"),
            ("20230573", "JOSE JAVIER ALVA CORNEJO", "jalvac@unsa.edu.pe"),
            ("20213145", "JHOSEP ANGEL CACSIRE SANCHEZ", "jcacsires@unsa.edu.pe"),
            ("20231537", "SERGIO ELISEO CALCINA MUCHICA", "scalcinam@unsa.edu.pe"),
            ("20233598", "JOSE LUIS CALIZAYA QUISPE", "jcalizayaq@unsa.edu.pe"),
            ("20222178", "ALEX ENRIQUE CANAPATANA VARGAS", "acanapatanav@unsa.edu.pe"),
            ("20222145", "PIERO ADRIANO CARDENAS VILLAGOMEZ", "pcardenasv@unsa.edu.pe"),
            # --- CORTE DE MITAD PARA GRUPO A/B (8 arriba, 8 abajo) ---
            ("20222179", "JOSE RODRIGO CARI ALMIRON", "jcaria@unsa.edu.pe"),
            ("20233582", "JOAQUIN ANDRE CASTELO CHOQUE", "jcasteloc@unsa.edu.pe"),
            ("20221737", "FERNANDO JESUS CHAVEZ MEDINA", "fchavezm@unsa.edu.pe"),
            ("20230579", "RIKI SANTHER COLOMA YUJRA", "rcolomay@unsa.edu.pe"),
            ("20233589", "ANTHONY RICHAR CONDORIOS CHAMBI", "acondoriosc@unsa.edu.pe"),
            ("20232279", "MAURICIO ANDRES CORNEJO ALVAREZ", "mcornejoa@unsa.edu.pe"),
            ("20200364", "KATHIA YERARDINE CUEVAS APAZA", "kcuevasa@unsa.edu.pe"),
            ("20232276", "ESDRAS AMADO DIAZ VASQUEZ", "ediazv@unsa.edu.pe"),
        ]

        # --- LISTA 2: Solo llevan 1703238 (Grupo A) ---
        lista_2_raw = [
            ("20232282", "BERLY MIULER DUENAS MANDAMIENTOS", "bduenasm@unsa.edu.pe"),
            ("20233577", "DAVID ALEJANDRO ESPINOZA BARRIOS", "despinozab@unsa.edu.pe"),
            ("20230585", "SOPHIA ALEJANDRA ESTEBA FERIA", "sestebaf@unsa.edu.pe"),
            ("20220724", "LEONARDO GUSTAVO GAONA BRICENO", "lgaonab@unsa.edu.pe"),
            ("20232274", "VALERIA GUZMAN AVALOS", "vguzmana@unsa.edu.pe"),
            ("20233595", "CESAR ALEJANDRO HANARI CUTIPA", "chanaric@unsa.edu.pe"),
            ("20224274", "LENIN MICHAEL HUAYHUA CARLOS", "lhuayhuac@unsa.edu.pe"),
        ]

        # --- LISTA 3: Solo llevan 1705267 (Grupo A) ---
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

        # Procesar Lista 1 (División Grupos A y B)
        mitad = len(lista_1_raw) // 2
        
        for i, (cui, nombre, email) in enumerate(lista_1_raw):
            apellidos, nombres = self.procesar_nombre(nombre) # Nombres vienen al reves en tu lista?
            # En tu lista: "DIEGO DANIEL ABENSUR ROMERO" -> Normalmente Nombre Apellido
            # Pero en UNSA suele ser Apellido Nombre. Asumiré formato ESTANDAR NOMBRES APELLIDOS
            # Corrección: Viendo tus datos "DIEGO DANIEL ABENSUR ROMERO", parece Nombres Apellidos.
            # Reajustaré la función procesar_nombre para tomar los dos ultimos como apellidos.
            
            # Recalculo para procesar nombre correctamente: "DIEGO DANIEL ABENSUR ROMERO"
            # Nombres: DIEGO DANIEL, Apellidos: ABENSUR ROMERO
            partes = nombre.split()
            mis_nombres = " ".join(partes[:-2])
            mis_apellidos = " ".join(partes[-2:])
            
            grupo_trabajo = 'A' if i < mitad else 'B'
            
            self.registrar_estudiante({
                'cui': cui, 'nombres': mis_nombres, 'apellidos': mis_apellidos, 'email': email
            }, [
                (cursos['1703240'], grupo_trabajo),
                (cursos['1703238'], 'A')
            ])

        # Procesar Lista 2
        for cui, nombre, email in lista_2_raw:
            partes = nombre.split()
            mis_nombres = " ".join(partes[:-2])
            mis_apellidos = " ".join(partes[-2:])
            
            self.registrar_estudiante({
                'cui': cui, 'nombres': mis_nombres, 'apellidos': mis_apellidos, 'email': email
            }, [(cursos['1703238'], 'A')])

        # Procesar Lista 3
        for cui, nombre, email in lista_3_raw:
            partes = nombre.split()
            mis_nombres = " ".join(partes[:-2])
            mis_apellidos = " ".join(partes[-2:])
            
            self.registrar_estudiante({
                'cui': cui, 'nombres': mis_nombres, 'apellidos': mis_apellidos, 'email': email
            }, [(cursos['1705267'], 'A')])