from ..repositories.sucursal_repository import SucursalRepository
from ..factories.recomendacion_factory import RecomendacionFactory
import math


class RecomendacionService:

    def __init__(self):

        # ============================
        # DIP (Dependency Inversion Principle)
        # ============================
        # Antes el servicio accedía directamente a:
        # Sucursal.objects / AfluenciaHistorica.objects
        #
        # Ahora depende de un REPOSITORY,
        # lo que desacopla el acceso a datos del ORM
        # ============================
        self.repo = SucursalRepository()

        # ============================
        # FACTORY METHOD
        # ============================
        # En lugar de instanciar directamente la estrategia:
        # EstrategiaDefault()
        #
        # Se usa una FACTORY que decide qué estrategia usar.
        # Esto permite cambiar la estrategia sin modificar el service.
        # ============================
        self.strategy = RecomendacionFactory.crear("default")

    def distancia_km(self, lat1, lon1, lat2, lon2):

        R = 6371

        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)

        a = (
            math.sin(dlat := dLat / 2) ** 2
            +
            math.cos(math.radians(lat1))
            *
            math.cos(math.radians(lat2))
            *
            math.sin(dLon / 2) ** 2
        )

        c = 2 * math.atan2(
            math.sqrt(a),
            math.sqrt(1 - a)
        )

        return R * c

    def recomendar(self, tramite, dia_actual, hora_actual):

        user_lat = tramite.zona.latitud
        user_lon = tramite.zona.longitud

        # ============================
        # DIP aplicado aquí
        # ============================
        # Antes:
        # sucursales = Sucursal.objects.all()
        #
        # Ahora:
        # el service usa el repository
        # ============================
        sucursales = self.repo.obtener_sucursales()

        if not sucursales.exists():

            return {
                "sucursal": "Sin sedes disponibles",
                "tiempo_espera": 0,
                "distancia_km": 0,
                "tiempo_total": 0,
                "ahorro_estimado": 0
            }

        resultados = []

        for s in sucursales:

            if s.latitud is None or s.longitud is None:
                continue

            distancia = self.distancia_km(
                user_lat,
                user_lon,
                float(s.latitud),
                float(s.longitud)
            )

            # ============================
            # DIP aplicado aquí también
            # ============================
            # Antes:
            # AfluenciaHistorica.objects.filter(...).first()
            #
            # Ahora:
            # el repository maneja la consulta
            # ============================
            historico = self.repo.obtener_historico(
                s,
                dia_actual,
                hora_actual
            )

            espera = (
                historico.espera_promedio_minutos
                if historico
                else 45
            )

            tiempo_viaje = distancia * 2

            # ============================
            # STRATEGY PATTERN
            # ============================
            # Antes:
            # score = tiempo_viaje + espera
            #
            # Ahora:
            # el cálculo del score está encapsulado en una estrategia
            # esto permite cambiar el algoritmo sin tocar el service
            # ============================
            score = self.strategy.calcular_score(
                tiempo_viaje,
                espera
            )

            resultados.append({

                "nombre": s.nombre,
                "espera": espera,
                "distancia": distancia,
                "tiempo_viaje": tiempo_viaje,
                "score": score

            })

        if not resultados:

            return {
                "sucursal": "Sin datos suficientes",
                "tiempo_espera": 0,
                "distancia_km": 0,
                "tiempo_total": 0,
                "ahorro_estimado": 0
            }

        mejor = min(
            resultados,
            key=lambda x: x["score"]
        )

        peor = max(
            resultados,
            key=lambda x: x["score"]
        )

        ahorro = round(
            peor["score"] - mejor["score"]
        )

        return {

            "sucursal": mejor["nombre"],
            "tiempo_espera": mejor["espera"],
            "distancia_km": round(mejor["distancia"], 2),
            "tiempo_total": round(mejor["score"]),
            "ahorro_estimado": ahorro

        }