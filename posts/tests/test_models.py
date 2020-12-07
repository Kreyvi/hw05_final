from django.contrib.auth.models import User
from django.test import TestCase

from posts.models import Post, Group


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        """Creating user-author and post"""
        super().setUpClass()
        User.objects.create(
            username='test_user',
            password=123456
        )
        cls.test_user = User.objects.get(username='test_user')
        Post.objects.create(
            text='Тестовый текст',
            author=cls.test_user
        )
        cls.post = Post.objects.get(author=cls.test_user)

    def test_post_help(self):
        """Checking help texts in Post"""
        post = self.post
        field_help_texts = {
            'text': 'Введите текст вашей записи',
            'group': 'Группа записи'
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected
                )

    def test_post_verbose(self):
        """Checking verbose names in Post"""
        post = self.post
        field_verboses = {
            'text': 'Текст',
            'group': 'Группа',
            'pub_date': 'Дата публикации'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected
                )

    def test_post_str(self):
        """Checking __str__ in Post"""
        post = self.post
        str_text = (f'{post.pub_date:%d.%m.%Y %H:%M:%S}'
                    f'| {post.author}| {post.text}')

        test_str = Post.objects.filter(author=self.test_user)
        self.assertEqual(str(test_str[0]), str_text)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        """Creating group"""
        super().setUpClass()
        Group.objects.create(
            title='Тестовая группа',
            slug='Testovaya-gruppa',
            description="Проверка создания тестовой группы"
        )
        cls.group = Group.objects.get(slug='Testovaya-gruppa')

    def test_group_str(self):
        """Checking __str__ in Group"""
        test_str = Group.objects.filter(slug='Testovaya-gruppa')
        self.assertEqual(test_str[0], self.group)
