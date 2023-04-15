import shutil

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Group, Post
from .const import AUTHOR_USERNAME, GROUP_SLUG, TEST_MEDIA

User = get_user_model()
image_data = (b"\x47\x49\x46\x38\x39\x61\x02\x00"
              b"\x01\x00\x80\x00\x00\x00\x00\x00"
              b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
              b"\x00\x00\x00\x2C\x00\x00\x00\x00"
              b"\x02\x00\x01\x00\x00\x02\x02\x0C"
              b"\x0A\x00\x3B")


@override_settings(MEDIA_ROOT=TEST_MEDIA)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create_user(username=AUTHOR_USERNAME)
        cls.comment_author = User.objects.create_user(
            username="comment_author"
        )
        cls.group = Group.objects.create(
            title="Тестовое название группы",
            slug=GROUP_SLUG,
            description="Тестовое описание группы",
        )
        cls.test_post = Post.objects.create(
            author=cls.post_author, text="Тестовый пост"
        )
        cls.URL_POST_COMMENT = reverse(
            "posts:add_comment", args=[cls.test_post.id]
        )
        cls.URL_POST_DETAIL = reverse(
            "posts:post_detail", args=[cls.test_post.id]
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA, ignore_errors=True)

    def setUp(self):
        self.guest_user = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.post_author)
        self.comment_user = Client()
        self.comment_user.force_login(self.comment_author)

    def test_authorized_user_create_post(self):
        """Проверка создания записи авторизированным клиентом."""
        posts_count = Post.objects.count()

        uploaded = SimpleUploadedFile(
            name="image_data.gif", content=image_data, content_type="image/gif"
        )

        form_data = {
            "text": "Текст поста",
            "group": self.group.id,
            "image": uploaded,
        }
        response = self.authorized_user.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                "posts:profile", kwargs={"username": self.post_author.username}
            ),
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.latest("id")
        self.assertEqual(post.text, form_data["text"])
        self.assertEqual(post.author, self.post_author)
        self.assertEqual(post.group_id, form_data["group"])
        self.assertEqual(post.image, f'posts/{form_data["image"]}')

    def test_authorized_user_edit_post(self):
        """Проверка редактирования записи авторизированным клиентом."""
        post = Post.objects.create(
            text="Текст поста для редактирования",
            author=self.post_author,
            group=self.group,
        )
        form_data = {
            "text": "Отредактированный текст поста",
            "group": self.group.id,
        }
        response = self.authorized_user.post(
            reverse("posts:post_edit", args=[post.id]),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, reverse("posts:post_detail", kwargs={"post_id": post.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post = Post.objects.latest("id")
        self.assertTrue(post.text == form_data["text"])
        self.assertTrue(post.author == self.post_author)
        self.assertTrue(post.group_id == form_data["group"])

    def test_nonauthorized_user_create_post(self):
        """Проверка создания записи не авторизированным пользователем."""
        posts_count = Post.objects.count()
        form_data = {"text": "Текст поста", "group": self.group.id}
        response = self.guest_user.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        redirect = reverse("login") + "?next=" + reverse("posts:post_create")
        self.assertRedirects(response, redirect)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_comment_post(self):
        post_comments = PostFormTests.test_post.comments.count()
        form_data = {"text": "Тестовый комментарий из формы"}
        response = self.comment_user.post(
            PostFormTests.URL_POST_COMMENT, data=form_data, follow=True
        )
        self.assertEqual(
            PostFormTests.test_post.comments.count(), post_comments + 1
        )
        self.assertRedirects(response, PostFormTests.URL_POST_DETAIL)
        added_comment = PostFormTests.test_post.comments.latest("id")
        self.assertEqual(added_comment.text, form_data["text"])

    def test_comment_post_anonymous(self):
        post_comments = PostFormTests.test_post.comments.count()
        form_data = {"text": "Тестовый комментарий из формы"}
        response = self.guest_user.post(
            PostFormTests.URL_POST_COMMENT, data=form_data, follow=True
        )
        self.assertEqual(
            PostFormTests.test_post.comments.count(), post_comments
        )
        self.assertRedirects(
            response, f"/auth/login/?next={PostFormTests.URL_POST_COMMENT}"
        )
