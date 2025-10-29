# Generated manually to handle silabo table update
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_ubicacion_accesoprof_alerta_generada_and_more'),
    ]

    operations = [
        # Primero eliminar la tabla silabo_contenidos si existe
        migrations.RunSQL(
            sql='DROP TABLE IF EXISTS silabo_contenidos;',
            reverse_sql='',
        ),
        
        # Crear nueva tabla silabo con la estructura correcta
        migrations.RunSQL(
            sql='''
                CREATE TABLE IF NOT EXISTS silabo_new (
                    curso_id INTEGER PRIMARY KEY REFERENCES curso(id) ON DELETE CASCADE,
                    archivo_pdf VARCHAR(100) NULL
                );
            ''',
            reverse_sql='DROP TABLE IF EXISTS silabo_new;',
        ),
        
        # Copiar datos del curso_id (sin archivo_pdf porque no existía)
        migrations.RunSQL(
            sql='INSERT OR IGNORE INTO silabo_new (curso_id) SELECT curso_id FROM silabo;',
            reverse_sql='',
        ),
        
        # Eliminar tabla antigua
        migrations.RunSQL(
            sql='DROP TABLE IF EXISTS silabo;',
            reverse_sql='',
        ),
        
        # Renombrar nueva tabla
        migrations.RunSQL(
            sql='ALTER TABLE silabo_new RENAME TO silabo;',
            reverse_sql='',
        ),
        
        # Crear tabla clase_dictada
        migrations.CreateModel(
            name='ClaseDictada',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(verbose_name='Fecha de la clase')),
                ('numero_clase', models.PositiveIntegerField(help_text='Número correlativo de la clase en el curso', verbose_name='Número de clase')),
                ('temas_tratados', models.TextField(help_text='Descripción de los temas tratados en la clase', verbose_name='Temas tratados')),
                ('observaciones', models.TextField(blank=True, null=True, verbose_name='Observaciones adicionales')),
                ('fecha_registro', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de registro')),
                ('curso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clases_dictadas', to='app.curso')),
                ('profesor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='clases_dictadas', to='app.profesor')),
            ],
            options={
                'verbose_name': 'Clase Dictada',
                'verbose_name_plural': 'Clases Dictadas',
                'db_table': 'clase_dictada',
                'ordering': ['curso', 'numero_clase'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='clasedictada',
            unique_together={('curso', 'fecha')},
        ),
    ]
