// src/components/Silabo/Profesor/GestionSilabo.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

// Define la URL base de tu API de Django
const API_BASE_URL = 'http://127.0.0.1:8000/app/api';

// Configuración global opcional para axios:
// - withCredentials true si usas sesiones/cookies (Django CSRF + sesión).
// - Puedes configurar header 'X-CSRFToken' si lo gestionas manualmente.
axios.defaults.withCredentials = true;

// Si manejas CSRF via cookie "csrftoken", esta función lo lee (si lo pones)
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}

function GestionSilabo() {
  // Estados del formulario
  const [tituloContenido, setTituloContenido] = useState('');
  const [descripcionContenido, setDescripcionContenido] = useState('');
  const [nombreExamen, setNombreExamen] = useState('');
  const [fechaExamen, setFechaExamen] = useState('');

  // Estados auxiliares
  const [examenesGuardados, setExamenesGuardados] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Al montar, traer exámenes desde la API
  useEffect(() => {
    async function fetchExamenes() {
      setCargando(true);
      setErrorMsg('');
      try {
        const res = await axios.get(`${API_BASE_URL}/examenes/`);
        // Asumimos que la API devuelve lista de examenes [{id, nombre, fecha}, ...]
        setExamenesGuardados(res.data);
      } catch (err) {
        console.error('Error al traer exámenes:', err);
        setErrorMsg('No se pudieron cargar los exámenes. Revisa la consola.');
        // Como fallback opcional, puedes inicializar con un ejemplo:
        // setExamenesGuardados([{ id: 1, nombre: 'Examen Parcial', fecha: '2025-10-25' }]);
      } finally {
        setCargando(false);
      }
    }

    fetchExamenes();
  }, []);

  // --- Contenido ---
  const handleGuardarContenido = async () => {
    setErrorMsg('');
    setSuccessMsg('');
    if (!tituloContenido.trim()) {
      setErrorMsg('Por favor, ingresa un título para el contenido.');
      return;
    }

    try {
      setCargando(true);
      // Si tu endpoint es POST /app/api/contenidos/
      const csrfToken = getCookie('csrftoken'); // si lo necesitas
      const res = await axios.post(
        `${API_BASE_URL}/contenidos/`,
        {
          titulo: tituloContenido,
          descripcion: descripcionContenido,
        },
        {
          headers: csrfToken ? { 'X-CSRFToken': csrfToken } : {},
        }
      );
      console.log('Contenido creado:', res.data);
      setSuccessMsg('Contenido guardado correctamente.');
      // limpia campos
      setTituloContenido('');
      setDescripcionContenido('');
    } catch (err) {
      console.error('Error guardando contenido:', err);
      setErrorMsg('Error guardando contenido. Revisa la consola o la API.');
    } finally {
      setCargando(false);
      // Limpiar mensajes tras unos segundos (opcional)
      setTimeout(() => { setSuccessMsg(''); setErrorMsg(''); }, 4000);
    }
  };

  // --- Examenes ---
  const handleGuardarExamen = async () => {
    setErrorMsg('');
    setSuccessMsg('');
    if (!nombreExamen.trim() || !fechaExamen) {
      setErrorMsg('Por favor, ingresa el nombre y la fecha del examen.');
      return;
    }

    try {
      setCargando(true);
      const csrfToken = getCookie('csrftoken'); // si lo necesitas
      // POST /app/api/examenes/
      const res = await axios.post(
        `${API_BASE_URL}/examenes/`,
        {
          nombre: nombreExamen,
          fecha: fechaExamen,
        },
        {
          headers: csrfToken ? { 'X-CSRFToken': csrfToken } : {},
        }
      );

      // Suponemos que la API responde con el examen creado { id, nombre, fecha }
      const nuevoExamen = res.data;
      setExamenesGuardados((prev) => [...prev, nuevoExamen]);
      setSuccessMsg('Examen añadido correctamente.');
      // limpiar formulario
      setNombreExamen('');
      setFechaExamen('');
    } catch (err) {
      console.error('Error guardando examen:', err);
      setErrorMsg('Error guardando examen. Revisa la consola o la API.');
    } finally {
      setCargando(false);
      setTimeout(() => { setSuccessMsg(''); setErrorMsg(''); }, 4000);
    }
  };

  const handleBorrarExamen = async (idExamen) => {
    setErrorMsg('');
    setSuccessMsg('');
    if (!window.confirm('¿Seguro que quieres eliminar este examen?')) return;

    try {
      setCargando(true);
      const csrfToken = getCookie('csrftoken'); // si lo necesitas
      // DELETE /app/api/examenes/{id}/
      await axios.delete(`${API_BASE_URL}/examenes/${idExamen}/`, {
        headers: csrfToken ? { 'X-CSRFToken': csrfToken } : {},
      });

      // Eliminar del estado local
      setExamenesGuardados((prev) => prev.filter((e) => e.id !== idExamen));
      setSuccessMsg('Examen eliminado correctamente.');
    } catch (err) {
      console.error('Error borrando examen:', err);
      setErrorMsg('Error borrando examen. Revisa la consola o la API.');
    } finally {
      setCargando(false);
      setTimeout(() => { setSuccessMsg(''); setErrorMsg(''); }, 3000);
    }
  };

  return (
    <div className="card shadow-sm">
      <div className="card-header bg-dark text-white">
        <h5 className="mb-0">Gestión del Sílabo</h5>
      </div>
      <div className="card-body">
        {cargando && (
          <div className="alert alert-warning" role="alert">
            <i className="bi bi-hourglass-split me-2"></i>Cargando...
          </div>
        )}
        {errorMsg && (
          <div className="alert alert-danger" role="alert">
            <i className="bi bi-exclamation-triangle-fill me-2"></i>{errorMsg}
          </div>
        )}
        {successMsg && (
          <div className="alert alert-success" role="alert">
            <i className="bi bi-check-circle-fill me-2"></i>{successMsg}
          </div>
        )}

        <div className="alert alert-info" role="alert">
          <i className="bi bi-info-circle-fill me-2"></i>
          <strong>Recordatorio:</strong> Debe subir el sílabo antes de la primera clase del curso.
        </div>

        <hr />

        {/* Contenido */}
        <section className="mb-4">
          <h6><i className="bi bi-file-earmark-plus-fill me-2"></i>Añadir/Editar Contenido del Sílabo</h6>
          <div className="mb-3">
            <label htmlFor="contenidoTitulo" className="form-label">Título del Tema *</label>
            <input
              type="text"
              className="form-control"
              id="contenidoTitulo"
              placeholder="Ej: Semana 1 - Introducción a Algoritmos"
              value={tituloContenido}
              onChange={(e) => setTituloContenido(e.target.value)}
              required
            />
          </div>
          <div className="mb-3">
            <label htmlFor="contenidoDesc" className="form-label">Descripción (Opcional)</label>
            <textarea
              className="form-control"
              id="contenidoDesc"
              rows="3"
              value={descripcionContenido}
              onChange={(e) => setDescripcionContenido(e.target.value)}
            ></textarea>
          </div>
          <button className="btn btn-success" onClick={handleGuardarContenido} disabled={cargando}>
            <i className="bi bi-check-lg me-2"></i>Guardar Tema
          </button>
        </section>

        <hr />

        {/* Exámenes */}
        <section>
          <h6><i className="bi bi-calendar-event-fill me-2"></i>Gestionar Fechas de Examen</h6>
          <div className="row g-3 align-items-end mb-3 p-3 bg-light border rounded">
            <div className="col-md-5">
              <label htmlFor="examenNombre" className="form-label">Nombre del Examen *</label>
              <input
                type="text"
                className="form-control"
                id="examenNombre"
                placeholder="Ej. Examen Parcial 1"
                value={nombreExamen}
                onChange={(e) => setNombreExamen(e.target.value)}
                required
              />
            </div>
            <div className="col-md-4">
              <label htmlFor="examenFecha" className="form-label">Fecha *</label>
              <input
                type="date"
                className="form-control"
                id="examenFecha"
                value={fechaExamen}
                onChange={(e) => setFechaExamen(e.target.value)}
                required
              />
            </div>
            <div className="col-md-3">
              <button className="btn btn-primary w-100" onClick={handleGuardarExamen} disabled={cargando}>
                <i className="bi bi-calendar-plus me-1"></i> Añadir/Actualizar
              </button>
            </div>
          </div>

          <h6>Exámenes Programados:</h6>
          {examenesGuardados.length === 0 ? (
            <p className="text-muted">Aún no hay exámenes programados.</p>
          ) : (
            <ul className="list-group">
              {examenesGuardados.map((examen) => (
                <li key={examen.id} className="list-group-item d-flex justify-content-between align-items-center">
                  <div>
                    <strong>{examen.nombre}</strong>
                    <div className="text-muted small">{examen.fecha}</div>
                  </div>
                  <div>
                    <button
                      className="btn btn-sm btn-outline-danger ms-2"
                      onClick={() => handleBorrarExamen(examen.id)}
                      title="Eliminar Examen"
                      disabled={cargando}
                    >
                      <i className="bi bi-trash-fill"></i>
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  );
}

export default GestionSilabo;

