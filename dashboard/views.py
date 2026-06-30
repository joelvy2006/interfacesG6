from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import RegistroCosecha, RegistroProductividad, Asistencia, Empleado, Categoria, Insumo, Proveedor, Pedido
from datetime import datetime
import json
from io import BytesIO
from .forms import CategoriaForm, InsumoForm
import openpyxl
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph


def inicio(request):
    return render(request, 'index.html')

def servicios(request):
    return render(request, 'servicios.html')


def tienda(request):
    pedidos = Pedido.objects.all()
    return render(request, 'tienda.html', {'pedidos': pedidos})


@csrf_exempt
@require_POST
def crear_pedido(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Datos de pedido inválidos.'}, status=400)

    comprador = data.get('comprador', '').strip()
    items = data.get('items', {})

    if not items:
        return JsonResponse({'success': False, 'message': 'No se encontraron productos en el carrito.'}, status=400)

    if isinstance(items, list):
        items = {item.get('nombre', ''): item for item in items if item.get('nombre')}

    if not isinstance(items, dict):
        return JsonResponse({'success': False, 'message': 'Formato de carrito inválido.'}, status=400)

    pedidos_creados = []
    for nombre, detalle in items.items():
        try:
            cantidad = int(detalle.get('cantidad', 0))
            precio = float(detalle.get('precio', 0))
        except (TypeError, ValueError):
            return JsonResponse({'success': False, 'message': f'Cantidad o precio inválido para {nombre}.'}, status=400)

        if cantidad <= 0 or precio <= 0:
            return JsonResponse({'success': False, 'message': f'Cantidad y precio deben ser mayores que cero para {nombre}.'}, status=400)

        total = round(cantidad * precio, 2)
        pedido = Pedido.objects.create(
            comprador=comprador,
            producto=nombre,
            cantidad=cantidad,
            precio_unitario=precio,
            total=total,
            estado='espera',
        )
        pedidos_creados.append(pedido.id)

    return JsonResponse({'success': True, 'message': 'Pedido registrado correctamente.', 'pedidos': pedidos_creados})


@login_required(login_url='login')
def cambiar_estado_pedido(request, id, estado):
    pedido = get_object_or_404(Pedido, id=id)
    estado = estado.lower()
    estados_validos = dict(Pedido.ESTADO_PEDIDO_CHOICES).keys()
    if estado not in estados_validos:
        messages.error(request, 'Estado de pedido inválido.')
    else:
        pedido.estado = estado
        pedido.save()
        messages.success(request, f'Pedido {pedido.producto} actualizado a {pedido.get_estado_display()}.')
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


def login_view(request):
    mensaje = ''
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            mensaje = 'Completa usuario y contraseña para iniciar sesión.'
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')

            if User.objects.filter(username=username).exists():
                mensaje = 'La contraseña es incorrecta.'
            else:
                mensaje = 'El usuario no existe.'

    return render(request, 'login.html', {'mensaje': mensaje})


def logout_view(request):
    logout(request)
    return redirect('inicio')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if not username or not email or not password1 or not password2:
            messages.error(request, 'Todos los campos son obligatorios, incluyendo correo y contraseña.')
            return render(request, 'register.html')

        if len(password1) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            return render(request, 'register.html')

        if password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Ese usuario ya existe.')
            return render(request, 'register.html')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name,
        )
        login(request, user)
        messages.success(request, 'Usuario registrado correctamente.')
        return redirect('dashboard')

    return render(request, 'register.html')


@login_required(login_url='login')
def personal(request):
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'empleado':
            nombre = request.POST.get('empleado_nombre')
            puesto = request.POST.get('empleado_puesto')
            correo = request.POST.get('empleado_correo')
            telefono = request.POST.get('empleado_telefono')
            if nombre:
                Empleado.objects.create(
                    nombre=nombre,
                    puesto=puesto or '',
                    correo=correo or '',
                    telefono=telefono or '',
                )
            return redirect('personal')

        fecha_str = request.POST.get('fecha')
        empleado = request.POST.get('empleado')
        turno = request.POST.get('turno')
        estado = request.POST.get('estado')
        notas = request.POST.get('notas')

        try:
            if not fecha_str or not empleado or not turno or not estado:
                messages.error(request, 'Completa fecha, empleado, turno y estado para registrar asistencia.')
                return redirect('personal')

            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            Asistencia.objects.create(
                fecha=fecha,
                empleado=empleado,
                turno=turno,
                estado=estado,
                notas=notas,
            )
            return redirect('personal')
        except Exception as e:
            print(f"Error al guardar asistencia: {e}")
            return redirect('personal')

    asistencias = Asistencia.objects.all()[:20]
    empleados = Empleado.objects.filter(activo=True).order_by('nombre')
    empleados_count = empleados.count()
    asistencia_count = Asistencia.objects.count()

    return render(request, 'personal.html', {
        'asistencias': asistencias,
        'empleados': empleados,
        'empleados_count': empleados_count,
        'asistencia_count': asistencia_count,
    })


