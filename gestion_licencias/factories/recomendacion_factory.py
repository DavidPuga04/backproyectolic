from ..strategies.estrategia_default import EstrategiaDefault


class RecomendacionFactory:

    @staticmethod
    def crear(tipo=None):
        """
        Selecciona la estrategia de recomendación
        """

        # Por ahora solo tenemos una estrategia
        if tipo == "default" or tipo is None:
            return EstrategiaDefault()

        # fallback por seguridad
        return EstrategiaDefault()