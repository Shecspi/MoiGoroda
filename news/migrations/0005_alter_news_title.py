# Generated by Django 4.1.2 on 2023-04-24 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0004_alter_news_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='title',
            field=models.CharField(help_text='Указанный заголовок новости будет отображатьсят только в админ-панели.<br>Пользователи его не увидят. Для них необходимо указывать заголовок новости в поле ниже.', max_length=256, verbose_name='Заголовок'),
        ),
    ]