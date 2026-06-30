from django.contrib import admin
from .models import RegistroCosecha, Asistencia, Empleado, Categoria, Insumo, Proveedor

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


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre_cat', 'estado_cat')
    search_fields = ('nombre_cat',)


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre_prov', 'ruc_prov', 'telefono_prov', 'estado_prov')
    search_fields = ('nombre_prov', 'ruc_prov')


@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    list_display = ('nombre_insu', 'cantidad_stock', 'proveedor', 'categoria', 'estado_insu')
    list_filter = ('estado_insu', 'categoria', 'proveedor')
    search_fields = ('nombre_insu',)
