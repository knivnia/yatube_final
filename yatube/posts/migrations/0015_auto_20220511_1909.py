# Generated by Django 2.2.16 on 2022-05-11 16:09

from django.db import migrations, models
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0014_auto_20220511_1858'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='unique following',
        ),
        migrations.RemoveConstraint(
            model_name='follow',
            name='check following',
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('user',), name='unique follower'),
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('author',), name='unique following'),
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.CheckConstraint(check=models.Q(_negated=True, author=django.db.models.expressions.F('user')), name='check follower is not following'),
        ),
    ]