from .base import RecommendationStrategy


class EstrategiaDefault(RecommendationStrategy):

    def calcular_score(self, tiempo_viaje, espera):
        return tiempo_viaje + espera