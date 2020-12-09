from django.contrib.auth import get_user_model
from django import forms
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Group, Post


class ContextCheckTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User = get_user_model()
        cls.user = User.objects.create_user(username='test_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        Group.objects.create(
            title='Тестовая группа',
            slug='Testovaya-gruppa',
            description="Проверка создания тестовой группы"
        )
        for post in range(25):
            Post.objects.create(
                author=cls.user,
                text='Text',
                group=Group.objects.get(id=1),
            )
        cls.group = Group.objects.get(id=1)

    def check_text_author_group(self, response):
        text_check = response.context.get('page')[0].text
        author_check = response.context.get('page')[0].author
        group_check = response.context.get('page')[0].group
        self.assertEqual('Text', text_check)
        self.assertEqual(self.user, author_check)
        self.assertEqual(self.group, group_check)

    def test_main_page_context_and_paginator(self):
        """Checking context and number of posts on page"""
        response = self.authorized_client.get(reverse('index'))
        self.check_text_author_group(response)
        post_count = len(response.context.get('page'))
        page_range = response.context.get('paginator').page_range
        self.assertEqual(10, post_count)
        self.assertEqual(range(1, 4), page_range)

    def test_group_page_context(self):
        response = self.authorized_client.get(reverse(
            'group',
            args=('Testovaya-gruppa',)
            )
        )
        self.check_text_author_group(response)

    def test_new_page_context(self):
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_page_context(self):
        response = self.authorized_client.get(
            reverse('post_edit', args=('test_user', 1,))
        )
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_add_new_post(self):
        counter = Post.objects.count()
        form_data = {
            'group': self.group,
            'text': '123123123123123',
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), counter)

    def test_profile_page_context(self):
        """Checking context and number of posts on page"""
        response = self.authorized_client.get(
            reverse('profile', args=('test_user',))
        )
        self.check_text_author_group(response)
        counter_check = response.context.get('counter')
        self.assertEqual(25, counter_check)

    def test_post_context(self):
        response = self.authorized_client.get(
            reverse('post', args=('test_user', 1,))
        )
        text_check = response.context.get('post').text
        author_check = response.context.get('post').author
        counter_check = response.context.get('counter')
        self.assertEqual('Text', text_check)
        self.assertEqual(self.user, author_check)
        self.assertEqual(25, counter_check)
