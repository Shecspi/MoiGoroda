from django.contrib.postgres.operations import AddIndexConcurrently
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('city', '0032_visitedcity_created_at_index_concurrent'),
    ]

    atomic = False

    operations = [
        AddIndexConcurrently(
            model_name='visitedcity',
            index=models.Index(fields=['user', 'city'], name='city_visite_user_id_166224_idx'),
        ),
    ]
