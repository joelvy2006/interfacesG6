from django.contrib import admin
from .models import RegistroCosecha, Asistencia, Empleado

@admin.register(RegistroCosecha)
class RegistroCosechaAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'bloque', 'variedad', 'cantidad', 'responsable', 'condicion')
    list_filter = ('condicion', 'variedad', 'fecha')
    search_fields = ('bloque', 'responsable', 'variedad')
    date_hierarchy = 'fecha'


@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'empleado', 'turno', 'estado')
    list_filter = ('turno', 'estado', 'fecha')
    search_fields = ('empleado',)
    date_hierarchy = 'fecha'


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'puesto', 'correo', 'telefono', 'activo')
    list_filter = ('activo', 'puesto')
    search_fields = ('nombre', 'correo', 'telefono')
