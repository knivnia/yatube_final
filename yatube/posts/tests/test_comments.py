from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Comment, Group, Post

User = get_user_model()


class CommentsTests(TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description',
        )
        self.user = User.objects.create_user(username='Grogu')
        self.post = Post.objects.create(
            author=self.user,
            text='Test post',
            group=self.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_guest_cannot_leave_comment(self):
        """Guest cannot leave comment."""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'There should not be a comment here',
        }
        self.guest_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count)

    def test_auth_user_can_leave_comment(self):
        """Authorized client can leave comment."""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Comment text',
        }
        self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
