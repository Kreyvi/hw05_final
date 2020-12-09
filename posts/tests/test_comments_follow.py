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
        """ Checking if unauthorized user redirected"""
        response = self.guest_user.get(
            reverse('add_comment', args=(self.user, self.post.id)), follow=True
        )
        self.assertRedirects(
            response, (reverse('login') +
                       '?next=' +
                       reverse('add_comment', args=(self.user, self.post.id))
                       ))

    def test_guest_comment_post(self):
        """ Checking that there is no form on comment page"""
        response = self.guest_user.get(
            path=reverse('post', args=(self.user, self.post.id)),
        )
        self.assertNotIn('<form', response.content.decode())

    def test_follow_unfollow(self):
        """ Checking follow page with and without follow
         Checking follow and unfollow functioning"""

        Post.objects.create(
            author=self.user,
            text='Text',
        )
        response = self.follower_client.get(reverse('follow_index'))
        self.assertEqual(0, len(response.context.get('page')))
        self.follower_client.get(
            reverse('profile_follow', args=(self.user,))
        )
        self.assertEqual(1, self.user.following.count())
        Post.objects.create(
            author=self.user,
            text='Text1',
        )
        response_follower = self.follower_client.get(reverse('follow_index'))
        self.assertNotEqual(0, len(response_follower.context.get('page')))
        response_following = self.authorized_user.get(reverse('follow_index'))
        self.assertEqual(0, len(response_following.context.get('page')))
        self.follower_client.get(
            reverse('profile_unfollow', args=(self.user,))
        )
        self.assertEqual(0, self.user.following.count())
        response_unfollow = self.follower_client.get(reverse('follow_index'))
        self.assertEqual(0, len(response_unfollow.context.get('page')))
