from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .models import TramiteLicencia, AfluenciaHistorica, Zona
from .serializers import TramiteSerializer, ZonaSerializer
from .services.recomendacion_service import RecomendacionService
from .services.monitoreo_service import MonitoreoService
from django.db.models import Avg


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
    # MONITOREO (REFACTORIZADO A SERVICE)
    # ============================

    @action(detail=False, methods=['get'])
    def listar_monitoreo(self, request):

        service = MonitoreoService()
        data = service.obtener_monitoreo()

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

            dia_actual = int(
                request.query_params.get('dia', 0)
            )

            hora_actual = int(
                request.query_params.get('hora', 10)
            )

            service = RecomendacionService()

            resultado = service.recomendar(
                tramite,
                dia_actual,
                hora_actual
            )

            return Response(resultado)

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
                    "espera_promedio": round(item['promedio'], 2),
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