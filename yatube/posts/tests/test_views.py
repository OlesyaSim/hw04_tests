from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post


User = get_user_model()


class PostDetailTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cache.clear()
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

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
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
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        '''Шаблон index.html сформирован с правильным контекстом'''
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post0_author = first_object.author.username
        post0_text = first_object.text
        post0_group = first_object.group.title
        self.assertEqual(post0_author, 'user')
        self.assertEqual(post0_text, 'Тестовый пост')
        self.assertEqual(post0_group, 'Группа Тест')

    def test_group_list_show_correct_context(self):
        '''Шаблон group_list.html сформирован с правильным контекстом'''
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        first_object = response.context['page_obj'][0]
        post0_author = first_object.author.username
        post0_text = first_object.text
        post0_group = first_object.group.title
        post0_group_slug = first_object.group.slug
        post0_group_description = first_object.group.description
        self.assertEqual(post0_author, 'user')
        self.assertEqual(post0_text, 'Тестовый пост')
        self.assertEqual(post0_group, 'Группа Тест')
        self.assertEqual(post0_group_slug, 'test-slug')
        self.assertEqual(post0_group_description, 'Тестовое описание группы')

    def test_profile_show_correct_context(self):
        '''Шаблон profile.html сформирован с правильным контекстом'''
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'user'})
        )
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.author.username, 'user')
        self.assertEqual(first_object.text, 'Тестовый пост')
        self.assertEqual(first_object.group.title, 'Группа Тест')

    def test_post_detail_show_correct_context(self):
        '''Шаблон post_detail.html сформирован с правильным контекстом.'''
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.context.get('post'), self.post)

    def test_create_post_show_correct_context(self):
        '''Шаблон create_post.html сформирован с правильным контекстом.'''
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_show_correct_context(self):
        '''Шаблон create_post.html /Edit сформирован с правильным
        контекстом.
        '''
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_appear_on_pages(self):
        '''Тест: если при создании поста указать группу, то этот пост
        появляется на главной странице сайта, на странице выбранной группы,
        в профайле пользователя и не попал в группу, для которой не был
        предназначен.
        '''
        form_fields = {
            reverse('posts:index'): Post.objects.get(group=self.post.group),
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): Post.objects.get(group=self.post.group),
            reverse(
                'posts:profile', kwargs={'username': self.user}
            ): Post.objects.get(group=self.post.group),
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                form_field = response.context['page_obj']
                self.assertIn(expected, form_field)
