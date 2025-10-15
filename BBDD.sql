create database Sistema_Academico;

use Sistema_Academico;

CREATE TABLE cursos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  curso_codigo VARCHAR(64) UNIQUE,
  curso_nombre VARCHAR(255),
  grupo VARCHAR(16),
  profesores_titular VARCHAR(255),
  profesores_practica VARCHAR(255),
  profesores_laboratorio VARCHAR(255),
  silabo TEXT,
  cantidad_matriculados INT
);

CREATE TABLE estudiantes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  codigo_estudiante VARCHAR(64) UNIQUE,
  nombre VARCHAR(255),
  curso_codigo VARCHAR(64), 
  curso_nombre VARCHAR(255),
  grupo VARCHAR(16)
);
