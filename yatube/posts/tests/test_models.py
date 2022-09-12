from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class ModelsTest(TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.user = User.objects.create_user(username='auth')
        self.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description',
        )
        self.post = Post.objects.create(
            author=self.user,
            text='Test post',
        )

    def test_models_have_correct_object_names(self):
        """Check if __str__ in models works correctly."""
        models = [
            (str(self.post), self.post.text[:15]),
            (str(self.group), self.group.title),
        ]
        for model, object_name in models:
            with self.subTest():
                self.assertEqual(object_name, model)

    def test_verbose_name(self):
        """Verbose names in models match ecpected"""
        verboses_list = [
            (self.post, 'text', 'Post'),
            (self.post, 'author', 'Author'),
            (self.post, 'pub_date', 'Publication date'),
            (self.post, 'group', 'Group'),
            (self.group, 'title', 'Group name'),
            (self.group, 'slug', 'Slug'),
            (self.group, 'description', 'Description'),
        ]
        for model, field, verbose in verboses_list:
            with self.subTest():
                self.assertEqual(
                    model._meta.get_field(field).verbose_name, verbose
                )

    def test_help_text(self):
        """help_text in models match expected."""
        help_text_list = [
            (self.post, 'text', 'Type your post here'),
            (self.post, 'group', 'Choose what your post is about (optional)'),
            (self.group, 'title', 'Type group name'),
            (self.group, 'slug', 'Type unique group slug'),
            (self.group, 'description', 'Type what this group is about'),
        ]
        for model, field, help_text in help_text_list:
            with self.subTest():
                self.assertEqual(
                    model._meta.get_field(field).help_text, help_text
                )
