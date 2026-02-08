# Convert existing Markdown content to HTML (e.g. after switching to CKEditor/HTML).

from typing import Any

from django.db import migrations
from markdown import markdown  # type: ignore[import-untyped]


def convert_markdown_to_html(apps: Any, schema_editor: Any) -> None:
    News = apps.get_model('news', 'News')
    for article in News.objects.iterator():
        article.content = markdown(article.content or '')
        article.save(update_fields=['content'])


def noop(apps: Any, schema_editor: Any) -> None:
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('news', '0006_alter_news_users_read'),
    ]

    operations = [
        migrations.RunPython(convert_markdown_to_html, reverse_code=noop),
    ]
