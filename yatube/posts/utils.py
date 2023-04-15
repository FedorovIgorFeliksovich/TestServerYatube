from django.conf import settings
from django.core.paginator import Paginator


def paginate_page(request, post_list, post_per_page=settings.NUMBER_POST):
    paginator = Paginator(post_list, settings.NUMBER_POST)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return page_obj
