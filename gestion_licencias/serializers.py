from rest_framework import serializers
from .models import TramiteLicencia, Zona


class TramiteSerializer(serializers.ModelSerializer):

    archivo_cedula = serializers.FileField(required=False, allow_null=True)
    archivo_sangre = serializers.FileField(required=False, allow_null=True)
    archivo_psico = serializers.FileField(required=False, allow_null=True)
    zona = serializers.PrimaryKeyRelatedField(
        queryset=Zona.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = TramiteLicencia
        fields = '__all__'

    def validate_cedula_numero(self, value):

        if not value.isdigit():
            raise serializers.ValidationError("Solo números")

        if len(value) != 10:
            raise serializers.ValidationError("Debe tener 10 dígitos")

        provincia = int(value[:2])
        if provincia < 1 or provincia > 24:
            raise serializers.ValidationError("Provincia inválida")

        return value


class ZonaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Zona
        fields = '__all__'