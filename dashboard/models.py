from django.db import models


class Categoria(models.Model):
    id_cat = models.AutoField(primary_key=True)
    nombre_cat = models.CharField(max_length=100)
    descripcion_cat = models.TextField(blank=True)
    estado_cat = models.CharField(max_length=20, default='activo')

    class Meta:
        ordering = ['nombre_cat']
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.nombre_cat


class Insumo(models.Model):
    id_insu = models.AutoField(primary_key=True)
    nombre_insu = models.CharField(max_length=100)
    cantidad_stock = models.IntegerField(default=0)
    fecha_ingreso = models.DateField()
    estado_insu = models.CharField(max_length=20, default='activo')
    proveedor = models.CharField(max_length=100, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='insumos')

    class Meta:
        ordering = ['nombre_insu']
        verbose_name = 'Insumo'
        verbose_name_plural = 'Insumos'

    def __str__(self):
        return self.nombre_insu


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
