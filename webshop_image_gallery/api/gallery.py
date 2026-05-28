import frappe
from frappe.utils import cint


@frappe.whitelist(allow_guest=True)
def get_website_item_gallery(website_item):
    """
    Return published gallery images for a Website Item.

    Resolution order for now:
    1. Product Gallery where gallery_scope = Website Item
    2. Fallback to Website Item.website_image
    3. Fallback to Item.image

    Later we will extend this for:
    - Item Template
    - Item Variant
    - Attribute Value
    """

    if not website_item:
        return {
            "source": None,
            "images": []
        }

    gallery_name = frappe.db.get_value(
        "Product Gallery",
        {
            "gallery_scope": "Website Item",
            "website_item": website_item,
            "published": 1,
        },
        "name",
        order_by="modified desc",
    )

    if gallery_name:
        gallery = frappe.get_doc("Product Gallery", gallery_name)

        images = []
        for row in gallery.images:
            if not cint(row.published):
                continue

            image_url = row.image or row.get("image_url")

            if not image_url:
                continue

            images.append({
                "image": image_url,
                "alt_text": row.alt_text or "",
                "sort_order": cint(row.sort_order),
                "is_primary": cint(row.is_primary),
                "idx": row.idx,
            })

        images = sorted(
            images,
            key=lambda image: (
                0 if image["is_primary"] else 1,
                image["sort_order"] or 9999,
                image["idx"],
            ),
        )

        if images:
            return {
                "source": "Product Gallery",
                "gallery": gallery.name,
                "images": images,
            }

    return _get_fallback_gallery(website_item)


def _get_fallback_gallery(website_item):
    website_item_data = frappe.db.get_value(
        "Website Item",
        website_item,
        ["website_image", "item_code"],
        as_dict=True,
    )

    images = []
    seen = set()

    if website_item_data:
        website_image = website_item_data.get("website_image")
        item_code = website_item_data.get("item_code")

        if website_image:
            images.append({
                "image": website_image,
                "alt_text": "",
                "sort_order": 1,
                "is_primary": 1,
                "idx": 1,
            })
            seen.add(website_image)

        if item_code:
            item_image = frappe.db.get_value("Item", item_code, "image")

            if item_image and item_image not in seen:
                images.append({
                    "image": item_image,
                    "alt_text": "",
                    "sort_order": 2,
                    "is_primary": 0 if images else 1,
                    "idx": 2,
                })

    return {
        "source": "Fallback",
        "gallery": None,
        "images": images,
    }

