from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.test import Client, TestCase


class FlatpageURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.site = Site(pk=1, domain='testserver')
        cls.site.save()
        cls.guest_client = Client()
        cls.flat_about = FlatPage.objects.create(
            url='/about-author/',
            title='Об авторе',
            content='<b>Тест-тест-тест-тест</b>'
        )
        cls.flat_about.save()
        cls.flat_spec = FlatPage.objects.create(
            url='/about-spec/',
            title='О технологиях',
            content='<b>Тест-тест-тест</b>'
        )
        cls.flat_spec.save()
        cls.static_pages = ('/about-author/', '/about-spec/')
        cls.titles = {
            '/about-author/': 'Об авторе',
            '/about-spec/': 'О технологиях',
        }
        cls.contents = {
            '/about-author/': '<b>Тест-тест-тест-тест</b>',
            '/about-spec/': '<b>Тест-тест-тест</b>',
        }
        cls.flat_spec.sites.add(cls.site)
        cls.flat_about.sites.add(cls.site)

    def test_static_page_response(self):
        for url in self.static_pages:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(200, response.status_code)

    def test_content(self):
        for url in self.static_pages:
            with self.subTest():
                response = self.guest_client.get(url)
                title = response.context.get('flatpage').title
                content = response.context.get('flatpage').content
                self.assertEqual(self.titles[url], title)
                self.assertEqual(self.contents[url], content)
