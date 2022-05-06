from enum import Enum

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group

User = get_user_model()


class AuthorizeRoles(Enum):
    AUTHOR = 1
    READER = 2
    GUEST = 3


class PostUrlsTests(TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()

        self.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description',
        )

        self.author = User.objects.create_user(username='Grogu')
        self.reader = User.objects.create_user(username='Luke')

        self.post = Post.objects.create(
            author=self.author,
            text='Test post',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()

    # test for URLs
    def test_pages_url(self):
        """Check if all URLs match expected."""
        pages_urls = [
            ('/', reverse('posts:main_page')),
            (f'/group/{self.group.slug}/', reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            )),
            (f'/profile/{self.post.author}/', reverse(
                'posts:profile',
                kwargs={'username': self.post.author}
            )),
            (f'/posts/{self.post.id}/', reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )),
            ('/create/', reverse('posts:post_create')),
            (f'/posts/{self.post.id}/edit/', reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            )),
        ]
        for url, expected in pages_urls:
            with self.subTest(url=url):
                self.assertEqual(url, expected)

    # test for pages statuses
    def test_pages_urls_exists_at_desired_location(self):
        """
           Main,group,profile and post detail pages are available for everyone.
           Create page is available only for authorized clients.
           Edit page is available only for post author.
        """
        page_list = [
            (reverse('posts:main_page'), 200, AuthorizeRoles.AUTHOR),
            (reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ), 200, AuthorizeRoles.GUEST),
            (reverse(
                'posts:profile',
                kwargs={'username': self.post.author}
            ), 200, AuthorizeRoles.GUEST),
            (reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ), 200, AuthorizeRoles.GUEST),
            (reverse('posts:post_create'), 302, AuthorizeRoles.GUEST),
            (reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ), 302, AuthorizeRoles.GUEST),
            ('/unexisting_page/', 404, AuthorizeRoles.GUEST),
            (reverse('posts:post_create'), 200, AuthorizeRoles.READER),
            (reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ), 200, AuthorizeRoles.AUTHOR),
            (reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ), 302, AuthorizeRoles.READER),
        ]
        for address, code, auth in page_list:
            with self.subTest():
                if auth == AuthorizeRoles.AUTHOR:
                    self.authorized_client.force_login(self.author)
                    response = self.authorized_client.get(address)
                elif auth == AuthorizeRoles.READER:
                    self.authorized_client.force_login(self.reader)
                    response = self.authorized_client.get(address)
                else:
                    response = self.guest_client.get(address)
                self.assertEqual(response.status_code, code)

    # test for templates
    def test_pages_use_correct_template(self):
        """Check if all URLs use the correct templates."""
        templates_pages_names = [
            (reverse('posts:main_page'), 'posts/index.html'),
            (reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ), 'posts/group_list.html'),
            (reverse(
                'posts:profile',
                kwargs={'username': self.post.author}
            ), 'posts/profile.html'),
            (reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ), 'posts/post_detail.html'),
            (reverse('posts:post_create'), 'posts/create_post.html'),
            (reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ), 'posts/create_post.html'),
            ('/unexisting_page/', 'core/404.html'),  # added in sprint6
        ]
        for url, template in templates_pages_names:
            with self.subTest(url=url):
                self.authorized_client.force_login(self.author)
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
