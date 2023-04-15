import tempfile

from django.urls import reverse
from django.conf import settings


AUTHOR_USERNAME = "test_user"
GROUP_SLUG = "test_slug"
URL_INDEX = reverse("posts:index")
URL_GROUP = reverse("posts:group_list", args=[GROUP_SLUG])
URL_AUTHOR_PROFILE = reverse("posts:profile", args=[AUTHOR_USERNAME])
URL_CREATE_POST = reverse("posts:post_create")
TEST_MEDIA = tempfile.mkdtemp(dir=settings.BASE_DIR)