@login_required(login_url='login')
def eliminar_empleado(request, id):
    empleado = get_object_or_404(Empleado, id=id)
    empleado.delete()
    return redirect('personal')

@login_required(login_url='login')
def editar_empleado(request, id):
    empleado = get_object_or_404(Empleado, id=id)
    if request.method == 'POST':
        nombre = request.POST.get('empleado_nombre')
        puesto = request.POST.get('empleado_puesto')
        correo = request.POST.get('empleado_correo')
        telefono = request.POST.get('empleado_telefono')

        if nombre:
            empleado.nombre = nombre
            empleado.puesto = puesto or ''
            empleado.correo = correo or ''
            empleado.telefono = telefono or ''
            empleado.save()
            return redirect('personal')

    return render(request, 'editar-empleado.html', {'empleado': empleado})

@login_required(login_url='login')
def eliminar_asistencia(request, id):
    asistencia = get_object_or_404(Asistencia, id=id)
    asistencia.delete()
    return redirect('personal')

@login_required(login_url='login')
def editar_asistencia(request, id):
    asistencia = get_object_or_404(Asistencia, id=id)
    empleados = Empleado.objects.filter(activo=True).order_by('nombre')

    if request.method == 'POST':
        fecha_str = request.POST.get('fecha')
        empleado_nombre = request.POST.get('empleado')
        turno = request.POST.get('turno')
        estado = request.POST.get('estado')
        notas = request.POST.get('notas')

        if fecha_str and empleado_nombre and turno and estado:
            try:
                asistencia.fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                asistencia.empleado = empleado_nombre
                asistencia.turno = turno
                asistencia.estado = estado
                asistencia.notas = notas
                asistencia.save()
                return redirect('personal')
            except Exception as e:
                print(f"Error al actualizar asistencia: {e}")

    return render(request, 'editar-asistencia.html', {
        'asistencia': asistencia,
        'empleados': empleados,
    })


def export_empleados_excel(request):
    empleados = Empleado.objects.all().order_by('nombre')
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Empleados'
    headers = ['Nombre', 'Puesto', 'Correo', 'Teléfono', 'Activo']
    sheet.append(headers)

    for empleado in empleados:
        sheet.append([
            empleado.nombre,
            empleado.puesto,
            empleado.correo,
            empleado.telefono,
            'Sí' if empleado.activo else 'No',
        ])

    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="empleados.xlsx"'
    return response


def export_empleados_pdf(request):
    empleados = Empleado.objects.all().order_by('nombre')
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    styles = getSampleStyleSheet()
    flowables = []

    title = Paragraph('Listado de Empleados', styles['Heading2'])
    flowables.append(title)
    flowables.append(Paragraph('Exportación de empleados registrada en el sistema.', styles['Normal']))
    flowables.append(Paragraph(' ', styles['Normal']))

    data = [['Nombre', 'Puesto', 'Correo', 'Teléfono', 'Activo']]
    for empleado in empleados:
        data.append([
            empleado.nombre,
            empleado.puesto or '-',
            empleado.correo or '-',
            empleado.telefono or '-',
            'Sí' if empleado.activo else 'No',
        ])

    table = Table(data, repeatRows=1, hAlign='LEFT')
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c7cfd')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
    ])
    table.setStyle(table_style)
    flowables.append(table)

    doc.build(flowables)
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="empleados.pdf"'
    return response


