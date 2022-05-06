from xml.etree.ElementTree import Comment
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

    def test_post_detail_page_shows_correct_context(self):
        """Guest cannot leave comment."""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'There should not be a comment here',
        }
        response = self.guest_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(len(response.context['comments']), comments_count)

    def test_post_detail_page_shows_correct_context(self):
        """Authorized client can leave comment."""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Comment text',
        }
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(len(response.context['comments']), comments_count + 1)
