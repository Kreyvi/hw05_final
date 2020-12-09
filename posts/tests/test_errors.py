from django.test import Client, TestCase


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        """Creating guest user"""
        cls.guest_user = Client()

    def test_404_code_template(self):
        response = self.guest_user.get('/@@@/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'misc/404.html')
