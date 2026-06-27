from ..models import Sucursal, AfluenciaHistorica


class SucursalRepository:

    def obtener_sucursales(self):
        return Sucursal.objects.all()

    def obtener_historico(self, sucursal, dia, hora):

        return (
            AfluenciaHistorica.objects
            .filter(
                sucursal=sucursal,
                dia_semana=dia,
                hora=hora
            )
            .first()
        )