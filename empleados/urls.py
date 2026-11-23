from django.urls import path
from . import views

urlpatterns = [
    path('empleados/', views.lista_empleados),
    path('empleados/<int:id>/', views.detalle_empleado),
]