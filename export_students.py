import re
import sys
import os
from pathlib import Path
import pandas as pd

DATA_DIR = Path(".")  # cambiar si los archivos están en otra carpeta

def guess_course_code_and_group_from_name(fn):
    name = fn.stem
    m_code = re.search(r"_(\d{5,10})_", name)
    course_code = m_code.group(1) if m_code else ""
    m_group = re.findall(r"_([A-Z])(?:_|$)", name)
    group = m_group[0] if m_group else ""
    return course_code, group

def find_name_and_cui_columns(df):
    cols = df.columns.astype(str).tolist()
    cui_patterns = ["cui", "codigo", "código", "ident", "dni", "cedula", "ci"]
    name_patterns = ["nombre", "apellidos", "estudiante", "alumno", "nombres", "apellido"]
    cui_col = None
    name_col = None
    for c in cols:
        lc = c.lower()
        if not cui_col and any(p in lc for p in cui_patterns):
            cui_col = c
        if not name_col and any(p in lc for p in name_patterns):
            name_col = c
    if not name_col and len(cols) >= 1:
        name_col = cols[0]
    if not cui_col and len(cols) >= 2:
        cui_col = cols[1]
    return name_col, cui_col

def safe_str(x):
    if pd.isna(x):
        return ""
    return str(x).strip()

def process_file(filepath, idx):
    print(f"Procesando: {filepath.name}")
    # escoger engine automáticamente: xlrd para .xls, openpyxl para .xlsx
    engine = None
    if filepath.suffix.lower() == ".xls":
        engine = "xlrd"
    # pandas auto-detectará openpyxl para .xlsx
    df = pd.read_excel(filepath, sheet_name=0, engine=engine) if engine else pd.read_excel(filepath, sheet_name=0)
    course_code, group_from_name = guess_course_code_and_group_from_name(filepath)
    # detectar nombre de asignatura (heurístico simple)
    course_name = ""
    # si hay columna que hable de 'asignatura' / 'curso' / 'materia' usarla (nombre de la columna)
    for c in df.columns:
        if isinstance(c, str) and re.search(r"asign|curso|materia", c, re.I):
            course_name = c
            break
    if not course_name:
        # mirar en filas cabezera (primeras 5 filas) por textos que contengan 'Asignatura'
        preview = df.head(5).astype(str).apply(lambda r: " | ".join(r.values), axis=1).tolist()
        for r in preview:
            if re.search(r"asignatura|curso|materia", r, re.I):
                part = r.split(":",1)[-1].strip()
                if len(part) > 2:
                    course_name = part
                    break
    name_col, cui_col = find_name_and_cui_columns(df)
    students = []
    for _, r in df.iterrows():
        nombre = safe_str(r[name_col]) if name_col in df.columns else ""
        cui = safe_str(r[cui_col]) if cui_col in df.columns else ""
        # omitir filas totalmente vacías
        if not (nombre or cui):
            continue
        students.append({
            "codigo_estudiante": cui,
            "nombre": nombre,
            "curso_codigo": course_code or "",
            "curso_nombre": course_name or "",
            "grupo": group_from_name or ""
        })
    cantidad_matriculados = len(students)
    # escribir CSVs
    students_df = pd.DataFrame(students)
    students_csv = DATA_DIR / f"students_{idx}_{filepath.stem}.csv"
    students_df.to_csv(students_csv, index=False, encoding="utf-8-sig")
    courses_df = pd.DataFrame([{
        "curso_codigo": course_code or f"UNKNOWN_{idx}",
        "curso_nombre": course_name or f"Curso_{filepath.stem}",
        "grupo": group_from_name or "",
        "profesores_titular": "",
        "profesores_practica": "",
        "profesores_laboratorio": "",
        "silabo": "",
        "cantidad_matriculados": cantidad_matriculados
    }])
    courses_csv = DATA_DIR / f"courses_{idx}_{filepath.stem}.csv"
    courses_df.to_csv(courses_csv, index=False, encoding="utf-8-sig")

    # generar SQL simples
    students_sql = DATA_DIR / f"students_{idx}_{filepath.stem}.sql"
    with open(students_sql, "w", encoding="utf-8") as fh:
        fh.write("-- INSERTs para tabla estudiantes (codigo_estudiante, nombre, curso_codigo, curso_nombre, grupo)\n")
        for s in students:
            cod = s['codigo_estudiante'].replace("'", "''")
            nom = s['nombre'].replace("'", "''")
            cc = s['curso_codigo'].replace("'", "''")
            cn = s['curso_nombre'].replace("'", "''")
            grp = s['grupo'].replace("'", "''")
            fh.write(f"INSERT INTO estudiantes (codigo_estudiante, nombre, curso_codigo, curso_nombre, grupo) VALUES ('{cod}', '{nom}', '{cc}', '{cn}', '{grp}');\n")

    courses_sql = DATA_DIR / f"courses_{idx}_{filepath.stem}.sql"
    with open(courses_sql, "w", encoding="utf-8") as fh:
        fh.write("-- INSERTs para tabla cursos (curso_codigo, curso_nombre, grupo, profesores_titular, profesores_practica, profesores_laboratorio, silabo, cantidad_matriculados)\n")
        row = courses_df.iloc[0]
        cc = row['curso_codigo'].replace("'", "''")
        cn = row['curso_nombre'].replace("'", "''")
        grp = row['grupo'].replace("'", "''")
        fh.write(f"INSERT INTO cursos (curso_codigo, curso_nombre, grupo, profesores_titular, profesores_practica, profesores_laboratorio, silabo, cantidad_matriculados) VALUES ('{cc}', '{cn}', '{grp}', '', '', '', '', {int(row['cantidad_matriculados'])});\n")

    print(f" -> Generados: {students_csv.name}, {courses_csv.name}, {students_sql.name}, {courses_sql.name}")

def main():
    files = sorted([p for p in DATA_DIR.iterdir() if p.name.lower().startswith("alumnos_") and p.suffix.lower() in ['.xls', '.xlsx']])
    if not files:
        print("No se encontraron archivos alumnos_*.xls/.xlsx en la carpeta actual.")
        return
    for idx, f in enumerate(files, start=1):
        try:
            process_file(f, idx)
        except Exception as e:
            print(f"Error procesando {f.name}: {e}")

if __name__ == "__main__":
    main()
