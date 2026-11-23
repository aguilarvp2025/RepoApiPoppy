import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Empleado

CAMPOS = ["nombre", "puesto", "departamento", "salario", "fecha_contratacion"]


def empleado_a_dict(e):
    return {
        "id": e.id,
        "nombre": e.nombre,
        "puesto": e.puesto,
        "departamento": e.departamento,
        "salario": str(e.salario),
        "fecha_contratacion": e.fecha_contratacion.isoformat(),
    }


def leer_json(request):
    """Convierte el body de la petición en un diccionario. Devuelve None si es inválido."""
    try:
        return json.loads(request.body)
    except json.JSONDecodeError:
        return None


@csrf_exempt
def lista_empleados(request):
    if request.method == "GET":
        datos = [empleado_a_dict(e) for e in Empleado.objects.all()]
        return JsonResponse(datos, safe=False)

    if request.method == "POST":
        datos = leer_json(request)
        if datos is None:
            return JsonResponse({"error": "JSON inválido"}, status=400)

        faltan = [c for c in CAMPOS if not datos.get(c)]
        if faltan:
            return JsonResponse({"error": f"Faltan campos: {', '.join(faltan)}"}, status=400)

        try:
            e = Empleado.objects.create(**{c: datos[c] for c in CAMPOS})
            e.refresh_from_db()
        except Exception as ex:
            return JsonResponse({"error": f"Datos inválidos: {ex}"}, status=400)

        return JsonResponse(empleado_a_dict(e), status=201)

@csrf_exempt
def detalle_empleado(request, id):
    try:
        e = Empleado.objects.get(id=id)
    except Empleado.DoesNotExist:
        return JsonResponse({"error": "Empleado no encontrado"}, status=404)

    if request.method == "GET":
        return JsonResponse(empleado_a_dict(e))

    if request.method == "PUT":
        datos = leer_json(request)
        if datos is None:
            return JsonResponse({"error": "JSON inválido"}, status=400)

        faltan = [c for c in CAMPOS if not datos.get(c)]
        if faltan:
            return JsonResponse({"error": f"Faltan campos: {', '.join(faltan)}"}, status=400)

        try:
            for c in CAMPOS:
                setattr(e, c, datos[c])
            e.save()
            e.refresh_from_db()
        except Exception as ex:
            return JsonResponse({"error": f"Datos inválidos: {ex}"}, status=400)

        return JsonResponse(empleado_a_dict(e))

    if request.method == "DELETE":
        e.delete()
        return JsonResponse({"mensaje": "Empleado eliminado"})

    return JsonResponse({"error": "Método no permitido"}, status=405)