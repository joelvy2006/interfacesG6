from django.db import models

# Modelo Categoría
class Categoria(models.Model):
    id_cat = models.AutoField(primary_key=True)
    nombre_cat = models.CharField(max_length=100)
    descripcion_cat = models.TextField(blank=True, null=True)
    estado_cat = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_cat

    class Meta:
        db_table = 'categoria'


# Modelo Proveedor
class Proveedor(models.Model):
    id_prov = models.AutoField(primary_key=True)
    ruc_prov = models.CharField(max_length=13, unique=True)
    nombre_prov = models.CharField(max_length=100)
    contacto_prov = models.CharField(max_length=100, blank=True, null=True)
    telefono_prov = models.CharField(max_length=20)
    correo_prov = models.EmailField(blank=True, null=True)
    direccion_prov = models.TextField(blank=True, null=True)
    estado_prov = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_prov

    class Meta:
        db_table = 'proveedor'


# Modelo Insumo (Consumo)
class Insumo(models.Model):
    id_insu = models.AutoField(primary_key=True)
    nombre_insu = models.CharField(max_length=100)
    cantidad_stock = models.IntegerField(default=0)
    fecha_ingreso = models.DateField(auto_now_add=True)
    estado_insu = models.BooleanField(default=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True, db_column='Proveedor_id_prov')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, db_column='categoria_id_cat')

    def __str__(self):
        return self.nombre_insu

    class Meta:
        db_table = 'consumo'