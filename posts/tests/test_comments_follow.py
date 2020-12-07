from django.contrib.auth.models import User

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post


class CommentFollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='Test_user')
        cls.user.save()
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)

        cls.follower = User.objects.create_user(username='Follower')
        cls.follower.save()
        cls.follower_client = Client()
        cls.follower_client.force_login(cls.follower)

        cls.guest_user = Client()

        Post.objects.create(
            text='тестовая запись',
            author=cls.user,
        )
        cls.post = Post.objects.get(text__contains='тестовая запись')
        cls.post.save()
        cls.form_data = {'text': 'erere'}

    def test_guest_comment(self):
        response = self.guest_user.get(
            reverse('add_comment', args=(self.user, self.post.id)), follow=True
        )
        self.assertRedirects(
            response, (reverse('login') +
                       '?next=' +
                       reverse('add_comment', args=(self.user, self.post.id))
                       ))

    def test_guest_comment_post(self):
        """ Проверяем отсутствие формы для комментирования"""
        response = self.guest_user.get(
            path=reverse('post', args=(self.user, self.post.id)),
        )
        self.assertNotIn('<form', response.content.decode())

    def test_follow(self):
        Post.objects.create(
            author=self.user,
            text='Text',
        )
        """ Проверяем что страница с подписками пуста """
        response = self.follower_client.get(reverse('follow_index'))
        self.assertEqual(0, len(response.context.get('page')))

        """ Подписываемся на юзера и проверяем подписку """
        self.follower_client.get(
            reverse('profile_follow', args=(self.user,))
        )
        self.assertEqual(1, self.user.following.count())
        Post.objects.create(
            author=self.user,
            text='Text1',
        )

        """ Проверяем где появляются посты """
        response_follower = self.follower_client.get(reverse('follow_index'))
        self.assertNotEqual(0, len(response_follower.context.get('page')))
        response_following = self.authorized_user.get(reverse('follow_index'))
        self.assertEqual(0, len(response_following.context.get('page')))



