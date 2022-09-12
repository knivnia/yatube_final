from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    id = models.AutoField(primary_key=True)
    text = models.TextField(
        verbose_name='Post',
        help_text='Type your post here'
    )
    pub_date = models.DateTimeField(
        verbose_name='Publication date',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        verbose_name='Author',
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        'Group',
        models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Group',
        help_text='Choose what your post is about (optional)'
    )
    image = models.ImageField(
        verbose_name='Image',
        upload_to='posts/',
        blank=True,
        help_text='Upload your image here (optional)'
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(
        verbose_name='Group name',
        help_text='Type group name',
        max_length=200)
    slug = models.SlugField(
        verbose_name='Slug',
        help_text='Type unique group slug',
        unique=True,
        max_length=20)
    description = models.TextField(
        verbose_name='Description',
        help_text='Type what this group is about')

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        'Post',
        verbose_name='Post',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Commenter',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(
        verbose_name='Comment',
        help_text='Type your comment here'
    )
    created = models.DateTimeField(
        verbose_name='Comment created',
        auto_now_add=True
    )

    class Meta:
        ordering = ('created',)


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique following'
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name='check following'
            )
        ]
