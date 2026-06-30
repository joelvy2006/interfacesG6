from django.test import TestCase
from .models import Categoria, Insumo


class CategoriaInsumoModelTests(TestCase):
    def test_crear_categoria_e_insumo_con_relacion(self):
        categoria = Categoria.objects.create(
            nombre_cat='Fertilizantes',
            descripcion_cat='Insumos para fertilización',
            estado_cat='activo',
        )
        insumo = Insumo.objects.create(
            nombre_insu='Nitrógeno',
            cantidad_stock=25,
            fecha_ingreso='2026-01-10',
            estado_insu='activo',
            categoria=categoria,
            proveedor='AgroSuministros',
        )

        self.assertEqual(str(categoria), 'Fertilizantes')
        self.assertEqual(str(insumo), 'Nitrógeno')
        self.assertEqual(insumo.categoria, categoria)
