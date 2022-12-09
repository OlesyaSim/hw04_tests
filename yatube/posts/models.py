from django.contrib.auth import get_user_model
from django.db import models

from .cons import LIMIT_CHAR


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название группы")
    slug = models.SlugField(max_length=200, unique=True,
                            verbose_name="URL")
    description = models.TextField(verbose_name="Описание группы")

    class Meta:
        verbose_name = "группа"
        verbose_name_plural = "группы"

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(blank=False, verbose_name="Ваш пост")
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Время публикации")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name="Имя автора поста"
    )
    group = models.ForeignKey(
        Group,
        related_name='groups',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Имя группы"
    )

    def __str__(self):
        return self.text[:LIMIT_CHAR]

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = "пост"
        verbose_name_plural = "посты"
