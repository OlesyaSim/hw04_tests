from django.test import TestCase

from ..cons import LIMIT_CHAR
from ..models import Group, Post, User


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

    # def test_post_have_correct_str_method(self):
    #     """Проверяем, что у модели Post корректно работает __str__
    #     и выводит первые 15 символов поста."""
    #     post = PostModelTest.post
    #     text = post.text[:15]
    #     self.assertEqual(
    #         text,
    #         str(post),
    #         'Метод _str_ модели Post работает не корректно'
    #     )

    # def test_group_have_correct_str_method(self):
    #     """Проверяем, что у модели Group корректно работает __str__
    #     и выводит название группы."""
    #     group = PostModelTest.group
    #     title = group.title
    #     self.assertEqual(
    #         title,
    #         str(group),
    #         'Метод _str_ модели Group работает не корректно'
    #     )

    def test_post_and_group_correct_str_method(self):
        """Проверяем, что у модели Post и Group корректно работает __str__
        и выводит первые 15 символов у Post и название группы у Group.
        """
        post = PostModelTest.post
        group = PostModelTest.group
        fields = {
            post.text[:LIMIT_CHAR]: post,
            group.title: group,
        }
        for key, value in fields.items():
            with self.subTest(key=key):
                self.assertEqual(
                   value.__str__(), key
                )
