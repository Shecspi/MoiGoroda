from django.contrib import admin
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from blog.admin import BlogArticleAdmin
from blog.models import BlogArticle, BlogArticleView


class BlogArticleAdminTests(TestCase):
    def setUp(self) -> None:
        self.site = admin.sites.AdminSite()
        self.admin = BlogArticleAdmin(BlogArticle, self.site)
        self.factory = RequestFactory()

    def test_get_queryset_annotates_view_counts(self) -> None:
        user = User.objects.create_user(username='john', password='secret')
        article = BlogArticle.objects.create(
            title='Админская статья',
            content='<p>text</p>',
            meta_description='Описание админской статьи',
            is_published=True,
        )
        # два просмотра: один авторизованный, один гость
        BlogArticleView.objects.create(article=article, user=user, ip_address='1.1.1.1')
        BlogArticleView.objects.create(article=article, user=None, ip_address='2.2.2.2')

        request = self.factory.get('/admin/blog/blogarticle/')
        qs = self.admin.get_queryset(request)
        obj = qs.get(pk=article.pk)

        self.assertEqual(self.admin.get_views_authenticated(obj), 1)
        self.assertEqual(self.admin.get_views_guest(obj), 1)
        self.assertEqual(self.admin.get_views_total(obj), 2)
