import frappe

from webshop.templates.pages.product_search import get_product_data
from webshop.webshop.api import get_product_filter_data as webshop_get_product_filter_data
from webshop.webshop.doctype.override_doctype.item_group import get_item_for_list_in_html
from webshop.webshop.shopping_cart.product_info import set_product_info_for_website

from webshop_image_gallery.api.gallery import get_website_item_card_image


@frappe.whitelist(allow_guest=True)
def get_product_list(search=None, start=0, limit=12):
    """
    Return product search/list results with Product Gallery primary image support.
    """

    data = get_product_data(search, start, limit)

    for item in data:
        set_product_info_for_website(item)
        _apply_gallery_card_image(item)

    return [get_item_for_list_in_html(item) for item in data]


@frappe.whitelist(allow_guest=True)
def get_product_filter_data(query_args=None):
    """
    Return /all-products and Item Group product data with Product Gallery primary image support.

    This wraps Webshop's core API and only changes returned item data in memory.
    It does not sync or write images into Website Item.
    """

    result = webshop_get_product_filter_data(query_args)

    if not result or result.get("exc"):
        return result

    for item in result.get("items") or []:
        _apply_gallery_card_image(item)

    return result


def _apply_gallery_card_image(item):
    gallery_image = get_website_item_card_image(item)

    if gallery_image:
        item.website_image = gallery_image
