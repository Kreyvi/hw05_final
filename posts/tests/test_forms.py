import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Post, Group
from yatube import settings


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Test_user')
        cls.user.save()
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)
        Group.objects.create(title='test', slug='test')
        cls.group = Group.objects.get(slug='test')
        Post.objects.create(
            text='тестовая запись',
            author=cls.user,
        )
        cls.post = Post.objects.get(author=cls.user)
        testfile = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b')
        cls.test_image = SimpleUploadedFile(
            'test.jpg',
            testfile,
            content_type='image/jpg'
        )
        cls.form_data = {
            'text': 'ratatatata',
            'image': cls.test_image,

        }
        cache.clear()

    def tearDownClass():
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_post_form(self):
        count = Post.objects.count()
        response = self.authorized_user.post(
            path=reverse('new_post'),
            data=self.form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), count + 1)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_edit_form(self):
        response = self.authorized_user.post(
            path=reverse('post_edit',
                         args=(self.user, self.post.id)
                         ),
            data=self.form_data,
            follow=True,
        )
        self.assertRedirects(response,
                             reverse('post', args=(self.user, self.post.id))
                             )
        self.assertNotEqual(Post.objects.get(author=self.user).text,
                            self.post.text
                            )
        self.assertEqual(Post.objects.get(author=self.user).author,
                         self.post.author
                         )

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_img_in_context(self):
        urls_names = [
            reverse('index'),
            reverse('profile', args=(self.user.username,)),
            reverse('post', args=(self.user.username, self.post.id)),
        ]
        self.authorized_user.post(
            path=reverse('post_edit',
                         args=(self.user, self.post.id)
                         ),
            data=self.form_data,
            follow=True,
        )
        for urls_name in urls_names:
            with self.subTest():
                response = self.authorized_user.get(urls_name)
                self.assertIn('<img', response.content.decode())
