from django.db import migrations

def crear_zonas(apps, schema_editor):

    Zona = apps.get_model('gestion_licencias', 'Zona')

    zonas = [
        "Norte",
        "Sur",
        "Centro",
        "Cumbayá",
        "Tumbaco",
        "Valle de los Chillos"
    ]

    for nombre in zonas:
        Zona.objects.get_or_create(nombre=nombre)


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_licencias', '0003_zona_tramitelicencia_zona'),
    ]

    operations = [
        migrations.RunPython(crear_zonas),
    ]