@login_required(login_url='login')
def registro_cosecha(request):
    if request.method == 'POST':
        fecha_str = request.POST.get('fecha')
        bloque = request.POST.get('lote')
        variedad = request.POST.get('variedad')
        cantidad = request.POST.get('cantidad')
        responsable = request.POST.get('responsable')
        condicion = request.POST.get('condicion')
        observaciones = request.POST.get('observaciones')
        
        try:
            if not fecha_str or not bloque or not variedad or not responsable or not condicion or cantidad in (None, ''):
                messages.error(request, 'Todos los campos de cosecha son obligatorios.')
                return redirect('registro_cosecha')

            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            cantidad_int = int(cantidad)
            if cantidad_int < 0:
                messages.error(request, 'La cantidad no puede ser negativa.')
                return redirect('registro_cosecha')
            
            RegistroCosecha.objects.create(
                fecha=fecha,
                bloque=bloque,
                variedad=variedad,
                cantidad=cantidad_int,
                responsable=responsable,
                condicion=condicion,
                observaciones=observaciones
            )
            messages.success(request, 'Registro de cosecha guardado correctamente.')
            return redirect('registro_cosecha')
        except ValueError:
            messages.error(request, 'La cantidad debe ser un número válido.')
            return redirect('registro_cosecha')
        except Exception as e:
            messages.error(request, 'No se pudo guardar el registro de cosecha.')
            print(f"Error al guardar: {e}")
            return redirect('registro_cosecha')
    
    # Obtener registros
    registros = RegistroCosecha.objects.all()
    
    # Filtros de búsqueda
    filtro_responsable = request.GET.get('filtro_responsable', '').strip()
    filtro_bloque = request.GET.get('filtro_bloque', '').strip()
    filtro_variedad = request.GET.get('filtro_variedad', '').strip()
    filtro_fecha_desde = request.GET.get('filtro_fecha_desde', '').strip()
    filtro_fecha_hasta = request.GET.get('filtro_fecha_hasta', '').strip()

    if filtro_responsable:
        registros = registros.filter(responsable__icontains=filtro_responsable)

    if filtro_bloque:
        registros = registros.filter(bloque__icontains=filtro_bloque)

    if filtro_variedad:
        registros = registros.filter(variedad=filtro_variedad)

    if filtro_fecha_desde:
        registros = registros.filter(fecha__gte=filtro_fecha_desde)

    if filtro_fecha_hasta:
        registros = registros.filter(fecha__lte=filtro_fecha_hasta)
    
    # Calcular estadísticas
    total_claveles = sum(r.cantidad for r in registros)
    total_registros = registros.count()
    promedio_claveles = round(total_claveles / total_registros, 2) if total_registros > 0 else 0
    
    # Total por condición
    condicion_stats = {}
    for registro in registros:
        condicion_display = registro.get_condicion_display()
        if condicion_display not in condicion_stats:
            condicion_stats[condicion_display] = 0
        condicion_stats[condicion_display] += registro.cantidad
    
    # Total por variedad
    variedad_stats = {}
    for registro in registros:
        variedad_display = registro.get_variedad_display()
        if variedad_display not in variedad_stats:
            variedad_stats[variedad_display] = 0
        variedad_stats[variedad_display] += registro.cantidad
    
    # Total por responsable
    responsable_stats = {}
    for registro in registros:
        if registro.responsable not in responsable_stats:
            responsable_stats[registro.responsable] = 0
        responsable_stats[registro.responsable] += registro.cantidad
    
    # Empleado más productivo
    empleado_top = max(responsable_stats.items(), key=lambda x: x[1])[0] if responsable_stats else "N/A"
    empleado_top_cantidad = max(responsable_stats.values()) if responsable_stats else 0
    
    # Total por bloque
    bloque_stats = {}
    for registro in registros:
        if registro.bloque not in bloque_stats:
            bloque_stats[registro.bloque] = 0
        bloque_stats[registro.bloque] += registro.cantidad
    
    # Bloque más productivo
    bloque_top = max(bloque_stats.items(), key=lambda x: x[1])[0] if bloque_stats else "N/A"
    bloque_top_cantidad = max(bloque_stats.values()) if bloque_stats else 0
    
    # Obtener listas de opciones para filtros
    todos_responsables = RegistroCosecha.objects.values_list('responsable', flat=True).distinct()
    todos_bloques = RegistroCosecha.objects.values_list('bloque', flat=True).distinct()
    
    context = {
        'registros': registros,
        'total_claveles': total_claveles,
        'condicion_stats': condicion_stats,
        'variedad_stats': variedad_stats,
        'responsable_stats': responsable_stats,
        'total_registros': total_registros,
        'promedio_claveles': promedio_claveles,
        'empleado_top': empleado_top,
        'empleado_top_cantidad': empleado_top_cantidad,
        'bloque_top': bloque_top,
        'bloque_top_cantidad': bloque_top_cantidad,
        'todos_responsables': todos_responsables,
        'todos_bloques': todos_bloques,
        'filtro_responsable': filtro_responsable,
        'filtro_bloque': filtro_bloque,
        'filtro_variedad': filtro_variedad,
        'filtro_fecha_desde': filtro_fecha_desde,
        'filtro_fecha_hasta': filtro_fecha_hasta,
    }
    
    return render(request, 'registro-cosecha.html', context)


