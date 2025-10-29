# Generated manually to add ProfesorCurso model
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_actualizar_silabo_y_clase_dictada'),
    ]

    operations = [
        # Crear tabla profesor_curso
        migrations.CreateModel(
            name='ProfesorCurso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_asignacion', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Asignación')),
                ('activo', models.BooleanField(default=True, verbose_name='Asignación Activa')),
                ('curso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profesores_asignados', to='app.curso')),
                ('profesor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cursos_asignados', to='app.profesor')),
                ('tipo_profesor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.tipoprofesor', verbose_name='Tipo de Profesor en este Curso')),
            ],
            options={
                'verbose_name': 'Asignación Profesor-Curso',
                'verbose_name_plural': 'Asignaciones Profesor-Curso',
                'db_table': 'profesor_curso',
                'ordering': ['curso', 'tipo_profesor'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='profesorcurso',
            unique_together={('profesor', 'curso', 'tipo_profesor')},
        ),
    ]
