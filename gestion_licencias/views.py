from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import TramiteLicencia, Sucursal, AfluenciaHistorica, Zona
from .serializers import TramiteSerializer, ZonaSerializer
from django.db.models import Avg
import math


# ==================================
# DISTANCIA ENTRE DOS PUNTOS (KM)
# ==================================

def distancia_km(lat1, lon1, lat2, lon2):

    R = 6371

    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)

    a = (
        math.sin(dLat / 2) ** 2
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


class TramiteViewSet(viewsets.ModelViewSet):

    queryset = TramiteLicencia.objects.all()
    serializer_class = TramiteSerializer
    permission_classes = [AllowAny]

    # ============================
    # VALIDAR CÉDULA
    # ============================

    @action(detail=False, methods=['post'])
    def validar_cedula(self, request):

        cedula = request.data.get("cedula_numero")

        if not cedula:
            return Response(
                {"error": "Cédula requerida"},
                status=400
            )

        if len(cedula) != 10 or not cedula.isdigit():
            return Response(
                {"cedula_numero": ["Cédula inválida"]},
                status=400
            )

        return Response({"ok": True})

    # ============================
    # MONITOREO
    # ============================

    @action(detail=False, methods=['get'])
    def listar_monitoreo(self, request):

        sucursales = Sucursal.objects.all()

        data = []

        for s in sucursales:

            historico = AfluenciaHistorica.objects.filter(
                sucursal=s,
                dia_semana=0,
                hora=10
            ).first()

            espera = (
                historico.espera_promedio_minutos
                if historico
                else 45
            )

            data.append({
                "nombre": s.nombre,
                "espera": f"{espera} min",
                "estado": "BAJA" if espera < 40 else "ALTA"
            })

        return Response(data)

    # ============================
    # RECOMENDACIÓN INTELIGENTE
    # ============================

    @action(detail=True, methods=['get'])
    def recomendar_sucursal(self, request, pk=None):

        try:

            tramite = TramiteLicencia.objects.get(id=pk)

            if not tramite.zona:

                return Response({
                    "error": "Debe seleccionar una zona"
                }, status=400)

            user_lat = tramite.zona.latitud
            user_lon = tramite.zona.longitud

            dia_actual = int(
                request.query_params.get('dia', 0)
            )

            hora_actual = int(
                request.query_params.get('hora', 10)
            )

            sucursales = Sucursal.objects.all()

            if not sucursales.exists():

                return Response({
                    "sucursal": "Sin sedes disponibles",
                    "tiempo_espera": 0,
                    "distancia_km": 0,
                    "tiempo_total": 0,
                    "ahorro_estimado": 0
                })

            resultados = []

            for s in sucursales:

                if s.latitud is None or s.longitud is None:
                    continue

                distancia = distancia_km(
                    user_lat,
                    user_lon,
                    float(s.latitud),
                    float(s.longitud)
                )

                historico = AfluenciaHistorica.objects.filter(
                    sucursal=s,
                    dia_semana=dia_actual,
                    hora=hora_actual
                ).first()

                espera = (
                    historico.espera_promedio_minutos
                    if historico
                    else 45
                )

                # Aproximación:
                # 1 km ≈ 2 min de viaje

                tiempo_viaje = distancia * 2

                score = tiempo_viaje + espera

                resultados.append({

                    "nombre": s.nombre,

                    "espera": espera,

                    "distancia": distancia,

                    "tiempo_viaje": tiempo_viaje,

                    "score": score

                })

            if not resultados:

                return Response({
                    "sucursal": "Sin datos suficientes",
                    "tiempo_espera": 0,
                    "distancia_km": 0,
                    "tiempo_total": 0,
                    "ahorro_estimado": 0
                })

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

            return Response({

                "sucursal": mejor["nombre"],

                "tiempo_espera": mejor["espera"],

                "distancia_km": round(
                    mejor["distancia"],
                    2
                ),

                "tiempo_total": round(
                    mejor["score"]
                ),

                "ahorro_estimado": ahorro

            })

        except Exception as e:

            return Response(
                {"error": str(e)},
                status=500
            )

    # ============================
    # TOP 3 SUCURSALES CON MAYOR AFLUENCIA
    # ============================

    @action(detail=False, methods=['get'])
    def top_sucursales_afluencia(self, request):

        try:

            dia_actual = int(
                request.query_params.get('dia', 0)
            )

            hora_actual = int(
                request.query_params.get('hora', 10)
            )

            top = (
                AfluenciaHistorica.objects
                .filter(
                    dia_semana=dia_actual,
                    hora=hora_actual
                )
                .values('sucursal__nombre')
                .annotate(
                    promedio=Avg('espera_promedio_minutos')
                )
                .order_by('-promedio')[:3]
            )

            data = []

            for item in top:

                estado = (
                    "ALTA"
                    if item['promedio'] >= 40
                    else "BAJA"
                )

                data.append({

                    "sucursal": item['sucursal__nombre'],

                    "espera_promedio": round(
                        item['promedio'],
                        2
                    ),

                    "estado": estado

                })

            return Response(data)

        except Exception as e:

            return Response(
                {"error": str(e)},
                status=500
            )


class ZonaViewSet(viewsets.ModelViewSet):

    queryset = Zona.objects.all()
    serializer_class = ZonaSerializer
    permission_classes = [AllowAny]
