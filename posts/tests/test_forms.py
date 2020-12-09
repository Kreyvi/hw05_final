import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Post, Group
from yatube import settings

FORM_ERROR_TEXT = ("Формат файлов 'txt' не поддерживается. "
                   "Поддерживаемые форматы файлов: 'bmp, dib, gif, tif, tiff, "
                   "jfif, jpe, jpg, jpeg, pbm, pgm, ppm, pnm, png, apng, blp, "
                   "bufr, cur, pcx, dcx, dds, ps, eps, fit, fits, fli, flc, "
                   "ftc, ftu, gbr, grib, h5, hdf, jp2, j2k, jpc, jpf, jpx, "
                   "j2c, icns, ico, im, iim, mpg, mpeg, mpo, msp, palm, pcd,"
                   " pdf, pxr, psd, bw, rgb, rgba, sgi, ras, tga, icb, vda, "
                   "vst, webp, wmf, emf, xbm, xpm'.")


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
        cls.broken_file = SimpleUploadedFile(
            'test.txt',
            testfile,
            content_type='txt/txt'
        )
        cls.form_data = {
            'text': 'ratatatata',
            'image': cls.test_image,
        }
        cls.broken_data = {
            'text': 'error maybe?',
            'image': cls.broken_file,
        }
        cache.clear()

    def tearDownClass():
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_post_form_without_image(self):
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

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_not_image_file_post_form(self):
        response = self.authorized_user.post(
            path=reverse('new_post'),
            data=self.broken_data,
            follow=True,
        )
        self.assertFormError(response, 'form', 'image', FORM_ERROR_TEXT)
