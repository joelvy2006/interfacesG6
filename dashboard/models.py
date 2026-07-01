from django.db import models


class RegistroCosecha(models.Model):
    VARIEDAD_CHOICES = [
        ('clavel-rojo', 'Clavel Rojo'),
        ('clavel-rosa', 'Clavel Rosa'),
        ('clavel-blanco', 'Clavel Blanco'),
        ('clavel-morado', 'Clavel Morado'),
        ('clavel-naranja', 'Clavel Naranja'),
        ('clavel-bicolor', 'Clavel Bicolor'),
    ]
    
    CONDICION_CHOICES = [
        ('exportacion', 'Exportación'),
        ('fanci', 'Fanci'),
        ('nacional', 'Nacional'),
        ('basura', 'Basura'),
    ]
    
    fecha = models.DateField()
    bloque = models.CharField(max_length=50)
    variedad = models.CharField(max_length=20, choices=VARIEDAD_CHOICES)
    cantidad = models.IntegerField()
    responsable = models.CharField(max_length=100)
    condicion = models.CharField(max_length=20, choices=CONDICION_CHOICES)
    observaciones = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-fecha_registro']
    
    def __str__(self):
        return f"{self.variedad} - {self.bloque} ({self.fecha})"


class RegistroProductividad(models.Model):
    fecha = models.DateField()
    bloque = models.CharField(max_length=50)
    responsable = models.CharField(max_length=100)
    embonches = models.IntegerField()
    observaciones = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"{self.embonches} embonches - {self.bloque} ({self.fecha})"


class Empleado(models.Model):
    nombre = models.CharField(max_length=120)
    puesto = models.CharField(max_length=80, blank=True)
    correo = models.EmailField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=200, blank=True)
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Asistencia(models.Model):
    TURNO_CHOICES = [
        ('mañana', 'Mañana'),
        ('tarde', 'Tarde'),
        ('noche', 'Noche'),
    ]

    ESTADO_CHOICES = [
        ('presente', 'Presente'),
        ('faltó', 'Faltó'),
        ('retardo', 'Retardo'),
    ]

    fecha = models.DateField()
    empleado = models.CharField(max_length=100)
    turno = models.CharField(max_length=10, choices=TURNO_CHOICES, default='mañana')
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='presente')
    notas = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha', '-fecha_registro']

    def __str__(self):
        return f"{self.empleado} - {self.fecha} - {self.turno}"


class Categoria(models.Model):
    id_cat = models.AutoField(primary_key=True)
    nombre_cat = models.CharField(max_length=100)
    descripcion_cat = models.TextField(blank=True, null=True)
    estado_cat = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_cat

    class Meta:
        db_table = 'categoria'


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


class Insumo(models.Model):
    id_insu = models.AutoField(primary_key=True)
    nombre_insu = models.CharField(max_length=100)
    cantidad_stock = models.IntegerField(default=0)
    fecha_ingreso = models.DateField()
    estado_insu = models.BooleanField(default=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True, db_column='Proveedor_id_prov')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, db_column='categoria_id_cat')

    def __str__(self):
        return self.nombre_insu

    class Meta:
        db_table = 'consumo'


class Pedido(models.Model):
    ESTADO_PEDIDO_CHOICES = [
        ('espera', 'Espera'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
    ]

    comprador = models.CharField(max_length=120, blank=True)
    producto = models.CharField(max_length=200)
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_PEDIDO_CHOICES, default='espera')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.producto} x{self.cantidad} - {self.comprador or 'Anónimo'}"


class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    class Meta:
        db_table = 'cliente'