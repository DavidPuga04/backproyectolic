from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import TramiteLicencia, Sucursal, AfluenciaHistorica, Zona
from .serializers import TramiteSerializer, ZonaSerializer
import math


class TramiteViewSet(viewsets.ModelViewSet):
    queryset = TramiteLicencia.objects.all()
    serializer_class = TramiteSerializer
    permission_classes = [AllowAny]

   
    # VALIDAR CÉDULA
    @action(detail=False, methods=['post'])
    def validar_cedula(self, request):
        cedula = request.data.get("cedula_numero")

        if not cedula:
            return Response({"error": "Cédula requerida"}, status=400)

        if len(cedula) != 10 or not cedula.isdigit():
            return Response({"cedula_numero": ["Cédula inválida"]}, status=400)

        return Response({"ok": True})


  
    # MONITOREO
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

            espera = historico.espera_promedio_minutos if historico else 45

            data.append({
                "nombre": s.nombre,
                "espera": f"{espera} min",
                "estado": "BAJA" if espera < 40 else "ALTA"
            })

        return Response(data)


   
    # RECOMENDACIÓN
    @action(detail=True, methods=['get'])
    def recomendar_sucursal(self, request, pk=None):

        try:
            user_lat = float(request.query_params.get('lat', -0.1807))
            user_lon = float(request.query_params.get('lon', -78.4678))
            dia_actual = int(request.query_params.get('dia', 0))
            hora_actual = int(request.query_params.get('hora', 10))

            sucursales = Sucursal.objects.all()

            if not sucursales.exists():
                return Response({
                    "sucursal": "Sin sedes disponibles",
                    "tiempo_espera": 0,
                    "ahorro_estimado": 0
                })

            resultados = []

            for s in sucursales:

                # Evitar NULL
                if s.latitud is None or s.longitud is None:
                    continue

                distancia = math.sqrt(
                    (float(s.latitud) - user_lat) ** 2 +
                    (float(s.longitud) - user_lon) ** 2
                )

                historico = AfluenciaHistorica.objects.filter(
                    sucursal=s,
                    dia_semana=dia_actual,
                    hora=hora_actual
                ).first()

                espera = historico.espera_promedio_minutos if historico else 45

                resultados.append({
                    "nombre": s.nombre,
                    "espera": espera,
                    "total": distancia * 100 + espera
                })

            if not resultados:
                return Response({
                    "sucursal": "Sin datos suficientes",
                    "tiempo_espera": 0,
                    "ahorro_estimado": 0
                })

            mejor = sorted(resultados, key=lambda x: x["total"])[0]

            return Response({
                "sucursal": mejor["nombre"],
                "tiempo_espera": mejor["espera"],
                "ahorro_estimado": 60 - mejor["espera"]
            })

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=500
            )


class ZonaViewSet(viewsets.ModelViewSet):
    queryset = Zona.objects.all()
    serializer_class = ZonaSerializer
    permission_classes = [AllowAny]