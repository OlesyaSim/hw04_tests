from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client, TestCase

from posts.forms import PostForm
from posts.models import Group, Post


User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='Группа Тест',
            slug='test-slug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_authorized_client(self):
        """Валидная форма создает запись в Posts."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse('posts:profile', kwargs={
                'username': PostCreateFormTests.post.author})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый пост',
                group=self.group.pk
            ).exists()
        )

    def test_create_post_guest_client(self):
        """Неавторизованный пользователь пытается создать пост"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст неавторизованного пользователя',
            'group': self.group.id,
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertFalse(Post.objects.filter(
            text='Тестовый текст неавторизованного пользователя').exists())
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(response.status_code, 200)

    def test_edit_post_authorized_client(self):
        """Авторизованный пользователь может редактировать пост"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Отредактированный пост',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True)
        self.post.refresh_from_db()
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertRedirects(
            response, reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        self.assertTrue(Post.objects.filter(text=form_data['text']).exists())
