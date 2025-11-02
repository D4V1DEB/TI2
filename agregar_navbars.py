#!/usr/bin/env python3
"""
Script para agregar navbars a los templates que no los tienen
"""
import os

NAVBARS = {
    'estudiante': '''    <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm">
        <div class="container">
            <a class="navbar-brand fw-bold" href="{% url 'estudiante_dashboard' %}">Portal Estudiante</a>
            <div class="collapse navbar-collapse">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link" href="{% url 'estudiante_dashboard' %}">Mi Panel</a></li>
                    <li class="nav-item"><a class="nav-link" href="{% url 'estudiante_cursos' %}">Mis Cursos</a></li>
                    <li class="nav-item"><a class="nav-link" href="{% url 'estudiante_horario' %}">Mi Horario</a></li>
                    <li class="nav-item"><a class="nav-link text-warning" href="{% url 'logout' %}">Cerrar Sesión</a></li>
                </ul>
            </div>
        </div>
    </nav>
''',
    'profesor': '''    <nav class="navbar navbar-expand-lg navbar-dark bg-dark shadow-sm">
        <div class="container">
            <a class="navbar-brand fw-bold" href="{% url 'profesor_dashboard' %}">Portal Docente</a>
            <div class="collapse navbar-collapse">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link" href="{% url 'profesor_dashboard' %}">Mi Panel</a></li>
                    <li class="nav-item"><a class="nav-link" href="{% url 'profesor_cursos' %}">Mis Cursos</a></li>
                    <li class="nav-item"><a class="nav-link" href="{% url 'profesor_horario' %}">Mi Horario</a></li>
                    <li class="nav-item"><a class="nav-link" href="{% url 'profesor_horario_ambiente' %}">Ambientes</a></li>
                    <li class="nav-item"><a class="nav-link text-warning" href="{% url 'logout' %}">Cerrar Sesión</a></li>
                </ul>
            </div>
        </div>
    </nav>
''',
}

def add_navbar_to_file(filepath, role):
    """Agrega navbar a un template que no lo tiene"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar si ya tiene navbar
    if '<nav class="navbar' in content:
        print(f"  - Ya tiene navbar: {os.path.basename(filepath)}")
        return
    
    # Encontrar el cierre de </head> y agregar bootstrap icons si no está
    if 'bootstrap-icons' not in content:
        content = content.replace(
            '</head>',
            '''    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
</head>'''
        )
    
    # Agregar navbar después de <body>
    navbar = NAVBARS[role]
    content = content.replace('<body>', f'<body>\n{navbar}\n    ')
    
    # Actualizar enlaces internos a Django URLs
    if role == 'profesor':
        content = content.replace('href="cursos.html"', 'href="{% url \'profesor_cursos\' %}"')
        content = content.replace('href="dashboard.html"', 'href="{% url \'profesor_dashboard\' %}"')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✓ Navbar agregado: {os.path.basename(filepath)}")

def main():
    base_path = '/home/d14/Documentos/TI2/final/TI2/Templates'
    
    for role in ['estudiante', 'profesor']:
        role_path = os.path.join(base_path, role)
        
        if not os.path.exists(role_path):
            continue
        
        print(f"\nProcesando templates de {role}...")
        
        for filename in os.listdir(role_path):
            if filename.endswith('.html'):
                filepath = os.path.join(role_path, filename)
                add_navbar_to_file(filepath, role)

if __name__ == '__main__':
    main()
