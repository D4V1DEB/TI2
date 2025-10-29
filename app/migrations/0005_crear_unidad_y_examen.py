# Generated manually to create Unidad and Examen tables
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_crear_profesor_curso'),
    ]

    operations = [
        # Crear tabla curso_unidad
        migrations.CreateModel(
            name='Unidad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('fecha_limite_notas', models.DateField()),
                ('curso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unidades', to='app.curso')),
            ],
            options={
                'verbose_name': 'Unidad',
                'verbose_name_plural': 'Unidades',
                'db_table': 'curso_unidad',
            },
        ),
        
        # Crear tabla curso_examen
        migrations.CreateModel(
            name='Examen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('fecha_inicio', models.DateField(verbose_name='Fecha de Inicio')),
                ('fecha_fin', models.DateField(verbose_name='Fecha de Fin')),
                ('descripcion', models.TextField(blank=True, null=True, verbose_name='Descripción')),
                ('curso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='examenes', to='app.curso')),
            ],
            options={
                'verbose_name': 'Examen',
                'verbose_name_plural': 'Exámenes',
                'db_table': 'curso_examen',
                'ordering': ['fecha_inicio'],
            },
        ),
    ]
