from django import forms
from .models import Categoria, Insumo


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre_cat', 'descripcion_cat', 'estado_cat']
        widgets = {
            'nombre_cat': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion_cat': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estado_cat': forms.Select(attrs={'class': 'form-select'}, choices=[('activo', 'Activo'), ('inactivo', 'Inactivo')]),
        }


class InsumoForm(forms.ModelForm):
    class Meta:
        model = Insumo
        fields = ['nombre_insu', 'cantidad_stock', 'fecha_ingreso', 'estado_insu', 'proveedor', 'categoria']
        widgets = {
            'nombre_insu': forms.TextInput(attrs={'class': 'form-control'}),
            'cantidad_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'fecha_ingreso': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado_insu': forms.Select(attrs={'class': 'form-select'}, choices=[('activo', 'Activo'), ('inactivo', 'Inactivo')]),
            'proveedor': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
        }
