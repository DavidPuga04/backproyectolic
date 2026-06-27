from ..models import Sucursal, AfluenciaHistorica


class MonitoreoService:

    def obtener_monitoreo(self):

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

        return data