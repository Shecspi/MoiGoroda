from __future__ import annotations

from typing import cast

from django.contrib.auth.models import AnonymousUser, User
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from blog.models import BlogArticle, BlogArticleView, BlogTag
from blog.views import BlogArticleDetail


class BlogArticleListViewTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.list_url = reverse('blog-list')

    def test_only_published_articles_visible_for_regular_user(self) -> None:
        published = BlogArticle.objects.create(
            title='Опубликовано',
            content='<p>text</p>',
            is_published=True,
        )
        BlogArticle.objects.create(
            title='Черновик',
            content='<p>text</p>',
            is_published=False,
        )

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        articles = list(response.context['article_list'])
        self.assertEqual(articles, [published])
        self.assertFalse(response.context['show_view_stats'])
        self.assertEqual(response.context['active_page'], 'blog')
        self.assertIn('page_title', response.context)
        self.assertIn('page_description', response.context)

    def test_superuser_sees_all_articles_and_view_stats_flag(self) -> None:
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='secret',
        )
        article = BlogArticle.objects.create(
            title='Статья для статистики',
            content='<p>text</p>',
            is_published=False,
        )
        # два просмотра: один авторизованный, один гость
        BlogArticleView.objects.create(article=article, user=admin, ip_address='1.1.1.1')
        BlogArticleView.objects.create(article=article, user=None, ip_address='2.2.2.2')

        self.client.force_login(admin)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        articles = list(response.context['article_list'])
        self.assertIn(article, articles)
        self.assertTrue(response.context['show_view_stats'])

        # Аннотированные поля должны быть доступны
        obj = articles[0]
        self.assertEqual(getattr(obj, 'view_count_total', None), 2)
        self.assertEqual(getattr(obj, 'view_count_auth', None), 1)
        self.assertEqual(getattr(obj, 'view_count_guest', None), 1)

    def test_filter_by_tag_and_context_filter_tag(self) -> None:
        tag = BlogTag.objects.create(name='Новости', slug='news')
        article_with_tag = BlogArticle.objects.create(
            title='С тегом',
            content='<p>text</p>',
            is_published=True,
        )
        article_with_tag.tags.add(tag)

        BlogArticle.objects.create(
            title='Без тега',
            content='<p>text</p>',
            is_published=True,
        )

        url = reverse('blog-list-by-tag', kwargs={'tag_slug': 'news'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        articles = list(response.context['article_list'])
        self.assertEqual(articles, [article_with_tag])
        self.assertEqual(response.context['filter_tag'], tag)
        self.assertIn('Новости', response.context['page_description'])

    def test_pagination_page_size(self) -> None:
        for i in range(7):
            BlogArticle.objects.create(
                title=f'Article {i}',
                content='<p>text</p>',
                is_published=True,
            )

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_paginated'])
        page_obj = response.context['page_obj']
        self.assertEqual(len(page_obj.object_list), 5)


class BlogArticleDetailViewTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.article = BlogArticle.objects.create(
            title='Детальная статья',
            content='<p>text</p>',
            is_published=True,
        )
        self.detail_url = reverse('blog-article-detail', kwargs={'pk': self.article.pk})

    def test_unpublished_article_not_visible_for_anonymous(self) -> None:
        self.article.is_published = False
        self.article.save()

        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 404)

    def test_unpublished_article_visible_for_superuser(self) -> None:
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='secret',
        )
        self.article.is_published = False
        self.article.save()

        self.client.force_login(admin)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)

    def test_view_creates_log_for_anonymous_user(self) -> None:
        response = self.client.get(self.detail_url, REMOTE_ADDR='10.0.0.1')
        self.assertEqual(response.status_code, 200)
        view = BlogArticleView.objects.get(article=self.article)
        self.assertIsNone(view.user)
        self.assertEqual(view.ip_address, '10.0.0.1')

    def test_view_creates_log_for_authenticated_user(self) -> None:
        user = User.objects.create_user(username='john', password='secret')
        self.client.force_login(user)

        response = self.client.get(self.detail_url, REMOTE_ADDR='10.0.0.2')
        self.assertEqual(response.status_code, 200)
        view = BlogArticleView.objects.get(article=self.article)
        self.assertEqual(view.user, user)
        self.assertEqual(view.ip_address, '10.0.0.2')

    def test_context_contains_basic_fields(self) -> None:
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['active_page'], 'blog')
        self.assertEqual(response.context['page_title'], self.article.title)
        self.assertEqual(response.context['page_description'], self.article.title)
        self.assertFalse(response.context['show_view_stats'])
        self.assertNotIn('view_count_total', response.context)

    def test_superuser_context_contains_view_stats(self) -> None:
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='secret',
        )
        # Предварительно создаём два просмотра: один авторизованный, один гость
        BlogArticleView.objects.create(
            article=self.article,
            user=admin,
            ip_address='1.1.1.1',
        )
        BlogArticleView.objects.create(
            article=self.article,
            user=None,
            ip_address='2.2.2.2',
        )

        self.client.force_login(admin)
        response = self.client.get(self.detail_url, REMOTE_ADDR='3.3.3.3')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['show_view_stats'])

        # Внутри get_context_data при заходе администратора создаётся ещё один лог просмотра (auth)
        self.assertEqual(BlogArticleView.objects.filter(article=self.article).count(), 3)
        self.assertEqual(response.context['view_count_total'], 3)
        self.assertEqual(
            response.context['view_count_auth'], 2
        )  # 1 предсозданный + 1 от текущего GET
        self.assertEqual(response.context['view_count_guest'], 1)

    def test_get_queryset_filters_unpublished_for_non_superuser(self) -> None:
        factory = RequestFactory()
        other_article = BlogArticle.objects.create(
            title='Черновик',
            content='<p>draft</p>',
            is_published=False,
        )
        request = factory.get(self.detail_url)

        class DummyUser:
            is_superuser = False

        request.user = cast(User | AnonymousUser, DummyUser())

        view = BlogArticleDetail()
        view.request = request
        qs = view.get_queryset()
        self.assertIn(self.article, qs)
        self.assertNotIn(other_article, qs)

    def test_get_queryset_does_not_filter_for_superuser(self) -> None:
        factory = RequestFactory()
        other_article = BlogArticle.objects.create(
            title='Черновик',
            content='<p>draft</p>',
            is_published=False,
        )
        request = factory.get(self.detail_url)

        class DummySuperUser:
            is_superuser = True

        request.user = cast(User | AnonymousUser, DummySuperUser())

        view = BlogArticleDetail()
        view.request = request
        qs = view.get_queryset()
        self.assertIn(self.article, qs)
        self.assertIn(other_article, qs)
