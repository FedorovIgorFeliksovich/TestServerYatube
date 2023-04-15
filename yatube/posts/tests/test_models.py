from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post
from .const import AUTHOR_USERNAME, GROUP_SLUG

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTHOR_USERNAME)
        cls.post = Post.objects.create(
            text="Тестовый текст больше 15 символов для проверки...",
            author=cls.user,
        )
        cls.post_model_field_to_verbose = {
            "text": "Текст поста",
            "pub_date": "Дата публикации",
            "author": "Автор",
            "group": "Группа",
        }
        cls.post_model_field_to_help = {
            "text": "Введите текст поста",
            "group": "Выберите группу",
        }

    def test_post_str(self):
        """Проверка __str__ у post."""
        self.assertEqual(PostModelTest.post.text[:15], str(PostModelTest.post))

    def test_post_verbose_name(self):
        """Проверка verbose_name у post."""
        for (
            value,
            expected,
        ) in PostModelTest.post_model_field_to_verbose.items():
            with self.subTest(value=value):
                verbose_name = self.post._meta.get_field(value).verbose_name
                self.assertEqual(verbose_name, expected)

    def test_post_help_text(self):
        """Проверка help_text у post."""
        for value, expected in PostModelTest.post_model_field_to_help.items():
            with self.subTest(value=value):
                help_text = self.post._meta.get_field(value).help_text
                self.assertEqual(help_text, expected)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug=GROUP_SLUG,
            description="Тестовое описание",
        )
        cls.group_model_field_to_verbose = {
            "title": "Заголовок",
            "slug": "ЧПУ",
            "description": "Описание",
        }

    def test_group_str(self):
        """Проверка __str__ у group."""
        self.assertEqual(GroupModelTest.group.title, str(GroupModelTest.group))

    def test_group_verbose_name(self):
        """Проверка verbose_name у group."""
        for (
            value,
            expected,
        ) in GroupModelTest.group_model_field_to_verbose.items():
            with self.subTest(value=value):
                verbose_name = self.group._meta.get_field(value).verbose_name
                self.assertEqual(verbose_name, expected)
