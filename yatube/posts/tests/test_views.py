import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from posts.models import Post, Group
from posts.forms import PostForm

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description',
        )
        self.wrong_group = Group.objects.create(
            title='Wrong group',
            slug='wrong-slug',
            description='Wrong description',
        )
        self.user = User.objects.create_user(username='Grogu')
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        self.post = Post.objects.create(
            author=self.user,
            text='Test post',
            group=self.group,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # tests for context on pages without forms
    def test_pages_shows_correct_context(self):
        """Check if main,group and profile pages show correct context."""
        page_list = (
            reverse('posts:main_page'),
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author}
            )
        )
        for page in page_list:
            with self.subTest():
                response = self.authorized_client.get(page)
                self.assertIn(self.post, response.context['page_obj'])

    def test_group_and_profile_pages_show_correct_context(self):
        """Check if group and profile pages show correct context."""
        page_list = [
            (reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ), 'group', self.group),
            (reverse(
                'posts:profile',
                kwargs={'username': self.post.author}
            ), 'author', self.post.author)
        ]
        for page, obj, expected_obj in page_list:
            with self.subTest():
                response = self.authorized_client.get(page)
                self.assertEqual(response.context[obj], expected_obj)

    def test_post_detail_shows_correct_context(self):
        """Check if post details page shows correct context."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        self.assertEqual(response.context['post'],
                         self.post)

    # test for context on page with form
    def test_edit_post_shows_correct_context(self):
        """Check if edit page shows correct context."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            )
        )
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertEqual(
            response.context['form'].instance,
            self.post
        )

    def test_first_wrong_group_page_contains_zero_records(self):
        """Check if new post does not showing in other group"""
        response = self.guest_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.wrong_group.slug}
            )
        )
        self.assertNotIn(self.post, response.context['page_obj'])

    # test for cache
    def test_cache_on_main_page(self):
        """Posts saved in cache on main page."""
        response = self.authorized_client.get(
            reverse('posts:main_page')
        )
        post_count = len(response.context['page_obj'])
        Post.objects.get(id=self.post.id).delete()
        self.assertEqual(post_count, len(response.context['page_obj']))
        cache.clear()
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())
