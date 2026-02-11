# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_add_blogarticle_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogarticle',
            name='meta_description',
            field=models.CharField(
                default='Описание статьи',
                help_text='Текст для мета-тега description на странице статьи (рекомендуется до 160 символов)',
                max_length=160,
                verbose_name='Описание для meta description',
            ),
            preserve_default=False,
        ),
    ]
