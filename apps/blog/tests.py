import pytest

from apps.common.constants import LanguageCodeTypes
from .models import Post


@pytest.mark.django_db
def test_post_name_lang_and_str():
	post = Post.objects.create(
		name="my-post",
		title="My Title",
		content="Lorem ipsum",
		language_code=LanguageCodeTypes.ENGLISH,
	)
	assert post.name_lang == "my-post-en"
	assert str(post) == "my-post - en - My Title"
