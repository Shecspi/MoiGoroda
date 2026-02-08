from django.core.management.base import BaseCommand
from markdown import markdown
from news.models import News
from typing import Any


class Command(BaseCommand):
    help = 'Convert Markdown articles to HTML'

    def handle(self, *args: Any, **options: Any) -> None:
        for article in News.objects.all():
            article.content = markdown(article.content)
            article.save(update_fields=['content'])
