from django import forms
from .models import Categoria, Insumo, Proveedor, Cliente


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
        fields = ['nombre_insu', 'cantidad_stock', 'fecha_ingreso', 'proveedor', 'categoria', 'estado_insu']
        widgets = {
            'nombre_insu': forms.TextInput(attrs={'class': 'form-control'}),
            'cantidad_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'fecha_ingreso': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'proveedor': forms.Select(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'estado_insu': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'email', 'telefono', 'direccion', 'estado']

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }