# Script rápido para tener datos de prueba en Pichincha
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings') # Ajusta 'backend' al nombre de tu carpeta de proyecto
django.setup()

from gestion_licencias.models import Sucursal, AfluenciaHistorica

# Crear Sucursales de ejemplo en Pichincha
s1, _ = Sucursal.objects.get_or_create(nombre="ANT Occidental", direccion="Av. Mariscal Sucre y José Sánchez, Quito.", latitud=-0.216, longitud=-78.509)
s2, _ = Sucursal.objects.get_or_create(nombre="ANT Tumbaco", direccion="Eugenio Espejo S2-58 y Av. Interoceánica Km 14 ½, Tumbaco", latitud=-0.175, longitud=-78.490)

# Crear datos de afluencia (Lunes a las 10 AM)
AfluenciaHistorica.objects.get_or_create(sucursal=s1, dia_semana=0, hora=10, espera_promedio_minutos=20)
AfluenciaHistorica.objects.get_or_create(sucursal=s2, dia_semana=0, hora=10, espera_promedio_minutos=80)

print("Datos de sucursales cargados con éxito.")