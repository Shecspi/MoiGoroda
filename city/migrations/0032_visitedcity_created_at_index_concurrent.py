from django.contrib.postgres.operations import AddIndexConcurrently
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('city', '0031_cityuserphoto'),
    ]

    atomic = False

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='visitedcity',
                    name='created_at',
                    field=models.DateTimeField(
                        auto_now_add=True,
                        verbose_name='Дата и время создания',
                        db_index=True,
                    ),
                ),
            ],
            database_operations=[
                AddIndexConcurrently(
                    model_name='visitedcity',
                    index=models.Index(
                        fields=['created_at'],
                        name='city_visitedcity_created_at_42b0dcef',
                    ),
                ),
            ],
        ),
    ]
