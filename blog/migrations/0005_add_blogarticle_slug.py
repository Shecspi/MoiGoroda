# Generated manually

from django.apps.registry import Apps
from django.db import migrations, models
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.utils.text import slugify


def populate_slug(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    BlogArticle = apps.get_model('blog', 'BlogArticle')
    for article in BlogArticle.objects.all():
        base = slugify(article.title, allow_unicode=True) or 'article'
        base = base[:256].rstrip('-')
        slug = base
        suffix = 0
        while BlogArticle.objects.filter(slug=slug).exclude(pk=article.pk).exists():
            suffix += 1
            slug = f'{base}-{suffix}'[:256]
        article.slug = slug
        article.save(update_fields=['slug'])


def noop(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_add_blogarticle_is_published'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogarticle',
            name='slug',
            field=models.SlugField(blank=True, max_length=256, null=True, unique=True, verbose_name='Слаг для URL'),
        ),
        migrations.RunPython(populate_slug, noop),
        migrations.AlterField(
            model_name='blogarticle',
            name='slug',
            field=models.SlugField(max_length=256, unique=True, verbose_name='Слаг для URL'),
        ),
    ]
