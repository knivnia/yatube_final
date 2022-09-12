import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Post, Group

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_new_post(self):
        """Check that create form creating new post in DB."""
        posts_count = Post.objects.count()
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
        form_data = {
            'text': 'New test post',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text=form_data['text'],
                group=self.group,
                image='posts/small.gif'
            ).exists()
        )

    def test_guest_cant_create_post(self):
        """Check that guest cannot create new post in DB."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'New test post',
            'group': self.group.id,
        }
        guest_response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            guest_response,
            f'{reverse("users:login")}?next='
            f'{reverse("posts:post_create")}')
        self.assertEqual(Post.objects.count(), posts_count)

    def test_edit_post(self):
        """Check that edited post changing in DB."""
        form_data = {
            'text': 'Edited post',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        self.assertEqual(Post.objects.get(pk=self.post.id).text,
                         form_data['text']
                         )

    def test_guest_cant_edit_post(self):
        """Check that guest cannot change post in DB."""
        form_data = {
            'text': 'Edited post',
            'group': self.group.id,
        }
        guest_response = self.guest_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            guest_response,
            f'{reverse("users:login")}?next='
            f'{reverse("posts:post_edit", kwargs={"post_id": self.post.pk})}'
        )
        self.assertNotEqual(Post.objects.get(pk=self.post.id).text,
                            form_data['text']
                            )
