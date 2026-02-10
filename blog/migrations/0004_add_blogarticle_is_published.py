# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_add_blogtag_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogarticle',
            name='is_published',
            field=models.BooleanField(default=True, verbose_name='Опубликована'),
        ),
    ]
