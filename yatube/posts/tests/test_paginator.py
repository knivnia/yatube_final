from math import ceil

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group

User = get_user_model()


class PaginatorTest(TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description',
        )
        self.user = User.objects.create_user(username='Grogu')
        self.POSTS_AMOUNT = 13
        Post.objects.bulk_create(
            Post(
                author=self.user,
                text=f'Test post {post_num}',
                group=self.group
            ) for post_num in range(self.POSTS_AMOUNT)
        )

    def setUp(self):
        self.guest_client = Client()

    def test_paginator_pages_show_correct_context(self):
        """Pages in paginator show correct context."""
        page_list = (
            reverse('posts:main_page'),
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': self.user}
            )
        )
        last_page_num = ceil(self.POSTS_AMOUNT / settings.PAGINATOR_AMOUNT)
        last_page_posts_amount = (self.POSTS_AMOUNT
                                  - (last_page_num - 1)
                                  * settings.PAGINATOR_AMOUNT)
        for page in page_list:
            with self.subTest():
                first_response = self.guest_client.get(page)
                self.assertEqual(len(
                    first_response.context['page_obj']),
                    settings.PAGINATOR_AMOUNT
                )
                last_response = self.guest_client.get(
                    page,
                    {'page': last_page_num}
                )
                self.assertEqual(len(
                    last_response.context['page_obj']),
                    last_page_posts_amount
                )
