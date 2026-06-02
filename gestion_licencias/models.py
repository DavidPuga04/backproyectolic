from django.db import models


class Sucursal(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    latitud = models.FloatField()
    longitud = models.FloatField()

    def __str__(self):
        return self.nombre


class AfluenciaHistorica(models.Model):
    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.CASCADE,
        related_name='historicos'
    )

    dia_semana = models.IntegerField(
        help_text="0=Lunes, 6=Domingo"
    )

    hora = models.IntegerField()

    espera_promedio_minutos = models.IntegerField()


class Zona(models.Model):

    nombre = models.CharField(max_length=100)

    latitud = models.FloatField(
        default=-0.1807
    )

    longitud = models.FloatField(
        default=-78.4678
    )

    def __str__(self):
        return self.nombre


class TramiteLicencia(models.Model):

    cedula_numero = models.CharField(
        max_length=10,
        unique=True
    )

    zona = models.ForeignKey(
        'Zona',
        on_delete=models.CASCADE,
        related_name='tramites',
        null=True,
        blank=True
    )

    # Paso 1
    archivo_cedula = models.FileField(
        upload_to='cedulas/',
        null=True,
        blank=True
    )

    # Paso 2
    archivo_sangre = models.FileField(
        upload_to='sangre/',
        null=True,
        blank=True
    )

    # Paso 3
    archivo_psico = models.FileField(
        upload_to='psicosensometrico/',
        null=True,
        blank=True
    )

    # Paso 4
    pago_completado = models.BooleanField(default=False)

    paso_actual = models.IntegerField(default=1)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cedula_numero