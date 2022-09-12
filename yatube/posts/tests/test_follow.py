from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group, Follow

User = get_user_model()


class FollowViewsTests(TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description',
        )
        self.author = User.objects.create_user(username='Grogu')
        self.follower = User.objects.create_user(username='Lea')
        self.post = Post.objects.create(
            author=self.author,
            text='Test post',
            group=self.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()

    def test_follow(self):
        """Check if user can follow other user."""
        self.authorized_client.force_login(self.follower)
        self.authorized_client.post(
            reverse(
                'posts:profile_follow',
                kwargs={
                    'username': self.author,
                }
            )
        )
        self.assertTrue(Follow.objects.filter(
            user=self.follower,
            author=self.author
        ).exists()
        )

    def test_unfollow(self):
        """Check if user can unfollow other user."""
        self.authorized_client.force_login(self.follower)
        self.authorized_client.post(
            reverse(
                'posts:profile_follow',
                kwargs={
                    'username': self.author,
                }
            )
        )
        self.authorized_client.post(
            reverse(
                'posts:profile_unfollow',
                kwargs={
                    'username': self.author,
                }
            )
        )
        self.assertFalse(Follow.objects.filter(
            user=self.follower,
            author=self.author
        ).exists()
        )

    def test_follow_index_shows_correct_context(self):
        """Check that new author post shows on follower feed."""
        new_post = Post.objects.create(
            author=self.author,
            text='Test post',
            group=self.group
        )
        self.authorized_client.force_login(self.follower)
        self.authorized_client.post(
            reverse(
                'posts:profile_follow',
                kwargs={
                    'username': self.author,
                }
            )
        )
        following_index = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertIn(new_post, following_index.context['page_obj'])
        self.authorized_client.post(
            reverse(
                'posts:profile_unfollow',
                kwargs={
                    'username': self.author,
                }
            )
        )
        following_index = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertNotIn(new_post, following_index.context['page_obj'])

    def test_cannot_follow_youself(self):
        """User cannot follow himself."""
        self.authorized_client.force_login(self.follower)
        self.authorized_client.post(
            reverse(
                'posts:profile_follow',
                kwargs={
                    'username': self.follower,
                }
            )
        )
        self.assertFalse(
            Follow.objects.filter(
                user=self.follower,
                author=self.follower
            ).exists()
        )
