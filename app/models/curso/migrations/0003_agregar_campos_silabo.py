from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        # Asegúrate que este nombre coincida con tu última migración en esta carpeta
        ('curso', '0002_initial'), 
    ]

    operations = [
        migrations.AddField(
            model_name='silabo',
            name='comentarios',
            field=models.TextField(blank=True, help_text='Comentarios adicionales del profesor', null=True),
        ),
        migrations.AddField(
            model_name='silabo',
            name='temas_adicionales',
            field=models.TextField(blank=True, help_text='Temas adicionales a tratar', null=True),
        ),
    ]