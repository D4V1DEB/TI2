#!/usr/bin/env python3
"""
Script para actualizar los navbars de todos los templates HTML con las URLs de Django
"""
import os
import re

# Definir los templates y sus navbars
TEMPLATES_CONFIG = {
    'estudiante': {
        'navbar_class': 'navbar-dark bg-primary',
        'brand_name': 'Portal Estudiante',
        'dashboard_url': 'estudiante_dashboard',
        'menu_items': [
            ('Mi Panel', 'estudiante_dashboard'),
            ('Mis Cursos', 'estudiante_cursos'),
            ('Mi Horario', 'estudiante_horario'),
        ]
    },
    'profesor': {
        'navbar_class': 'navbar-dark bg-dark',
        'brand_name': 'Portal Docente',
        'dashboard_url': 'profesor_dashboard',
        'menu_items': [
            ('Mi Panel', 'profesor_dashboard'),
            ('Mis Cursos', 'profesor_cursos'),
            ('Mi Horario', 'profesor_horario'),
            ('Ambientes', 'profesor_horario_ambiente'),
        ]
    },
    'secretaria': {
        'navbar_class': 'navbar-dark bg-danger',
        'brand_name': 'Portal de Administración',
        'dashboard_url': 'secretaria_dashboard',
        'menu_items': [
            ('Panel Principal', 'secretaria_dashboard'),
            ('Reportes', 'secretaria_reportes'),
            ('Matrículas Lab.', 'secretaria_matriculas_lab'),
            ('Gestión Ambientes', 'secretaria_horario_ambiente'),
        ]
    }
}

def update_navbar_in_file(filepath, role):
    """Actualiza el navbar en un archivo HTML"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    config = TEMPLATES_CONFIG[role]
    
    # Crear el nuevo navbar
    navbar_html = f'''    <nav class="navbar navbar-expand-lg {config['navbar_class']} shadow-sm">
        <div class="container">
            <a class="navbar-brand fw-bold" href="{{% url '{config['dashboard_url']}' %}}">{{config['brand_name']}}</a>
            <div class="collapse navbar-collapse">
                <ul class="navbar-nav ms-auto">'''
    
    for label, url_name in config['menu_items']:
        navbar_html += f'''
                    <li class="nav-item"><a class="nav-link" href="{{% url '{url_name}' %}}">{label}</a></li>'''
    
    navbar_html += f'''
                    <li class="nav-item"><a class="nav-link text-warning" href="{{% url 'logout' %}}">Cerrar Sesión</a></li>
                </ul>
            </div>
        </div>
    </nav>'''
    
    # Buscar y reemplazar el navbar existente
    pattern = r'<nav class="navbar[^>]*>.*?</nav>'
    
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, navbar_html, content, count=1, flags=re.DOTALL)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Actualizado: {filepath}")
        return True
    else:
        print(f"✗ No se encontró navbar en: {filepath}")
        return False

def main():
    base_path = '/home/d14/Documentos/TI2/final/TI2/Templates'
    
    for role in ['estudiante', 'profesor', 'secretaria']:
        role_path = os.path.join(base_path, role)
        
        if not os.path.exists(role_path):
            continue
            
        print(f"\nActualizando templates de {role}...")
        
        for filename in os.listdir(role_path):
            if filename.endswith('.html'):
                filepath = os.path.join(role_path, filename)
                update_navbar_in_file(filepath, role)

if __name__ == '__main__':
    main()
