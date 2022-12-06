from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_post_have_correct_str_method(self):
        """Проверяем, что у модели Post корректно работает __str__
        и выводит первые 15 символов поста."""
        post = PostModelTest.post
        text = post.text[:15]
        self.assertEqual(
            text,
            str(post),
            'Метод _str_ модели Post работает не корректно'
        )

    def test_group_have_correct_str_method(self):
        """Проверяем, что у модели Group корректно работает __str__
        и выводит название группы."""
        group = PostModelTest.group
        title = group.title
        self.assertEqual(
            title,
            str(group),
            'Метод _str_ модели Group работает не корректно'
        )