@login_required(login_url='login')
def registro_productividad(request):
    registros = RegistroProductividad.objects.all().order_by('-fecha_registro')

    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        bloque = request.POST.get('bloque', '').strip()
        responsable = request.POST.get('responsable', '').strip()
        embonches = request.POST.get('embonches', '0').strip()
        observaciones = request.POST.get('observaciones', '').strip()

        if not fecha or not bloque or not responsable or not embonches:
            messages.error(request, 'Completa fecha, bloque, responsable y cantidad de embonches.')
            return render(request, 'registro-productividad.html', {'registros': registros})

        try:
            if int(embonches) < 0:
                messages.error(request, 'La cantidad de embonches no puede ser negativa.')
                return render(request, 'registro-productividad.html', {'registros': registros})

            RegistroProductividad.objects.create(
                fecha=datetime.strptime(fecha, '%Y-%m-%d').date(),
                bloque=bloque,
                responsable=responsable,
                embonches=int(embonches),
                observaciones=observaciones,
            )
            messages.success(request, 'Registro de productividad guardado correctamente.')
            return redirect('registro_productividad')
        except ValueError:
            messages.error(request, 'La cantidad de embonches debe ser un número válido.')

    return render(request, 'registro-productividad.html', {'registros': registros})


@login_required(login_url='login')
def editar_productividad(request, id):
    registro = get_object_or_404(RegistroProductividad, id=id)

    if request.method == 'POST':
        fecha_str = request.POST.get('fecha')
        bloque = request.POST.get('bloque', '').strip()
        responsable = request.POST.get('responsable', '').strip()
        embonches = request.POST.get('embonches', '0').strip()
        observaciones = request.POST.get('observaciones', '').strip()

        if not fecha_str or not bloque or not responsable or not embonches:
            messages.error(request, 'Completa fecha, bloque, responsable y cantidad de embonches.')
            return render(request, 'editar-productividad.html', {'registro': registro})

        try:
            cantidad_int = int(embonches)
            if cantidad_int < 0:
                messages.error(request, 'La cantidad de embonches no puede ser negativa.')
                return render(request, 'editar-productividad.html', {'registro': registro})

            registro.fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            registro.bloque = bloque
            registro.responsable = responsable
            registro.embonches = cantidad_int
            registro.observaciones = observaciones
            registro.save()
            messages.success(request, 'Registro de productividad actualizado correctamente.')
            return redirect('registro_productividad')
        except ValueError:
            messages.error(request, 'La cantidad de embonches debe ser un número válido.')
            return render(request, 'editar-productividad.html', {'registro': registro})
        except Exception as e:
            messages.error(request, 'No se pudo actualizar el registro de productividad.')
            print(f"Error al actualizar productividad: {e}")
            return render(request, 'editar-productividad.html', {'registro': registro})

    return render(request, 'editar-productividad.html', {'registro': registro})


@login_required(login_url='login')
def eliminar_productividad(request, id):
    registro = get_object_or_404(RegistroProductividad, id=id)
    registro.delete()
    messages.success(request, 'Registro de productividad eliminado correctamente.')
    return redirect('registro_productividad')


@login_required(login_url='login')
def ver_productividad(request, id):
    registro = get_object_or_404(RegistroProductividad, id=id)
    return render(request, 'detalle-productividad.html', {'registro': registro})


def editar_cosecha(request, id):
    registro = get_object_or_404(RegistroCosecha, id=id)
    
    if request.method == 'POST':
        fecha_str = request.POST.get('fecha')
        bloque = request.POST.get('lote')
        variedad = request.POST.get('variedad')
        cantidad = request.POST.get('cantidad')
        responsable = request.POST.get('responsable')
        condicion = request.POST.get('condicion')
        observaciones = request.POST.get('observaciones')
        
        try:
            if not fecha_str or not bloque or not variedad or not responsable or not condicion or cantidad in (None, ''):
                messages.error(request, 'Completa todos los campos del registro de cosecha.')
                return redirect('registro_cosecha')

            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            cantidad_int = int(cantidad)
            if cantidad_int < 0:
                messages.error(request, 'La cantidad no puede ser negativa.')
                return redirect('registro_cosecha')
            
            registro.fecha = fecha
            registro.bloque = bloque
            registro.variedad = variedad
            registro.cantidad = cantidad_int
            registro.responsable = responsable
            registro.condicion = condicion
            registro.observaciones = observaciones
            registro.save()
            messages.success(request, 'Registro de cosecha actualizado correctamente.')
            return redirect('registro_cosecha')
        except ValueError:
            messages.error(request, 'La cantidad debe ser un número válido.')
            return redirect('registro_cosecha')
        except Exception as e:
            messages.error(request, 'No se pudo actualizar el registro de cosecha.')
            print(f"Error al actualizar: {e}")
            return redirect('registro_cosecha')
    
    return render(request, 'editar-cosecha.html', {'registro': registro})


def eliminar_cosecha(request, id):
    registro = get_object_or_404(RegistroCosecha, id=id)
    registro.delete()
    return redirect('registro_cosecha')


@login_required(login_url='login')
def clasificacion_calidad(request):
    return render(request, 'clasificacion-calidad.html')


@login_required(login_url='login')
def inventario(request):
    return render(request, 'inventario.html')


@login_required(login_url='login')
def reportes(request):
    return render(request, 'reportes.html')


@login_required(login_url='login')
def configuracion(request):
    return render(request, 'configuracion.html')


@login_required(login_url='login')
def historial(request):
    return render(request, 'historial.html')


@login_required(login_url='login')
def metricas_empleado(request):
    return render(request, 'metricas-empleado.html')


@login_required(login_url='login')
def listar_usuarios(request):
    usuarios = User.objects.all().order_by('id')
    return render(request, 'listar_usuarios.html', {'usuarios': usuarios})


@login_required(login_url='login')
def editar_usuario(request, id):
    usuario = get_object_or_404(User, pk=id)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        if not username or not email:
            messages.error(request, 'Usuario y correo son obligatorios.')
        elif User.objects.exclude(pk=usuario.pk).filter(username=username).exists():
            messages.error(request, 'Ese usuario ya está en uso.')
        else:
            usuario.username = username
            usuario.email = email
            usuario.first_name = first_name
            usuario.last_name = last_name
            usuario.save()
            messages.success(request, 'Usuario actualizado correctamente.')
            return redirect('listar_usuarios')

    return render(request, 'editar-usuario.html', {'usuario': usuario})


@login_required(login_url='login')
def cambiar_estado_usuario(request, id):
    usuario = get_object_or_404(User, pk=id)

    if request.method == 'POST':
        usuario.is_active = not usuario.is_active
        usuario.save()
        estado = 'activado' if usuario.is_active else 'desactivado'
        messages.success(request, f'Usuario {estado} correctamente.')

    return redirect('listar_usuarios')


@login_required(login_url='login')
def eliminar_usuario(request, id):
    usuario = get_object_or_404(User, pk=id)

    if request.method == 'POST':
        nombre = usuario.get_full_name() or usuario.username
        usuario.delete()
        messages.success(request, f'Usuario "{nombre}" eliminado correctamente.')

    return redirect('listar_usuarios')


@login_required(login_url='login')
def crear_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if not username or not email or not password1 or not password2:
            messages.error(request, 'Todos los campos son obligatorios.')
        elif password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Ese usuario ya existe.')
        else:
            User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
            )
            messages.success(request, 'Usuario creado correctamente.')
            return redirect('listar_usuarios')

    return render(request, 'crear-usuario.html')


@login_required(login_url='login')
def dashboard(request):
    registros_productividad = RegistroProductividad.objects.all()
    registros_cosecha = RegistroCosecha.objects.all()
    pedidos = Pedido.objects.all()

    total_embonches = registros_productividad.aggregate(Sum('embonches'))['embonches__sum'] or 0
    total_cosecha = registros_cosecha.aggregate(Sum('cantidad'))['cantidad__sum'] or 0
    total_registros = registros_productividad.count()
    objetivo_embonches = 1500

    promedio_embonches = round(total_embonches / total_registros, 1) if total_registros else 0
    rendimiento = min(100, round((total_embonches / objetivo_embonches) * 100)) if objetivo_embonches else 0
    productividad = min(100, round((total_embonches / max(total_cosecha, 1)) * 100)) if total_cosecha else 0

    calidad_exportacion = registros_cosecha.filter(condicion='exportacion').aggregate(Sum('cantidad'))['cantidad__sum'] or 0
    calidad_premium = round((calidad_exportacion / total_cosecha) * 100) if total_cosecha else 0
    calidad_labels = {
        'exportacion': 'Exportación',
        'fanci': 'Fanci',
        'nacional': 'Nacional',
        'basura': 'Basura',
    }
    quality_breakdown = [
        {
            'label': calidad_labels.get(item['condicion'], item['condicion']),
            'total': item['total'],
        }
        for item in registros_cosecha.values('condicion').annotate(total=Sum('cantidad')).order_by('-total')
    ]

    top_responsables = [
        {
            'responsable': item['responsable'],
            'total_embonches': item['total_embonches'],
        }
        for item in registros_productividad.values('responsable').annotate(total_embonches=Sum('embonches')).order_by('-total_embonches')[:5]
    ]

    bloques_activos = registros_productividad.values('bloque').distinct().count()

    context = {
        'total_embonches': total_embonches,
        'promedio_embonches': promedio_embonches,
        'rendimiento': rendimiento,
        'productividad': productividad,
        'calidad_premium': calidad_premium,
        'bloques_activos': bloques_activos,
        'total_cosecha': total_cosecha,
        'quality_breakdown': quality_breakdown,
        'top_responsables': top_responsables,
        'pedidos': pedidos,
    }

    return render(request, 'dashboard/index.html', context)
 
# ============= CRUD CATEGORÍA =============

@login_required(login_url='login')
def lista_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, 'categorias/lista.html', {'categorias': categorias})

@login_required(login_url='login')
def crear_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría creada exitosamente')
            return redirect('lista_categorias')
    else:
        form = CategoriaForm()
    return render(request, 'categorias/form.html', {'form': form, 'titulo': 'Crear Categoría'})

@login_required(login_url='login')
def editar_categoria(request, id_cat):
    categoria = get_object_or_404(Categoria, id_cat=id_cat)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría actualizada exitosamente')
            return redirect('lista_categorias')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'categorias/form.html', {'form': form, 'titulo': 'Editar Categoría'})

@login_required(login_url='login')
def eliminar_categoria(request, id_cat):
    categoria = get_object_or_404(Categoria, id_cat=id_cat)
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, 'Categoría eliminada exitosamente')
        return redirect('lista_categorias')
    return render(request, 'categorias/confirmar_eliminar.html', {'objeto': categoria})

# ============= CRUD INSUMO =============

@login_required(login_url='login')
def lista_insumos(request):
    insumos = Insumo.objects.select_related('categoria', 'proveedor').all()
    return render(request, 'insumos/lista.html', {'insumos': insumos})

@login_required(login_url='login')
def crear_insumo(request):
    if request.method == 'POST':
        form = InsumoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Insumo creado exitosamente')
            return redirect('lista_insumos')
    else:
        form = InsumoForm()
    return render(request, 'insumos/form.html', {'form': form, 'titulo': 'Crear Insumo'})

@login_required(login_url='login')
def editar_insumo(request, id_insu):
    insumo = get_object_or_404(Insumo, id_insu=id_insu)
    if request.method == 'POST':
        form = InsumoForm(request.POST, instance=insumo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Insumo actualizado exitosamente')
            return redirect('lista_insumos')
    else:
        form = InsumoForm(instance=insumo)
    return render(request, 'insumos/form.html', {'form': form, 'titulo': 'Editar Insumo'})

@login_required(login_url='login')
def eliminar_insumo(request, id_insu):
    insumo = get_object_or_404(Insumo, id_insu=id_insu)
    if request.method == 'POST':
        insumo.delete()
        messages.success(request, 'Insumo eliminado exitosamente')
        return redirect('lista_insumos')
    return render(request, 'insumos/confirmar_eliminar.html', {'objeto': insumo})
