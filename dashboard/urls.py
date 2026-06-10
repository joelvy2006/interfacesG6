from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('personal/', views.personal, name='personal'),
    path('personal/exportar/empleados/excel/', views.export_empleados_excel, name='export_empleados_excel'),
    path('personal/exportar/empleados/pdf/', views.export_empleados_pdf, name='export_empleados_pdf'),
    path('personal/eliminar-empleado/<int:id>/', views.eliminar_empleado, name='eliminar_empleado'),
    path('registro-cosecha/', views.registro_cosecha, name='registro_cosecha'),
    path('registro-productividad/', views.registro_productividad, name='registro_productividad'),
    path('registro-cosecha/<int:id>/editar/', views.editar_cosecha, name='editar_cosecha'),
    path('registro-cosecha/<int:id>/eliminar/', views.eliminar_cosecha, name='eliminar_cosecha'),
    path('clasificacion-calidad/', views.clasificacion_calidad, name='clasificacion_calidad'),
    path('inventario/', views.inventario, name='inventario'),
    path('reportes/', views.reportes, name='reportes'),
    path('configuracion/', views.configuracion, name='configuracion'),
    path('historial/', views.historial, name='historial'),
    path('metricas-empleado/', views.metricas_empleado, name='metricas_empleado'),
    path('dashboard/', views.dashboard, name='dashboard'),
]