from unittest.mock import Mock, patch

from django.template import Context
from django.test import TestCase
from django.utils.safestring import SafeString

from blog.templatetags import content_ads


class ContentWithAdsTagTests(TestCase):
    def setUp(self) -> None:
        self.context = Context({'user': None})

    def test_returns_original_html_when_empty(self) -> None:
        result = content_ads.content_with_ads(self.context, '', 'dummy.html')
        self.assertIsInstance(result, SafeString)
        self.assertEqual(str(result), '')

    def test_returns_original_html_when_no_placeholders(self) -> None:
        html = '<p>Без рекламы</p>'
        result = content_ads.content_with_ads(self.context, html, 'dummy.html')
        self.assertEqual(str(result), html)

    @patch('blog.templatetags.content_ads.loader.get_template')
    def test_inserts_ads_for_comment_placeholder(self, mock_get_template: Mock) -> None:
        mock_tpl = Mock()
        mock_tpl.render.return_value = '[AD]'
        mock_get_template.return_value = mock_tpl

        html = '<p>Преди</p><!-- rtb_banner --><p>После</p>'
        result = content_ads.content_with_ads(self.context, html, 'dummy.html')
        rendered = str(result)

        # Комментарий заменён на один рекламный блок
        self.assertIn('[AD]', rendered)
        self.assertIn('ad-insert-in-content', rendered)
        self.assertNotIn('<!-- rtb_banner -->', rendered)

    @patch('blog.templatetags.content_ads.loader.get_template')
    def test_inserts_ads_for_div_placeholder(self, mock_get_template: Mock) -> None:
        mock_tpl = Mock()
        mock_tpl.render.return_value = '[AD]'
        mock_get_template.return_value = mock_tpl

        html = (
            '<p>До</p>'
            '<div class="ad-placeholder-rtb-banner" data-ad="rtb_banner"></div>'
            '<p>После</p>'
        )
        result = content_ads.content_with_ads(self.context, html, 'dummy.html')
        rendered = str(result)

        # Див-маркер приведён к комментарию и обработан
        self.assertIn('[AD]', rendered)
        self.assertIn('ad-insert-in-content', rendered)
        self.assertNotIn('ad-placeholder-rtb-banner', rendered)

    @patch('blog.templatetags.content_ads.loader.get_template')
    def test_inserts_correct_template_for_inside_article_placeholder(
        self, mock_get_template: Mock
    ) -> None:
        mock_tpl1 = Mock()
        mock_tpl1.render.return_value = '[AD_INSIDE_1]'
        mock_tpl2 = Mock()
        mock_tpl2.render.return_value = '[AD_INSIDE_2]'
        mock_get_template.side_effect = lambda name: mock_tpl1 if '1' in name else mock_tpl2

        html = (
            '<p>До</p>'
            '<div class="ad-placeholder-rtb-banner" data-ad="rtb_banner_inside_article_1"></div>'
            '<p>Между</p>'
            '<div class="ad-placeholder-rtb-banner" data-ad="rtb_banner_inside_article_2"></div>'
            '<p>После</p>'
        )
        result = content_ads.content_with_ads(self.context, html, 'advertisement/rtb_banner.html')
        rendered = str(result)

        self.assertIn('[AD_INSIDE_1]', rendered)
        self.assertIn('[AD_INSIDE_2]', rendered)
        self.assertNotIn('ad-placeholder-rtb-banner', rendered)

    @patch('blog.templatetags.content_ads.loader.get_template')
    def test_multiple_placeholders_insert_multiple_ads(self, mock_get_template: Mock) -> None:
        mock_tpl = Mock()
        mock_tpl.render.return_value = '[AD]'
        mock_get_template.return_value = mock_tpl

        html = '<p>1</p><!-- rtb_banner --><p>2</p><!-- rtb_banner --><p>3</p>'
        result = content_ads.content_with_ads(self.context, html, 'dummy.html')
        rendered = str(result)

        self.assertEqual(rendered.count('[AD]'), 2)
        self.assertEqual(rendered.count('ad-insert-in-content'), 2)
