from django import forms
from .models import Categoria, Insumo, Proveedor

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre_cat', 'descripcion_cat', 'estado_cat']
        widgets = {
            'nombre_cat': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion_cat': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estado_cat': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class InsumoForm(forms.ModelForm):
    class Meta:
        model = Insumo
        fields = ['nombre_insu', 'cantidad_stock', 'proveedor', 'categoria', 'estado_insu']
        widgets = {
            'nombre_insu': forms.TextInput(attrs={'class': 'form-control'}),
            'cantidad_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'proveedor': forms.Select(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'estado_insu': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }