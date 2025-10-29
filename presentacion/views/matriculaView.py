from django.shortcuts import render, redirect
from django.http import JsonResponse
from presentacion.controllers.matriculaController import MatriculaController

controller = MatriculaController()


# ----------------------------------------------------------
# 1. Registrar matrícula (formulario HTML)
# ----------------------------------------------------------
def registrar_matricula_view(request):
    if request.method == "POST":
        estudiante_id = request.POST.get("estudiante_id")
        curso_id = request.POST.get("curso_id")
        semestre = request.POST.get("semestre")

        resultado = controller.registrar_matricula(estudiante_id, curso_id, semestre)
        return JsonResponse(resultado)

    return render(request, "matricula/registrar.html")


# ----------------------------------------------------------
# 2. Asignar laboratorio automáticamente
# ----------------------------------------------------------
def asignar_laboratorio_view(request):
    if request.method == "POST":
        estudiante_id = request.POST.get("estudiante_id")
        curso_lab_id = request.POST.get("curso_lab_id")
        semestre = request.POST.get("semestre")

        resultado = controller.matricula_service.asignarLaboratorio(estudiante_id, curso_lab_id, semestre)
        return JsonResponse({"success": True, "mensaje": "Laboratorio asignado exitosamente."})

    return JsonResponse({"success": False, "error": "Método no permitido"})


# ----------------------------------------------------------
# 3. Ver horario del estudiante
# ----------------------------------------------------------
def ver_horario_view(request, estudiante_id, semestre):
    horarios = controller.obtener_horario_estudiante(estudiante_id, semestre)
    return render(request, "matricula/horario.html", {"horarios": horarios})


# ----------------------------------------------------------
# 4. Resolver cruces (Secretaría)
# ----------------------------------------------------------
def resolver_cruce_view(request, matricula_id):
    if request.method == "POST":
        aprobar = request.POST.get("aprobar") == "true"
        resultado = controller.matricula_service.resolverCruces(matricula_id, aprobar)
        return JsonResponse({
            "success": True,
            "mensaje": f"Matrícula {resultado.estado.nombre.lower()} correctamente."
        })

    return render(request, "matricula/resolver.html", {"matricula_id": matricula_id})

