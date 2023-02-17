from django.views.generic import ListView

from news.models import News


class News_List(ListView):
    model = News
    paginate_by = 5
    ordering = '-created'
    template_name = 'news/list.html'
