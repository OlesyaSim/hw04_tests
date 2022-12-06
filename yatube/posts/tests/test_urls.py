from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group


User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_not_auth = User.objects.create_user(username='not_auth')
        cls.group = Group.objects.create(
            title='test',
            slug='test_slug',
            description='test_description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_not_auth = Client()
        self.authorized_client_not_auth.force_login(self.user_not_auth)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {

            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.post.author
                            }): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id
                            }): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id
                            }): 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_200_url_exists_at_desired_location(self):
        """Страница доступна пользователю код 200."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

        response = self.guest_client.get('/group/test_slug/')
        self.assertEqual(response.status_code, 200)

        response = self.guest_client.get('/profile/auth/')
        self.assertEqual(response.status_code, 200)

        response = self.guest_client.get('/posts/1/')
        self.assertEqual(response.status_code, 200)

        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

        response = self.authorized_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, 200)

    def test_nonexistent_url_exists_at_desired_location(self):
        """Тест несуществующей страницы."""
        response = self.guest_client.get('-5')
        self.assertEqual(response.status_code, 404)

    def test_edit_url_redirect_guest_client(self):
        """Тест неавторизованый пользователь edit -> редирект страницы."""
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, 302)

        response = self.guest_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, 302)
