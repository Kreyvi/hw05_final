from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post
from posts.views import index


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        """Creating guest user"""
        cls.guest_user = Client()

        """Creating authorized user"""
        cls.user = User.objects.create_user(username='Test_user')
        cls.user.save()
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)

        """Creating authorized user != author"""
        not_author = User.objects.create_user(username='not_author')
        not_author.save()
        cls.authorized_not_author = Client()
        cls.authorized_not_author.force_login(not_author)

        '''Creating Group'''
        cls.group = Group.objects.create(
            title='Test_group',
            slug='test-group',
        )

        """Creating Post"""
        Post.objects.create(
            text='test text',
            author=cls.user,
        )

        """Preparing urls for tests"""
        cls.post = Post.objects.get(text__contains='test')

    def test_urls_guest(self):
        """Checking availability for unauthorized user"""
        urls_responses = {
            reverse('index'): 200,
            reverse('new_post'): 302,
            reverse('group', args=(self.group.slug,)): 200,
            reverse('profile', args=(self.user.username,)): 200,
            reverse('post', args=(self.user.username, self.post.id)): 200,
            reverse('post_edit', args=(self.user.username, self.post.id)): 302,
        }
        for url, answer in urls_responses.items():
            with self.subTest():
                response = self.guest_user.get(url)
                self.assertEqual(response.status_code, answer)

    def test_urls_authorized_author(self):
        """Checking availability for authorized user == author"""
        urls_responses = {
            reverse('new_post'): 200,
            reverse('post_edit', args=(self.user.username, self.post.id)): 200,
        }
        for url, answer in urls_responses.items():
            with self.subTest():
                response = self.authorized_user.get(url)
                self.assertEqual(response.status_code, answer)

    def test_urls_authorized_not_author(self):
        """Checking availability for authorized user != author"""
        response = self.authorized_not_author.get(
            reverse('post_edit', args=(self.user.username, self.post.id))
        )
        self.assertNotEqual(response.status_code, 200)

    def test_redirects_check(self):
        """Checking redirect for authorized user != author for Edit page"""
        response = self.authorized_not_author.get(
            reverse('post_edit', args=(self.user.username, self.post.id)),
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('post', args=(self.user.username, self.post.id)),
            status_code=302,
            target_status_code=200
        )

    def test_redirects_new_check(self):
        """Checking redirect for guest user for New page"""
        response = self.guest_user.get(
            path=reverse('new_post'),
            follow=True
        )
        self.assertRedirects(
            response=response,
            expected_url=reverse('login')+'?next='+reverse('new_post'),
            status_code=302,
            target_status_code=200
        )


class TemplatesUrlsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Описание ' * 5,
        )
        cls.group = Group.objects.get(slug='test')
        cls.user = get_user_model().objects.create_user(username='Test_user')
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)

        Post.objects.create(
            text='тест',
            author=cls.user,
            group=Group.objects.get(slug='test'),
        )
        cls.post = Post.objects.get(author=cls.user)

    def test_correct_templates(self):
        templates_urls_names = {
            reverse('index'): 'posts/index.html',
            reverse('group', args=(self.group.slug,)): 'group.html',
            reverse('new_post'): 'posts/new.html',
            reverse(
                'post_edit',
                args=(self.user.username, self.post.id)
            ): 'posts/new.html',
        }
        for url_name, template in templates_urls_names.items():
            with self.subTest():
                response = self.authorized_user.get(url_name)
                self.assertTemplateUsed(response, template)
