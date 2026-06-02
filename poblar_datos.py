# Script rápido para tener datos de prueba en Pichincha
import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from gestion_licencias.models import Sucursal, AfluenciaHistorica, Zona

# =====================
# ZONAS
# =====================

zona, created = Zona.objects.update_or_create(
    nombre="Norte",
    defaults={
        "latitud": -0.135,
        "longitud": -78.490
    }
)

zona, created = Zona.objects.update_or_create(
    nombre="Centro",
    defaults={
        "latitud": -0.220,
        "longitud": -78.510
    }
)

zona, created = Zona.objects.update_or_create(
    nombre="Sur",
    defaults={
        "latitud": -0.305,
        "longitud": -78.545
    }
)

zona, created = Zona.objects.update_or_create(
    nombre="Cumbayá",
    defaults={
        "latitud": -0.197,
        "longitud": -78.430
    }
)

zona, created = Zona.objects.update_or_create(
    nombre="Tumbaco",
    defaults={
        "latitud": -0.209,
        "longitud": -78.405
    }
)

zona, created = Zona.objects.update_or_create(
    nombre="Valle de los Chillos",
    defaults={
        "latitud": -0.295,
        "longitud": -78.445
    }
)

# =====================
# SUCURSALES
# =====================

s1, _ = Sucursal.objects.update_or_create(
    nombre="ANT Occidental",
    defaults={
        "direccion": "Av. Mariscal Sucre y José Sánchez, Quito.",
        "latitud": -0.216,
        "longitud": -78.509
    }
)

s2, _ = Sucursal.objects.update_or_create(
    nombre="ANT Tumbaco",
    defaults={
        "direccion": "Eugenio Espejo S2-58 y Av. Interoceánica Km 14 ½, Tumbaco",
        "latitud": -0.175,
        "longitud": -78.490
    }
)

s3, _ = Sucursal.objects.update_or_create(
    nombre="Plataforma Gubernamental Sur",
    defaults={
        "direccion": "Av. Amaru Ñan y Av. Quitumbe Ñan, Quito",
        "latitud": -0.2921,
        "longitud": -78.5456
    }
)

s4, _ = Sucursal.objects.update_or_create(
    nombre="Plataforma Gubernamental Norte",
    defaults={
        "direccion": "Av. Amazonas y Alfonso Pereira, Quito",
        "latitud": -0.1768,
        "longitud": -78.4862
    }
)

s5, _ = Sucursal.objects.update_or_create(
    nombre="Agencia Rumiñahui",
    defaults={
        "direccion": "Sangolquí, calle Venezuela 819 y Montúfar",
        "latitud": -0.3340,
        "longitud": -78.4520
    }
)

s6, _ = Sucursal.objects.update_or_create(
    nombre="Agencia Cayambe",
    defaults={
        "direccion": "José de San Martín S/N y Dolores Veintimilla, Cayambe",
        "latitud": 0.0405,
        "longitud": -78.1450
    }
)

s7, _ = Sucursal.objects.update_or_create(
    nombre="Agencia Machachi",
    defaults={
        "direccion": "Calle Barriga S/N y César Calvache, Machachi",
        "latitud": -0.5105,
        "longitud": -78.5678
    }
)

# =====================
# AFLUENCIA HISTÓRICA
# =====================

horarios = [8, 10, 12, 14, 16]
dias = range(5)  # Lunes-Viernes

# Base de afluencia por sucursal
bases = {
    s1: 40,  # ANT Occidental
    s2: 35,  # Tumbaco
    s3: 45,  # Plataforma Sur
    s4: 38,  # Plataforma Norte
    s5: 42,  # Rumiñahui
    s6: 30,  # Cayambe
    s7: 32,  # Machachi
}

for sucursal, base in bases.items():

    for dia in dias:

        for hora in horarios:

            espera = base

            # Hora pico
            if hora == 10:
                espera += 20
            elif hora == 12:
                espera += 10
            elif hora == 14:
                espera += 15
            elif hora == 16:
                espera -= 10

            # Más afluencia martes, miércoles y jueves
            if dia in [1, 2, 3]:
                espera += 10

            # Variación aleatoria
            espera += random.randint(-5, 5)

            espera = max(5, espera)

            AfluenciaHistorica.objects.update_or_create(
                sucursal=sucursal,
                dia_semana=dia,
                hora=hora,
                defaults={
                    'espera_promedio_minutos': espera
                }
            )

print("Datos históricos generados correctamente.")